# P5-A 死代码清理 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 消除 P5-A 范围内已确认无消费者的代码与启动路径延迟导入，为 P5-B（并发单模型）与 P5-C（空壳清理）铺路。

**Architecture:** 纯删除 + 两处导入位置后移，不引入新依赖。所有任务先改/删测试（TDD 删除变体：先写「期望状态」断言）再改实现，保证删除后行为不变。服务容器是活跃代码，仅删死字段/方法；两套事件总线（`EventBus` 纯死、`DomainEventBus` 有发布无订阅）整体移除；命令/死方法/`_execute_parallel` 确认无调用方后删除。

**Tech Stack:** Python 3.x，PyQt6，pytest（`uv run pytest`），pylint（`uv run pylint`）。

---

## 文件结构

| 文件 | 责任 | 任务 |
|---|---|---|
| `src/battery_analysis/main/services/service_container/container.py` | 服务容器；删 `_name_map`/`register`，`get()` 改 `getattr` | T1 |
| `tests/battery_analysis/main/services/test_service_container.py` | 容器测试；删 register 测试 + 加删除锁测试 | T1 |
| `src/battery_analysis/main/services/event_bus.py` | **删除**（EventBus 纯死代码） | T2 |
| `src/battery_analysis/utils/domain_events.py` | **删除**（DomainEventBus 无订阅者） | T2 |
| `src/battery_analysis/main/controllers/main_controller.py` | 移除 DomainEventBus 发布点 | T2 |
| `src/battery_analysis/utils/__init__.py` | 移除 lazy-import 映射 | T2 |
| `src/battery_analysis/main/commands/*` + `managers/command_manager.py` | 删 7 个未注册命令 + 未用方法 | T3 |
| `src/battery_analysis/main/business_logic/data_processor.py` | 删 5 个死方法 | T4 |
| `src/battery_analysis/main/initialization/orchestrator*.py` | 删 `_execute_parallel` | T4 |
| `src/battery_analysis/main/business_logic/excel_validator.py` | pandas 导入后移函数内 | T5 |
| `src/battery_analysis/main/visualization/visualization_manager.py` | matplotlib 导入后移函数内 | T5 |

---

## Task 1: 服务容器瘦身（删除 `_name_map` / `register`）

**Files:**
- Modify: `src/battery_analysis/main/services/service_container/container.py:32-48,107-110`
- Modify: `tests/battery_analysis/main/services/test_service_container.py`（删 :47-55、:67-73，补锁测试）
- Modify: `tests/manual/test_service_container_optimization.py`（删 :46、:141 的 register 调用）

**背景**：`Services._name_map` 是 name→attr 的恒等映射（8 条，全等于字段名），`get()` 用它间接取值；`ServiceContainer.register()` 自 DI 简化后仅打印 deprecated warning 并返回 `False`。两者无生产调用方（grep 全项目仅 container.py 自身 + 测试）。`get()` 直接改 `getattr(self, name, None)` 后，对已知服务名行为不变（`get('application')` 因 `application` 字段存在但默认 `None`，返回值不变；未知名返回 `None` 不变）。

- [ ] **Step 1: 更新测试文件**

修改 `tests/battery_analysis/main/services/test_service_container.py`：
1. import 追加 `Services`：改为
   ```python
   from battery_analysis.main.services.service_container import ServiceContainer, Services, get_service_container
   ```
2. 删除 `test_register_is_deprecated`（:47-55 整段）与 `test_register_invalid_service`（:67-73 整段）。
3. 文件末尾追加两个删除锁测试（注意：`_name_map` 是 dataclass `default_factory` 字段，类级不保留属性，`hasattr(Services, '_name_map')` 在删除前就为 `False`，类级断言不可验证；**必须用实例级断言** `hasattr(Services(), '_name_map')` 才能实现红→绿）：
   ```python
   def test_name_map_removed():
       """_name_map 死代码已删除，get 改用 getattr"""
       assert not hasattr(Services(), '_name_map')


   def test_register_removed():
       """register() 死代码已删除"""
       assert not hasattr(ServiceContainer, 'register')
   ```

