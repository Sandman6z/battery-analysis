# P1 数据读加速 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Excel 读取引擎从 openpyxl/xlrd 迁移到 calamine（Rust 实现），移除 xlrd 依赖，消除 CSV 双读，使大文件读取性能提升 5-10 倍。

**Architecture:** 三个读取入口分别处理——(1) `read_xlsx_sheets` 用 calamine 引擎一次 `sheet_name=[0,1,2]` 读三表替代三次 openpyxl 读；(2) `extract_test_date_from_xls` 用 calamine 读前 20 行替代 xlrd 全表扫描（`nrows` 唯一适用点）；(3) `_parallel_process_file` 删除 xlrd 回退路径，读取失败归一化为 `BatteryAnalysisException`。预览/校验函数（`excel_processor`、`excel_validator`）只换引擎不加 nrows（其返回完整统计 `row_count`/`describe`/`missing_values`，nrows 会破坏语义）。`data_loader.csv_read` 用流式计数替代 `list(csvreader)` 全量读。`num2letter` 改用 `xlsxwriter.utility.xl_col_to_name`。

**Tech Stack:** pandas（`engine='calamine'`）、python-calamine（Rust，pandas ≥2.3 内置引擎）、xlsxwriter（已有依赖，`xl_col_to_name`）、删除 xlrd。

**设计修正（相对路线图）：** 路线图"预览/校验加 nrows"经代码审查确认**只适用于 `extract_test_date_from_xls`**。`read_excel_file`/`analyze_single_excel` 返回 `row_count`/`basic_stats`/`missing_values`，`validate_excel_file` 返回完整 df 供 `data_processor.py:261` 算 `row_count`——三者都依赖完整数据，nrows 会破坏统计语义。nrows 收益仅在日期提取（只搜前 20 行）处获得。

**执行状态（2026-08-20）：**
- ✅ Task 1 `read_xlsx_sheets` calamine 化 + 依赖 — 9d93fb3, f670cc1
- ✅ Task 2 `extract_test_date_from_xls` calamine + nrows + fixture — c72dcfc, c1e3c04（全量 521 passed/9 skipped）
- ✅ Task 3 删除 xlrd 回退 + 异常归一化 — 67eefd9, a876272（全量 522 passed/9 skipped，删 195 行）
- ✅ Task 4 excel_processor/excel_validator 换 calamine — d3fc6b9（全量 523 passed/9 skipped）
- ✅ Task 5 num2letter 改用 xlsxwriter — 8761e851（含边界契约锁，7 passed；**规格偏差修正见下**）+ 0f0bd10（code quality Minor 修复：陈旧注释改 0 基读数 + 负数契约 guard，8 passed，复核 ✅）
- ⬜ Task 6-8 待执行

**Task 5 规格修正（2026-08-20，implementer 发现 + 实证核验）：**
计划原写 `xl_col_to_name(_intCol + 1)`，假设 xl_col_to_name 1 基计数。**实测 xlsxwriter 3.0.9 源码该函数是 0 基**（文档 `Convert a zero indexed column cell reference to a string`，`xl_col_to_name(0)=='A'`），内部自行 `col_num += 1`。而 openpyxl `get_column_letter(1)=='A'` 是 1 基。原始 `num2letter(_intCol)` 输入即 0 基，正确替换为 **`xl_col_to_name(_intCol)` 不加偏移**——照搬 `+1` 会把输出整体平移一位（0→B），破坏行为保留。边界测试 `test_num2letter_boundaries` 正是为此设的回归锁。已更新下方 Step 3 代码。

**Task 4 审查遗留（Minor，可选）：**
- **M1** test_excel_processor.py:77-82 — 游离 docstring 字符串 + 重复 `import pandas`/`import read_excel_file`（顶部已导入），`TestCalamineEngine` 建议就近放 TestReadExcelFile 后。纯风格，未改。
- **M2** 引擎回归锁只覆盖 `read_excel_file` 一个调用点；`analyze_single_excel`（excel_processor.py:69）与 `validate_excel_file`（excel_validator.py:100）同款替换无独立锁。全量套件 + 实证对比已给出行为保障，未补。
- **注意** Task 1 契约锁（`assert_frame_equal(check_exact=True)`）锁的是 `read_xlsx_sheets` header=None 三 sheet 路径，非 Task 4 的 header=0 单 sheet 路径；code quality review 实证两引擎在该路径输出一致，风险可控。

---

## File Structure

