# DeepDoc PDF Parser

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://python.org)

**专业的 PDF 解析库 - 基于 RAGFlow DeepDoc 模块抽取**

这是一个从 [RAGFlow](https://github.com/infiniflow/ragflow) 项目的 DeepDoc 模块中抽取出来的专门用于 PDF 解析的 Python 库。它提供了强大的 PDF 文档解析能力，支持 OCR 文字识别、智能布局分析、表格提取等高级功能。

## ✨ 特性

- 🔍 **智能 OCR 识别** - 基于深度学习的文字识别，支持中英文混合文档
- 📄 **布局分析** - 自动识别文档结构，区分标题、正文、表格、图片等
- 📊 **表格提取** - 智能识别和提取表格内容，输出结构化 HTML
- 🚀 **高性能** - 支持并行处理，提高解析速度
- 🎯 **智能分块** - 自动将文档分割成有意义的文本块
- 📱 **易于使用** - 提供简洁的 API 接口，一行代码即可使用

## 📦 安装

使用 uv（推荐）：

```bash
uv add deepdoc-pdfparser
```

使用 pip：

```bash
pip install deepdoc-pdfparser
```

## 🚀 快速开始

### 基本用法

```python
from deepdoc_pdfparser import parse_pdf

# 解析PDF文件
result = parse_pdf("document.pdf")

# 查看解析结果
print(f"共解析出 {len(result)} 个文本块")
print(f"包含 {len(result.tables)} 个表格")

# 遍历文本块
for chunk in result:
    print(f"页码: {chunk.page_number}")
    print(f"内容: {chunk.content}")
    print(f"布局类型: {chunk.layout_type}")
    print("-" * 50)
```

### 提取所有文本

```python
from deepdoc_pdfparser import extract_text

# 直接提取所有文本
text = extract_text("document.pdf")
print(text)
```

### 按页面提取

```python
from deepdoc_pdfparser import extract_text_by_page

# 提取第一页的文本
page_text = extract_text_by_page("document.pdf", page_number=0)
print(page_text)
```

### 提取表格

```python
from deepdoc_pdfparser import extract_tables

# 提取所有表格（HTML格式）
tables = extract_tables("document.pdf")
for i, table_html in enumerate(tables):
    print(f"表格 {i+1}:")
    print(table_html)
```

### 高级用法

```python
from deepdoc_pdfparser import PdfParser

# 创建解析器实例
parser = PdfParser()

# 自定义进度回调
def progress_callback(progress, message):
    print(f"进度: {progress:.1%} - {message}")

# 解析指定页面范围
result = parser.parse(
    "document.pdf",
    from_page=0,      # 起始页（从0开始）
    to_page=10,       # 结束页
    callback=progress_callback
)

# 按页面获取文本
page_2_text = result.get_text_by_page(2)
print(page_2_text)

# 按页面获取表格
page_2_tables = result.get_tables_by_page(2)
for table in page_2_tables:
    print(table.html)
```

### 简单解析模式

如果你的 PDF 文档质量较好，可以使用简单模式（不使用 OCR）：

```python
from deepdoc_pdfparser import parse_pdf_simple

# 简单解析（更快，但不支持OCR）
result = parse_pdf_simple("document.pdf")
text = result.get_text()
```

### 处理二进制数据

```python
from deepdoc_pdfparser import parse_pdf_binary

# 从二进制数据解析
with open("document.pdf", "rb") as f:
    pdf_binary = f.read()

result = parse_pdf_binary(pdf_binary, filename="document.pdf")
```

## 📚 API 参考

### 主要类

#### `PdfParser`

专业的 PDF 解析器，支持 OCR 和布局分析。

**方法**：

- `parse(pdf_path, from_page=0, to_page=100000, callback=None, **kwargs)` - 解析 PDF 文件
- `parse_binary(pdf_binary, filename="document.pdf", **kwargs)` - 解析二进制数据

#### `PlainPdfParser`

简单的 PDF 解析器，不使用 OCR。

**方法**：

- `parse(pdf_path, **kwargs)` - 简单解析 PDF 文件

### 数据类型

#### `ParseResult`

解析结果容器。

**属性**：

- `chunks: List[ChunkResult]` - 文本块列表
- `tables: List[TableResult]` - 表格列表
- `metadata: Dict[str, Any]` - 元数据

**方法**：

- `get_text() -> str` - 获取所有文本
- `get_text_by_page(page_number: int) -> str` - 获取指定页面文本
- `get_tables_by_page(page_number: int) -> List[TableResult]` - 获取指定页面表格

#### `ChunkResult`

文本块结果。

**属性**：

- `content: str` - 文本内容
- `page_number: int` - 页码
- `position: Optional[Tuple[float, float, float, float]]` - 位置信息
- `layout_type: Optional[str]` - 布局类型
- `raw_data: Optional[Dict[str, Any]]` - 原始数据

#### `TableResult`

表格结果。

**属性**：

- `html: str` - 表格 HTML
- `page_number: Optional[int]` - 页码
- `position: Optional[Tuple[float, float, float, float]]` - 位置信息

### 便捷函数

- `parse_pdf(pdf_path, **kwargs)` - 解析 PDF（推荐）
- `parse_pdf_simple(pdf_path, **kwargs)` - 简单解析 PDF
- `extract_text(pdf_path, **kwargs)` - 提取所有文本
- `extract_text_by_page(pdf_path, page_number, **kwargs)` - 提取指定页面文本
- `extract_tables(pdf_path, **kwargs)` - 提取所有表格
- `parse_pdf_binary(pdf_binary, filename, **kwargs)` - 解析二进制数据

## 🎯 支持的文档类型

- **PDF 文档** - 主要支持的格式
- **扫描版 PDF** - 通过 OCR 识别文字
- **多语言文档** - 支持中英文混合文档
- **复杂布局** - 支持多栏、表格、图文混排

## ⚙️ 系统要求

- Python 3.8+
- 建议使用 GPU（可选，用于加速深度学习模型）
- 内存建议 4GB 以上

## 🤝 致谢

本项目基于 [RAGFlow](https://github.com/infiniflow/ragflow) 的 DeepDoc 模块开发，感谢 RAGFlow 团队的杰出工作。

**原始项目**：

- GitHub: https://github.com/infiniflow/ragflow
- 许可证: Apache 2.0

## 📄 许可证

本项目采用 Apache 2.0 许可证。详见 [LICENSE](LICENSE) 文件。

## 🚧 注意事项

1. **首次使用**：首次运行时会自动下载深度学习模型，请确保网络连接正常
2. **模型文件**：模型文件会缓存到本地，约需要几百 MB 空间
3. **性能优化**：建议在 GPU 环境下运行以获得更好的性能
4. **内存使用**：解析大型 PDF 文件时可能需要较多内存

## 🔧 开发

### 安装开发依赖

```bash
uv add deepdoc-pdfparser[dev]
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black deepdoc_pdfparser/
isort deepdoc_pdfparser/
```

## 📞 支持

如果你遇到问题或有建议，请：

1. 查看 [FAQ](#)
2. 提交 [Issue](https://github.com/yourusername/deepdoc-pdfparser/issues)
3. 参考原始 [RAGFlow 项目](https://github.com/infiniflow/ragflow)
