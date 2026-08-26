# P5-B 并发单模型（Concurrency Single Model）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 消除并发多模型，统一为 TaskRunner+TaskManager 唯一并发路径；删除 2 处 `QThread.terminate()` 换协作式取消；AnalysisWorker 迁移到 TaskRunner；generation counter 替换启发式 stale guard。

**Architecture:** 上游执行 spec `docs/superpowers/specs/2026-08-25-p5-architecture-execution-design.md` :41-49（P5-B 定义，用户已批准）。核心手段是让全部后台任务走 `workers/task_runner.py` 的 TaskRunner（QRunnable+QThreadPool）+ TaskSignals 信号，利用 Qt AutoConnection 信号天然回主线程的机制替代手动 `_MainThreadCallback`。

**Tech Stack:** Python 3.13 / PyQt6（QThreadPool / QRunnable / pyqtSignal）/ threading（协作式取消标志）。

---

## 摸底事实（2026-08-26 确认，P5-B 基线）

- **统一执行器已存在**：`src/battery_analysis/main/workers/task_runner.py` 含 `TaskSignals`（started/progress/finished/error/cancelled）、`TaskRunner`（QRunnable，`run()` 强制传 `progress_callback=wrapped_cb` 给 task_func）、`TaskManager`（生命周期管理）。**但无任何单元测试**。
- **两处 `run_in_background` 同构**：`data_processor.py:85-99` 与 `version_manager.py:197-212` 都是 `QThread + BackgroundWorker + moveToThread` 模式，`_cleanup_background_thread`（data_processor:76-83 / version_manager:214-221）都用 `terminate()`。P3 memory 已确立：terminate 只在新字节码边界生效，且不协作——需删。
- **BackgroundWorker 已弃用**：`background_worker.py` 只是 TaskRunner 的薄包装（docstring 明示「已弃用，请使用 TaskRunner」），仅被 data_processor:14 与 version_manager:18 import。
- **`_MainThreadCallback`**（data_processor.py:20-37）是 Qt 信号→主线程回跳的私有中继器，仅被 data_processor:96,98 与 version_manager:209,211（run_in_background 内部）使用。**TaskRunner.signals 是主线程创建的 QObject，worker 线程 emit 时 AutoConnection 自动 Queued 回主线程——迁移后不再需要它**。
- **两处启发式 stale guard**：data_processor `_scanning_input_dir`（:117 设置、:229/:273 检查）与 version_manager `_checksum_input_dir`（:52 设置、:79-82 检查）。都是「当前 text() != 记录值」判断，双派发周期重叠时会误放行（见 `[[p3-worker-race-known-limitation]]`）。
- **AnalysisWorker**（`workers/analysis_worker.py`，297 LOC）：独立 QRunnable，5 信号（info(bool,int,str)/thread_end/rename_path(str)/progress_update(int,str)/start_visualizer），自建 `_TaskCancelled` + `_emit_progress` 取消检查。main_controller.py:74-92 实例化/连接信号/`thread_pool.start`。
- **调用方**：data_processor 的 run_in_background 被 `_on_scan_finished`(:125) 与 `get_xlsxinfo`(:161) 调用；version_manager 的被 `get_version`(:53) 调用；AnalysisWorker 仅 main_controller 使用。
- **现有测试**：无 test_task_runner.py；`tests/battery_analysis/main/workers/test_analysis_worker.py` 仅 2 个属性测试（set_info/request_cancel）；test_data_processor.py、test_version_manager.py、test_main_controller.py 覆盖既有行为。全量基线 **518 passed / 9 skipped**。

## 设计决策（相对执行 spec 的明确化）