| 文件 | 职责 | 操作 |
|---|---|---|
| `pyproject.toml` | 依赖管理 | Modify：加 `python-calamine`（Task 1），删 `xlrd==1.2.0`（Task 7） |
| `src/battery_analysis/utils/readers/xlsx_reader.py` | xlsx 读取器 | Modify：`read_xlsx_sheets` calamine 化（Task 1）、`extract_test_date_from_xls` 重写（Task 2） |
| `src/battery_analysis/utils/processors/battery_analysis.py` | 电池分析 | Modify：删 xlrd import、删回退路径、异常归一化（Task 3） |
| `src/battery_analysis/utils/processors/excel_processor.py` | Excel 统计预览 | Modify：engine → calamine（Task 4） |
| `src/battery_analysis/main/business_logic/excel_validator.py` | Excel 校验 | Modify：engine → calamine（Task 4） |
| `src/battery_analysis/utils/writers/excel_utils.py` | 列字母工具 | Modify：num2letter 用 xlsxwriter（Task 5） |
| `src/battery_analysis/main/visualization/data_loader.py` | CSV 数据加载 | Modify：去 `list(csvreader)` 双读（Task 6） |
| `tests/conftest.py` | 测试 fixture | Modify：加 `create_sample_xlsx_with_test_date` + `sample_xlsx_with_test_date`（Task 2） |
| `tests/battery_analysis/utils/readers/test_xlsx_reader.py` | xlsx_reader 测试 | Create：read_xlsx_sheets + extract_test_date（Task 1/2） |
| `tests/battery_analysis/utils/test_battery_analysis.py` | battery_analysis 测试 | Modify：mock xlrd 测试改真实文件（Task 3） |
| `tests/battery_analysis/utils/test_excel_processor.py` | excel_processor 测试 | Modify：engine 断言（Task 4） |
| `tests/battery_analysis/utils/test_excel_utils.py` | excel_utils 测试 | Modify：补边界断言（Task 5） |
| `tests/battery_analysis/main/visualization/test_data_loader.py` | data_loader 测试 | Create：csv_read 行为（Task 6） |
| `tests/test_battery_analysis_pandas.py` | pandas 集成测试 | Modify：4 处 `engine='openpyxl'` → calamine（Task 7） |

**任务依赖：** Task 1 → Task 2 → Task 3 顺序执行（同文件/同依赖链）；Task 4、5、6 相互独立可任意顺序；Task 7 依赖全部前置（删 xlrd 前必须清干净所有引用）。

---

### Task 1: read_xlsx_sheets 迁移 calamine + 添加依赖

**Files:**
- Modify: `pyproject.toml`（dependencies 段）
- Modify: `src/battery_analysis/utils/readers/xlsx_reader.py:12-17`
- Create: `tests/battery_analysis/utils/readers/test_xlsx_reader.py`

- [ ] **Step 1: 添加 python-calamine 依赖并安装**

Run: `uv add "python-calamine>=0.3.0,<1.0.0"`
Expected: 依赖写入 pyproject.toml、uv.lock 更新、安装成功。

验证安装与引擎可用：

Run: `.venv\Scripts\python.exe -c "import calamine, pandas as pd; print(calamine.__version__); print(pd.__version__)"`
Expected: 打印版本号，无 ImportError。

- [ ] **Step 2: 写 read_xlsx_sheets 契约锁定测试（新建测试文件）**

Create: `tests/battery_analysis/utils/readers/test_xlsx_reader.py`

```python
"""xlsx_reader 读取器测试（calamine 引擎回归锁）"""
import pandas as pd

from battery_analysis.utils.readers.xlsx_reader import read_xlsx_sheets


class TestReadXlsxSheets:
    def test_returns_three_dataframes(self, sample_xlsx):
        cycle_df, step_df, record_df = read_xlsx_sheets(str(sample_xlsx))
        assert isinstance(cycle_df, pd.DataFrame)
        assert isinstance(step_df, pd.DataFrame)
        assert isinstance(record_df, pd.DataFrame)

    def test_calamine_matches_openpyxl_content(self, sample_xlsx):
        """calamine 读取结果与 openpyxl 完全一致（值/类型回归锁）"""
        cycle_df, step_df, record_df = read_xlsx_sheets(str(sample_xlsx))

        expected_cycle = pd.read_excel(sample_xlsx, sheet_name=0, header=None, engine="openpyxl")
        expected_step = pd.read_excel(sample_xlsx, sheet_name=1, header=None, engine="openpyxl")
        expected_record = pd.read_excel(sample_xlsx, sheet_name=2, header=None, engine="openpyxl")

        pd.testing.assert_frame_equal(cycle_df, expected_cycle)
        pd.testing.assert_frame_equal(step_df, expected_step)
        pd.testing.assert_frame_equal(record_df, expected_record)
```

注意：`sample_xlsx` fixture 已在 `tests/conftest.py:80-83` 定义，返回 `Path`。

- [ ] **Step 3: 运行测试，确认当前实现通过（契约已锁定）**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/utils/readers/test_xlsx_reader.py -v`
Expected: 2 passed（当前 openpyxl 实现满足契约——这是重构前的契约锁定，非红绿测试）。

- [ ] **Step 4: 实现 calamine 一次性读三表**

Modify: `src/battery_analysis/utils/readers/xlsx_reader.py:12-17`，将

```python
def read_xlsx_sheets(filepath: str):
    """用 pandas 读取 xlsx 的三个工作表，返回 (cycle_df, step_df, record_df)"""
    cycle_df = pd.read_excel(filepath, sheet_name=0, header=None, engine='openpyxl')
    step_df = pd.read_excel(filepath, sheet_name=1, header=None, engine='openpyxl')
    record_df = pd.read_excel(filepath, sheet_name=2, header=None, engine='openpyxl')
    return cycle_df, step_df, record_df
