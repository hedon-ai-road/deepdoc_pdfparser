# DeepDoc PDF Parser

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.12+-brightgreen.svg)](https://python.org)

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

### 便捷函数

#### `parse_pdf(pdf_path, from_page=0, to_page=100000, callback=None, **kwargs)`

使用深度学习模型解析 PDF 文件的主要函数。

**参数**：

- `pdf_path` (str): PDF 文件路径
- `from_page` (int): 起始页码（从 0 开始）
- `to_page` (int): 结束页码
- `callback` (Callable): 进度回调函数
- `**kwargs`: 其他参数

**返回**：

- `ParseResult`: 解析结果对象

#### `extract_text(pdf_path, **kwargs)`

提取 PDF 中的所有文本。

**参数**：

- `pdf_path` (str): PDF 文件路径
- `**kwargs`: 其他参数

**返回**：

- `str`: 提取的文本内容

#### `extract_text_by_page(pdf_path, page_number, **kwargs)`

提取 PDF 指定页面的文本。

**参数**：

- `pdf_path` (str): PDF 文件路径
- `page_number` (int): 页码（从 0 开始）
- `**kwargs`: 其他参数

**返回**：

- `str`: 提取的文本内容

#### `extract_tables(pdf_path, **kwargs)`

提取 PDF 中的所有表格（HTML 格式）。

**参数**：

- `pdf_path` (str): PDF 文件路径
- `**kwargs`: 其他参数

**返回**：

- `List[str]`: 表格的 HTML 列表

#### `parse_pdf_binary(pdf_binary, filename="document.pdf", **kwargs)`

解析 PDF 二进制数据。

**参数**：

- `pdf_binary` (bytes): PDF 二进制数据
- `filename` (str): 文件名（用于显示）
- `**kwargs`: 其他参数

**返回**：

- `ParseResult`: 解析结果对象

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
- `confidence: Optional[float]` - 置信度
- `raw_data: Optional[Dict[str, Any]]` - 原始数据

#### `TableResult`

表格结果。

**属性**：

- `html: str` - 表格 HTML
- `page_number: Optional[int]` - 页码
- `position: Optional[Tuple[float, float, float, float]]` - 位置信息

## 📋 示例

### 完整示例

```python
from deepdoc_pdfparser import parse_pdf, extract_text, extract_tables

# 解析PDF文件
pdf_path = "example.pdf"

# 方法1: 使用便捷函数快速提取文本
text = extract_text(pdf_path)
print("提取的文本:")
print(text)

# 方法2: 使用便捷函数提取表格
tables = extract_tables(pdf_path)
print(f"\n找到 {len(tables)} 个表格:")
for i, table in enumerate(tables):
    print(f"表格 {i+1}:")
    print(table)

# 方法3: 使用完整解析获取详细信息
result = parse_pdf(pdf_path)
print(f"\n解析结果:")
print(f"总文本块: {len(result.chunks)}")
print(f"总表格: {len(result.tables)}")
print(f"元数据: {result.metadata}")

# 查看每个文本块的详细信息
for chunk in result.chunks:
    print(f"页码: {chunk.page_number}")
    print(f"布局类型: {chunk.layout_type}")
    print(f"内容: {chunk.content[:100]}...")
    if chunk.position:
        print(f"位置: {chunk.position}")
    print("-" * 50)
```

## ⚙️ 配置和依赖

本库依赖于 RAGFlow 的 DeepDoc 模块。请确保：

1. 已正确安装所有依赖
2. 模型文件位于正确的路径
3. 系统有足够的内存处理大型 PDF 文件

## 🤝 贡献

欢迎贡献代码！请：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 Apache 2.0 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

本项目基于 [RAGFlow](https://github.com/infiniflow/ragflow) 项目的 DeepDoc 模块开发。感谢 RAGFlow 团队的出色工作。

## 📞 支持

如果您遇到问题或有功能请求，请：

1. 查看 [文档](README.md)
2. 搜索 [已有问题](issues)
3. 创建 [新问题](issues/new)

---

**注意**: 这是一个实验性项目，从 RAGFlow 中抽取。建议在生产环境使用前进行充分测试。