同时修改 `tests/manual/test_service_container_optimization.py`：删除 :46 `result = container.register("test", TestService)` 与 :141 `container.register("another", AnotherService)` 两行及其相关断言（该文件是 manual 基准，不在 CI 常规路径，但需保持可运行）。若删除后该文件出现未使用变量/引用，一并清理。

- [ ] **Step 2: 运行测试验证新测试失败**

Run: `uv run pytest tests/battery_analysis/main/services/test_service_container.py -v`
Expected: `test_name_map_removed` FAIL（`hasattr(Services, '_name_map')` 为 `True`）、`test_register_removed` FAIL；其余测试 PASS。

- [ ] **Step 3: 实现——删除死代码**

修改 `src/battery_analysis/main/services/service_container/container.py`：

1. 删除 `Services` 类的 `_name_map` 字段（:32-41）：
   ```python
   _name_map: Dict[str, str] = field(default_factory=lambda: {
       "config": "config",
       "environment": "environment",
       "file": "file",
       "progress": "progress",
       "validation": "validation",
       "main_controller": "main_controller",
       "file_controller": "file_controller",
       "validation_controller": "validation_controller",
   })
   ```
2. `Services.get()`（:43-48）改为：
   ```python
   def get(self, name: str) -> Any:
       """按字符串名获取服务（保持向后兼容）。"""
       return getattr(self, name, None)
   ```
3. 删除 `ServiceContainer.register()`（:107-110）：
   ```python
   def register(self, name: str, implementation, singleton=True) -> bool:
       """不再支持动态注册（保留方法签名避免调用方报错）。"""
       self.logger.warning("ServiceContainer.register('%s') is deprecated; services are created statically via create_services()", name)
       return False
   ```
4. 收窄 import：`from dataclasses import dataclass, field` → `from dataclasses import dataclass`；`from typing import Optional, Dict, Any` → `from typing import Optional, Any`（`field`/`Dict` 仅被 `_name_map` 使用）。

- [ ] **Step 4: 运行测试验证通过**

Run: `uv run pytest tests/battery_analysis/main/services/test_service_container.py -v`
Expected: 全部 PASS（含 2 个新锁测试；`test_get_existing_service`/`test_get_nonexistent_service`/`test_has_*` 保持通过证明 `get`/`has` 行为不变）。

- [ ] **Step 5: 全量回归 + pylint**

Run: `uv run pytest`
Expected: 全绿（基线 575 passed / 9 skipped，无新增失败）。
Run: `uv run pylint src/battery_analysis/main/services/service_container/container.py`
Expected: 无新增告警（若该文件已有 pre-existing 告警，不新增即可）。

- [ ] **Step 6: Commit**