```

替换为

```python
def read_xlsx_sheets(filepath: str):
    """用 calamine 引擎一次性读取 xlsx 的三个工作表，返回 (cycle_df, step_df, record_df)"""
    sheets = pd.read_excel(filepath, sheet_name=[0, 1, 2], header=None, engine='calamine')
    return sheets[0], sheets[1], sheets[2]
```

`sheet_name=[0, 1, 2]` 返回 `dict`，通过 `[0]`/`[1]`/`[2]` 取值，保持元组返回契约。文件缺 sheet 时 pandas 抛 `KeyError`（原 openpyxl 三次读抛 `ValueError`）——Task 3 的异常归一化会统一处理。

- [ ] **Step 5: 运行测试确认通过**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/utils/readers/test_xlsx_reader.py -v`
Expected: 2 passed（calamine 与 openpyxl 结果完全一致）。

- [ ] **Step 6: 提交**

```bash
git add pyproject.toml uv.lock src/battery_analysis/utils/readers/xlsx_reader.py tests/battery_analysis/utils/readers/test_xlsx_reader.py
git commit -m "feat: read_xlsx_sheets 迁移 calamine 引擎，一次读取三个工作表

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: extract_test_date_from_xls 迁移 calamine（nrows 读前 20 行）

**Files:**
- Modify: `src/battery_analysis/utils/readers/xlsx_reader.py:20-166`
- Modify: `tests/conftest.py`（`create_sample_xlsx` 定义后、`sample_xlsx` fixture 前）
- Modify: `tests/battery_analysis/utils/readers/test_xlsx_reader.py`（追加测试）

- [ ] **Step 1: 添加 Test Date fixture**

Modify: `tests/conftest.py`，在 `create_sample_xlsx`（line 77 的 `return filepath`）之后、`sample_xlsx` fixture 之前插入：

```python
def create_sample_xlsx_with_test_date(
    tmp_path: Path,
    filename: str = "test_date_sample.xlsx",
    test_date_value: str = "10.06.2025 - 08.07.2025",
) -> Path:
    """Create a test xlsx file with a Test Date field in the Cycle sheet

    文件名故意不含 8 位连续数字，避免触发 extract_test_date 的文件名回退，
    从而隔离验证 Test Date 单元格提取路径。
    """
    filepath = tmp_path / filename
    wb = openpyxl.Workbook()

    ws0 = wb.active
    ws0.title = "Cycle"
    ws0.append(["Test Date", test_date_value])
    ws0.append(["Cycle#", "CycleBegin", "CycleEnd", "Charge"])
    ws0.append([1, "2025-06-10 08:00:00", "2025-06-10 08:30:00", 0.5])

    ws1 = wb.create_sheet("Step")
    ws1.append(["Cycle#", "Step#", "Charge"])
    ws1.append([1, "Charge", 0.4])

    ws2 = wb.create_sheet("Record")
    ws2.append(["Cycle#", "Step#", "Current", "Voltage", "Charge"])
    ws2.append([1, "脉冲", -4.0, 4.2, 0.0])

    wb.save(filepath)
    return filepath


@pytest.fixture
def sample_xlsx_with_test_date(tmp_path):
    """pytest fixture: xlsx file containing a Test Date field"""
    return create_sample_xlsx_with_test_date(tmp_path)
```

- [ ] **Step 2: 写 extract_test_date 行为测试**

Modify: `tests/battery_analysis/utils/readers/test_xlsx_reader.py`，追加：

```python
from battery_analysis.utils.readers.xlsx_reader import (
    extract_test_date_from_xls,
    read_xlsx_sheets,
)


class TestExtractTestDate:
    def test_from_test_date_cell(self, sample_xlsx_with_test_date):
        """Test Date 单元格右侧的日期值（10.06.2025 - 08.07.2025 取起始日）"""
        assert extract_test_date_from_xls(str(sample_xlsx_with_test_date)) == "20250610"

    def test_from_filename(self, tmp_path):
        """无 Test Date 单元格时回退文件名解析"""
        import openpyxl

        file_path = tmp_path / "test_20250715_data.xlsx"
        wb = openpyxl.Workbook()
        ws0 = wb.active
        ws0.title = "Cycle"
        ws0.append(["Cycle#", "CycleBegin", "CycleEnd"])
        ws0.append([1, "2025-06-10 08:00:00", "2025-06-10 08:30:00"])
        wb.save(file_path)
        assert extract_test_date_from_xls(str(file_path)) == "20250715"

    def test_broken_file_returns_default(self, tmp_path):
        broken = tmp_path / "broken.xlsx"
        broken.write_bytes(b"not a real xlsx file")
        assert extract_test_date_from_xls(str(broken)) == "00000000"
