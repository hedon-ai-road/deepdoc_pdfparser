"""
DeepDoc PDF Parser - 基于RAGFlow DeepDoc的专业PDF解析库

该库从RAGFlow的deepdoc模块中抽取，专门用于智能解析PDF文件，
支持OCR、布局识别、表格提取等高级功能。

Original RAGFlow Repository: https://github.com/infiniflow/ragflow
"""

from .parser import PdfParser
from .parse_types import ChunkResult, ParseResult, TableResult
from .utils import parse_pdf, extract_text, extract_text_by_page, extract_tables, parse_pdf_binary

__version__ = "0.1.4"
__author__ = "Extracted from RAGFlow DeepDoc"
__license__ = "Apache-2.0"

__all__ = [
    "PdfParser", 
    "ChunkResult", 
    "ParseResult",
    "TableResult",
    "parse_pdf", 
    "extract_text",
    "extract_text_by_page", 
    "extract_tables",
    "parse_pdf_binary"
] 