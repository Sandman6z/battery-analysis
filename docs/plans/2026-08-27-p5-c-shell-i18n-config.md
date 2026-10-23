# P5-C 空壳清理 + i18n 去 eval Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 回退 UIBridge 仪式性抽象（删 app_context.py 全文件 + 21 个 manager 的 ctx 参数），移除 translator.py 的 eval 注入风险，完成 P5-C（空壳+i18n）。

**Architecture:** 3 个子任务顺次收口：① 3 个真正使用 ctx 的 manager（visualization/report/environment）逻辑回退到直接 `main_window` 访问（fallback 分支已就绪，纯收敛）；② 18 个把 ctx 当死参数存了从不读的类机械删参；③ 删 app_context.py 整个文件。i18n 独立：`_compile_plural_formula` 的 eval 替换为已知公式表（以归一化公式串为键），删 `_c_ternary_to_python`。

**Tech Stack:** PyQt6（QtWidgets/QThreadPool）、Python stdlib（gettext/typing）、pytest、pylint。

---

## 范围决策

**config JSON：cut（不实施）**——执行 spec `2026-08-25-p5-architecture-execution-design.md:55` 授权「plan 阶段如价值不成比例可砍」。摸底结论：`DEFAULT_CONFIG`（184 行 Python dict）移动到 JSON 资源**非纯移动**——① `DEFAULT_CONFIG["battery"]["specifications"]` 在 import 时由 `derive_specifications(DEFAULT_CONFIG["battery"]["rules"])` 派生（JSON 无法静态表达，需保留 loader + 派生函数，破坏 `test_config_defaults.py` 的「specifications 必须从 rules 派生」不变量）；② 需新建资源加载基建（`importlib.resources` + `pyproject.toml` package-data + PyInstaller `sys._MEIPASS` 路径）；③ 引用点仅 4 处 src + 2 处 test，无非 Python 消费者，启动零收益。**改动面明显大于收益，cut**。

---

## 文件结构

- Delete: `src/battery_analysis/main/app_context.py`（UIBridge/UIBridgeImpl/AppContext/PathContext 全部）
- Modify（A 类 3 个，逻辑回退）:
  - `src/battery_analysis/main/managers/visualization_manager.py`
  - `src/battery_analysis/main/managers/report_manager.py`
  - `src/battery_analysis/main/managers/environment_manager.py`
- Modify（B 类 18 个，死参数删除）:
  - `src/battery_analysis/main/business_logic/data_processor.py`、`version_manager.py`、`help_manager.py`、`validation_manager.py`
  - `src/battery_analysis/main/handlers/temperature_handler.py`
  - `src/battery_analysis/main/managers/analysis_runner.py`、`path_manager.py`、`test_profile_manager.py`
  - `src/battery_analysis/main/ui_components/config_manager.py`、`dialog_manager.py`、`menu_manager.py`、`message_manager.py`、`table_manager.py`、`theme_manager.py`、`ui_manager.py`、`window_setup.py`
  - `src/battery_analysis/main/utils/environment_adapter.py`、`signal_connector.py`
- Modify: `src/battery_analysis/i18n/translator.py`（去 eval）
- Test: `tests/battery_analysis/i18n/test_i18n.py`（新增公式表测试）
- Init steps 3 个文件（handlers/managers/processors_initialization_step.py）**无需改动**（均只传 `main_window`，从不传 `ctx=`，已 grep 确认）。

---

## Task C1: 回退 3 个 A 类 manager（visualization/report/environment）

**Files:**
- Modify: `src/battery_analysis/main/managers/visualization_manager.py`
- Modify: `src/battery_analysis/main/managers/report_manager.py`
- Modify: `src/battery_analysis/main/managers/environment_manager.py`

这 3 个类真正消费 `ctx`（`self._ui` / `self._ctx`），但**每处使用点都已带 `elif self.main_window` / `if self.main_window` 直接访问 fallback**（摸底确认）。revert = 删 `_ui`/`_ctx` 分支、保留 main_window 分支。无测试引用（tests 只传 main_window/Mock()），纯重构、无行为变更。

- [ ] **Step 1: visualization_manager.py 回退**

删头部 `from battery_analysis.main.app_context import AppContext, UIBridge`。`__init__` 改为：

```python
    def __init__(self, main_window=None):
        """
        初始化可视化管理器

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._parent_widget = main_window
```

删 `_make_bridge` 静态方法（原 :25-28）。回退 3 个使用点：

