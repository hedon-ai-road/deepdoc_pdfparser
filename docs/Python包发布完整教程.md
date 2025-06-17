# Python 包发布完整教程 - PyPI 发布实战指南

本教程记录了 `deepdoc-pdfparser` 从开发到发布到 PyPI 的完整流程，可作为其他 Python 包发布的参考指南。

## 📋 目录

1. [项目准备阶段](#1-项目准备阶段)
2. [配置文件设置](#2-配置文件设置)
3. [代码质量保证](#3-代码质量保证)
4. [构建和测试](#4-构建和测试)
5. [PyPI 账号准备](#5-pypi-账号准备)
6. [发布流程](#6-发布流程)
7. [验证和使用](#7-验证和使用)
8. [版本管理](#8-版本管理)
9. [常见问题解决](#9-常见问题解决)

## 1. 项目准备阶段

### 1.1 项目结构

确保项目具有清晰的结构：

```
your_project/
├── your_package/          # 主包目录
│   ├── __init__.py       # 包初始化文件
│   ├── core.py           # 核心模块
│   └── utils.py          # 工具模块
├── tests/                # 测试目录
│   └── test_*.py         # 测试文件
├── docs/                 # 文档目录
│   └── *.md              # 文档文件
├── fixtures/             # 测试数据
├── pyproject.toml        # 项目配置文件
├── README.md             # 项目说明
├── LICENSE               # 许可证文件
└── .gitignore            # Git忽略文件
```

### 1.2 核心文件检查

**必需文件**：

- `pyproject.toml` - 项目配置和构建设置
- `README.md` - 项目介绍和使用说明
- `LICENSE` - 开源许可证
- `__init__.py` - 包的公开 API 定义

**推荐文件**：

- `CHANGELOG.md` - 版本更新日志
- `CONTRIBUTING.md` - 贡献指南
- `docs/` - 详细文档

### 1.3 `__init__.py` 设置

确保包的公开 API 清晰定义：

```python
"""
Package Name - 简短描述

详细的包说明...
"""

from .core import MainClass
from .utils import utility_function1, utility_function2

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "Apache-2.0"

__all__ = [
    "MainClass",
    "utility_function1",
    "utility_function2"
]
```

## 2. 配置文件设置

### 2.1 `pyproject.toml` 完整配置

这是最重要的配置文件，决定了包的构建和发布：

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "your-package-name"
version = "0.1.0"
description = "简短的包描述"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "Apache-2.0"}
authors = [
    { name = "Your Name", email = "your.email@example.com" },
]
maintainers = [
    { name = "Your Name", email = "your.email@example.com" },
]
keywords = ["keyword1", "keyword2", "category"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

dependencies = [
    "requests>=2.25.0",
    "numpy>=1.20.0",
    # 其他依赖...
]

[project.urls]
Homepage = "https://github.com/username/repository"
Repository = "https://github.com/username/repository.git"
Documentation = "https://github.com/username/repository#readme"
"Bug Tracker" = "https://github.com/username/repository/issues"
"Source Code" = "https://github.com/username/repository"

[tool.hatch.build.targets.wheel]
packages = ["."]

[tool.hatch.build.targets.sdist]
include = [
    "/your_package",
    "/README.md",
    "/LICENSE",
]
exclude = [
    "/.git",
    "/tests",
    "/docs",
    "/fixtures",
    "*.pyc",
    "__pycache__",
]
```

### 2.2 关键配置说明

**包名选择**：

- 使用小写字母和连字符
- 避免与现有包冲突
- 简洁而描述性

**版本号规范**：

- 遵循语义化版本 (SemVer): `MAJOR.MINOR.PATCH`
- 初始版本建议从 `0.1.0` 开始

**分类器 (Classifiers)**：

- 帮助用户找到你的包
- 从 [PyPI 分类器列表](https://pypi.org/classifiers/) 选择

**依赖管理**：

- 指定最小版本而非固定版本
- 使用 `>=` 而不是 `==`

## 3. 代码质量保证

### 3.1 代码清理

在发布前进行代码审查：

```bash
# 检查未使用的导入和代码
# 删除调试代码和注释
# 确保所有公开函数都有文档字符串
```

### 3.2 编写测试

确保有充分的测试覆盖：

```python
# tests/test_main.py
import pytest
from your_package import MainClass, utility_function1

class TestMainClass:
    def test_basic_functionality(self):
        """测试基本功能"""
        obj = MainClass()
        result = obj.process("test_input")
        assert result is not None

    def test_edge_cases(self):
        """测试边界情况"""
        obj = MainClass()
        with pytest.raises(ValueError):
            obj.process(None)

def test_utility_function():
    """测试工具函数"""
    result = utility_function1("input")
    assert isinstance(result, str)
```

### 3.3 运行测试

```bash
# 安装测试依赖
uv add --dev pytest

# 运行所有测试
pytest tests/ -v

# 检查测试覆盖率
uv add --dev pytest-cov
pytest tests/ --cov=your_package --cov-report=html
```

## 4. 构建和测试

### 4.1 安装构建工具

```bash
# 使用 uv 安装构建工具
uv add --dev build twine

# 或使用 pip
pip install build twine
```

### 4.2 构建包

```bash
# 使用 uv 构建 (推荐)
uv build

# 或使用 python -m build
python -m build
```

构建成功后会在 `dist/` 目录生成两个文件：

- `your_package-0.1.0.tar.gz` (源码包)
- `your_package-0.1.0-py3-none-any.whl` (wheel 包)

### 4.3 检查包完整性

```bash
# 检查构建的包是否符合标准
twine check dist/*
```

如果检查通过，会看到：

```
Checking dist/your_package-0.1.0-py3-none-any.whl: PASSED
Checking dist/your_package-0.1.0.tar.gz: PASSED
```

### 4.4 本地测试安装

```bash
# 在虚拟环境中测试安装
pip install dist/your_package-0.1.0-py3-none-any.whl

# 测试导入
python -c "import your_package; print('Import successful!')"
```

## 5. PyPI 账号准备

### 5.1 注册账号

**TestPyPI (测试环境)**:

- 网址: https://test.pypi.org/account/register/
- 用于测试发布流程

**PyPI (正式环境)**:

- 网址: https://pypi.org/account/register/
- 用于正式发布

### 5.2 生成 API Token

**在 TestPyPI**:

1. 登录 → Account settings → API tokens
2. 点击 "Add API token"
3. Token name: `your-package-testpypi`
4. Scope: 选择 "Entire account" 或创建项目后选择具体项目
5. 点击 "Create token"
6. **重要**: 立即复制保存 token，格式为 `pypi-...`

**在 PyPI** (重复上述步骤):

1. Token name: `your-package-pypi`
2. 同样保存生成的 token

### 5.3 配置凭据

**方法 1: 使用 `.pypirc` 文件 (推荐)**

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-actual-pypi-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-actual-testpypi-token-here
```

**方法 2: 环境变量**

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
```

**方法 3: 命令行输入** (每次都需要输入)

## 6. 发布流程

### 6.1 发布到 TestPyPI (强烈推荐)

先发布到测试环境验证一切正常：

```bash
# 发布到 TestPyPI
twine upload --repository testpypi dist/*

# 如果没有配置 .pypirc，会提示输入:
# Username: __token__
# Password: 你的TestPyPI token
```

成功后会看到类似输出：

```
Uploading distributions to https://test.pypi.org/legacy/
Uploading your_package-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uploading your_package-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View at:
https://test.pypi.org/project/your-package/
```

### 6.2 从 TestPyPI 安装测试

```bash
# 从 TestPyPI 安装
pip install -i https://test.pypi.org/simple/ your-package

# 或指定版本
pip install -i https://test.pypi.org/simple/ your-package==0.1.0

# 测试功能
python -c "
import your_package
print('Version:', your_package.__version__)
# 测试主要功能...
"
```

### 6.3 发布到正式 PyPI

确认 TestPyPI 一切正常后，发布到正式 PyPI：

```bash
# 发布到正式 PyPI
twine upload dist/*

# 成功后访问
# https://pypi.org/project/your-package/
```

### 6.4 验证正式发布

```bash
# 从正式 PyPI 安装
pip install your-package

# 或使用 uv
uv add your-package

# 验证安装
python -c "import your_package; print('Success!')"
```

## 7. 验证和使用

### 7.1 检查包页面

访问你的包页面：

- TestPyPI: `https://test.pypi.org/project/your-package/`
- PyPI: `https://pypi.org/project/your-package/`

检查内容：

- 包描述是否正确显示
- README 内容是否正确渲染
- 依赖列表是否准确
- 下载链接是否可用

### 7.2 用户使用测试

创建新的虚拟环境测试用户体验：

```bash
# 创建新环境
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# test_env\Scripts\activate   # Windows

# 安装你的包
pip install your-package

# 按照 README 进行使用测试
python -c "
from your_package import MainClass
obj = MainClass()
print('User test successful!')
"
```

### 7.3 文档和示例验证

确保 README 中的所有示例代码都能正常运行：

```python
# 复制 README 中的示例代码逐个测试
# 确保没有错误的导入或函数调用
```

## 8. 版本管理

### 8.1 版本号策略

遵循 [语义化版本控制](https://semver.org/lang/zh-CN/)：

- `MAJOR.MINOR.PATCH` (例如: 1.2.3)
- **MAJOR**: 不兼容的 API 修改
- **MINOR**: 向下兼容的功能性新增
- **PATCH**: 向下兼容的问题修正

### 8.2 更新发布流程

```bash
# 1. 更新版本号
# 编辑 pyproject.toml 中的 version

# 2. 更新 __init__.py 中的 __version__
# 编辑 your_package/__init__.py

# 3. 更新 CHANGELOG.md (如果有)

# 4. 提交更改
git add .
git commit -m "bump: version 0.1.0 → 0.2.0"
git tag v0.2.0
git push origin main --tags

# 5. 重新构建和发布
rm -rf dist/
uv build
twine check dist/*
twine upload --repository testpypi dist/*  # 先测试
twine upload dist/*  # 正式发布
```

### 8.3 自动化版本管理

考虑使用工具自动化版本管理：

```bash
# 使用 bump2version
pip install bump2version

# 配置 .bumpversion.cfg
# 然后可以自动更新版本
bump2version patch  # 0.1.0 → 0.1.1
bump2version minor  # 0.1.1 → 0.2.0
bump2version major  # 0.2.0 → 1.0.0
```

## 9. 常见问题解决

### 9.1 构建问题

**问题**: `ModuleNotFoundError` 在构建时

```bash
# 解决: 确保包结构正确，__init__.py 存在
find your_package -name "*.py" -exec python -m py_compile {} \;
```

**问题**: 依赖冲突

```bash
# 解决: 放宽依赖版本限制
# 从 dependency==1.0.0 改为 dependency>=1.0.0
```

### 9.2 发布问题

**问题**: `403 Forbidden` 错误

```bash
# 检查:
# 1. Token 是否正确
# 2. 包名是否已被占用
# 3. 是否有权限上传
```

**问题**: 包名已存在

```bash
# 解决:
# 1. 更改包名
# 2. 或联系现有包维护者
```

**问题**: 文件太大

```bash
# 检查包内容
tar -tf dist/your_package-0.1.0.tar.gz | head -20

# 更新 .gitignore 和 pyproject.toml 的 exclude
```

### 9.3 测试问题

**问题**: 导入错误

```bash
# 确保测试环境中包路径正确
python -c "import sys; print('\n'.join(sys.path))"
```

**问题**: 依赖问题

```bash
# 在干净环境中测试
pip list  # 查看已安装包
pip install --force-reinstall your-package
```

### 9.4 文档问题

**问题**: README 在 PyPI 显示不正确

```bash
# 检查 Markdown 格式
# 避免使用 GitHub 特定语法
# 测试在 rst.ninjaneer.org 或 GitHub 预览
```

**问题**: 元数据不完整

```bash
# 检查 pyproject.toml 中的所有必需字段
# 确保 classifiers 正确
```

## 📚 参考资源

### 官方文档

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [setuptools Documentation](https://setuptools.pypa.io/)

### 工具链

- [uv](https://github.com/astral-sh/uv) - 现代 Python 包管理器
- [hatchling](https://hatch.pypa.io/) - 现代构建后端
- [twine](https://twine.readthedocs.io/) - PyPI 上传工具

### 最佳实践

- [Python 包布局](https://packaging.python.org/tutorials/packaging-projects/)
- [语义化版本](https://semver.org/)
- [开源许可证选择](https://choosealicense.com/)

## 🎉 总结

完成以上步骤后，你的 Python 包就成功发布到 PyPI 了！用户可以通过 `pip install your-package` 或 `uv add your-package` 来安装和使用你的包。

记住：

- **先发布到 TestPyPI 测试**
- **确保文档和示例准确**
- **遵循语义化版本控制**
- **及时回应用户反馈**

祝你的包能帮助到更多开发者！🚀
