"""
DeepDoc PDF Parser - 基于RAGFlow DeepDoc的专业PDF解析库

该库从RAGFlow的deepdoc模块中抽取，专门用于智能解析PDF文件，
支持OCR、布局识别、表格提取等高级功能。

Original RAGFlow Repository: https://github.com/infiniflow/ragflow
"""

from .parser import PdfParser, PlainPdfParser
from .parse_types import ChunkResult, ParseResult
from .utils import parse_pdf, parse_pdf_simple

__version__ = "0.1.0"
__author__ = "Extracted from RAGFlow DeepDoc"
__license__ = "Apache-2.0"

__all__ = [
    "PdfParser", 
    "PlainPdfParser", 
    "ChunkResult", 
    "ParseResult",
    "parse_pdf", 
    "parse_pdf_simple"
] 