```python
    def _get_test_profile(self) -> str:
        if self.main_window and hasattr(self.main_window, 'lineEdit_TestProfile'):
            return self.main_window.lineEdit_TestProfile.text()
        return ""

    def _status(self, msg: str):
        if self.main_window and hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage(msg)
```

```python
    def _critical(self, title, msg):
        if self.main_window:
            QW.QMessageBox.critical(self.main_window, title, msg)
```

> `_parent_widget` 保留（`_handle_visualization_error` :107 用 `self._parent_widget or self.main_window`）。`_get_visualizer_factory`、`run_visualizer`、`_cleanup_matplotlib_resources`、`_handle_visualization_error`、`show_visualizer_error` 不动。

- [ ] **Step 2: report_manager.py 回退**

删头部 `from battery_analysis.main.app_context import AppContext, UIBridge`。`__init__` 改为：

```python
    def __init__(self, main_window=None):
        """
        初始化报告管理器

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._parent_widget = main_window  # 对话框需要 parent
```

删 `_make_bridge`（原 :27-30）。回退使用点：

```python
    def _get_output_path(self) -> str:
        if self.main_window:
            return self.main_window.lineEdit_OutputPath.text()
        return ""

    def _get_version(self) -> str:
        if self.main_window:
            return self.main_window.lineEdit_Version.text()
        return ""
```

```python
    def _warn(self, title, msg):
        if self.main_window:
            QW.QMessageBox.warning(self.main_window, title, msg)

    def _info(self, title, msg):
        if self.main_window:
            QW.QMessageBox.information(self.main_window, title, msg)

    def _critical(self, title, msg):
        if self.main_window:
            QW.QMessageBox.critical(self.main_window, title, msg)
```

> `_parent()`（原 :32-33）、`show_analysis_complete_dialog`（已直接用 self.main_window）不动。

- [ ] **Step 3: environment_manager.py 回退**

删头部 `from battery_analysis.main.app_context import AppContext`。`__init__` 改为：

```python
    def __init__(self, main_window=None):
        """
        初始化环境管理器

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._env_info = {}  # 当无 main_window 时使用本地存储
```

`_get_env_service` 回退（删 `if self._ctx:` 分支）：

```python
    def _get_env_service(self):
        if self.main_window:
            return self.main_window._get_service("environment")
        return None
```

- [ ] **Step 4: 验证 + 回归**

Run: `uv run pytest tests/battery_analysis/main/managers/ -q` → 全绿
Run: `uv run pytest -q` → 全绿（基线 537 passed / 9 skipped）
Run: `uv run pylint src/battery_analysis/main/managers/visualization_manager.py src/battery_analysis/main/managers/report_manager.py src/battery_analysis/main/managers/environment_manager.py` → 无新增
Run: `grep -rn "app_context\|UIBridge\|_make_bridge\|self\._ui\|self\._ctx" src/battery_analysis/main/managers/visualization_manager.py src/battery_analysis/main/managers/report_manager.py src/battery_analysis/main/managers/environment_manager.py` → 空

- [ ] **Step 5: Commit**

