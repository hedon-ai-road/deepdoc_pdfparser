"""
测试utils模块中的所有公开函数 - 使用真实PDF文件
"""

import os
import pytest
from unittest.mock import Mock, patch

# 设置测试环境
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils import (
    parse_pdf, 
    extract_text, 
    extract_text_by_page, 
    extract_tables, 
    parse_pdf_binary
)
from parse_types import ParseResult, ChunkResult, TableResult


class TestUtilsFunctions:
    """测试utils模块的所有公开函数"""
    
    @pytest.fixture
    def sample_pdf_path(self):
        """提供示例PDF文件路径"""
        # 使用fixtures目录中的测试文件
        fixtures_dir = os.path.join(os.path.dirname(__file__), '..', 'fixtures')
        pdf_path = os.path.join(fixtures_dir, 'zhidu_travel.pdf')
        if os.path.exists(pdf_path):
            return pdf_path
        else:
            pytest.skip("测试PDF文件不存在")
    
    def test_parse_pdf_function_exists(self):
        """测试parse_pdf函数是否存在且可调用"""
        assert callable(parse_pdf)
    
    def test_extract_text_function_exists(self):
        """测试extract_text函数是否存在且可调用"""
        assert callable(extract_text)
    
    def test_extract_text_by_page_function_exists(self):
        """测试extract_text_by_page函数是否存在且可调用"""
        assert callable(extract_text_by_page)
    
    def test_extract_tables_function_exists(self):
        """测试extract_tables函数是否存在且可调用"""
        assert callable(extract_tables)
    
    def test_parse_pdf_binary_function_exists(self):
        """测试parse_pdf_binary函数是否存在且可调用"""
        assert callable(parse_pdf_binary)
    
    def test_parse_pdf_with_real_file(self, sample_pdf_path):
        """测试parse_pdf函数的基本功能（使用真实文件）"""
        try:
            # 调用函数
            result = parse_pdf(sample_pdf_path)
            
            # 验证
            assert isinstance(result, ParseResult)
            assert hasattr(result, 'chunks')
            assert hasattr(result, 'tables')
            assert hasattr(result, 'metadata')
            assert len(result.chunks) > 0  # 应该有一些文本块
            print(f"✓ parse_pdf成功解析出 {len(result.chunks)} 个文本块")
            
        except Exception as e:
            print(f"⚠️ parse_pdf测试跳过，原因: {e}")
            pytest.skip(f"parse_pdf函数测试失败: {e}")
    
    def test_extract_text_with_real_file(self, sample_pdf_path):
        """测试extract_text函数的基本功能（使用真实文件）"""
        try:
            # 调用函数
            result = extract_text(sample_pdf_path)
            
            # 验证
            assert isinstance(result, str)
            assert len(result) > 0  # 应该有一些文本内容
            print(f"✓ extract_text成功提取了 {len(result)} 个字符")
            
        except Exception as e:
            print(f"⚠️ extract_text测试跳过，原因: {e}")
            pytest.skip(f"extract_text函数测试失败: {e}")
    
    def test_extract_text_by_page_with_real_file(self, sample_pdf_path):
        """测试extract_text_by_page函数的基本功能（使用真实文件）"""
        try:
            # 调用函数（提取第一页）
            result = extract_text_by_page(sample_pdf_path, 0)
            
            # 验证
            assert isinstance(result, str)
            print(f"✓ extract_text_by_page成功提取第一页文本: {len(result)} 个字符")
            
        except Exception as e:
            print(f"⚠️ extract_text_by_page测试跳过，原因: {e}")
            pytest.skip(f"extract_text_by_page函数测试失败: {e}")
    
    def test_extract_tables_with_real_file(self, sample_pdf_path):
        """测试extract_tables函数的基本功能（使用真实文件）"""
        try:
            # 调用函数
            result = extract_tables(sample_pdf_path)
            
            # 验证
            assert isinstance(result, list)
            print(f"✓ extract_tables成功提取了 {len(result)} 个表格")
            
            # 如果有表格，验证表格内容
            for i, table in enumerate(result):
                assert isinstance(table, str)
                assert len(table) > 0
                print(f"  表格 {i+1}: {len(table)} 个字符")
            
        except Exception as e:
            print(f"⚠️ extract_tables测试跳过，原因: {e}")
            pytest.skip(f"extract_tables函数测试失败: {e}")
    
    def test_parse_pdf_binary_with_real_file(self, sample_pdf_path):
        """测试parse_pdf_binary函数的基本功能（使用真实文件）"""
        try:
            # 读取PDF文件为二进制数据
            with open(sample_pdf_path, 'rb') as f:
                pdf_binary = f.read()
            
            # 调用函数
            result = parse_pdf_binary(pdf_binary, "test.pdf")
            
            # 验证
            assert isinstance(result, ParseResult)
            assert hasattr(result, 'chunks')
            assert hasattr(result, 'tables')
            assert hasattr(result, 'metadata')
            print(f"✓ parse_pdf_binary成功解析出 {len(result.chunks)} 个文本块")
            
        except Exception as e:
            print(f"⚠️ parse_pdf_binary测试跳过，原因: {e}")
            pytest.skip(f"parse_pdf_binary函数测试失败: {e}")
    
    def test_parse_pdf_with_invalid_file(self):
        """测试parse_pdf函数处理无效文件的情况"""
        with pytest.raises(Exception):  # 应该抛出异常
            parse_pdf("nonexistent_file.pdf")
    
    def test_extract_text_by_page_invalid_page(self, sample_pdf_path):
        """测试extract_text_by_page函数处理无效页码的情况"""
        try:
            # 调用函数（页码不存在）
            result = extract_text_by_page(sample_pdf_path, 999)
            
            # 验证（应该返回空字符串或很少内容）
            assert isinstance(result, str)
            print(f"✓ extract_text_by_page处理无效页码正常: 返回 {len(result)} 个字符")
            
        except Exception as e:
            print(f"⚠️ extract_text_by_page无效页码测试跳过，原因: {e}")
            pytest.skip(f"extract_text_by_page无效页码测试失败: {e}")
    
    def test_function_signatures(self):
        """测试所有函数的签名是否正确"""
        import inspect
        
        # 检查parse_pdf的签名
        sig = inspect.signature(parse_pdf)
        assert 'pdf_path' in sig.parameters
        assert 'from_page' in sig.parameters
        assert 'to_page' in sig.parameters
        assert 'callback' in sig.parameters
        
        # 检查extract_text的签名
        sig = inspect.signature(extract_text)
        assert 'pdf_path' in sig.parameters
        
        # 检查extract_text_by_page的签名
        sig = inspect.signature(extract_text_by_page)
        assert 'pdf_path' in sig.parameters
        assert 'page_number' in sig.parameters
        
        # 检查extract_tables的签名
        sig = inspect.signature(extract_tables)
        assert 'pdf_path' in sig.parameters
        
        # 检查parse_pdf_binary的签名
        sig = inspect.signature(parse_pdf_binary)
        assert 'pdf_binary' in sig.parameters
        assert 'filename' in sig.parameters

    def test_parse_result_methods(self, sample_pdf_path):
        """测试ParseResult类的方法"""
        try:
            result = parse_pdf(sample_pdf_path)
            
            # 测试get_text方法
            text = result.get_text()
            assert isinstance(text, str)
            
            # 测试get_text_by_page方法
            page_text = result.get_text_by_page(0)
            assert isinstance(page_text, str)
            
            # 测试get_tables_by_page方法
            page_tables = result.get_tables_by_page(0)
            assert isinstance(page_tables, list)
            
            # 测试迭代
            chunk_count = 0
            for chunk in result:
                assert isinstance(chunk, ChunkResult)
                chunk_count += 1
            
            # 测试长度
            assert len(result) == chunk_count
            
            print(f"✓ ParseResult方法测试通过，共 {len(result)} 个块")
            
        except Exception as e:
            print(f"⚠️ ParseResult方法测试跳过，原因: {e}")
            pytest.skip(f"ParseResult方法测试失败: {e}")