| 决策点 | 结论 | 理由 |
|---|---|---|
| `_MainThreadCallback` 处置 | **删除**（非「提取到公共位置」） | 执行 spec :47 写「提取」时未考虑 TaskRunner 信号已内建主线程回跳。迁移后该私有类零引用，保留即死代码（违背 P5 目标）。plan Task B4 删除。 |
| 协作式取消机制 | TaskRunner 的 progress_callback 包装器每次调用检查 `self._cancelled`，取消则抛 `_TaskCancelled`；run() 捕获后发 cancelled 信号 | 复用 AnalysisWorker 已验证的「进度点即取消检查点」模式；task_func 在长跑循环内调用 progress_callback 即获得取消点，不依赖 terminate。 |
| TaskSignals 扩展 | 在 TaskSignals 直接加 `info(bool,int,str)`/`thread_end()`/`rename_path(str)`/`start_visualizer()` 4 信号；`progress_update` 由既有 `progress(int,str)` 承担（AnalysisWorker 改发 progress） | 执行 spec :45「5 个自定义信号并入 TaskSignals 扩展」；progress_update 与 progress 签名重复，保留一份。 |
| AnalysisWorker 形态 | 改为 `AnalysisWorker(TaskRunner)` 子类：复用 TaskRunner 的 `_cancelled`/`cancel()`/QThreadPool 兼容，重写 `run()` 保留 297 LOC 分析流程，signals 用扩展 TaskSignals | 最小侵入；main_controller 的 `thread_pool.start(worker)` 与 `request_cancel()` 调用面基本不变。 |
| generation counter | `_scan_generation`/`_checksum_generation` 单调递增：触发扫描/校验时自增并捕获到 closure，回调带 generation 参数，`generation != 当前值` 即丢弃 | 精确匹配派发代次，根治双派发误放行（`[[p3-worker-race-known-limitation]]` 建议方案）。 |
| 任务排队 | data_processor/version_manager 用 `TaskManager.submit(runner)`（非裸 `QThreadPool.start`） | 执行 spec :43「TaskRunner + TaskManager」；TaskManager 提供 active 追踪与 all_completed。 |

**验收**：并发单一实现（`background_worker.py` 删除，`src/` 与 `tests/` 无 `QThread.terminate()` 残留）；pytest 全绿 + pylint 无新增告警；`_MainThreadCallback`/`_scanning_input_dir`/`_checksum_input_dir` 无残留引用。

---

## Task B1: TaskRunner 协作式取消 + 单元测试（基础设施）

**Files:**
- Modify: `src/battery_analysis/main/workers/task_runner.py`
- Create: `tests/battery_analysis/main/workers/test_task_runner.py`

**背景**：TaskRunner 当前零测试且取消机制薄弱（`cancel()` 只在 run() 开头与 finished 前检查，长跑 task_func 无法中断）。本 Task 建立「协作式取消」基础，后续 B2/B3 迁移依赖它。

- [ ] **Step 1: 写失败测试**

新建 `tests/battery_analysis/main/workers/test_task_runner.py`（同步调用 `run()`，不经 QThreadPool，避免测试跨线程复杂性；信号直接连接同线程同步 emit，用 `QSignalSpy` 捕获）：

```python
"""TaskRunner 单元测试——执行/错误/进度/协作式取消"""
from PyQt6 import QtCore as QC
from PyQt6.QtTest import QSignalSpy

from battery_analysis.main.workers.task_runner import TaskRunner, _TaskCancelled


def test_success_emits_finished_with_result():
    runner = TaskRunner(lambda: 42)
    spy = QSignalSpy(runner.signals.finished)
    spy_error = QSignalSpy(runner.signals.error)
    runner.run()
    assert spy_error.count() == 0
    assert spy.count() == 1
    assert spy[0][0] == 42


def test_error_emits_error_with_message():
    def boom():
        raise ValueError("kaboom")
    runner = TaskRunner(boom)
    spy = QSignalSpy(runner.signals.error)
    runner.run()
    assert spy.count() == 1
    assert "kaboom" in spy[0][0]


def test_progress_callback_forwards_to_progress_signal():
    def task(progress_callback=None, **kwargs):
        progress_callback(50, "halfway")
        return "done"
    runner = TaskRunner(task)
    spy = QSignalSpy(runner.signals.progress)
    runner.run()
    assert spy.count() == 1
    assert spy[0][0] == 50
    assert spy[0][1] == "halfway"


def test_cancelled_before_run_emits_cancelled():
    runner = TaskRunner(lambda: "never runs")
    spy = QSignalSpy(runner.signals.cancelled)
    runner.cancel()
    runner.run()
    assert spy.count() == 1


def test_cancel_mid_execution_raises_at_next_progress_point():
    calls = []

    def task(progress_callback=None, **kwargs):
        progress_callback(10, "start")
        calls.append("after first progress")
        progress_callback(20, "second")
        calls.append("after second progress")
        return "done"

    runner = TaskRunner(task)
    spy_cancelled = QSignalSpy(runner.signals.cancelled)
    spy_finished = QSignalSpy(runner.signals.finished)

    # 第一次 progress_callback 调用前已取消 → 首次调用即抛 _TaskCancelled
    runner.cancel()
    runner.run()
    assert spy_cancelled.count() == 1
    assert spy_finished.count() == 0
    assert calls == []  # 取消点在第一次 progress_callback 处拦截
```