```bash
git add src/battery_analysis/main/managers/visualization_manager.py src/battery_analysis/main/managers/report_manager.py src/battery_analysis/main/managers/environment_manager.py
git commit -m "refactor(p5-c): 回退 UIBridge——3 个 manager 收敛直接 main_window 访问" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task C2: 批量清 18 个 B 类死参数

**Files:** 见「文件结构」B 类 18 个。

这 18 个类 `ctx` 是死参数：`__init__` 存 `self._ctx = ctx` 后从不读取（摸底已逐一确认），且不 import app_context（无类型注解依赖）。**机械删除**，每个文件同一模式。

- [ ] **Step 1: 逐文件按统一模式删参（18 个）**

每个文件：

1. `def __init__(self, main_window=None, ctx=None):` → `def __init__(self, main_window=None):`
   - 例外：`table_manager.py` 是 `def __init__(self, main_window: Any = None, ctx=None) -> None:` → 删 `, ctx=None` 保留 `main_window: Any = None` 与 `-> None`。
   - 例外：`message_manager.py` 是 `def __init__(self, parent=None, ctx=None):` → `def __init__(self, parent=None):`（形参名是 `parent` 不是 `main_window`，**勿误改**）。
2. 删 `self._ctx = ctx` 那一行（各文件行号见摸底：data_processor:30 / version_manager:33 / help_manager:36 / validation_manager:35 / temperature_handler:24 / analysis_runner:39 / path_manager:20 / test_profile_manager:31 / config_manager:51 / dialog_manager:44 / menu_manager:38 / message_manager:29 / table_manager:29 / theme_manager:36 / ui_manager:39 / window_setup:26 / environment_adapter:27 / signal_connector:38）。
3. 删 docstring 里 `ctx: AppContext（新接口）` / `ctx: 应用上下文（新接口）` 那一行（如存在）。

> 若某文件 `self._ctx` 之后被读取（`if self._ctx:` / `self._ctx.get...`）——**立即停下**，那不是 B 类（摸底已排除，但以 grep 实际为准），报告 controller。删除前自行再 grep 该文件 `_ctx` 确认零读取。

- [ ] **Step 2: 验证 + 回归**

Run: `grep -rn "self\._ctx\|ctx=None\|ctx: AppContext" src/battery_analysis/main/ --include="*.py"` → 空（C1 已清 A 类，C2 清 B 类后全 main/ 归零）
Run: `uv run pytest -q` → 全绿（537 passed / 9 skipped）
Run: `uv run pylint`（对全部改动文件）→ 无新增

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "refactor(p5-c): 批量删除 18 个类 ctx 死参数（仅存从不读）" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task C3: 删 app_context.py

**Files:**
- Delete: `src/battery_analysis/main/app_context.py`

C1/C2 已删全部引用（3 个 import + 21 个 ctx 参数）。此时文件零引用。

- [ ] **Step 1: 先锁删除（验证零引用）**

Run: `grep -rn "app_context\|UIBridge\|AppContext\|PathContext" src/ tests/ --include="*.py"` → 空
> 若残留：先报告（说明残留位置），勿删文件。预期 `scripts/rebuild_po.py`、`docs/` 等非 src/tests 路径不受此 grep 影响（本 grep 限 src/ + tests/）。

- [ ] **Step 2: 删文件**

```bash
git rm src/battery_analysis/main/app_context.py
```

- [ ] **Step 3: 验证 + 回归**

Run: `uv run pytest -q` → 全绿（537 passed / 9 skipped）
Run: `uv run pylint src/battery_analysis/main/ --fail-under=8.5` → 通过

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore(p5-c): 删除 UIBridge/AppContext/PathContext 死壳（app_context.py，零引用）" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task C4: i18n 去 eval

**Files:**
- Modify: `src/battery_analysis/i18n/translator.py`
- Test: `tests/battery_analysis/i18n/test_i18n.py`

`_compile_plural_formula`（:15-45）用 `eval(f"lambda n: int({py})", ...)` 编译 `.po` 头解析出的复数公式——**eval 注入风险**（roadmap #3）。替换为已知公式表。现有 `.po` 只有 en/zh_CN，公式均为 `(n != 1)`；现有测试无一条测 `_compile_plural_formula`/eval（摸底确认）。

- [ ] **Step 1: 先加测试锁行为（test_i18n.py 追加）**

```python
from battery_analysis.i18n.translator import _compile_plural_formula


def test_compile_plural_formula_simple_no_parens():
    fn = _compile_plural_formula("n != 1")
    assert fn(1) == 0
    assert fn(5) == 1


def test_compile_plural_formula_simple_parens():
    fn = _compile_plural_formula("(n != 1)")
    assert fn(1) == 0
    assert fn(5) == 1


def test_compile_plural_formula_greater_than():
    fn = _compile_plural_formula("n > 1")
    assert fn(1) == 0
    assert fn(2) == 1


def test_compile_plural_formula_always_zero():
    fn = _compile_plural_formula("0")
    assert fn(0) == 0
    assert fn(999) == 0


def test_compile_plural_formula_russian_three_forms():
    fn = _compile_plural_formula(
        "n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2")
    assert fn(1) == 0
    assert fn(2) == 1
    assert fn(5) == 2
    assert fn(11) == 2
    assert fn(21) == 1


def test_compile_plural_formula_unknown_formula_returns_zero():
    fn = _compile_plural_formula("n == 7")  # 不在表中
    assert fn(0) == 0
    assert fn(7) == 0  # 未知公式降级为单数形式（与当前 eval 失败 fallback 语义一致）