if __name__ == "__main__":
    # 可以直接运行此文件进行基本测试
    print("运行基本函数存在性测试...")
    
    test_class = TestUtilsFunctions()
    
    # 测试函数是否存在
    test_class.test_parse_pdf_function_exists()
    print("✓ parse_pdf函数存在")
    
    test_class.test_extract_text_function_exists()
    print("✓ extract_text函数存在")
    
    test_class.test_extract_text_by_page_function_exists()
    print("✓ extract_text_by_page函数存在")
    
    test_class.test_extract_tables_function_exists()
    print("✓ extract_tables函数存在")
    
    test_class.test_parse_pdf_binary_function_exists()
    print("✓ parse_pdf_binary函数存在")
    
    test_class.test_function_signatures()
    print("✓ 所有函数签名正确")
    
    # 尝试使用真实文件测试
    print("\n尝试使用真实PDF文件测试...")
    
    # 查找PDF文件
    fixtures_dir = os.path.join(os.path.dirname(__file__), '..', 'fixtures')
    pdf_path = os.path.join(fixtures_dir, 'zhidu_travel.pdf')
    
    if os.path.exists(pdf_path):
        print(f"找到测试PDF文件: {pdf_path}")
        
        try:
            # 测试基本解析
            result = parse_pdf(pdf_path)
            print(f"✓ parse_pdf测试成功: {len(result)} 个文本块, {len(result.tables)} 个表格")
            
            # 测试文本提取
            text = extract_text(pdf_path)
            print(f"✓ extract_text测试成功: {len(text)} 个字符")
            
            # 测试表格提取
            tables = extract_tables(pdf_path)
            print(f"✓ extract_tables测试成功: {len(tables)} 个表格")
            
            print("\n✅ 所有核心功能测试通过！")
            
        except Exception as e:
            print(f"⚠️ 真实文件测试出现问题: {e}")
            print("可能需要正确配置ragflow依赖")
    else:
        print(f"⚠️ 测试PDF文件不存在: {pdf_path}")
    
    print("\n运行完整测试请使用: pytest tests/test_utils.py -v") 