"""
数据类型定义
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass


@dataclass
class ChunkResult:
    """PDF解析的文本块结果"""
    content: str  # 文本内容
    page_number: int  # 页码
    position: Optional[Tuple[float, float, float, float]] = None  # 位置信息 (x0, y0, x1, y1)
    layout_type: Optional[str] = None  # 布局类型 (text, table, figure等)
    confidence: Optional[float] = None  # 置信度
    raw_data: Optional[Dict[str, Any]] = None  # 原始数据
    
    def __str__(self) -> str:
        return self.content
        
    def __repr__(self) -> str:
        return f"ChunkResult(page={self.page_number}, content='{self.content[:50]}...', layout_type='{self.layout_type}')"


@dataclass 
class TableResult:
    """表格解析结果"""
    html: str  # 表格的HTML格式
    position: Optional[Tuple[float, float, float, float]] = None  # 位置信息
    page_number: Optional[int] = None  # 页码
    
    def __str__(self) -> str:
        return self.html
        
    def __repr__(self) -> str:
        return f"TableResult(page={self.page_number}, html_length={len(self.html)})"


@dataclass
class ParseResult:
    """完整的解析结果"""
    chunks: List[ChunkResult]  # 文本块列表
    tables: List[TableResult]  # 表格列表
    metadata: Dict[str, Any]  # 元数据
    
    def __len__(self) -> int:
        return len(self.chunks)
        
    def __iter__(self):
        return iter(self.chunks)
        
    def get_text(self) -> str:
        """获取所有文本内容"""
        return "\n".join(chunk.content for chunk in self.chunks)
        
    def get_text_by_page(self, page_number: int) -> str:
        """获取指定页面的文本"""
        page_chunks = [chunk for chunk in self.chunks if chunk.page_number == page_number]
        return "\n".join(chunk.content for chunk in page_chunks)
        
    def get_tables_by_page(self, page_number: int) -> List[TableResult]:
        """获取指定页面的表格"""
        return [table for table in self.tables if table.page_number == page_number] 