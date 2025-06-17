# RAGFlow DeepDOC 代码架构深度解析

## 项目结构概览

```
ragflow/
├── api/                    # API层：配置和工具函数
│   ├── constants.py       # 常量定义
│   ├── settings.py        # 配置管理
│   └── utils/             # 工具函数
│       ├── __init__.py    # 通用工具（加密、序列化等）
│       └── file_utils.py  # 文件操作工具
├── deepdoc/               # 深度文档处理核心
│   ├── parser/           # 文档解析器
│   │   ├── pdf_parser.py # PDF解析引擎(核心)
│   │   ├── docx_parser.py# DOCX解析器
│   │   ├── txt_parser.py # TXT解析器
│   │   └── utils.py      # 解析工具
│   └── vision/           # 计算机视觉模块
│       ├── ocr.py        # OCR引擎
│       ├── layout_recognizer.py    # 布局识别
│       ├── table_structure_recognizer.py # 表格识别
│       ├── recognizer.py # 基础识别器
│       ├── operators.py  # 图像操作
│       └── postprocess.py# 后处理
├── rag/                   # RAG处理层
│   ├── app/              # 应用入口
│   │   ├── manual.py     # Manual模式处理(入口)
│   │   ├── picture.py    # 图片处理
│   │   └── prompts.py    # 提示词模板
│   ├── nlp/              # 自然语言处理
│   │   ├── __init__.py   # NLP工具函数
│   │   └── rag_tokenizer.py # 分词器
│   ├── utils/            # RAG工具
│   │   └── __init__.py   # Token计算等
│   └── res/              # 资源文件
│       ├── deepdoc/      # 深度学习模型
│       │   ├── det.onnx  # 文本检测模型
│       │   ├── rec.onnx  # 文字识别模型
│       │   ├── layout.manual.onnx # 布局识别模型
│       │   ├── tsr.onnx  # 表格结构识别
│       │   └── updown_concat_xgb.model # 文本合并
│       ├── huqie.txt     # 中文分词词典
│       └── huqie.txt.trie# 分词索引
└── conf/
    └── service_conf.yaml  # 服务配置
```

## 核心组件详细分析

### 1. 入口层：manual.py

```python
# file_load/ragflow/rag/app/manual.py
def chunk(filename, binary=None, from_page=0, to_page=100000,
          lang="Chinese", callback=None, **kwargs):
    """
    主要入口函数：处理PDF文档并返回语义分块

    Args:
        filename: PDF文件路径
        binary: 二进制数据（可选）
        from_page, to_page: 页面范围
        lang: 语言类型
        callback: 进度回调函数

    Returns:
        sections: 文本段落列表 [(text, layout_type, position), ...]
        tables: 表格列表
    """

    # 1. 初始化PDF解析器
    pdf_parser = Pdf()  # 继承自RAGFlowPdfParser

    # 2. 执行核心解析流程
    sections, tbls = pdf_parser(
        filename,
        from_page=from_page,
        to_page=to_page,
        callback=callback
    )

    # 3. 基于文档大纲进行智能分块
    if has_outlines:
        chunks = outline_based_chunking(sections)
    else:
        chunks = content_based_chunking(sections)

    return chunks, tbls
```

**设计亮点**：

- **简洁的 API 设计**：一个函数完成复杂的 PDF 处理
- **灵活的参数配置**：支持页面范围、语言、回调等
- **多种分块策略**：基于大纲或内容的自适应分块

### 2. 核心引擎：RAGFlowPdfParser

