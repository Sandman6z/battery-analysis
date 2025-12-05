# 自动测试流程指南

## 概述

本项目采用 pytest 框架进行自动测试，主要用于验证核心功能的正确性，特别是确保 ReportedBy 与 TesterLocation 的匹配逻辑符合预期。

## 测试环境搭建

### 安装依赖

项目已在 `pyproject.toml` 中配置了测试所需的依赖，您可以通过以下命令安装：

```bash
# 使用 pip 安装开发依赖
pip install -e "[dev]"

# 或使用 uv 安装（推荐）
uv install
```

## 运行测试

### 使用 pytest 直接运行

您可以使用 pytest 命令直接运行测试：

```bash
# 运行所有测试
python -m pytest

# 运行特定目录的测试
python -m pytest tests/battery_analysis/main/

# 运行特定测试文件
python -m pytest tests/battery_analysis/main/test_main_window.py

# 运行特定测试用例
python -m pytest tests/battery_analysis/main/test_main_window.py::test_reported_by_matching
```

### 使用测试脚本运行

项目提供了一个简化的测试脚本 `scripts/run_tests.py`，您可以使用它来运行测试：

```bash
# 运行所有测试
python scripts/run_tests.py

# 运行特定目录的测试
python scripts/run_tests.py tests/battery_analysis/main/

# 运行特定测试文件
python scripts/run_tests.py tests/battery_analysis/main/test_main_window.py

# 生成 HTML 测试报告
python scripts/run_tests.py --report

# 生成 XML 测试报告
python scripts/run_tests.py --report --format xml
```

## 测试报告

### 生成 HTML 报告

HTML 报告包含详细的测试结果、测试用例信息和错误堆栈：

```bash
python -m pytest --html=test_report.html --self-contained-html
```

或使用测试脚本：

```bash
python scripts/run_tests.py --report
```

### 生成 XML 报告

XML 报告（JUnit 格式）适用于 CI/CD 集成：

```bash
python -m pytest --junitxml=test_report.xml
```

或使用测试脚本：

```bash
python scripts/run_tests.py --report --format xml
```

## 添加新测试用例

### 测试文件命名规范

测试文件应遵循以下命名规范之一：
- `test_*.py`（推荐）
- `*_test.py`

### 测试函数命名规范

测试函数应遵循以下命名规范：
- `test_*`

### 测试类命名规范

测试类应遵循以下命名规范：
- `Test*`

## 编写测试用例

### 单元测试

单元测试用于测试单个函数或方法的功能：

```python
def test_add():
    """测试加法函数"""
    assert add(1, 2) == 3
```

### 参数化测试

参数化测试用于测试多个输入组合的情况：

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    """测试加法函数的多种输入情况"""
    assert add(a, b) == expected
```

### 模拟测试

模拟测试用于测试依赖外部资源的功能：

```python
from unittest.mock import Mock, patch

def test_read_file():
    """测试读取文件的功能"""
    with patch('builtins.open', return_value=Mock(read=lambda: 'test content')):
        assert read_file('test.txt') == 'test content'
```

## 测试覆盖率

### 安装覆盖率工具

```bash
pip install pytest-cov
```

### 生成覆盖率报告

```bash
# 生成覆盖率报告
python -m pytest --cov=src

# 生成 HTML 覆盖率报告
python -m pytest --cov=src --cov-report=html
```

## CI/CD 集成

项目已配置 GitHub Actions 工作流，用于自动运行测试和生成报告。您可以在 `.github/workflows/` 目录下查看详细配置。

## 常见问题

### 测试失败

如果测试失败，您可以查看失败信息以定位问题：

```bash
# 查看失败信息
python -m pytest -v

# 查看更详细的失败信息
python -m pytest -vv
```

### 依赖问题

如果遇到依赖问题，您可以尝试重新安装依赖：

```bash
# 重新安装所有依赖
pip install -e "[dev]" --force-reinstall

# 或使用 uv
uv install --force-reinstall
```

## 结语

自动测试是确保软件质量的重要手段，建议您在开发新功能或修复 bug 时，编写相应的测试用例，以提高代码的可靠性和可维护性。