```bash
git add src/battery_analysis/main/services/service_container/container.py tests/battery_analysis/main/services/test_service_container.py tests/manual/test_service_container_optimization.py
git commit -m "chore(p5): 删除 ServiceContainer.register() 与 Services._name_map 死代码，get() 改 getattr

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: 事件总线删除（EventBus + DomainEventBus）

> 删除任务 TDD 变体：本任务无「红→绿」失败循环（删除死代码不产生新行为）。流程为「先移除针对死代码的测试 → 再删实现 → 全量回归确认无引用残留」。

**Files:**
- Delete: `src/battery_analysis/main/services/event_bus.py`（EventBus，162 LOC，生产零引用）
- Delete: `src/battery_analysis/utils/domain_events.py`（DomainEventBus，134 LOC，无订阅者）
- Delete: `tests/battery_analysis/main/services/test_event_bus.py`
- Delete: `tests/battery_analysis/main/services/test_event_bus_supplementary.py`
- Modify: `src/battery_analysis/main/controllers/main_controller.py:9`（删 import）、`:143-144`（删发布点）
- Modify: `src/battery_analysis/utils/__init__.py:38-39`（删 lazy_map 两行）

**背景**：两套事件总线均为死代码——`EventBus`（`main/services/event_bus.py`）无任何生产 import/使用；`DomainEventBus`（`utils/domain_events.py`）唯一发布点是 main_controller.py:143，但全项目**无任何 subscribe 调用**（零订阅者）。main_controller.py:9 还 import 了从未使用的 `analysis_failed`。

- [ ] **Step 1: 删除事件总线测试文件**

```bash
git rm tests/battery_analysis/main/services/test_event_bus.py tests/battery_analysis/main/services/test_event_bus_supplementary.py
```

- [ ] **Step 2: 运行测试确认收集正常**

Run: `uv run pytest tests/battery_analysis/main/services -q`
Expected: 绿（此时生产代码未删，测试文件已删，无失败；仅确认 pytest 收集与其余 service 测试正常）。

- [ ] **Step 3: 删除生产代码 + 清理引用**

1. 删除生产文件：
   ```bash
   git rm src/battery_analysis/main/services/event_bus.py src/battery_analysis/utils/domain_events.py
   ```
2. 修改 `src/battery_analysis/main/controllers/main_controller.py`：
   - 删除 :9 `from battery_analysis.utils.domain_events import DomainEventBus, analysis_completed, analysis_failed`
   - 在 `_on_analysis_completed` 中删除 :143-144 两行（`DomainEventBus.instance().publish(` 与其参数括号对）。**保留** :141-142（`self.is_analysis_running = False` 与 `self.analysis_completed.emit()` 是真实业务）。
3. 修改 `src/battery_analysis/utils/__init__.py`：删除 :38-39 两行 lazy_map 条目：
   ```python
           'DomainEventBus': ('battery_analysis.utils.domain_events', 'DomainEventBus'),
           'DomainEvent': ('battery_analysis.utils.domain_events', 'DomainEvent'),
   ```

- [ ] **Step 4: 全量回归**

Run: `uv run pytest`
Expected: 全绿（基线 575 passed / 9 skipped；删除 2 个 event_bus 测试文件后计数相应减少，无新增失败）。同时 grep 确认无残留：`rg "event_bus|DomainEventBus|domain_events" src tests -g '!*.pyc'` 应无生产引用命中（允许 docs/ 与注释残留）。

- [ ] **Step 5: pylint**

Run: `uv run pylint src/battery_analysis/main/controllers/main_controller.py src/battery_analysis/utils/__init__.py`
Expected: 无新增告警（main_controller 若有 pre-existing 告警不新增即可）。

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore(p5): 删除双事件总线（EventBus 纯死代码 + DomainEventBus 无订阅者）

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: 命令空壳删除（7 个未注册命令 + CommandManager 未用方法）

> 删除任务 TDD 变体，同 Task 2。**顺序在 Task 4 之前**：Task 4 删 data_processor 死方法依赖本任务先删 3 个引用它们的死命令（ProcessExcelCommand/ProcessAllExcelCommand/UpdateConfigCommand）。

**Files:**
- Modify: `src/battery_analysis/main/commands/data_commands.py`（删 7 个类，保留 `AnalyzeDataCommand`）
- Modify: `src/battery_analysis/main/managers/command_manager.py:61-101`（删 `get_command`/`execute_command`/`get_all_commands`）
- Delete: `tests/battery_analysis/main/managers/test_command_manager.py`（4 个测试全测将删的 3 个方法）
- Modify: `tests/battery_analysis/main/commands/test_commands_supplementary.py`

**背景**：`data_commands.py` 共 8 个命令，7 个未注册（ProcessExcelCommand/ProcessAllExcelCommand/GetXlsxInfoCommand/SaveTableCommand/UpdateConfigCommand/CheckInputCommand/HandleDataErrorCommand）且生产零调用；`AnalyzeDataCommand` 已注册（command_manager.py:55）保留。`CommandManager` 生产唯一价值是 `_initialize_commands` 实例化 7 个已注册命令挂到 main_window；`get_command`/`execute_command`/`get_all_commands` 三个方法**无生产调用方**（仅测试），删除。

- [ ] **Step 1: 先改测试文件**

1. 删除 `tests/battery_analysis/main/managers/test_command_manager.py`（4 个测试全部测将删方法）：
   ```bash
   git rm tests/battery_analysis/main/managers/test_command_manager.py
   ```
2. 修改 `tests/battery_analysis/main/commands/test_commands_supplementary.py`：
   - `SPECIAL_CMDS`（:62-72）删除 7 个条目：`ProcessExcelCommand`、`ProcessAllExcelCommand`、`GetXlsxInfoCommand`、`SaveTableCommand`、`UpdateConfigCommand`、`CheckInputCommand`、`HandleDataErrorCommand`。
   - `cmd_name` fixture 参数列表（:81-87）删除同名 7 个命令名。
   - `test_execute_error_returns_fallback` 中 `ProcessExcelCommand`/`ProcessAllExcelCommand` 特判（:106-109）删除（保留 `assert cmd.execute() is False` 分支）。
   - `_build` 中：data_commands import（:122-126）删 7 个，只留 `AnalyzeDataCommand`；`classes` dict（:128-143）删 7 个；删除 `ProcessExcelCommand`（:159-162）、`ProcessAllExcelCommand`（:164-167）、`CheckInputCommand`（:169-172）、`GetXlsxInfoCommand/SaveTableCommand/UpdateConfigCommand/HandleDataErrorCommand`（:174-182）的 `_build` 分支。
   - `_method_name`（:186-203）删除 7 个命令名对应条目。
   - `TestCommandManagerSupplementary` 删除 `test_execute_command_success`（:213-226）、`test_execute_command_catches_exception`（:228-242）、`test_get_all_commands_returns_copy`（:244-260）、`test_all_commands_registered`（:283-303）。**保留** `test_initialize_sets_all_command_attributes`（:262-281，验证 7 个已注册命令属性仍挂在 main_window）。
   - 若删除后出现未使用的 import（如 `patch`），一并清理。

- [ ] **Step 2: 运行测试确认（此时生产代码未删，测试已不引用将删对象）**

Run: `uv run pytest tests/battery_analysis/main/managers tests/battery_analysis/main/commands -q`
Expected: 绿。

- [ ] **Step 3: 修改生产代码**

1. `src/battery_analysis/main/commands/data_commands.py`：删除 7 个类（ProcessExcelCommand :32-56、ProcessAllExcelCommand :59-83、GetXlsxInfoCommand :86-109、SaveTableCommand :112-135、UpdateConfigCommand :138-163、CheckInputCommand :166-188、HandleDataErrorCommand :191-216）。**保留** `AnalyzeDataCommand`（:6-29）与模块顶部 import。删除后若 `data_commands.py` 出现未使用 import，一并清理。
2. `src/battery_analysis/main/managers/command_manager.py`：删除 `get_command`（:61-71）、`execute_command`（:73-92）、`get_all_commands`（:94-101）三个方法。**保留** `_commands` dict 与 `_initialize_commands`（生产仍用）。

- [ ] **Step 4: 全量回归 + pylint**

Run: `uv run pytest`
Expected: 全绿（计数变化来自删除命令相关测试，无新增失败）。
Run: `uv run pylint src/battery_analysis/main/commands/data_commands.py src/battery_analysis/main/managers/command_manager.py`
Expected: 无新增告警。

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore(p5): 删除 7 个未注册 data_commands 与 CommandManager 未用查询方法

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: 死方法删除（DataProcessor 5 个 + orchestrator `_execute_parallel`）

> 删除任务 TDD 变体。**必须在 Task 3 之后**：`process_excel_with_pandas`/`process_all_excel_files`/`update_config` 仅被 Task 3 删除的 3 个死命令引用。

**Files:**
- Modify: `src/battery_analysis/main/business_logic/data_processor.py`（删 5 个方法）
- Modify: `src/battery_analysis/main/initialization/initialization_orchestrator.py`（删 `_execute_parallel` + `import concurrent.futures`）
- Modify: `tests/battery_analysis/main/business_logic/test_data_processor.py`（删相关测试）

**背景**：5 个方法构成互引死簇——`_read_excel_worker`（模块级 :22-28）与 `process_excel_with_pandas`（:122-130）被 `process_all_excel_files`（:132-176）内部调用，而后者只被死命令引用；`update_config`（:438-443）与 `analyze_data`（:445-504）亦无活调用。注意**勿误删同名不同对象**：`main_window.analyze_data`（main_window.py:403）、`main_window.update_config`（:539）、`ui_components/config_manager.py:163` 的 `update_config`、`presenters/main_presenter.py:89` 的 `on_analyze_data` 均为真实代码，必须保留。orchestrator `_execute_parallel`（:145-160）经 `_execute_phase`（:119）调用但实测**不可达**（4 个 phase 内步骤 priority 全部互异，`len(group) > 1` 永不成立）；`import concurrent.futures`（:10）是其唯一使用者，同步删。

- [ ] **Step 1: 先删测试**

修改 `tests/battery_analysis/main/business_logic/test_data_processor.py`，删除以下测试/断言（均引用将删死方法）：
- `test_process_excel_with_pandas_success`（:42-~76）
- `test_process_excel_with_pandas_failure`（:78-~84）
- `test_process_all_excel_files_empty_directory`（:86-~96）
- `test_process_all_excel_files_success`（:98-135，patch `_read_excel_worker`）
- `test_analyze_data_shows_error_dialog_on_failure`（:204-215）
- pickle 断言（:357-359，涉及 `_read_excel_worker` 与 `process_excel_with_pandas`）
- `test_process_all_excel_files_real_pool_skips_bad_files`（:361-~388）
- `test_process_all_excel_files_re_raises_broken_process_pool`（:390-~424）

删除后检查文件是否残留对上述方法名的引用（grep `process_excel_with_pandas|process_all_excel_files|_read_excel_worker|analyze_data|update_config` in 该测试文件），清理未使用 import。

- [ ] **Step 2: 运行测试确认（生产代码未删）**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_data_processor.py -q`
Expected: 绿（删除的测试不再运行，剩余测试不受影响）。

- [ ] **Step 3: 修改生产代码**

1. `src/battery_analysis/main/business_logic/data_processor.py` 删除：模块级 `_read_excel_worker`（:22-28）、`process_excel_with_pandas`（:122-130）、`process_all_excel_files`（:132-176）、`update_config`（:438-443）、`analyze_data`（:445-504）。删除后 grep 确认无残留引用，并清理因删除而变为未使用的 import（如 `concurrent.futures`/`ProcessPoolExecutor`/`pickle` 等，以实际 diff 为准；**只删确认无其他引用者**）。
2. `src/battery_analysis/main/initialization/initialization_orchestrator.py`：
   - 删除 `_execute_parallel` 方法（:145-160）与 `import concurrent.futures`（:10；删除前 grep `concurrent.futures` 确认该文件内仅此方法使用，无其他引用）。
   - `_execute_phase` 中 :116-119 的调用点改为遍历执行（保留分组语义，同优先级步骤依次执行；该分支实测不可达，不改变现有行为）：
     ```python
                 for step in group:
                     self._execute_step(step, main_window)
     ```
   - 同时更新 `_execute_phase` 的 docstring（:87-88「按优先级分组，同优先级并行」→「按优先级分组执行」），删除「并行」表述。

- [ ] **Step 4: 全量回归 + pylint**

Run: `uv run pytest`
Expected: 全绿，无新增失败。
Run: `uv run pylint src/battery_analysis/main/business_logic/data_processor.py src/battery_analysis/main/initialization/initialization_orchestrator.py`
Expected: 无新增告警。

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore(p5): 删除 DataProcessor 5 个死方法与 orchestrator 不可达 _execute_parallel

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: 启动延迟导入（pandas / matplotlib）

**Files:**
- Modify: `src/battery_analysis/main/business_logic/excel_validator.py`（:6 删顶层 `import pandas as pd`，函数内加）
- Modify: `src/battery_analysis/main/managers/visualization_manager.py`（:3 删顶层 `import matplotlib.pyplot as plt`，函数内加）
- Modify: `tests/battery_analysis/main/business_logic/test_excel_validator.py`（加延迟导入锁测试）
- Create: `tests/battery_analysis/main/managers/test_visualization_manager.py`（新建，加延迟导入锁测试）

**背景**：两模块都在启动导入路径（`_deferred_init` → `InitializationManager` → 对应 step 顶层 import）。`excel_validator` 的 pandas 仅 2 处使用（:43 `pd.to_numeric`、:100 `pd.read_excel`）；`visualization_manager` 的 `plt` 仅 1 处（:95 `plt.close('all')`，在 `_cleanup_matplotlib_resources`）。改为函数内延迟导入后，启动不再同步加载 pandas/matplotlib。既有函数级导入模式：`excel_processor.py:14`、`battery_analysis.py:506`、`data_utils.py:19`。

> 注意：visualization_manager 实际路径为 `src/battery_analysis/main/managers/visualization_manager.py`（不在 `main/visualization/`）。模块顶层还 import 了 `AppContext`/`UIBridge`（P5-C 处理），本任务不动。

- [ ] **Step 1: 写失败测试（subprocess 隔离验证 sys.modules）**

在 `tests/battery_analysis/main/business_logic/test_excel_validator.py` 末尾追加：
```python
def test_pandas_import_is_deferred():
    """excel_validator 顶层不再 import pandas（启动路径延迟导入）"""
    import subprocess
    import sys
    code = (
        "import sys;"
        "from battery_analysis.main.business_logic import excel_validator;"
        "assert 'pandas' not in sys.modules"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
```

新建 `tests/battery_analysis/main/managers/test_visualization_manager.py`：
```python
"""可视化管理器测试——当前仅验证 matplotlib 延迟导入"""
import subprocess
import sys


def test_matplotlib_import_is_deferred():
    """visualization_manager 顶层不再 import matplotlib"""
    code = (
        "import sys;"
        "from battery_analysis.main.managers.visualization_manager import VisualizationManager;"
        "assert 'matplotlib' not in sys.modules"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
```

> 用 subprocess 是因为 pytest 进程可能已加载 pandas/matplotlib（其他测试触发），`sys.modules` 直接断言不可靠；subprocess 隔离保证锁测试只验证目标模块自身的顶层 import。

- [ ] **Step 2: 运行测试验证失败**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_excel_validator.py::test_pandas_import_is_deferred tests/battery_analysis/main/managers/test_visualization_manager.py -q`
Expected: 两个测试 FAIL（顶层 import 使 `pandas`/`matplotlib` 进入 `sys.modules`）。

- [ ] **Step 3: 实现延迟导入**

1. `src/battery_analysis/main/business_logic/excel_validator.py`：
   - 删除 :6 `import pandas as pd`（保留 :5 `import logging` 与 :7 `from battery_analysis.utils.file_validator import FileValidator`）。
   - 在 `validate_excel_file_content`（:19-69，使用 `pd.to_numeric` 处 :43）方法/函数体内加 `import pandas as pd`（函数体首行）。
   - 在 `validate_excel_file`（:72-116，使用 `pd.read_excel` 处 :100）函数体内加 `import pandas as pd`。
2. `src/battery_analysis/main/managers/visualization_manager.py`：
   - 删除 :3 `import matplotlib.pyplot as plt`。
   - 在 `_cleanup_matplotlib_resources`（:92-97，使用 `plt.close` 处 :95）方法体内加 `import matplotlib.pyplot as plt`（方法体首行）。

- [ ] **Step 4: 运行测试验证通过 + 既有测试不回归**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_excel_validator.py tests/battery_analysis/main/managers/test_visualization_manager.py -q`
Expected: 全部 PASS（含两个新锁测试；`test_validate_excel_file_uses_calamine_engine` 等既有测试通过证明函数内 import 后 `validate_excel_file` 行为不变）。

- [ ] **Step 5: 全量回归 + pylint**

Run: `uv run pytest`
Expected: 全绿，无新增失败。
Run: `uv run pylint src/battery_analysis/main/business_logic/excel_validator.py src/battery_analysis/main/managers/visualization_manager.py`
Expected: 无新增告警（函数内 import 可能触发 C0415，属 pylint 常规 lazy-import 提示；项目已有同模式，若 pylint 因 C0415 报错需与项目现有忽略配置对齐——参考 `excel_processor.py` 的处理方式）。

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore(p5): pandas/matplotlib 移入函数级延迟导入，加速启动路径

Co-Authored-By: Claude <noreply@anthropic.com>"
```