```python
# file_load/ragflow/deepdoc/parser/pdf_parser.py
class RAGFlowPdfParser:
    def __init__(self, **kwargs):
        """初始化多模态处理组件"""
        # 1. OCR引擎：文字检测与识别
        self.ocr = OCR()

        # 2. 布局识别器：根据模型类型选择
        if hasattr(self, "model_speciess"):
            self.layouter = LayoutRecognizer("layout." + self.model_speciess)
        else:
            self.layouter = LayoutRecognizer("layout")

        # 3. 表格结构识别器
        self.tbl_det = TableStructureRecognizer()

        # 4. XGBoost文本合并模型
        self.updown_cnt_mdl = xgb.Booster()
        self.updown_cnt_mdl.load_model("updown_concat_xgb.model")

        # 5. 并行处理支持
        if PARALLEL_DEVICES > 1:
            self.parallel_limiter = [
                trio.CapacityLimiter(1)
                for _ in range(PARALLEL_DEVICES)
            ]

    def __call__(self, fnm, need_image=True, zoomin=3, return_html=False):
        """主要处理流程"""
        # 第一阶段：图像提取与OCR
        self.__images__(fnm, zoomin)

        # 第二阶段：布局识别
        self._layouts_rec(zoomin)

        # 第三阶段：表格检测
        self._table_transformer_job(zoomin)

        # 第四阶段：文本合并
        self._text_merge()
        self._concat_downward()

        # 第五阶段：后处理
        self._filter_forpages()
        tbls = self._extract_table_figure(need_image, zoomin, return_html, False)

        return self.__filterout_scraps(deepcopy(self.boxes), zoomin), tbls
```

**架构优势**：

- **模块化设计**：每个阶段功能独立，便于维护和优化
- **可配置性**：支持不同模型和参数配置
- **异步并行**：支持多 GPU 并行处理
- **内存优化**：流式处理避免内存溢出

### 3. 智能文本合并算法

这是 RAGFlow 最核心的创新算法：

```python
def _updown_concat_features(self, up, down):
    """提取32维特征向量用于文本合并判断"""
    w = max(self.__char_width(up), self.__char_width(down))
    h = max(self.__height(up), self.__height(down))
    y_dis = self._y_dis(up, down)

    # 提取文本特征
    tks_down = rag_tokenizer.tokenize(down["text"][:6]).split()
    tks_up = rag_tokenizer.tokenize(up["text"][-6:]).split()

    # 构建32维特征向量
    features = [
        # 位置关系特征
        up.get("R", -1) == down.get("R", -1),        # 同一行
        y_dis / h,                                    # 垂直距离比
        down["page_number"] - up["page_number"],      # 跨页关系

        # 布局类型特征
        up["layout_type"] == down["layout_type"],     # 布局类型相同
        up["layout_type"] == "text",                  # 上文本框是文本
        down["layout_type"] == "text",                # 下文本框是文本

        # 语言语义特征
        bool(re.search(r"([。？！；!?;+)）]|[a-z]\.)$", up["text"])),    # 句子结束
        bool(re.search(r"[，：'"、0-9（+-]$", up["text"])),              # 逗号结束
        bool(re.search(r"(^.?[/,?;:\]，。；：'"？！》】）-])", down["text"])), # 标点开始

        # 项目符号匹配
        self._match_proj(down),                       # 下文本是项目符号

        # 格式特征
        bool(re.match(r"[A-Z]", down["text"])),       # 大写字母开始
        bool(re.match(r"[0-9.%,-]+$", down["text"])), # 纯数字内容

        # 几何特征
        up["x0"] > down["x1"],                        # 位置关系
        abs(self.__height(up) - self.__height(down)) / min(self.__height(up), self.__height(down)), # 高度比
        self._x_dis(up, down) / max(w, 0.000001),     # 水平距离

        # 文本长度特征
        (len(up["text"]) - len(down["text"])) / max(len(up["text"]), len(down["text"])),

        # 分词特征
        len(tks_down) - len(tks_up),                  # 分词数量差
        tks_down[-1] == tks_up[-1] if tks_down and tks_up else False, # 尾词相同

        # 行内位置特征
        max(down["in_row"], up["in_row"]),            # 最大行内位置
        abs(down["in_row"] - up["in_row"]),           # 行内位置差

        # 更多语义特征...
    ]
    return features

def _concat_downward(self, concat_between_pages=True):
    """基于特征的智能文本合并"""
    # 1. 为每对相邻文本框提取特征
    for i in range(len(self.boxes) - 1):
        up, down = self.boxes[i], self.boxes[i + 1]
        features = self._updown_concat_features(up, down)

        # 2. 使用XGBoost模型预测合并概率
        merge_prob = self.updown_cnt_mdl.predict([features])[0]

        # 3. 基于概率阈值决定是否合并
        if merge_prob > 0.5:  # 可调节的阈值
            # 执行合并操作
            merged_text = up["text"] + " " + down["text"]
            # 更新边界框信息
            # 保持位置追踪信息
```

**算法创新点**：