Run: `uv run pytest tests/battery_analysis/main/workers/test_task_runner.py -q`
Expected: FAIL——`_TaskCancelled` 不存在（ImportError）、取消语义未实现。

- [ ] **Step 2: 实现协作式取消**

修改 `src/battery_analysis/main/workers/task_runner.py`：

1. 模块顶部加：
```python
class _TaskCancelled(Exception):
    """协作式取消信号——progress_callback 检测到取消请求时抛出，run() 捕获后发 cancelled。"""
```

2. `TaskRunner.run()` 重写 progress_callback 包装逻辑，统一包一层取消检查：
```python
    def run(self):
        """执行任务（QRunnable 入口）。"""
        if self._cancelled:
            self.signals.cancelled.emit()
            return

        # 包装 progress_callback：每次调用检查取消标志，取消则抛 _TaskCancelled
        def wrapped_cb(pct, msg):
            if self._cancelled:
                raise _TaskCancelled
            self.signals.progress.emit(pct, msg)

        try:
            self.signals.started.emit()
            result = self._task_func(
                *self._args,
                progress_callback=wrapped_cb,
                **self._kwargs,
            )
            if not self._cancelled:
                self.signals.finished.emit(result)
        except _TaskCancelled:
            self.signals.cancelled.emit()
        except Exception as e:
            self.logger.error("Task execution failed: %s", e)
            self.signals.error.emit(str(e))
```
> 说明：取消检查统一放进 wrapped_cb（无论调用方传不传 progress_callback，task_func 收到的 progress_callback 都是 wrapped_cb）。task_func 长跑循环内调用 progress_callback 即得取消点；不调用则无法协作取消（这是协作式取消的固有边界，与 P3 memory 记录一致）。原 `_progress_cb` 若传入，需保留语义——本设计将用户传入回调并入 wrapped_cb 链路，检查取消后先发 progress 信号，再由用户回调转发。

- [ ] **Step 3: 运行测试验证通过**

Run: `uv run pytest tests/battery_analysis/main/workers/test_task_runner.py -q`
Expected: 全部 PASS。

- [ ] **Step 4: 全量回归 + pylint**

Run: `uv run pytest tests/battery_analysis/main/workers/ -q`
Expected: 绿（含既有 test_analysis_worker.py）。
Run: `uv run pylint src/battery_analysis/main/workers/task_runner.py`
Expected: 无新增告警。

- [ ] **Step 5: Commit**

```bash
git add src/battery_analysis/main/workers/task_runner.py tests/battery_analysis/main/workers/test_task_runner.py
git commit -m "feat(p5): TaskRunner 协作式取消（progress_callback 取消检查点）+ 单元测试
Co-Authored-By: Claude <noreply@anthropic.com>"
```
> Bash 工具不要用 here-string 传多行消息——用两个 `-m` 参数。

---

## Task B2: data_processor 迁移 TaskRunner + generation counter

**Files:**
- Modify: `src/battery_analysis/main/business_logic/data_processor.py`
- Modify: `tests/battery_analysis/main/business_logic/test_data_processor.py`

**背景**：data_processor 的 `run_in_background`（QThread+BackgroundWorker+terminate）替换为 TaskRunner + TaskManager；`_scanning_input_dir` 启发式 stale guard 换 `_scan_generation` 单调递增 counter。回调经 TaskRunner.signals 自动回主线程，不再需要 `_MainThreadCallback`。

