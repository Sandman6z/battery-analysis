# GLM (Round 2): 务实建议：先诊断修复bug（信号连接），确认问题后再决定是否重构状态机

## GLM Round 2：务实架构审查

### 一、问题量化分析

**按钮状态操作统计：**
```
setEnabled(True):   12处
setEnabled(False):   3处
setText("Run"):      4处
setText("Rerun"):    6处
setText("Running"):  1处
```

**分布：**
- `signal_connector.py`: 12处（60%）
- `analysis_runner.py`: 5处（25%）
- `validation_manager.py`: 3处（15%）

### 二、重构方向评估

#### 方向A：重构状态机

**改动清单：**
1. 创建 `AnalysisStateMachine` 类
2. 修改 `MainController` 使用状态机
3. 修改 `SignalConnector` 订阅状态
4. 修改 `AnalysisRunner` 查询状态
5. 添加状态机单元测试

**工作量估算：** 3-5天

**风险：**
- 可能引入新的 bug
- 需要全面回归测试
- 信号连接需要重新验证

#### 方向B：重构按钮部分

**改动清单：**
1. 创建 `RunButtonController` 类
2. 迁移所有按钮操作到控制器
3. 添加控制器单元测试

**工作量估算：** 1-2天

**风险：**
- 风险较低
- 改动范围小
- 易于回滚

### 三、务实建议

**推荐：先修复 bug，再考虑重构**

**步骤1：添加诊断日志（立即）**
```python
# main_controller.py
def start_analysis(self):
    print(f"[DEBUG] start_analysis called, is_running={self.is_analysis_running}")
    if self.is_analysis_running:
        print("[DEBUG] BLOCKED: already running!")
        return False
    # ...

def _on_analysis_completed(self):
    print(f"[DEBUG] _on_analysis_completed called")
    self.is_analysis_running = False
    # ...
```

**步骤2：验证信号连接（立即）**
```python
# signal_connector.py - connect_controllers()
def connect_controllers(self):
    main_controller = self._get_controller("main_controller")
    if main_controller:
        # 添加连接验证
        print(f"[DEBUG] Connecting status_changed: "
              f"{main_controller.status_changed.connect(self._on_status_changed)}")
        print(f"[DEBUG] Connecting analysis_completed: "
              f"{main_controller.analysis_completed.connect(...)}")
```

**步骤3：修复信号连接（如果确认问题）**
```python
# 确保 analysis_completed 连接到按钮重置
main_controller.analysis_completed.connect(
    lambda: (
        self.main_window.pushButton_Run.setEnabled(True),
        self.main_window.pushButton_Run.setText("Run")
    )
)
```

**步骤4：重构（如果需要）**
- 确认 bug 修复后
- 根据团队需求决定是否重构
- 优先级：状态机 > 按钮控制器

### 四、决策树

```
问题确认
├─ 信号连接断裂 → 修复连接 → 测试 → 重构（可选）
├─ 事件循环阻塞 → 异步对话框 → 测试 → 重构（可选）
└─ 状态管理混乱 → 重构状态机 → 测试
```

**我的建议：先走信号连接分支，成本最低，收益最快。**