- **多维度特征**: 结合位置、语义、格式、几何等 32 个特征
- **机器学习驱动**: 使用 XGBoost 模型替代手工规则
- **语义感知**: 理解句法结构和标点符号含义
- **跨页处理**: 智能处理跨页文本的连接

### 4. 多模态视觉组件

#### 4.1 OCR 引擎架构

```python
# file_load/ragflow/deepdoc/vision/ocr.py
class OCR:
    def __init__(self):
        # 文本检测模型：det.onnx (4.5MB)
        self.det_model = DetModel("det.onnx")

        # 文字识别模型：rec.onnx (10MB)
        self.rec_model = RecModel("rec.onnx")

        # 后处理器
        self.postprocessor = DBPostProcess()

    def __call__(self, image_list):
        """端到端OCR处理"""
        results = []
        for img in image_list:
            # 1. 文本检测：找到文字区域
            text_boxes = self.det_model(img)

            # 2. 文字识别：识别文字内容
            texts = []
            for box in text_boxes:
                cropped = crop_image(img, box)
                text = self.rec_model(cropped)
                texts.append(text)

            # 3. 后处理：坐标转换和置信度过滤
            result = self.postprocessor(text_boxes, texts)
            results.append(result)

        return results
```

#### 4.2 布局识别器

```python
# file_load/ragflow/deepdoc/vision/layout_recognizer.py
class LayoutRecognizer(Recognizer):
    labels = [
        "title", "text", "reference", "figure", "figure caption",
        "table", "table caption", "equation", "footer", "header"
    ]

    def __call__(self, image_list, ocr_res, scale_factor=3, thr=0.2):
        """布局识别主流程"""
        # 1. 调用深度学习模型进行布局检测
        layouts = super().__call__(image_list, thr)

        # 2. 将布局信息与OCR结果关联
        boxes = []
        for pn, lts in enumerate(layouts):
            bxs = ocr_res[pn]

            # 为每个OCR文本框分配布局标签
            for layout_type in self.labels:
                self._assign_layout_type(bxs, lts, layout_type)

            # 3. 处理特殊情况（页眉页脚过滤等）
            bxs = self._filter_garbage(bxs, lts)
            boxes.extend(bxs)

        return boxes, layouts

    def _assign_layout_type(self, boxes, layouts, layout_type):
        """为文本框分配布局类型"""
        layout_regions = [lt for lt in layouts if lt["type"] == layout_type]

        for box in boxes:
            if box.get("layout_type"):
                continue

            # 找到重叠度最高的布局区域
            best_overlap = self.find_overlapped_with_threashold(
                box, layout_regions, thr=0.4
            )

            if best_overlap is not None:
                box["layout_type"] = layout_type
                box["layoutno"] = f"{layout_type}-{best_overlap}"
```

### 5. 表格结构识别

```python
# file_load/ragflow/deepdoc/vision/table_structure_recognizer.py
class TableStructureRecognizer(Recognizer):
    def __call__(self, images):
        """表格结构识别"""
        results = []
        for img in images:
            # 1. 使用tsr.onnx模型检测表格结构
            table_structure = self.model(img)

            # 2. 解析单元格、行、列信息
            cells = self._parse_cells(table_structure)
            rows = self._parse_rows(table_structure)
            cols = self._parse_cols(table_structure)

            # 3. 构建表格HTML结构
            html_table = self._build_html_table(cells, rows, cols)

            results.append({
                "cells": cells,
                "rows": rows,
                "cols": cols,
                "html": html_table
            })

        return results

    def _build_html_table(self, cells, rows, cols):
        """构建结构化HTML表格"""
        html = "<table>"

        for row in sorted(rows, key=lambda r: r["top"]):
            html += "<tr>"
            row_cells = self._get_cells_in_row(cells, row)

            for cell in sorted(row_cells, key=lambda c: c["left"]):
                # 处理合并单元格
                colspan = self._calculate_colspan(cell, cols)
                rowspan = self._calculate_rowspan(cell, rows)

                attrs = ""
                if colspan > 1: attrs += f' colspan="{colspan}"'
                if rowspan > 1: attrs += f' rowspan="{rowspan}"'

                html += f"<td{attrs}>{cell['text']}</td>"

            html += "</tr>"

        html += "</table>"
        return html
```

## 性能优化设计

### 1. 并行处理架构