- [ ] **Step 1: 先改测试（TDD 语义：改期望 + 补 generation 测试）**

在 `tests/battery_analysis/main/business_logic/test_data_processor.py` 确认现有测试（get_xlsxinfo/scan/process 相关）仍绿；新增 generation counter 行为测试（无需真跑后台线程，直接调回调验证）：

```python
def test_stale_generation_result_is_discarded():
    """旧代次结果被丢弃（守卫拦截，UI 零访问）；需实现后按实际签名调整"""
    from unittest.mock import MagicMock
    dp = DataProcessor()
    dp.main_window = MagicMock()
    dp._scan_generation = 5
    # 旧代次：守卫在触碰 main_window 之前 return，可断言零 UI 访问
    dp._on_excel_files_processed((["a.xlsx"], [{"filename": "a.xlsx"}], []), generation=4)
    dp.main_window.lineEdit_InputPath.assert_not_called()
```

> 关键断言：旧代次（generation=4）在守卫处 return，`main_window.lineEdit_InputPath` 不被访问。若实现后签名变化（如 generation 从 closure 捕获而非显式参数），调整测试以匹配——**核心是「旧代次回调被丢弃、不产生 UI 副作用」**。

- [ ] **Step 2: 实现迁移**

修改 `src/battery_analysis/main/business_logic/data_processor.py`：

1. 删 `_background_thread`/`_background_worker` 初始化（:58-59）与 `_scanning_input_dir`（:60），改加：
```python
        self._scan_generation = 0
```

2. 删 `_cleanup_background_thread`（:76-83）与 `run_in_background`（:85-99）。新增统一派发：
```python
    def _run_async(self, task_func, on_finished, on_error, *args, **kwargs):
        """TaskRunner 派发：回调经 TaskSignals 自动回主线程（AutoConnection Queued）。"""
        from battery_analysis.main.workers.task_runner import TaskRunner
        runner = TaskRunner(task_func, *args, **kwargs)
        if on_finished:
            runner.signals.finished.connect(on_finished)
        if on_error:
            runner.signals.error.connect(on_error)
        QC.QThreadPool.globalInstance().start(runner)
        return runner
```

3. `_on_scan_finished`（:114-130）改为 generation 捕获：
```python
    def _on_scan_finished(self, excel_files):
        input_dir = self.main_window.lineEdit_InputPath.text()
        self._cache['directory_files'].put(input_dir, excel_files)
        self._scan_generation += 1
        generation = self._scan_generation

        if not excel_files:
            self._handle_no_excel_files(input_dir)
            return

        self._run_async(
            self._process_excel_files_task,
            lambda result, g=generation: self._on_excel_files_processed(result, g),
            lambda error, g=generation: self._on_excel_files_process_error(error, g),
            input_dir, excel_files,
        )
```

4. `_on_excel_files_processed`（:225-231）签名加 `generation`，替换守卫：
```python
    def _on_excel_files_processed(self, result, generation):
        """主线程：_process_excel_files_task 完成后的 UI 更新"""
        # 过期结果守卫（generation 精确匹配）：用户已切换输入路径时丢弃旧代次结果。
        if generation != self._scan_generation:
            self.logger.info("Discarding stale Excel parse result for changed input path")
            return
```
（函数体其余部分不变）

5. `_on_excel_files_process_error`（:270-275）同样加 `generation` 参数并替换守卫。

6. `_process_excel_files_task`（:199-223）逐文件加 progress_callback（取消检查点）：
```python
    def _process_excel_files_task(self, input_dir, excel_files, progress_callback=None, **kwargs):
        """后台线程：逐文件验证并提取 Excel 元信息（不触碰任何 UI）。

        progress_callback 由 TaskRunner 注入，每次调用即协作式取消检查点。
        """
        excel_data = []
        error_files = []
        for index, filename in enumerate(excel_files):
            if progress_callback:
                progress_callback(index, f"Validating {filename}...")
            ...
```

7. `get_xlsxinfo`（:161-162）的调用同步改为 `self._run_async(self._scan_excel_files_task, self._on_scan_finished, self._on_scan_error, input_dir)`。