```

注意：`create_sample_xlsx` 定义在 `tests/conftest.py`，conftest 内的工厂函数不能从测试模块 import（pytest 约定），因此 `test_from_filename` 在测试内联生成最小 xlsx。

- [ ] **Step 3: 运行测试，确认当前实现通过（契约锁定）**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/utils/readers/test_xlsx_reader.py -v`
Expected: 5 passed（xlrd 旧实现也能从这些文件提取日期——重构前的契约锁定）。

- [ ] **Step 4: 重写 extract_test_date_from_xls（去 xlrd，calamine + nrows=20）**

Modify: `src/battery_analysis/utils/readers/xlsx_reader.py:20-166`，删除整个 `extract_test_date_from_xls` 原实现（含 `import xlrd as rd` 一并删除——见 Step 5），替换为：

```python
def extract_test_date_from_xls(filepath: str) -> str:
    """
    从 Excel 文件中提取 Test Date 字段

    用 calamine 引擎只读取各工作表前 20 行，搜索 "Test Date" 或 "测试日期"
    单元格，尝试多种日期格式解析。如果无法提取，尝试从文件名解析。

    Args:
        filepath: Excel 文件路径

    Returns:
        str: 格式化的日期字符串 (YYYYMMDD)，如果无法提取则返回默认值
    """
    try:
        sheets = pd.read_excel(
            filepath, sheet_name=None, header=None, nrows=20, engine="calamine")

        # 搜索所有工作表中的 "Test Date" 字段（只查前 20 行）
        for sheet_df in sheets.values():
            for row in range(min(20, len(sheet_df))):
                for col in range(len(sheet_df.columns)):
                    cell_value = sheet_df.iloc[row, col]
                    if isinstance(cell_value, str) and (
                        "Test Date" in cell_value or "测试日期" in cell_value
                    ):
                        # 右侧相邻单元格
                        if col + 1 < len(sheet_df.columns):
                            parsed = _parse_date_str(sheet_df.iloc[row, col + 1])
                            if parsed:
                                return parsed
                        # 下方单元格
                        if row + 1 < len(sheet_df):
                            parsed = _parse_date_str(sheet_df.iloc[row + 1, col])
                            if parsed:
                                return parsed

        # 找不到 Test Date 字段，尝试从文件名提取
        file_name = os.path.basename(filepath)
        logger.debug("Parsing date from file name: %s", file_name)
        parsed = _parse_date_from_filename(file_name)
        if parsed:
            return parsed

    except Exception as e:  # pylint: disable=broad-exception-caught
        # 日期提取是尽力而为：任何读取/解析失败都回退默认值
        logger.error(
            "Failed to extract Test Date from Excel: %s, error: %s", filepath, e)

    # 确保总是有返回值
    return "00000000"


def _parse_date_str(date_value) -> str | None:
    """尝试把单元格值解析为日期，返回 YYYYMMDD；无法解析返回 None"""
    if not isinstance(date_value, str) or not date_value.strip():
        return None
    date_str = date_value.strip()
    # 格式1: 10.06.2025 - 08.07.2025（取起始日期）
    if "-" in date_str and "." in date_str:
        start = date_str.split("-")[0].strip()
        parts = start.split(".")
        if len(parts) == 3:
            day, month, year = parts
            return f"{year.zfill(4)}{month.zfill(2)}{day.zfill(2)}"
    # 格式2: 2025-06-10
    if "-" in date_str:
        parts = date_str.split("-")
        if len(parts) >= 3:
            year, month, day = parts[:3]
            return f"{year.zfill(4)}{month.zfill(2)}{day.zfill(2)}"
    return None


def _parse_date_from_filename(file_name: str) -> str | None:
    """尝试从文件名提取日期，返回 YYYYMMDD；无法解析返回 None"""
    # 匹配文件名中所有连续的数字组，取最后一组的前 8 位
    digit_groups = re.findall(r"(\d+)", file_name)
    if digit_groups:
        last_digit_group = digit_groups[-1]
        if len(last_digit_group) >= 8:
            date_str = last_digit_group[:8]
            try:
                year = int(date_str[:4])
                if 2000 <= year <= 2100:
                    return date_str
                logger.warning("Extracted year %s is not in valid range", year)
            except ValueError:
                logger.error("Could not parse year")

    # 其他常见日期格式
    date_patterns = [
        (r"(\d{4})-(\d{2})-(\d{2})", False),  # 2025-06-10
        (r"(\d{2})\.(\d{2})\.(\d{4})", True),  # 10.06.2025
    ]
    for pattern, is_dmy in date_patterns:
        match = re.search(pattern, file_name)
        if match:
            groups = match.groups()
            if is_dmy:
                day, month, year = groups
                return f"{year}{month.zfill(2)}{day.zfill(2)}"
            year, month, day = groups
            return f"{year}{month.zfill(2)}{day.zfill(2)}"
    return None
```

- [ ] **Step 5: 删除 xlrd import**

Modify: `src/battery_analysis/utils/readers/xlsx_reader.py:7`，删除 `import xlrd as rd`（全文件已无 xlrd 引用）。

