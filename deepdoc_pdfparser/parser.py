"""
PDF解析器主模块

基于RAGFlow的deepdoc模块，提供专业的PDF文档解析功能
"""

import os
import logging
from typing import Optional, Callable

from deepdoc_pdfparser.ragflow.rag.app.manual import Pdf as RagflowPdf, chunk as ragflow_chunk
from deepdoc_pdfparser.ragflow.rag.nlp import rag_tokenizer
from deepdoc_pdfparser.ragflow.rag.utils import num_tokens_from_string
from deepdoc_pdfparser.ragflow.api.db import ParserType

from deepdoc_pdfparser.parse_types import ChunkResult, ParseResult, TableResult


class PdfParser:
    """
    专业的PDF解析器
    
    基于RAGFlow的deepdoc模块，支持：
    - OCR文字识别
    - 布局分析
    - 表格提取
    - 智能分块
    """
    
    def __init__(self, model_type: str = "manual"):
        """
        初始化PDF解析器
        
        Args:
            model_type: 模型类型，默认为"manual"
        """
        self.model_type = model_type
        self._parser = None
        self._init_parser()
    
    def _init_parser(self):
        """初始化内部解析器"""
        try:
            self._parser = RagflowPdf()
            self._parser.model_speciess = ParserType.MANUAL.value
        except Exception as e:
            logging.error(f"初始化PDF解析器失败: {e}")
            raise RuntimeError(f"无法初始化PDF解析器: {e}")
    
    def _process_results(self, results: list, file_identifier: str) -> ParseResult:
        """
        处理ragflow的解析结果，转换为标准格式
        
        Args:
            results: ragflow的解析结果列表
            file_identifier: 文件标识（路径或名称）
            
        Returns:
            ParseResult: 标准化的解析结果
        """
        chunks = []
        tables = []
        
        for result in results:
            # 提取文本内容
            content = result.get('content_with_weight', '')
            if not content:
                continue
            
            # 提取页码信息（从page_num_int数组中取第一个值）
            page_nums = result.get('page_num_int', [0])
            page_number = page_nums[0] if page_nums else 0
            
            # 提取位置信息（从position_int数组中取第一个值）
            positions = result.get('position_int', [])
            position = None
            if positions:
                # position_int格式: (page, x0, y0, x1, y1)
                pos_data = positions[0]
                if len(pos_data) >= 5:
                    position = (pos_data[1], pos_data[2], pos_data[3], pos_data[4])  # (x0, y0, x1, y1)
            
            # 判断是否为表格内容
            is_table = content.strip().startswith('<table')
            layout_type = 'table' if is_table else 'text'
            
            # 创建ChunkResult
            chunk = ChunkResult(
                content=content,
                page_number=page_number,
                position=position,
                layout_type=layout_type,
                raw_data=result
            )
            chunks.append(chunk)
            
            # 如果是表格，也添加到tables列表中
            if is_table:
                table = TableResult(
                    html=content,
                    position=position,
                    page_number=page_number
                )
                tables.append(table)
        
        # 创建元数据
        metadata = {
            'total_chunks': len(chunks),
            'total_tables': len(tables),
            'file_identifier': file_identifier,
            'parser_type': self.model_type
        }
        
        return ParseResult(
            chunks=chunks,
            tables=tables,
            metadata=metadata
        )
    
    def parse(self, 
              pdf_path: str,
              from_page: int = 0,
              to_page: int = 100000,
              callback: Optional[Callable[[Optional[float], str], None]] = None,
              **kwargs) -> ParseResult:
        """
        解析PDF文件
        
        Args:
            pdf_path: PDF文件路径
            from_page: 起始页码（从0开始）
            to_page: 结束页码
            callback: 进度回调函数
            **kwargs: 其他参数
            
        Returns:
            ParseResult: 解析结果
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        if callback is None:
            callback = self._default_callback
            
        try:
            # 使用ragflow的chunk函数进行解析
            results = ragflow_chunk(
                filename=pdf_path,
                from_page=from_page,
                to_page=to_page,
                callback=callback,
                **kwargs
            )
            
            # 使用公共方法处理结果
            parse_result = self._process_results(results, pdf_path)
            
            # 计算实际解析的页面数量（从chunks中获取最大页码）
            actual_pages = 0
            if parse_result.chunks:
                max_page = max(chunk.page_number for chunk in parse_result.chunks)
                actual_pages = max_page + 1  # 页码从0开始，所以总页数是最大页码+1
            
            # 添加页面相关的元数据
            parse_result.metadata.update({
                'total_pages': actual_pages,
                'parsed_page_range': f"{from_page}-{min(to_page, actual_pages)}",
                'file_path': pdf_path,
            })
            
            return parse_result
            
        except Exception as e:
            logging.error(f"解析PDF文件失败: {e}")
            raise RuntimeError(f"解析PDF文件失败: {e}")
    
    def parse_binary(self, 
                     pdf_binary: bytes,
                     filename: str = "document.pdf",
                     **kwargs) -> ParseResult:
        """
        解析PDF二进制数据
        
        Args:
            pdf_binary: PDF二进制数据
            filename: 文件名（用于显示）
            **kwargs: 其他参数
            
        Returns:
            ParseResult: 解析结果
        """
        try:
            # 使用ragflow的chunk函数进行解析
            results = ragflow_chunk(
                filename=filename,
                binary=pdf_binary,
                **kwargs
            )
            
            # 使用公共方法处理结果
            parse_result = self._process_results(results, filename)
            
            # 添加文件名相关的元数据
            parse_result.metadata.update({
                'file_name': filename,
            })
            
            return parse_result
            
        except Exception as e:
            logging.error(f"解析PDF二进制数据失败: {e}")
            raise RuntimeError(f"解析PDF二进制数据失败: {e}")
    
    @staticmethod
    def _default_callback(progress: Optional[float] = None, message: str = "", msg: str = "", prog: Optional[float] = None):
        """默认回调函数"""
        # 使用prog参数如果提供了，否则使用progress参数
        display_progress = prog if prog is not None else progress
        if display_progress is not None:
            print(f"解析进度: {display_progress:.1%}")
        # 使用msg参数如果提供了，否则使用message参数
        display_message = msg or message
        if display_message:
            print(f"状态: {display_message}")


if __name__ == "__main__":
    parser = PdfParser()
    res = parser.parse(pdf_path="./fixtures/zhidu_travel.pdf")
    print("chunk:")
    for chunk in res.chunks:
        print("="*100)
        print(chunk)

    print()
    print("table:")
    for table in res.tables:
        print("="*100)
        print(table)

    print()
    print("metadata:")
    print(res.metadata)
    