8. 删 :14 `from ...background_worker import BackgroundWorker` import（本 Task 内即无引用）；`_MainThreadCallback` 相关连接（:96,98）随 run_in_background 删除而消失。

- [ ] **Step 3: 运行测试验证**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_data_processor.py -q`
Expected: 绿。若 test_data_processor 有直接调用 `run_in_background`/`_cleanup_background_thread` 的用例，删除或改写为 `_run_async` 断言。
Run: `uv run pytest tests/battery_analysis/main/test_main_window.py tests/battery_analysis/e2e/test_end_to_end.py -q`
Expected: 绿（这些文件走真实扫描路径，验证迁移后行为不变）。

- [ ] **Step 4: 全量回归 + pylint**

Run: `uv run pytest`
Expected: 全绿，无新增失败（基线 518 passed / 9 skipped）。
Run: `uv run pylint src/battery_analysis/main/business_logic/data_processor.py`
Expected: 无新增告警。

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(p5): data_processor 后台任务迁移 TaskRunner，terminate 换协作式取消，generation counter 替换 stale guard
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task B3: version_manager 迁移 TaskRunner + generation counter

**Files:**
- Modify: `src/battery_analysis/main/business_logic/version_manager.py`
- Modify: `tests/battery_analysis/main/business_logic/test_version_manager.py`

**背景**：与 B2 同构。version_manager 的 `run_in_background`（:197-212）+ `_cleanup_background_thread`（:214-221，terminate）+ `_checksum_input_dir` stale guard（:52/:79-82）迁移到 TaskRunner + `_checksum_generation`。

- [ ] **Step 1: 改测试（新增 generation 测试）**

在 `tests/battery_analysis/main/business_logic/test_version_manager.py` 增加 generation 行为测试（MagicMock main_window 模式）：
```python
def test_stale_checksum_generation_is_discarded():
    """旧代次校验和结果被丢弃（守卫拦截，UI 零访问）；需实现后按实际签名调整"""
    from unittest.mock import MagicMock
    vm = VersionManager()
    vm.main_window = MagicMock()
    vm._checksum_generation = 3
    vm._on_checksum_ready(None, generation=2)
    vm.main_window.lineEdit_InputPath.assert_not_called()
```

- [ ] **Step 2: 实现迁移**

修改 `src/battery_analysis/main/business_logic/version_manager.py`：

1. `__init__` 删 `_background_thread`/`_background_worker`（:38-39），`_checksum_input_dir`（:40）改 `self._checksum_generation = 0`。
2. 删 `_cleanup_background_thread`（:214-221）与 `run_in_background`（:197-212），加与 B2 相同的 `_run_async` 私有方法。
3. `get_version`（:42-58）改：
```python
        if os.path.exists(strInPutDir) and os.path.exists(strOutoutDir):
            self._checksum_generation += 1
            generation = self._checksum_generation
            self._run_async(
                self._calc_checksum_task,
                lambda checksum, g=generation: self._on_checksum_ready(checksum, g),
                lambda error, g=generation: self._on_checksum_error(error, g),
                strInPutDir,
            )
        else:
            self.main_window.lineEdit_Version.setText("")
```
4. `_on_checksum_ready`（:75-82）签名加 `generation`，守卫改：
```python
    def _on_checksum_ready(self, checksum, generation):
        """主线程：校验和计算完成后的版本号落盘 + UI 更新"""
        # 过期结果守卫（generation 精确匹配）
        if generation != self._checksum_generation:
            self.logger.info("Discarding stale checksum result for changed input path")
            return
```
（函数体其余部分不变）
5. 删 :18 `from ...background_worker import BackgroundWorker` 与 :19 `from ...data_processor import _MainThreadCallback` import。

- [ ] **Step 3-4: 验证 + 回归**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_version_manager.py tests/battery_analysis/main/test_main_window.py -q` → 绿
Run: `uv run pytest` → 全绿
Run: `uv run pylint src/battery_analysis/main/business_logic/version_manager.py` → 无新增

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(p5): version_manager 后台任务迁移 TaskRunner，generation counter 替换 stale guard
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task B4: 删 background_worker.py + _MainThreadCallback（死代码收尾）