- [ ] **Step 6: 运行测试确认通过**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/utils/readers/test_xlsx_reader.py -v`
Expected: 5 passed（calamine 路径提取日期）。

- [ ] **Step 7: 提交**

```bash
git add src/battery_analysis/utils/readers/xlsx_reader.py tests/conftest.py tests/battery_analysis/utils/readers/test_xlsx_reader.py
git commit -m "feat: extract_test_date_from_xls 迁移 calamine，nrows=20 只读前 20 行

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: battery_analysis 删除 xlrd 回退路径

**Files:**
- Modify: `src/battery_analysis/utils/processors/battery_analysis.py`
- Modify: `tests/battery_analysis/utils/test_battery_analysis.py`

- [ ] **Step 1: 写红测试——读取失败归一化为 BatteryAnalysisException**

Modify: `tests/battery_analysis/utils/test_battery_analysis.py`，在文件顶部补 import，并给 `TestBatteryAnalysis` 加方法：

```python
import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.exceptions import BatteryAnalysisException
from battery_analysis.utils.processors.battery_analysis import BatteryAnalysis
```

```python
    def test_parallel_process_file_normalizes_read_failure(self, sample_xlsx):
        """read_xlsx_sheets 失败时应归一化为 BatteryAnalysisException，而非走 xlrd 回退"""
        args = (str(sample_xlsx), [500, 1000], [3.0, 4.0])
        with patch(
            "battery_analysis.utils.processors.battery_analysis.read_xlsx_sheets",
            side_effect=ValueError("simulated corrupt file"),
        ):
            with pytest.raises(BatteryAnalysisException, match="Failed to read Excel file"):
                BatteryAnalysis._parallel_process_file(args)
```

- [ ] **Step 2: 运行测试，确认当前实现失败**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/utils/test_battery_analysis.py::TestBatteryAnalysis::test_parallel_process_file_normalizes_read_failure -v`
Expected: **FAIL**（当前实现 `read_xlsx_sheets` 失败后调用 xlrd 回退，真实读 sample_xlsx 成功，不抛 `BatteryAnalysisException`）。

- [ ] **Step 3: 实现——删除回退路径、异常归一化、清理 xlrd 引用**

Modify: `src/battery_analysis/utils/processors/battery_analysis.py`：

(a) 删除 `_parallel_process_file_xlrd_fallback` 方法：删除 **line 339-499** 的全部内容（line 339-341 的 `# 文件级处理（xlrd 回退路径）` 分隔注释块、line 342 的 `@staticmethod`、line 343-499 的方法体）。**保留** line 500-502 的 `# 日期工具` 注释块（属于下一个方法 `_str_compare_date`）。

(b) 修改 `_parallel_process_file`（原 line 256-260）：将

```python
        try:
            cycle_df, step_df, record_df = read_xlsx_sheets(strPath)
        except Exception as e:
            logging.error("pandas read failed %s, falling back to xlrd. Original error: %s", strPath, e)
            return BatteryAnalysis._parallel_process_file_xlrd_fallback(args)
```

替换为

```python
        try:
            cycle_df, step_df, record_df = read_xlsx_sheets(strPath)
        except Exception as e:  # pylint: disable=broad-exception-caught
            # calamine 引擎异常类型随 pandas 版本变化，统一归一化为业务异常，
            # 由 worker 层的异常处理跳过该文件
            raise BatteryAnalysisException(
                f"Failed to read Excel file: {strPath}: {e}") from e
```

(c) 删除模块级 `import xlrd as rd`（原 line 25）。

(d) 清理 run() 主循环的 except 子句（原 line 242）：从 `except (IOError, OSError, ValueError, rd.XLRDError, BatteryAnalysisException, KeyError):` 中移除 `rd.XLRDError,`，改为 `except (IOError, OSError, ValueError, BatteryAnalysisException, KeyError):`。

(e) 运行 grep 确认全文件无残留 xlrd 引用：

Run: `git grep -n "xlrd\|XLRDError\|_parallel_process_file_xlrd_fallback" src/battery_analysis/utils/processors/battery_analysis.py`
Expected: 无输出。

- [ ] **Step 4: 重写 test_uba_get_test_date_from_excel（mock xlrd → 真实文件）**

现有测试（line 7-33）patch `battery_analysis.utils.processors.battery_analysis.rd.open_workbook`——该 patch 目标无效（`extract_test_date_from_xls` 实际使用 `xlsx_reader.rd`），且删除 xlrd 后 patch 目标不存在。用真实文件验证 calamine 路径：

Modify: `tests/battery_analysis/utils/test_battery_analysis.py`，将 `test_uba_get_test_date_from_excel` 方法体替换为：

```python
    def test_uba_get_test_date_from_excel(self, sample_xlsx_with_test_date):
        """UBA_GetTestDateFromExcel 应委托 extract_test_date_from_xls 返回 YYYYMMDD"""
        analysis = Mock(spec=BatteryAnalysis)
        analysis.UBA_GetTestDateFromExcel = BatteryAnalysis.UBA_GetTestDateFromExcel.__get__(analysis)
        result = analysis.UBA_GetTestDateFromExcel(str(sample_xlsx_with_test_date))
        assert result == "20250610"
```