```

Run: `uv run pytest tests/battery_analysis/i18n/test_i18n.py -q` → 新测试应 PASS（当前 eval 实现能正确编译这些公式；unknown 走 :37/:45 fallback）。这些测试是**行为锁**，非先红——本 Task 是等价重构。

- [ ] **Step 2: 实现——公式表替换 eval**

`translator.py`：

1. 在 `_compile_plural_formula` 之前（:15 前）新增公式表：

```python
# 已知 Plural-Forms 公式表（键 = .po 头解析出的公式字符串，已 strip）。
# 覆盖 language_manager.SUPPORTED_LOCALES（13 个）的标准 gettext 公式，
# 以及当前仓库实际使用的 en/zh_CN 公式（nplurals=2, plural=(n != 1)）。
# 未知公式降级为单数形式（lambda _n: 0），与旧 eval 失败 fallback 语义一致。
_PLURAL_FORMULA_TABLE: Dict[str, Callable[[int], int]] = {
    # nplurals=1（zh_TW/ja/ko）
    "0": lambda _n: 0,
    # nplurals=2 常见形式（en/zh_CN/de/es/it/pt/hi 及带括号变体）
    "n != 1": lambda n: 0 if n == 1 else 1,
    "(n != 1)": lambda n: 0 if n == 1 else 1,
    # nplurals=2, plural=(n > 1)（fr）
    "n > 1": lambda n: 0 if n <= 1 else 1,
    # nplurals=3（ru）——俄语式嵌套三元
    "n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2":
        lambda n: (0 if n % 10 == 1 and n % 100 != 11
                   else 1 if n % 10 >= 2 and n % 10 <= 4
                   and (n % 100 < 10 or n % 100 >= 20) else 2),
    # nplurals=6（ar）——阿拉伯语
    "n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5":
        lambda n: (0 if n == 0 else
                   1 if n == 1 else
                   2 if n == 2 else
                   3 if n % 100 >= 3 and n % 100 <= 10 else
                   4 if n % 100 >= 11 else 5),
}
```

2. `_compile_plural_formula` 整个函数体替换为（删掉两处 `eval` 与 `_c_ternary_to_python` 调用）：

```python
def _compile_plural_formula(formula: str) -> Callable[[int], int]:
    """Compile a C-style ``Plural-Forms`` formula to a Python callable.

    只支持已知公式表（_PLURAL_FORMULA_TABLE）。未知公式记录 warning 并
    降级为单数形式（lambda _n: 0）——不再使用 eval 动态编译。
    """
    formula = formula.strip()
    fn = _PLURAL_FORMULA_TABLE.get(formula)
    if fn is None:
        logger.warning("Unknown plural formula %r — falling back to singular form", formula)
        return lambda _n: 0
    return fn
```

3. 删除整个 `_c_ternary_to_python` 函数（原 :48-95，不再被调用；grep 确认无测试引用）。

> `_nplurals` 字段（:128、:171）与 `.po` 解析（:135-229）**保留不动**——只替换公式编译器。

- [ ] **Step 3: 验证 + 回归**

Run: `uv run pytest tests/battery_analysis/i18n/test_i18n.py -q` → 全绿（原测试 + 6 个新测试）
Run: `uv run pytest -q` → 全绿（537 + 6 = 543 passed / 9 skipped；若不同报告）
Run: `grep -n "eval(" src/battery_analysis/i18n/translator.py` → 空（**关键验收：eval 归零**）
Run: `grep -n "_c_ternary_to_python" src/ tests/ --include="*.py"` → 空
Run: `uv run pylint src/battery_analysis/i18n/translator.py` → 无新增（原 eval 相关行删除，C0301 应减少）

- [ ] **Step 4: Commit**

```bash
git add src/battery_analysis/i18n/translator.py tests/battery_analysis/i18n/test_i18n.py
git commit -m "refactor(p5-c): translator.py 去 eval——plural 公式表替换动态编译" -m "Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 最终验收（全部 4 Task 后）

- Run: `uv run pytest` → 全绿（543 passed / 9 skipped）
- Run: `uv run pylint src/battery_analysis/` → 全源码零新增（重点：translator.py 无 eval 相关告警、main/ 无 UIBridge 残留）
- Run: `grep -rn "app_context\|UIBridge\|AppContext\|PathContext\|self\._ctx\|eval(" src/battery_analysis/ --include="*.py"` → 空
  - 例外（不匹配）：`utils/resource_manager.py:91` `ctx = multiprocessing.get_context('spawn')`、`utils/processors/battery_analysis.py:153` `ctx = ResourceManager.get_processing_context()`、`main/launcher.py:65` `def _qt_msg_handler(mode, ctx, msg)`——非 UIBridge 的 ctx，不碰。
  - 例外：`scripts/`、`docs/`、`tests/manual/` 不在扫描范围。
- 分支提交 4 个（C1-C4）+ plan 落档 1 个。

## 交付

- 分支：`feat/p5-architecture`（从 main 重新拉取，P5-A/B 已 merge）
- PR → CI → 用户手动 merge
- 测试演进：537 → 543 passed / 9 skipped
