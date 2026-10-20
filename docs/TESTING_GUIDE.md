# 自动测试流程指南

## 概述

本项目采用 pytest 验证 NDAX 读取/配方、报告判定、版本与输出安全、GUI 信号和配置等功能。v5.0.0 的完整功能、真实数据验证与未验边界见 [发布说明](RELEASE_NOTES_v5.0.0.md)。

## v5.0.0 发布验证基线

- 自动回归：891 passed；`uv run ruff check src/ tests/ scripts/` 和 `git diff --check` 通过。
- 核心回归覆盖：Step.xml 配方、Profile 对照、输出路径占用、失败/取消清理、成功计次、手动版本及规范化重复、普通/必需缺失、无有效时间戳拒绝、类型同源和异常审计。
- GUI 测试通过 `QT_QPA_PLATFORM=offscreen` 运行，不等于人工完成所有界面分支验收。
- 真实 9 文件曾与旧 Excel 读取链逐槽对照；另用 CP5022121 16 文件临时输出重跑，保留全部 29 条原始异常，0 次普通缺失阻断、1 次成功信号，绘图 CSV 与历史报告逐字节相同。
- 禁止为了回归而覆盖用户既有报告或增加真实项目的成功次数。比较脚本应使用临时输出目录及隔离账本，结束后清理本次测试产物。
- 待验：全空容量报告（区别于无时间戳失败）、真实电流偏差、超大文件内存、多版本 BTS、完整人工 GUI 路径。未承诺 PNG/Word 二进制相同或完整 PDF 合规。

推荐发布前运行：

```bash
uv sync --all-extras
uv run python -m pytest -q --tb=short
uv run ruff check src/ tests/ scripts/
git diff --check
uv run python -c "from battery_analysis import __version__; assert __version__ == '5.0.0'; print(__version__)"
```

测试运行和打包不是同一项验收；通过测试并不表示已生成或发布新版安装包。

## 测试环境搭建

### 安装依赖

项目已在 `pyproject.toml` 中配置了测试所需的依赖，您可以通过以下命令安装：

```bash
# 使用 pip 安装开发依赖
pip install -e "[dev]"

# 或使用 uv 安装（推荐）
uv sync --all-extras
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