- [ ] **Step 5: 运行测试**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/utils/test_battery_analysis.py tests/battery_analysis/utils/readers/test_xlsx_reader.py -v`
Expected: 全部通过（含 Step 2 的红测试转绿，以及重写后的日期提取测试）。

- [ ] **Step 6: 提交**

```bash
git add src/battery_analysis/utils/processors/battery_analysis.py tests/battery_analysis/utils/test_battery_analysis.py
git commit -m "refactor: 删除 xlrd 回退路径，读取失败归一化为 BatteryAnalysisException

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: excel_processor + excel_validator 换 calamine 引擎

**Files:**
- Modify: `src/battery_analysis/utils/processors/excel_processor.py:38,69`
- Modify: `src/battery_analysis/main/business_logic/excel_validator.py:100`
- Modify: `tests/battery_analysis/utils/test_excel_processor.py`

**说明：** 这两个模块**不加 nrows**——`read_excel_file`/`analyze_single_excel` 返回 `row_count`/`basic_stats`/`missing_values`，`validate_excel_file` 返回完整 df 供 `data_processor.py:261` 算 `row_count`，nrows 会破坏统计语义。只换引擎即获得 calamine 提速。

- [ ] **Step 1: 写红测试——引擎参数断言**

Modify: `tests/battery_analysis/utils/test_excel_processor.py`，追加：

```python
"""excel_processor 引擎迁移测试（calamine）"""
from unittest.mock import patch

import pandas as pd

from battery_analysis.utils.processors.excel_processor import read_excel_file


class TestCalamineEngine:
    def test_read_excel_file_uses_calamine_engine(self, sample_xlsx):
        with patch("pandas.read_excel") as mock_read:
            mock_read.return_value = pd.DataFrame({"A": [1, 2, 3]})
            read_excel_file(str(sample_xlsx))
        assert mock_read.call_args.kwargs["engine"] == "calamine"
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/utils/test_excel_processor.py::TestCalamineEngine -v`
Expected: **FAIL**（当前 `engine="openpyxl"`）。

- [ ] **Step 3: 实现——engine 改 calamine**

Modify: `src/battery_analysis/utils/processors/excel_processor.py`：
- line 38：`engine="openpyxl"` → `engine="calamine"`
- line 69：`engine="openpyxl"` → `engine="calamine"`

Modify: `src/battery_analysis/main/business_logic/excel_validator.py:100`：`engine='openpyxl'` → `engine='calamine'`

- [ ] **Step 4: 运行测试**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/utils/test_excel_processor.py tests/battery_analysis/main/business_logic/test_data_processor.py -v`
Expected: 全部通过。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/utils/processors/excel_processor.py src/battery_analysis/main/business_logic/excel_validator.py tests/battery_analysis/utils/test_excel_processor.py
git commit -m "perf: excel_processor/excel_validator 换 calamine 引擎（保留全量统计语义）

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: num2letter 改用 xlsxwriter.xl_col_to_name

**Files:**
- Modify: `src/battery_analysis/utils/writers/excel_utils.py`
- Modify: `tests/battery_analysis/utils/test_excel_utils.py`

- [ ] **Step 1: 补边界断言测试**

Modify: `tests/battery_analysis/utils/test_excel_utils.py`，在现有 `test_num2letter` 后追加：

```python
    def test_num2letter_boundaries(self):
        """Z/AA/AZ 列边界——get_column_letter 与 xl_col_to_name 计数差异回归锁"""
        assert num2letter(25) == "Z"
        assert num2letter(26) == "AA"
        assert num2letter(51) == "AZ"
```

（`num2letter` 与现有测试的 import 方式保持一致——如现有测试用 `from battery_analysis.utils.writers.excel_utils import num2letter`。）

- [ ] **Step 2: 运行测试确认通过（契约锁定）**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/utils/test_excel_utils.py -v`
Expected: 全部通过（openpyxl 实现满足边界断言）。

- [ ] **Step 3: 实现——改用 xlsxwriter**

Modify: `src/battery_analysis/utils/writers/excel_utils.py:2`，将

```python
from openpyxl.utils import get_column_letter
```

替换为

```python
from xlsxwriter.utility import xl_col_to_name
```

并将 `num2letter`（line 17-18）替换为：

```python
def num2letter(_intCol: int) -> str:
    """列序号转列字母（0 → A, 25 → Z, 26 → AA）"""
    return xl_col_to_name(_intCol)
```

**注意：`xl_col_to_name` 是 0 基**（`xl_col_to_name(0) == "A"`，源码文档 `Convert a zero indexed column cell reference to a string`），而 `get_column_letter` 是 1 基（`get_column_letter(1) == "A"`）。原始 `num2letter(_intCol)` 输入即为 0 基，故**不加 `+1` 偏移**。早期计划片段误写为 `+1`（会把输出整体平移一位，0→B），2026-08-20 由 implementer 实证修正，边界测试 `test_num2letter_boundaries` 是回归锁。

