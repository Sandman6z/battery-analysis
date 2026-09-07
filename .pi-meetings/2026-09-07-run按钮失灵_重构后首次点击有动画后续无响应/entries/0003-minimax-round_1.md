# MiniMax (Round 1): 创造性视角：按钮动画与信号处理分离，可能是QPushButton内部状态机被锁死

## 创造性横向思维：Run按钮失灵的非显而易见原因

### 一、跳出常规思维

GPT和DeepSeek都聚焦在信号连接问题上，但让我换个角度思考：

**现象回顾：**
- 首次点击"有动画"（按钮按下效果）
- 后续点击"无响应"（连动画都没有）

### 二、非常规假设

**假设1：QPushButton 内部状态锁死**

PyQt6的QPushButton在某些情况下会进入"死锁"状态：
```python
# 可能的触发路径
pushButton_Run.setEnabled(False)  # 禁用
# ... 某些异常路径 ...
# setEnabled(True) 未被调用
# 但按钮仍然可以接收点击事件（视觉上）
# 只是 clicked 信号不再发射
```

**假设2：事件过滤器干扰**

重构过程中可能意外引入了事件过滤器：
```python
# 某个父组件可能安装了事件过滤器
self.installEventFilter(some_object)
# 拦截了 MouseButtonRelease 事件
```

**假设3：焦点策略问题**

```python
# ui_builder.py
mw.pushButton_Run.setFocusPolicy(QC.Qt.FocusPolicy.ClickFocus)
```

如果焦点被其他控件"偷走"，按钮可能无法响应后续点击。

### 三、诊断实验

**实验1：添加调试日志**
```python
# 在 RunAnalysisCommand.execute() 开头
def execute(self):
    print(f"[DEBUG] Run button clicked at {time.time()}")
    logging.info("Run button clicked")
    ...
```

**实验2：强制重绘**
```python
# 在 _on_status_changed 中
self.main_window.pushButton_Run.repaint()  # 强制重绘
self.main_window.pushButton_Run.setEnabled(True)
```

**实验3：检查事件过滤器**
```python
# 在 Main.__init__ 中
print(f"Event filters on pushButton_Run: "
      f"{self.pushButton_Run.eventFilters()}")
```

### 四、创造性修复方案

**方案A：按钮重建（激进但有效）**
```python
def _recreate_run_button(self):
    """销毁并重建Run按钮"""
    old_btn = self.pushButton_Run
    new_btn = QPushButton("Run", self)
    # 复制所有属性
    new_btn.setGeometry(old_btn.geometry())
    new_btn.setFont(old_btn.font())
    # 重新连接信号
    new_btn.clicked.connect(self.run_analysis_command.execute)
    # 替换
    old_btn.deleteLater()
    self.pushButton_Run = new_btn
```

**方案B：定时器心跳**
```python
# 每5秒检查按钮状态
self._button_health_timer = QTimer(self)
self._button_health_timer.timeout.connect(self._check_button_health)
self._button_health_timer.start(5000)

def _check_button_health(self):
    if not self.pushButton_Run.isEnabled():
        logging.warning("Run button stuck in disabled state!")
        self.pushButton_Run.setEnabled(True)
```