**Files:**
- Delete: `src/battery_analysis/main/business_logic/background_worker.py`
- Modify: `src/battery_analysis/main/business_logic/data_processor.py`（删 `_MainThreadCallback` 类 :20-37）
- Modify: `tests/battery_analysis/main/business_logic/test_data_processor.py`（删相关引用）

**背景**：B2/B3 迁移后，`BackgroundWorker`（薄包装）与 `_MainThreadCallback`（信号回主线程中继）均零引用。执行 spec :47 原写「提取到公共位置」，本 plan 设计决策为**删除**（TaskRunner 信号已内建主线程回跳）。

- [ ] **Step 1: 确认零引用**

Run: `grep -rn "BackgroundWorker\|_MainThreadCallback" src/ tests/`
Expected: 除本 Task 将删的定义/import 外无其他引用。若有（如测试文件），一并清理。

- [ ] **Step 2: 删除**

1. `git rm src/battery_analysis/main/business_logic/background_worker.py`
2. 从 `data_processor.py` 删 `_MainThreadCallback` 类（:20-37）与其所在位置的 `QC.QObject` 依赖（`QC` 仍被文件内其他代码使用则保留 import）。
3. 清理 `tests/` 中任何引用（grep 确认）。

- [ ] **Step 3: 验证**

Run: `uv run pytest -q` → 全绿
Run: `uv run pylint src/battery_analysis/main/business_logic/data_processor.py src/battery_analysis/main/business_logic/version_manager.py` → 无新增
Run: `grep -rn "background_worker\|_MainThreadCallback" src/ tests/` → 空

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore(p5): 删除已弃用 BackgroundWorker 与私有 _MainThreadCallback（TaskRunner 信号自动回主线程）
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task B5: AnalysisWorker 迁移 TaskRunner + TaskSignals 扩展

**Files:**
- Modify: `src/battery_analysis/main/workers/task_runner.py`（TaskSignals 扩展 4 信号）
- Modify: `src/battery_analysis/main/workers/analysis_worker.py`（继承 TaskRunner，重写 run()）
- Modify: `src/battery_analysis/main/controllers/main_controller.py`（progress_update → progress 连接）
- Modify: `tests/battery_analysis/main/workers/test_analysis_worker.py`（适配新取消语义）
- Modify: `tests/battery_analysis/main/controllers/test_main_controller.py`（如引用 progress_update）

**背景**：AnalysisWorker（297 LOC）独立 QRunnable + 私有 Signals + 自建取消。迁移为 `AnalysisWorker(TaskRunner)` 子类，signals 用扩展 TaskSignals（info/thread_end/rename_path/start_visualizer 并入，progress_update 由 progress 承担），复用 TaskRunner 的 `_cancelled`/`cancel()`。run() 保留电池分析全流程。

- [ ] **Step 1: TaskSignals 扩展**

`task_runner.py` 的 `TaskSignals` 增加：
```python
class TaskSignals(QC.QObject):
    """任务信号 — 所有 TaskRunner 共享的信号集合。"""
    started = QC.pyqtSignal()
    progress = QC.pyqtSignal(int, str)  # (百分比, 状态文本)
    finished = QC.pyqtSignal(object)    # 返回结果
    error = QC.pyqtSignal(str)          # 错误消息
    cancelled = QC.pyqtSignal()
    # P5-B：AnalysisWorker 并入的信号
    info = QC.pyqtSignal(bool, int, str)     # (is_running, 状态码, 消息)
    thread_end = QC.pyqtSignal()             # 分析线程结束
    rename_path = QC.pyqtSignal(str)         # 输出目录重命名后的日期
    start_visualizer = QC.pyqtSignal()       # 通知主线程启动可视化
```

- [ ] **Step 2: 改 AnalysisWorker 测试（先红）**