- [ ] **Step 4: 运行测试**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/utils/test_excel_utils.py -v`
Expected: 全部通过。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/utils/writers/excel_utils.py tests/battery_analysis/utils/test_excel_utils.py
git commit -m "refactor: num2letter 改用 xlsxwriter.xl_col_to_name，openpyxl 运行时引用清零

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: data_loader 消除 list(csvreader) 全量双读

**Files:**
- Modify: `src/battery_analysis/main/visualization/data_loader.py:217-228`
- Create: `tests/battery_analysis/main/visualization/test_data_loader.py`

- [ ] **Step 1: 写行为锁定测试**

Create: `tests/battery_analysis/main/visualization/test_data_loader.py`

```python
"""data_loader.csv_read 行为测试"""
from battery_analysis.main.visualization.data_loader import DataLoaderMixin


class _StubDataLoader(DataLoaderMixin):
    """最小 DataLoader 实现，覆盖 csv_read 依赖的钩子"""

    def __init__(self, csv_path):
        self.strInfoImageCsvPath = str(csv_path)
        self.strPltPath = str(csv_path.parent)
        self.listBatteryName = ["Battery_1"]
        self.intCurrentLevelNum = 1
        self.intBatteryNum = 0
        self.last_data_path = None
        self.listPlt = [[0, 1, True, 2, 3, 4]]
        self.processed_rows = 0

    def _initialize_data_structures(self):
        self.listPlt = [[0, 1, True, 2, 3, 4]]

    def _process_csv_data(self, csvreader):
        self.processed_rows = sum(1 for _ in csvreader)

    def _parse_battery_names(self):
        pass

    def _filter_all_data(self):
        pass


class TestCsvRead:
    def test_processes_all_rows(self, tmp_path):
        csv_path = tmp_path / "Info_Image.csv"
        csv_path.write_text(
            "\n".join(f"{i},0,0,0,0" for i in range(20)), encoding="utf-8")
        loader = _StubDataLoader(csv_path)
        loader.csv_read()
        assert loader.processed_rows == 20
        assert loader.intBatteryNum == 1

    def test_rejects_too_few_rows(self, tmp_path):
        csv_path = tmp_path / "Info_Image.csv"
        csv_path.write_text("a,b,c\n", encoding="utf-8")
        loader = _StubDataLoader(csv_path)
        loader.csv_read()
        assert loader.intBatteryNum == 0
```

- [ ] **Step 2: 运行测试确认通过（契约锁定）**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/main/visualization/test_data_loader.py -v`
Expected: 2 passed（当前 `list(csvreader)` 实现满足行为）。

- [ ] **Step 3: 实现——流式计数替代全量 list**

Modify: `src/battery_analysis/main/visualization/data_loader.py:217-228`，将

```python
            with open(csv_path, mode='r', encoding='utf-8') as f:
                csvreader = csv.reader(f)
                all_rows = list(csvreader)
                if len(all_rows) < 5:
                    logger.error(
                        "Error: CSV file %s has insufficient data rows", self.strInfoImageCsvPath)
                    self.intBatteryNum = 0
                    return

                f.seek(0)
                csvreader = csv.reader(f)
                self._process_csv_data(csvreader)
```

替换为

```python
            with open(csv_path, mode='r', encoding='utf-8') as f:
                csvreader = csv.reader(f)
                # 流式计数替代 list() 全量读，避免大文件内存翻倍（all_rows 只用于行数检查）
                row_count = sum(1 for _ in csvreader)
                if row_count < 5:
                    logger.error(
                        "Error: CSV file %s has insufficient data rows", self.strInfoImageCsvPath)
                    self.intBatteryNum = 0
                    return

                f.seek(0)
                csvreader = csv.reader(f)
                self._process_csv_data(csvreader)
```

`all_rows` 在原代码中仅用于 `len(all_rows) < 5` 检查（line 220），`seek(0)` 后重新读取是既有行为，保留。

- [ ] **Step 4: 运行测试**

Run: `.venv\Scripts\python.exe -m pytest tests/battery_analysis/main/visualization/test_data_loader.py -v`
Expected: 2 passed。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/main/visualization/data_loader.py tests/battery_analysis/main/visualization/test_data_loader.py
git commit -m "perf: data_loader.csv_read 用流式计数替代 list() 全量读，消除内存翻倍

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 7: 移除 xlrd 依赖 + 全量回归 + 基准验证

**Files:**
- Modify: `pyproject.toml`（删除 `xlrd==1.2.0`）
- Modify: `tests/test_battery_analysis_pandas.py`（4 处 `engine='openpyxl'` → `'calamine'`）

- [ ] **Step 1: 确认全仓无 xlrd 残留引用**

Run: `git grep -n "xlrd\|XLRDError\|open_workbook" src tests pyproject.toml`
Expected: **无输出**（Task 1-6 已清理全部 xlrd 引用；若 `tests/test_battery_analysis_pandas.py` 出现 `open_workbook` 则一并处理——见 Step 3）。

- [ ] **Step 2: 移除 xlrd 依赖**

Modify: `pyproject.toml` line 36，删除 `    "xlrd==1.2.0",` 这一行。