```python
# 异步并行OCR处理
async def __img_ocr_launcher():
    async def __img_ocr(i, id, img, chars, limiter):
        async with limiter:  # 限制并发数
            return await self.__ocr(i, img, chars, device_id=id)

    # 创建并行任务
    tasks = []
    for i, (img, chars) in enumerate(zip(images, char_list)):
        device_id = i % PARALLEL_DEVICES
        limiter = self.parallel_limiter[device_id]

        task = __img_ocr(i, device_id, img, chars, limiter)
        tasks.append(task)

    # 并行执行所有OCR任务
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 内存管理策略

```python
def __images__(self, fnm, zoomin=3, page_from=0, page_to=299, callback=None):
    """流式图像处理，避免内存溢出"""
    self.page_images = []

    # 分批处理页面，避免一次性加载所有页面
    batch_size = 10  # 每批处理10页

    for batch_start in range(page_from, min(page_to, self.total_page), batch_size):
        batch_end = min(batch_start + batch_size, page_to, self.total_page)

        # 处理当前批次
        batch_images = self._load_page_batch(fnm, batch_start, batch_end, zoomin)
        self.page_images.extend(batch_images)

        # 及时回调进度
        if callback:
            progress = (batch_end - page_from) / (page_to - page_from)
            callback(progress, f"Processed pages {batch_start}-{batch_end}")

        # 可选：释放已处理的图像内存
        if batch_start > 0:
            self._cleanup_old_images(batch_start)
```

### 3. 模型懒加载机制

```python
class ModelManager:
    def __init__(self):
        self._models = {}

    def get_model(self, model_name):
        """懒加载模型，避免启动时内存占用过大"""
        if model_name not in self._models:
            model_path = self._get_model_path(model_name)
            self._models[model_name] = self._load_model(model_path)
        return self._models[model_name]

    def _load_model(self, model_path):
        """根据模型类型选择加载方式"""
        if model_path.endswith('.onnx'):
            return onnxruntime.InferenceSession(model_path)
        elif model_path.endswith('.model'):
            booster = xgb.Booster()
            booster.load_model(model_path)
            return booster
        else:
            raise ValueError(f"Unsupported model format: {model_path}")
```

## 可扩展性设计

### 1. 插件化解析器架构

```python
class ParserFactory:
    """解析器工厂，支持动态注册新的解析器"""
    _parsers = {
        ParserType.MANUAL: RAGFlowPdfParser,
        ParserType.PLAIN: PlainParser,
        # 可以轻松添加新的解析器类型
    }

    @classmethod
    def create_parser(cls, parser_type: ParserType):
        parser_class = cls._parsers.get(parser_type)
        if not parser_class:
            raise ValueError(f"Unknown parser type: {parser_type}")
        return parser_class()

    @classmethod
    def register_parser(cls, parser_type: ParserType, parser_class):
        """注册新的解析器类型"""
        cls._parsers[parser_type] = parser_class
```

### 2. 可配置的处理流水线

```python
class ProcessingPipeline:
    """可配置的文档处理流水线"""
    def __init__(self, config):
        self.stages = []

        # 根据配置动态构建处理阶段
        if config.get("enable_ocr", True):
            self.stages.append(OCRStage())

        if config.get("enable_layout", True):
            layout_model = config.get("layout_model", "layout.manual")
            self.stages.append(LayoutStage(layout_model))

        if config.get("enable_table", True):
            self.stages.append(TableStage())

        if config.get("enable_merge", True):
            merge_threshold = config.get("merge_threshold", 0.5)
            self.stages.append(MergeStage(merge_threshold))

    def process(self, document):
        """执行完整的处理流水线"""
        result = document
        for stage in self.stages:
            result = stage.process(result)
        return result
```

## 总结

RAGFlow DeepDOC 的代码架构具有以下突出特点：

1. **分层设计**: API 层 → 应用层 → 核心引擎层 → 视觉组件层，职责清晰
2. **模块化**: 每个组件功能独立，便于测试和维护
3. **可扩展**: 支持新解析器类型和处理流水线的动态配置
4. **高性能**: 异步并行、内存优化、模型懒加载等优化策略
5. **智能化**: 基于机器学习的文本合并，替代传统启发式规则

这种架构设计使得 RAGFlow DeepDOC 既能处理复杂的文档解析任务，又保持了良好的代码质量和可维护性。
