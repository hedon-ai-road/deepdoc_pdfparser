"""
便捷工具函数

提供简单易用的PDF解析API
"""

from typing import List, Optional, Callable
from deepdoc_pdfparser.parser import PdfParser
from deepdoc_pdfparser.parse_types import ParseResult


def parse_pdf(pdf_path: str, 
              from_page: int = 0, 
              to_page: int = 100000,
              callback: Optional[Callable] = None,
              **kwargs) -> ParseResult:
    """
    使用深度学习模型解析PDF文件（推荐）
    
    Args:
        pdf_path: PDF文件路径
        from_page: 起始页码（从0开始）
        to_page: 结束页码
        callback: 进度回调函数
        **kwargs: 其他参数
        
    Returns:
        ParseResult: 解析结果
        
    Example:
        >>> result = parse_pdf("document.pdf")
        >>> print(f"共解析出 {len(result)} 个文本块")
        >>> for chunk in result:
        ...     print(chunk.content)
    """
    parser = PdfParser()
    return parser.parse(pdf_path, from_page, to_page, callback, **kwargs)


def extract_text(pdf_path: str, **kwargs) -> str:
    """
    提取PDF中的所有文本
    
    Args:
        pdf_path: PDF文件路径
        **kwargs: 其他参数
        
    Returns:
        str: 提取的文本内容
    """
    result = parse_pdf(pdf_path, **kwargs)
    return result.get_text()


def extract_text_by_page(pdf_path: str, page_number: int, **kwargs) -> str:
    """
    提取PDF指定页面的文本
    
    Args:
        pdf_path: PDF文件路径
        page_number: 页码（从0开始）
        **kwargs: 其他参数
        
    Returns:
        str: 提取的文本内容
    """
    result = parse_pdf(pdf_path, from_page=page_number, to_page=page_number+1, **kwargs)
    return result.get_text_by_page(page_number)


def extract_tables(pdf_path: str, **kwargs) -> List[str]:
    """
    提取PDF中的所有表格（HTML格式）
    
    Args:
        pdf_path: PDF文件路径
        **kwargs: 其他参数
        
    Returns:
        List[str]: 表格的HTML列表
    """
    result = parse_pdf(pdf_path, **kwargs)
    return [table.html for table in result.tables]


def parse_pdf_binary(pdf_binary: bytes, filename: str = "document.pdf", **kwargs) -> ParseResult:
    """
    解析PDF二进制数据
    
    Args:
        pdf_binary: PDF二进制数据
        filename: 文件名（用于显示）
        **kwargs: 其他参数
        
    Returns:
        ParseResult: 解析结果
    """
    parser = PdfParser()
    return parser.parse_binary(pdf_binary, filename, **kwargs) 