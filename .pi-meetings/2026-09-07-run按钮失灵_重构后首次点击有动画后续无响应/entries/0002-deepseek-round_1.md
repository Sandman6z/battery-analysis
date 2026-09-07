# DeepSeek (Round 1): 系统视角：信号流断裂点在 _on_status_changed 的调用路径上，存在时序竞争风险

## 系统思维分析：信号流与状态管理

### 一、信号流全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                        信号流架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  UI层 (pushButton_Run)                                          │
│       │ clicked                                                 │
│       ▼                                                         │
│  RunAnalysisCommand.execute()                                   │
│       │                                                         │
│       ▼                                                         │
│  AnalysisRunner.run_analysis()                                  │
│       │                                                         │
│       ▼                                                         │
│  MainController.start_analysis()                                │
│       │                                                         │
│       ├─► signals.info ──────────────────────► _on_status_changed│
│       │                                          │               │
│       ├─► signals.thread_end ──► _on_analysis_completed         │
│       │                              │                           │
│       │                              └─► analysis_completed ──► set_version
│       │                                                         │
│       └─► signals.progress ──────────────────► _on_progress_updated
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 二、关键断裂点分析

**问题1：`analysis_completed` 信号连接单向**

```python
# signal_connector.py
main_controller.analysis_completed.connect(
    self.main_window.version_manager.set_version
)
# 只连接到版本管理器，没有连接到按钮状态重置！
```

**问题2：`_on_status_changed` 调用路径**

理论上，`_on_status_changed` 应该重置按钮：
```python
def _on_status_changed(self, is_running, stateindex, threadinfo):
    if not is_running:
        if stateindex == 0 and "success" in threadinfo:
            self.main_window.pushButton_Run.setEnabled(True)  # ← 应该执行
```

**但存在以下风险：**
1. **时序问题**：`signals.info` 和 `signals.thread_end` 几乎同时发射
2. **异常路径**：如果 `_on_analysis_completed` 抛出异常，`_on_status_changed` 可能未被调用
3. **信号队列**：Qt 信号队列处理顺序可能导致竞态条件

### 三、状态机视角

**当前状态管理：**
```
状态：is_analysis_running (bool)
      ├─ True: 分析中，按钮禁用
      └─ False: 空闲，按钮启用
```

**问题：**
- 状态只在 `MainController` 中管理
- 按钮状态在 `SignalConnector` 中管理
- 两处状态不同步的风险

### 四、系统性修复方案

**方案A：强化信号连接（最小改动）**
```python
# signal_connector.py
main_controller.analysis_completed.connect(
    lambda: self.main_window.pushButton_Run.setEnabled(True)
)
```

**方案B：状态同步机制（推荐）**
```python
# MainController
def _on_analysis_completed(self):
    self.is_analysis_running = False
    self.current_worker = None
    self.analysis_completed.emit()
    # 新增：直接发射按钮启用信号
    self.button_state_changed.emit(True)
```

**方案C：状态机模式（长期）**
- 引入显式状态机（Idle/Running/Completed/Error）
- 统一状态管理，避免分散的状态检查