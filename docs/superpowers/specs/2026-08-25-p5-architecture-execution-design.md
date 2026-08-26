# P5 架构收敛 — 执行设计

> 上游：`docs/superpowers/specs/2026-08-18-tech-stack-modernization-roadmap-design.md`（P5 定义 :158-168，验收 :168，分支规范 :173）
> 状态：**已批准**（2026-08-25，用户确认 4 项范围决策）

## 目标

消除并发/依赖/事件多重实现与仪式性抽象，消除 eval 注入风险（roadmap P5）。拆为 3 个子阶段，全部在 `feat/p5-architecture` 分支顺序推进，每个子阶段独立 spec/plan/PR、独立可合并。

## 已确认范围决策

| 决策点 | 结论 |
|---|---|
| 推进方式 | 3 子阶段顺序（P5-A 删死代码 → P5-B 并发单模型 → P5-C 空壳+i18n+config） |
| UIBridge | **Revert 删掉**（AppContext 从未构造，迁移半成品；完成迁移 blast radius 过大） |
| i18n | **只移除 eval()**（plural formula 编译器替换，保留 .po 解析与现有测试） |
| AnalysisWorker | **迁移到 TaskRunner**（5 信号并入 TaskSignals，实现单一并发模型） |
| DI | **不引入全面 DI**，降级为删除死代码（roadmap :192 允许） |
| `battery_analysis.py` ProcessPoolExecutor | **保留**（真实并行计算，非死代码） |

## 摸底事实修正（相对 Explore 初报）

- `ServiceContainer` 是**活跃代码**：`get("validation"/"file"/"config")` 被 file_controller、validation_controller、main_window:232、analysis_worker:210、data_loader:58、config_path_provider:30、service_locator 等 7+ 处生产调用。P5-A 只删 `_name_map` 字段 + `register()` 方法（`get()` 改 `getattr`），**不得删容器本身**。
- 存在**两套事件总线**（roadmap #7「双总线」）：
  - `services/event_bus.py` 的 `EventBus`：纯死代码（连发布点都没有）。
  - `utils/domain_events.py` 的 `DomainEventBus`：一个发布点（main_controller.py:143）但**零订阅者**。删除需连发布点 + `utils/__init__.py` 的 lazy-import 映射（:38-39）一起移除。
- `register()` 的调用方仅测试：`tests/battery_analysis/main/services/test_service_container.py:52,69,72` + `tests/manual/test_service_container_optimization.py:46,141`。

## P5-A 死代码清理（Dead Code Purge）— 风险 S

| 任务 | 改动 |
|---|---|
| A1 容器瘦身 | 删 `container.Services._name_map` 字段（:32-41）+ `ServiceContainer.register()`（:107-110）；`Services.get()` 改 `getattr`（:43-48）；同步更新 register 测试 |
| A2 事件总线删除 | 删 `services/event_bus.py` + `utils/domain_events.py`；移除 main_controller.py:143 发布点与 `utils/__init__.py:38-39` lazy-import 映射 |
| A3 命令空壳删除 | 删 7 个未注册 `data_commands` + `CommandManager` 未用方法（保留 `RunAnalysisCommand`） |
| A4 死方法删除 | `data_processor` 的 `analyze_data`/`process_all_excel_files`/`process_excel_with_pandas`/`update_config`/`_read_excel_worker`；orchestrator `_execute_parallel` |
| A5 启动延迟导入 | `excel_validator.py:6` pandas、`visualization_manager.py:3` matplotlib 改函数内导入 |

**验收**：pytest 全绿 + pylint 通过；导入 smoke 验证 pandas/matplotlib 不在启动导入栈。

## P5-B 并发单模型（Concurrency Single Model）— 风险 M

- P3 的 2 处 `run_in_background`（data_processor/version_manager）→ TaskRunner + TaskManager。
- 删 `background_worker.py`；删 2 处 `QThread.terminate()`（换协作式取消 threading.Event 逐项检查）。
- AnalysisWorker（297 LOC）→ 基于 TaskRunner，5 个自定义信号并入 TaskSignals 扩展。
- generation counter 替换启发式 stale guard（见 `[[p3-worker-race-known-limitation]]`）。
- `_MainThreadCallback` 从 data_processor 提取到公共位置。

**验收**：并发单一实现（TaskRunner+TaskManager 唯一并发路径）；pytest 全绿 + pylint 通过。

## P5-C 空壳清理 + i18n + config — 风险 M

- UIBridge revert：删 `UIBridge`/`UIBridgeImpl`/`AppContext`/`PathContext` + 各 manager 的 `ctx` 参数，回退直接 `main_window` 访问。
- i18n 去 eval：`translator.py:34,42` 的 plural formula 编译器替换为已知 locale 公式表（保留 .po 解析与现有测试）。
- config JSON：`DEFAULT_CONFIG` → JSON 资源（纯移动，无启动收益，plan 阶段如价值不成比例可砍）。

**验收**：pytest 全绿 + pylint 通过；i18n 测试无重写通过。

## 交付流程

- 分支：`feat/p5-architecture`（roadmap :173）。
- 节奏：每子阶段先补回归测试（TDD）→ 本地 pytest 全绿 + pylint 通过 → 提交到分支。
- PR 门槛：push → PR → CI（flake8 + pytest + 构建）→ 用户手动合并（gh pr merge 会被 auto mode 拦截）。
- 阶段间：一个子阶段合并后立即开始下一个，不跨阶段累积变更。