Run: `uv sync`
Expected: 依赖移除成功，无报错。

验证 xlrd 已卸载：

Run: `.venv\Scripts\python.exe -c "import xlrd"`
Expected: **ModuleNotFoundError**（依赖已移除）。

- [ ] **Step 3: test_battery_analysis_pandas.py 的 openpyxl 引擎改 calamine**

Modify: `tests/test_battery_analysis_pandas.py`，将全部 4 处 `engine='openpyxl'` 改为 `engine='calamine'`（line 14、15、16、24、35、52）。

- [ ] **Step 4: 全量回归**

Run: `.venv\Scripts\python.exe -m pytest -q`
Expected: 全部通过（预计 515+ passed，9 skipped）。

- [ ] **Step 5: 运行 pylint**

Run: `.venv\Scripts\python.exe -m pylint src/battery_analysis --rcfile=pyproject.toml`
Expected: 评分不低于 8.7/10，无新增 error。

- [ ] **Step 6: 基准验证——calamine vs openpyxl 大文件读取**

创建临时基准脚本（**不提交**，放 `$CLAUDE_JOB_DIR/tmp/benchmark_read.py`）：

```python
"""临时基准：calamine vs openpyxl 读取大 xlsx 三表耗时对比（不提交）"""
import tempfile
import time
from pathlib import Path

import pandas as pd

# 生成 ~50k 行 xlsx
def make_big_xlsx(path: Path) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet, n in [("Cycle", 50000), ("Step", 50000), ("Record", 50000)]:
            df = pd.DataFrame(
                {"a": range(n), "b": [float(i) for i in range(n)], "c": ["x"] * n}
            )
            df.to_excel(writer, sheet_name=sheet, header=None, index=False)


def bench(read, label: str, path: Path, times: int = 3) -> float:
    best = float("inf")
    for _ in range(times):
        t0 = time.perf_counter()
        read(path)
        best = min(best, time.perf_counter() - t0)
    print(f"{label}: {best:.3f}s")
    return best


def read_openpyxl(path: Path):
    for idx in range(3):
        pd.read_excel(path, sheet_name=idx, header=None, engine="openpyxl")


def read_calamine(path: Path):
    pd.read_excel(path, sheet_name=[0, 1, 2], header=None, engine="calamine")


with tempfile.TemporaryDirectory() as tmp:
    big = Path(tmp) / "big.xlsx"
    print("Generating big xlsx...")
    make_big_xlsx(big)
    print(f"File size: {big.stat().st_size / 1024 / 1024:.1f} MB")
    t_openpyxl = bench(read_openpyxl, "openpyxl", big)
    t_calamine = bench(read_calamine, "calamine", big)
    print(f"\nSpeedup: {t_openpyxl / t_calamine:.1f}x")
```

Run: `.venv\Scripts\python.exe "$CLAUDE_JOB_DIR/tmp/benchmark_read.py"`
Expected: 输出 `Speedup: 5-10x`（P1 验收标准）。若低于 5x，记录实际倍率并说明原因，不阻塞合并。

- [ ] **Step 7: 提交**

```bash
git add pyproject.toml uv.lock tests/test_battery_analysis_pandas.py
git commit -m "build: 移除 xlrd 依赖，测试全量改用 calamine 引擎

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 8: 收尾——最终审查 + PR

- [ ] **Step 1: 复核验收标准**

对照路线图 P1 定义核对：
1. 大文件读取基准提升 5-10 倍（Task 7 Step 6 输出）
2. `xlrd` 从依赖移除（Task 7 Step 2 验证）
3. calamine 类型差异过回归（Task 7 Step 4 全量 + Task 1 的 `assert_frame_equal` 锁定）

Run: `git diff main --stat`
Expected: 变更集中在 P1 范围文件，无意外文件。

- [ ] **Step 2: 运行最终全量回归 + pylint**

Run: `.venv\Scripts\python.exe -m pytest -q && .venv\Scripts\python.exe -m pylint src/battery_analysis --rcfile=pyproject.toml`
Expected: 全部通过，评分 ≥8.7。

- [ ] **Step 3: 创建 PR 合并到 main**

按 P0 先例：推送分支，创建 PR，等 ci-cd build-and-test 全绿后合入 main。

---

## 验收标准

1. **性能**：大文件读取基准提升 5-10 倍（Task 7 实测，`Speedup: Nx` 记录在案）
2. **依赖**：`xlrd` 从 `pyproject.toml` 移除，`uv sync` 后 `import xlrd` 报 ModuleNotFoundError
3. **回归**：全量 pytest 通过（≥515 passed/9 skipped）；pylint ≥8.7
4. **类型一致性**：Task 1 的 `assert_frame_equal` 锁定 calamine 与 openpyxl 值/类型完全一致
5. **异常路径**：损坏 xlsx 读取失败归一化为 `BatteryAnalysisException`，worker 层跳过该文件而非崩溃
6. **CSV 内存**：`csv_read` 不再 `list()` 全量读（流式计数），内存占用不随行数翻倍