`tests/battery_analysis/main/workers/test_analysis_worker.py` 适配：
```python
from battery_analysis.main.workers.analysis_worker import AnalysisWorker


class TestAnalysisWorker:
    def setup_method(self):
        self.worker = AnalysisWorker()

    def test_set_info(self):
        self.worker.set_info("path", "input", "output", ["info"])
        assert self.worker.str_path == "path"

    def test_request_cancel(self):
        self.worker.request_cancel()
        assert self.worker.b_cancel_requested is True

    def test_signals_are_task_signals(self):
        # 信号集合为扩展后的 TaskSignals（含 info/thread_end/rename_path/start_visualizer）
        assert self.worker.signals.info
        assert self.worker.signals.thread_end
        assert self.worker.signals.rename_path
        assert self.worker.signals.start_visualizer
        assert self.worker.signals.progress  # progress_update 语义由 progress 承担
```
Run: `uv run pytest tests/battery_analysis/main/workers/test_analysis_worker.py -q`
Expected: `test_signals_are_task_signals` FAIL（当前 AnalysisWorker 无 progress 信号、signals 是私有 Signals）。

- [ ] **Step 3: 重构 AnalysisWorker**

`analysis_worker.py`：
1. 头部 import 改为 `from battery_analysis.main.workers.task_runner import TaskRunner, _TaskCancelled`；删除私有 `Signals` 类与本地 `_TaskCancelled` 定义。
2. 类定义改 `class AnalysisWorker(TaskRunner):`。
3. `__init__`：调用 `super().__init__(self._run_placeholder)`（task_func 占位，run() 重写不使用），`self.signals = TaskSignals()`（TaskRunner.__init__ 已创建，子类保持），保留现有属性初始化（str_path/b_thread_run/b_cancel_requested/progress_value/...）。
4. `request_cancel()` 改为调用 `super().cancel()` 并保持发进度提示：
```python
    def request_cancel(self):
        """请求取消任务（协作式：下次 progress_callback 检查点生效）"""
        self.b_cancel_requested = True
        self.cancel()
        self.signals.progress.emit(self.progress_value, "Canceling task...")
```
5. `_emit_progress` 内取消检查由 `self.b_cancel_requested` 改 `self.b_cancel_requested or self._cancelled`；`progress_update.emit` 改 `progress.emit`。
6. `run()` 内所有 `self.signals.progress_update.emit(...)` → `self.signals.progress.emit(...)`；`info.emit`/`thread_end.emit`/`rename_path.emit`/`start_visualizer.emit` 不变（信号已并入 TaskSignals）。`_start_visualizer` 不变。
7. `b_thread_run`/`str_path` 等属性保留（test_set_info 依赖 str_path）。

> 保持 run() 297 LOC 分析逻辑不变，仅机械替换信号名与取消检查来源。若 `TaskRunner.__init__` 的 `progress_callback` 语义与 AnalysisWorker 冲突（AnalysisWorker 自管进度），确保 `super().__init__` 传入占位 task_func 不影响 run()。

- [ ] **Step 4: 适配 main_controller**

`main_controller.py:83-89` 中 `progress_update.connect(self._on_progress_update)` → `progress.connect(self._on_progress_update)`（其余信号连接不变）。`thread_pool.start(self.current_worker)` 不变（TaskRunner 是 QRunnable 子类）。

- [ ] **Step 5: 验证 + 回归**

Run: `uv run pytest tests/battery_analysis/main/workers/test_analysis_worker.py tests/battery_analysis/main/controllers/test_main_controller.py -q` → 绿
Run: `uv run pytest` → 全绿
Run: `uv run pylint src/battery_analysis/main/workers/analysis_worker.py src/battery_analysis/main/workers/task_runner.py src/battery_analysis/main/controllers/main_controller.py` → 无新增

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor(p5): AnalysisWorker 迁移 TaskRunner，5 信号并入 TaskSignals 扩展
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 最终验收（全 5 Task 后）

- Run: `uv run pytest` → 全绿（基线 518 passed / 9 skipped，数字可能小幅变化）
- Run: `uv run pylint src/battery_analysis/ --errors-only` → 零 error
- Run: `grep -rn "background_worker\|_MainThreadCallback\|terminate()" src/` → 空（并发单一实现 + 无 terminate 残留）
- Run: `grep -rn "_scanning_input_dir\|_checksum_input_dir" src/` → 空（generation counter 落地）
- 全部 5 Task 经 spec compliance + code quality 两阶段 review 后创建 PR（用户手动 merge）。
