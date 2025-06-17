#!/usr/bin/env python3
"""
构建和发布 deepdoc-pdfparser 库的脚本

使用方法:
    python build_deepdoc_pdfparser.py --help
    python build_deepdoc_pdfparser.py build
    python build_deepdoc_pdfparser.py test
    python build_deepdoc_pdfparser.py publish --test
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


class DeepDocPdfParserBuilder:
    """DeepDoc PDF Parser 构建器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "dist"
        self.package_dir = self.project_root / "deepdoc_pdfparser"
        
    def print_info(self, message):
        """打印信息"""
        print(f"ℹ️  {message}")
        
    def print_success(self, message):
        """打印成功信息"""
        print(f"✅ {message}")
        
    def print_error(self, message):
        """打印错误信息"""
        print(f"❌ {message}")
        
    def print_warning(self, message):
        """打印警告信息"""
        print(f"⚠️  {message}")
    
    def check_prerequisites(self):
        """检查构建前提条件"""
        self.print_info("检查构建前提条件...")
        
        # 检查必要文件
        required_files = [
            "deepdoc_pdfparser/__init__.py",
            "deepdoc_pdfparser/parser.py",
            "deepdoc_pdfparser/types.py",
            "deepdoc_pdfparser/utils.py",
            "deepdoc_pdfparser_pyproject.toml",
            "README_DEEPDOC.md",
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.print_error(f"缺少必要文件: {', '.join(missing_files)}")
            return False
        
        # 检查ragflow模块
        ragflow_path = self.project_root / "file_load" / "ragflow"
        if not ragflow_path.exists():
            self.print_warning("ragflow模块不存在，这可能会影响功能")
        
        self.print_success("前提条件检查通过")
        return True
    
    def prepare_build_environment(self):
        """准备构建环境"""
        self.print_info("准备构建环境...")
        
        # 创建临时构建目录
        temp_build_dir = self.project_root / "temp_deepdoc_build"
        if temp_build_dir.exists():
            shutil.rmtree(temp_build_dir)
        
        temp_build_dir.mkdir()
        
        # 复制包文件
        shutil.copytree(self.package_dir, temp_build_dir / "deepdoc_pdfparser")
        
        # 复制ragflow模块
        ragflow_src = self.project_root / "file_load" / "ragflow"
        if ragflow_src.exists():
            ragflow_dst = temp_build_dir / "deepdoc_pdfparser" / "ragflow"
            shutil.copytree(ragflow_src, ragflow_dst)
        
        # 复制配置文件
        shutil.copy2("deepdoc_pdfparser_pyproject.toml", temp_build_dir / "pyproject.toml")
        shutil.copy2("README_DEEPDOC.md", temp_build_dir / "README.md")
        
        # 创建LICENSE文件
        license_content = """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

[Full Apache 2.0 license text would go here]

This software contains code extracted from RAGFlow (https://github.com/infiniflow/ragflow)
which is also licensed under Apache 2.0.
"""
        with open(temp_build_dir / "LICENSE", "w", encoding="utf-8") as f:
            f.write(license_content)
        
        self.print_success(f"构建环境准备完成: {temp_build_dir}")
        return temp_build_dir
    
    def build_package(self):
        """构建包"""
        self.print_info("开始构建包...")
        
        if not self.check_prerequisites():
            return False
        
        temp_dir = self.prepare_build_environment()
        
        try:
            # 切换到临时目录
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            # 检查uv是否可用
            try:
                subprocess.run(["uv", "--version"], check=True, capture_output=True)
                build_cmd = ["uv", "build"]
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.print_warning("uv不可用，尝试使用pip build")
                try:
                    subprocess.run(["python", "-m", "build", "--version"], check=True, capture_output=True)
                    build_cmd = ["python", "-m", "build"]
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.print_error("无法找到构建工具（uv或build）")
                    return False
            
            # 执行构建
            result = subprocess.run(build_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 复制构建结果
                dist_src = temp_dir / "dist"
                dist_dst = self.project_root / "dist"
                
                if dist_dst.exists():
                    shutil.rmtree(dist_dst)
                
                shutil.copytree(dist_src, dist_dst)
                
                self.print_success("包构建成功!")
                self.print_info(f"构建文件位于: {dist_dst}")
                
                # 列出构建的文件
                for file in dist_dst.glob("*"):
                    self.print_info(f"  - {file.name}")
                
                return True
            else:
                self.print_error(f"构建失败: {result.stderr}")
                return False
                
        finally:
            os.chdir(original_cwd)
            # 清理临时目录
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def run_tests(self):
        """运行测试"""
        self.print_info("运行测试...")
        
        # 运行基本的模块测试
        test_file = self.project_root / "tests" / "test_deepdoc_pdfparser.py"
        if test_file.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(test_file)
                ], capture_output=True, text=True, cwd=self.project_root)
                
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                
                if result.returncode == 0:
                    self.print_success("基本测试通过")
                else:
                    self.print_warning("基本测试有警告或错误")
                
            except Exception as e:
                self.print_error(f"运行测试失败: {e}")
        
        # 尝试使用pytest
        try:
            subprocess.run(["pytest", "--version"], check=True, capture_output=True)
            
            result = subprocess.run([
                "pytest", "tests/test_deepdoc_pdfparser.py", "-v"
            ], cwd=self.project_root)
            
            if result.returncode == 0:
                self.print_success("pytest测试通过")
            else:
                self.print_warning("pytest测试有问题")
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_info("pytest不可用，跳过pytest测试")
    
    def publish_package(self, test_pypi=False):
        """发布包"""
        target = "TestPyPI" if test_pypi else "PyPI"
        self.print_info(f"发布包到 {target}...")
        
        dist_dir = self.project_root / "dist"
        if not dist_dir.exists() or not list(dist_dir.glob("*.whl")):
            self.print_error("没有找到构建的包，请先运行构建")
            return False
        
        try:
            # 检查uv是否可用
            subprocess.run(["uv", "--version"], check=True, capture_output=True)
            
            if test_pypi:
                publish_cmd = ["uv", "publish", "--repository", "testpypi"]
            else:
                publish_cmd = ["uv", "publish"]
            
            result = subprocess.run(publish_cmd, cwd=self.project_root)
            
            if result.returncode == 0:
                self.print_success(f"成功发布到 {target}!")
                if test_pypi:
                    self.print_info("测试安装: pip install -i https://test.pypi.org/simple/ deepdoc-pdfparser")
                else:
                    self.print_info("安装: uv add deepdoc-pdfparser")
                return True
            else:
                self.print_error(f"发布到 {target} 失败")
                return False
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_error("uv不可用，无法发布包")
            return False
    
    def clean(self):
        """清理构建文件"""
        self.print_info("清理构建文件...")
        
        paths_to_clean = [
            self.project_root / "dist",
            self.project_root / "temp_deepdoc_build",
            self.project_root / "deepdoc_pdfparser" / "__pycache__",
        ]
        
        for path in paths_to_clean:
            if path.exists():
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
                self.print_info(f"删除: {path}")
        
        self.print_success("清理完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DeepDoc PDF Parser 构建工具")
    parser.add_argument("command", choices=["build", "test", "publish", "clean"], 
                       help="要执行的命令")
    parser.add_argument("--test", action="store_true", 
                       help="发布到TestPyPI（仅用于publish命令）")
    
    args = parser.parse_args()
    
    builder = DeepDocPdfParserBuilder()
    
    if args.command == "build":
        success = builder.build_package()
        sys.exit(0 if success else 1)
        
    elif args.command == "test":
        builder.run_tests()
        
    elif args.command == "publish":
        if not builder.build_package():
            sys.exit(1)
        success = builder.publish_package(test_pypi=args.test)
        sys.exit(0 if success else 1)
        
    elif args.command == "clean":
        builder.clean()


if __name__ == "__main__":
    main() 