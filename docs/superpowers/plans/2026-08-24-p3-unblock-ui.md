# P3 主线程解阻塞 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 消除 UI 冻结——把大文件扫描后的 Excel 解析与 SHA-256 校验和计算移入后台线程，并移除低收益 `processEvents`、去抖高频列宽重排、非阻塞 CPU 采样。

**Architecture:** 复用 `DataProcessor.run_in_background`（QThread + 已废弃 BackgroundWorker + `_MainThreadCallback` QueuedConnection 切主线程）的既有 worker 模式。核心改动把 `_process_excel_files` 拆成「后台任务函数（只读文件，不碰 UI）」+「主线程回调（弹窗/状态栏/表格）」。`VersionManager` 获得同款 `run_in_background`，把 `get_version` 的 SHA-256 计算拆到后台，CSV 落盘与 UI 更新保留在主线程回调。跨线程共享的 `LRUCache` 因 CPython GIL 下单项 dict 操作原子 + 校验幂等，维持既有用法。

**Tech Stack:** PyQt6（QThread / QueuedConnection / QTimer.singleShot）、psutil、pytest + pytest-qt。

**Spec 依据:** `docs/superpowers/specs/2026-08-18-tech-stack-modernization-roadmap-design.md` P3 节（#9 扫描后解析+SHA-256 后台化、#12 非阻塞 CPU 采样、#13 列宽去抖、移除 processEvents）。

**两处记录在案的范围决定（偏离/澄清 spec）：**
1. **保留 launcher.py:42 与 main_window.py:580 的 splash `processEvents`**。spec #12 列了 launcher，但这两处是启动时尚未进入事件循环的 QSplashScreen 官方绘制模式（移除会导致 splash 空白），不是防重入场景。其余 4 处（progress_dialog ×2、theme_manager、battery_chart_viewer）全部移除。
2. **不后台化 `data_processor.analyze_data`（:405）与 `process_all_excel_files`（:131）**。二者均为 GUI 不可达死代码：`AnalyzeDataCommand` → `presenter.on_analyze_data()` 只调用 `_notify_integrated("Data Analysis")`（弹状态栏 "Ready"），从不触达 `data_processor.analyze_data`；`ProcessAllExcelCommand` 未在 `command_manager` 注册。spec #9 的 "analyze_data 移入后台" 指的就是这段死代码，YAGNI 跳过，仅记录。

**约束：** 所有公开 API 签名不变；`get_version` 仍同步返回 `None`（内部改为异步派发）。基准脚本位于 `scripts/benchmark_p2.py`（P3 不触碰核心计算路径，无需跑）。TDD：每步先写失败测试再实现。

---

### Task 1: ResourceManager 非阻塞 CPU 采样

**Files:**
- Modify: `src/battery_analysis/utils/resource_manager.py:43`
- Test: `tests/battery_analysis/utils/test_resource_manager.py`

- [ ] **Step 1: 写失败测试**

在 `tests/battery_analysis/utils/test_resource_manager.py` 的 `TestResourceManager` 类内追加：

```python
def test_cpu_percent_uses_non_blocking_sample(self):
    """cpu_percent 用 interval=None 非阻塞采样，且高负载时缩容进程数。

    原 interval=1 会阻塞调用线程整整 1 秒——在 GUI 主线程触发时直接冻结 UI。
    """
    fake_psutil = Mock()
    fake_psutil.cpu_percent.return_value = 90.0  # 高负载
    fake_psutil.virtual_memory.return_value = Mock(available=32 * 1024 ** 3)
    with patch('battery_analysis.utils.resource_manager.psutil', fake_psutil):
        result = ResourceManager.get_optimal_process_count(max_processes_default=8)
    fake_psutil.cpu_percent.assert_called_once_with(interval=None, percpu=False)
    # 高负载 → 上限 min(8, 2)=2；32GB 内存 → 320 进程不进一步缩
    assert result == 2
```

- [ ] **Step 2: 运行验证失败**

Run: `uv run pytest tests/battery_analysis/utils/test_resource_manager.py::TestResourceManager::test_cpu_percent_uses_non_blocking_sample -v`
Expected: FAIL，`assert_called_once_with` 报 `interval=1` 与期望 `interval=None` 不符。

- [ ] **Step 3: 实现**

`src/battery_analysis/utils/resource_manager.py:42-43` 改为：

```python
                # 检测系统CPU使用率（非阻塞采样）
                # interval=None 立即返回自上次调用以来的占用率（首次调用返回 0.0）；
                # 原 interval=1 会阻塞调用线程整整 1 秒，GUI 主线程调用时直接冻结 UI
                #（roadmap #12）。首次调用返回 0.0 → 走低负载默认分支，语义安全。
                cpu_usage = psutil.cpu_percent(interval=None, percpu=False)
```

- [ ] **Step 4: 运行验证通过**

Run: `uv run pytest tests/battery_analysis/utils/test_resource_manager.py -v`
Expected: PASS（2 个用例，原有 `test_get_optimal_process_count` 用真实 psutil 首次调用返回 0.0 → 低负载 → 默认值，仍满足 `isinstance(result, int) and result >= 1`）。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/utils/resource_manager.py tests/battery_analysis/utils/test_resource_manager.py
git commit -m "feat(p3): cpu_percent 非阻塞采样 interval=None（#12）

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: resizeColumnsToContents 去抖

**Files:**
- Modify: `src/battery_analysis/main/main_window.py:542-547`
- Test: `tests/battery_analysis/main/test_main_window.py`

- [ ] **Step 1: 写失败测试**

在 `tests/battery_analysis/main/test_main_window.py` 的 `TestMainWindow` 类内追加：

```python
def test_resize_event_debounces_resize_columns(self):
    """resize 只调度 150ms 去抖的列宽自适应，不逐帧同步执行"""
    table = MagicMock()
    table.rowCount.return_value = 3
    self.main_window.tableWidget_TestInformation = table
    from PyQt6.QtCore import QResizeEvent, QSize
    event = QResizeEvent(QSize(800, 600), QSize(790, 590))
    with patch('battery_analysis.main.main_window.QC.QTimer.singleShot') as mock_single_shot:
        self.main_window.resizeEvent(event)
        mock_single_shot.assert_called_once_with(150, self.main_window._resize_table_columns)
        table.resizeColumnsToContents.assert_not_called()
    # 去抖到期后真正触发列宽自适应
    self.main_window._resize_table_columns()
    table.resizeColumnsToContents.assert_called_once()

def test_resize_event_skips_empty_table(self):
    """空表格不调度去抖"""
    table = MagicMock()
    table.rowCount.return_value = 0
    self.main_window.tableWidget_TestInformation = table
    from PyQt6.QtCore import QResizeEvent, QSize
    event = QResizeEvent(QSize(800, 600), QSize(790, 590))
    with patch('battery_analysis.main.main_window.QC.QTimer.singleShot') as mock_single_shot:
        self.main_window.resizeEvent(event)
        mock_single_shot.assert_not_called()
```

- [ ] **Step 2: 运行验证失败**

Run: `uv run pytest tests/battery_analysis/main/test_main_window.py::TestMainWindow::test_resize_event_debounces_resize_columns -v`
Expected: FAIL——`resizeEvent` 现直接调用 `resizeColumnsToContents`，`assert_not_called` 不满足；且 `_resize_table_columns` 尚不存在（AttributeError）。

- [ ] **Step 3: 实现**

`src/battery_analysis/main/main_window.py:542-547` 的 `resizeEvent` 替换，并在其后新增 `_resize_table_columns`：

```python
    def resizeEvent(self, event):
        """窗口大小改变时的事件处理函数"""
        super().resizeEvent(event)
        if hasattr(self, 'tableWidget_TestInformation'):
            if self.tableWidget_TestInformation.rowCount() > 0:
                # 去抖（roadmap #13）：resize 事件高频触发，逐帧同步
                # resizeColumnsToContents 是 O(rows×cols) 重排。
                # singleShot 150ms 合并快速连发；首次布局由 _deferred_init
                # 同步执行一次。
                QC.QTimer.singleShot(150, self._resize_table_columns)

    def _resize_table_columns(self):
        """去抖后的列宽自适应（由 resizeEvent 的 QTimer.singleShot 触发）"""
        if hasattr(self, 'tableWidget_TestInformation'):
            if self.tableWidget_TestInformation.rowCount() > 0:
                self.tableWidget_TestInformation.resizeColumnsToContents()
```

- [ ] **Step 4: 运行验证通过**

Run: `uv run pytest tests/battery_analysis/main/test_main_window.py::TestMainWindow::test_resize_event_debounces_resize_columns tests/battery_analysis/main/test_main_window.py::TestMainWindow::test_resize_event_skips_empty_table -v`
Expected: PASS（2 个用例）。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/main/main_window.py tests/battery_analysis/main/test_main_window.py
git commit -m "feat(p3): resizeColumnsToContents 150ms 去抖（#13）

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: 移除低收益 processEvents（保留 2 处 splash）

**Files:**
- Modify: `src/battery_analysis/main/ui_components/progress_dialog.py:131,140`
- Modify: `src/battery_analysis/main/ui_components/theme_manager.py:198`
- Modify: `src/battery_analysis/main/battery_chart_viewer.py:333`
- Modify（仅加注释）: `src/battery_analysis/main/launcher.py:42`、`src/battery_analysis/main/main_window.py:580`
- Test: `tests/battery_analysis/main/ui_components/test_progress_dialog.py`、`tests/battery_analysis/main/ui_components/test_theme_manager.py`

- [ ] **Step 1: 写失败测试**

`tests/battery_analysis/main/ui_components/test_progress_dialog.py` 的 `TestProgressDialog` 类内追加：

```python
def test_update_progress_does_not_process_events(self):
    """update_progress 不调用 processEvents（防重入，roadmap #12）"""
    with patch('battery_analysis.main.ui_components.progress_dialog.QW.QApplication.processEvents') as mock_pe:
        self.dialog.update_progress(50, "Test progress")
        mock_pe.assert_not_called()

def test_on_cancel_does_not_process_events(self):
    """_on_cancel 不调用 processEvents"""
    with patch('battery_analysis.main.ui_components.progress_dialog.QW.QApplication.processEvents') as mock_pe:
        self.dialog._on_cancel()
        mock_pe.assert_not_called()
```

`tests/battery_analysis/main/ui_components/test_theme_manager.py` 的 `TestThemeManager` 类内追加：

```python
def test_set_theme_does_not_process_events(self):
    """set_theme 不调用 processEvents（unpolish/polish 已触发重绘）"""
    with patch('battery_analysis.main.ui_components.theme_manager.QW.QApplication.processEvents') as mock_pe:
        self.manager.set_theme("System Default")
        mock_pe.assert_not_called()
```

- [ ] **Step 2: 运行验证失败**

Run: `uv run pytest tests/battery_analysis/main/ui_components/test_progress_dialog.py tests/battery_analysis/main/ui_components/test_theme_manager.py -v`
Expected: FAIL——3 个新用例的 `assert_not_called` 不满足（processEvents 当前被调用）。

- [ ] **Step 3: 实现**

`src/battery_analysis/main/ui_components/progress_dialog.py`：
- 删除 `update_progress` 内 :130-131 的注释块与 `QW.QApplication.processEvents()`（:131）。保留其余方法体：

```python
    def update_progress(self, progress, status_text):
        """
        更新进度信息

        Args:
            progress: 进度值
            status_text: 状态文本
        """
        self.progress_bar.setValue(progress)
        self.status_label.setText(status_text)

        # 更新窗口标题，显示百分比
        self.setWindowTitle(f"{_("Battery Analysis Progress")} - {progress}%")
        # 移除 processEvents()（roadmap #12）：进度刷新走 Qt 事件循环自然调度，
        # 显式 processEvents 会深度重入事件循环，造成嵌套 dispatch 风险。
```

- 删除 `_on_cancel` 内 :140 的 `QW.QApplication.processEvents()`：

```python
    def _on_cancel(self):
        """
        处理取消按钮点击事件
        """
        self.is_canceled = True
        self.canceled.emit()
        self.status_label.setText(_("Task canceled..."))
        # 移除 processEvents()（roadmap #12）：同 update_progress，避免重入。
```

`src/battery_analysis/main/ui_components/theme_manager.py:197-198`，删除 `processEvents` 并留注释：

```python
        # 确保界面立即更新
        # 移除 processEvents()（roadmap #12）：setStyleSheet 走 Qt 样式系统
        # 自动重绘，显式 processEvents 只会重入事件循环。
```

`src/battery_analysis/main/battery_chart_viewer.py:333`，删除 `app.processEvents()` 并留注释：

```python
            with open(unified_style_path, 'r', encoding='utf-8') as f:
                unified_style = f.read()
                app.setStyleSheet(unified_style)
                # 移除 processEvents()（roadmap #12）：unpolish/polish 已触发完整重绘
                app.style().unpolish(app)
                app.style().polish(app)
                app.update()
```

`src/battery_analysis/main/launcher.py:42`（保留调用，加注释）：

```python
        # 保留 processEvents()：启动时尚未进入事件循环，QSplashScreen 官方模式
        # 要求在此绘制 splash。roadmap #12 移除的是 progress_dialog/theme_manager/
        # battery_chart_viewer 的防重入调用，此处移除会导致启动 splash 空白。
        app.processEvents()
```

`src/battery_analysis/main/main_window.py:580`（保留调用，加注释）：

```python
        # 保留 processEvents()：同 launcher，启动期 splash 绘制（进入事件循环前）。
        app.processEvents()
```

- [ ] **Step 4: 运行验证通过**

Run: `uv run pytest tests/battery_analysis/main/ui_components/test_progress_dialog.py tests/battery_analysis/main/ui_components/test_theme_manager.py -v`
Expected: PASS。随后确认仅剩 2 处 processEvents：

Run: `uv run python -c "import re, pathlib; hits=[(str(p),i,l.strip()) for p in pathlib.Path('src').rglob('*.py') for i,l in enumerate(open(p,encoding='utf-8')) if 'processEvents' in l]; [print(f'{p}:{i+1} {l}') for p,i,l in hits]"`
Expected: 恰好两行——`launcher.py` 与 `main_window.py` 各一处（splash 保留项）。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/main/ui_components/progress_dialog.py src/battery_analysis/main/ui_components/theme_manager.py src/battery_analysis/main/battery_chart_viewer.py src/battery_analysis/main/launcher.py src/battery_analysis/main/main_window.py tests/battery_analysis/main/ui_components/test_progress_dialog.py tests/battery_analysis/main/ui_components/test_theme_manager.py
git commit -m "feat(p3): 移除 4 处低收益 processEvents，保留 splash 2 处并注明理由

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: `_process_excel_files` 后台化（核心）

**Files:**
- Modify: `src/battery_analysis/main/business_logic/data_processor.py:180-200`（`_on_scan_finished`）
- Modify: `src/battery_analysis/main/business_logic/data_processor.py:269-308`（删除 `_process_excel_files`，替换为后台任务 + 主线程回调）
- Test: `tests/battery_analysis/main/business_logic/test_data_processor.py`

**设计：** `_on_scan_finished` 不再同步执行逐文件 `pd.read_excel`，改为再派发一个后台任务。新任务函数 `_process_excel_files_task` 只读文件、返回 `(excel_files, excel_data, error_files)`；新主线程回调 `_on_excel_files_processed` 负责弹窗/状态栏/表格/规格信号重连。`LRUCache` 跨线程写入维持既有用法（GIL 原子 + 校验幂等）。

- [ ] **Step 1: 写失败测试**

`tests/battery_analysis/main/business_logic/test_data_processor.py` 的 `TestDataProcessor` 类内追加（沿用该文件既有 `from battery_analysis.main.business_logic import data_processor as dp` 局部导入模式）：

```python
def test_on_scan_finished_dispatches_background_processing(self):
    """扫描完成 → 后台线程处理 Excel 解析，主线程不阻塞"""
    self.mock_main_window.lineEdit_InputPath.text.return_value = '/fake/dir'
    with patch.object(self.processor, 'run_in_background') as mock_run:
        self.processor._on_scan_finished(['a.xlsx', 'b.xlsx'])
    mock_run.assert_called_once()
    task_func, on_finished, on_error, input_dir, excel_files = mock_run.call_args[0]
    assert task_func == self.processor._process_excel_files_task
    assert on_finished == self.processor._on_excel_files_processed
    assert on_error == self.processor._on_excel_files_process_error
    assert input_dir == '/fake/dir'
    assert excel_files == ['a.xlsx', 'b.xlsx']

def test_on_scan_finished_empty_files_no_background(self):
    """无文件 → 走 _handle_no_excel_files，不派发后台任务"""
    with patch.object(self.processor, '_handle_no_excel_files') as mock_handle, \
         patch.object(self.processor, 'run_in_background') as mock_run:
        self.processor._on_scan_finished([])
    mock_handle.assert_called_once()
    mock_run.assert_not_called()

def test_process_excel_files_task_returns_data_and_errors(self, tmp_path):
    """后台任务只读文件：返回 (excel_files, excel_data, error_files)，不碰 UI"""
    valid = tmp_path / 'valid.xlsx'
    pd.DataFrame({'Capacity': [1000, 2000]}).to_excel(valid, index=False)
    invalid = tmp_path / 'broken.xlsx'
    invalid.write_bytes(b'not a real xlsx')
    result = self.processor._process_excel_files_task(str(tmp_path), ['valid.xlsx', 'broken.xlsx'])
    excel_files, excel_data, error_files = result
    assert excel_files == ['valid.xlsx', 'broken.xlsx']
    assert len(excel_data) == 1
    assert excel_data[0]['filename'] == 'valid.xlsx'
    assert excel_data[0]['row_count'] == 2
    assert len(error_files) == 1
    assert error_files[0][0] == 'broken.xlsx'

def test_on_excel_files_processed_success(self):
    """处理成功 → 更新 UI + 解析首个文件 + 重连规格信号"""
    excel_files = ['a.xlsx']
    excel_data = [{'filename': 'a.xlsx'}]
    with patch.object(self.processor, '_update_ui_with_excel_info') as mock_ui, \
         patch.object(self.processor, '_process_first_excel_file') as mock_first, \
         patch.object(self.processor, '_reconnect_specification_signals') as mock_reconnect:
        self.processor._on_excel_files_processed((excel_files, excel_data, []))
    mock_ui.assert_called_once_with(excel_files, excel_data)
    mock_first.assert_called_once_with('a.xlsx')
    mock_reconnect.assert_called_once()

def test_on_excel_files_processed_all_failed(self):
    """全部文件失败 → 设置错误提示，不进入成功流程"""
    self.mock_main_window.checker_input_xlsx = Mock()
    with patch.object(self.processor, '_update_ui_with_excel_info') as mock_ui:
        self.processor._on_excel_files_processed((['a.xlsx'], [], []))
    mock_ui.assert_not_called()
    self.mock_main_window.checker_input_xlsx.set_error.assert_called()
    self.mock_main_window.statusBar_BatteryAnalysis.showMessage.assert_called()

def test_on_excel_files_processed_shows_error_dialog(self):
    """存在错误文件 → 主线程弹 QMessageBox 明细"""
    mock_msgbox = Mock()
    with patch.object(dp.QW, 'QMessageBox', return_value=mock_msgbox):
        self.processor._on_excel_files_processed((['a.xlsx'], [], [('a.xlsx', 'bad format')]))
    mock_msgbox.exec.assert_called_once()
    mock_msgbox.setDetailedText.assert_called_once()
```

- [ ] **Step 2: 运行验证失败**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_data_processor.py -v`
Expected: FAIL——`_process_excel_files_task` / `_on_excel_files_processed` / `_on_excel_files_process_error` 尚不存在（AttributeError）。

- [ ] **Step 3: 实现**

`src/battery_analysis/main/business_logic/data_processor.py`：

**(a)** 替换 `_on_scan_finished`（:180-200 现有整体）为：

```python
    def _on_scan_finished(self, excel_files):
        input_dir = self.main_window.lineEdit_InputPath.text()
        self._cache['directory_files'].put(input_dir, excel_files)

        if not excel_files:
            self._handle_no_excel_files(input_dir)
            return

        # 逐文件 pd.read_excel 校验是重活，放后台线程执行；回调在
        # 主线程弹窗/更新 UI（roadmap #9）。
        self.run_in_background(
            self._process_excel_files_task,
            self._on_excel_files_processed,
            self._on_excel_files_process_error,
            input_dir, excel_files,
        )
```

**(b)** 删除旧 `_process_excel_files`（:269-308 整体），替换为三个新方法：

```python
    def _process_excel_files_task(self, input_dir, excel_files, **kwargs):
        """后台线程：逐文件验证并提取 Excel 元信息（不触碰任何 UI）。

        返回 (excel_files, excel_data, error_files)；progress_callback 由
        TaskRunner 强制注入，此处忽略。
        """
        excel_data = []
        error_files = []
        for filename in excel_files:
            file_path = os.path.join(input_dir, filename)
            is_valid, error_msg, df = excel_validator.validate_excel_file(
                file_path, filename, self._cache['file_validation'], optimize_dataframe_memory)
            if not is_valid:
                self.logger.error(error_msg)
                error_files.append((filename, error_msg))
                continue
            file_info = {
                'filename': filename,
                'sheet_name': df.columns.tolist(),
                'row_count': len(df),
                'column_count': len(df.columns),
                'first_five_rows': df.head().to_dict('records'),
            }
            excel_data.append(file_info)
        return excel_files, excel_data, error_files

    def _on_excel_files_processed(self, result):
        """主线程：_process_excel_files_task 完成后的 UI 更新"""
        excel_files, excel_data, error_files = result

        if error_files:
            error_message = "The following files have issues:\n" + "\n".join(
                f"- {f}: {m}" for f, m in error_files)
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    f"[Error]: Found {len(error_files)} problematic files")
            if hasattr(self.main_window, 'checker_input_xlsx'):
                self.main_window.checker_input_xlsx.set_error(error_message)
            try:
                msg = QW.QMessageBox(self.main_window)
                msg.setIcon(QW.QMessageBox.Icon.Warning)
                msg.setWindowTitle("File Validation Error")
                msg.setText(f"Found {len(error_files)} problematic files that cannot be analyzed")
                msg.setInformativeText("Please check the file format and content, then retry")
                msg.setDetailedText(error_message)
                msg.setStandardButtons(QW.QMessageBox.StandardButton.Ok)
                msg.exec()
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.logger.warning("Error showing error dialog: %s", e)

        if not excel_data:
            self.logger.error("No Excel files were processed successfully")
            if hasattr(self.main_window, 'checker_input_xlsx'):
                self.main_window.checker_input_xlsx.set_error(
                    "No Excel files were processed successfully. Please check the file format.")
            if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
                self.main_window.statusBar_BatteryAnalysis.showMessage(
                    "[Error]: No Excel files were processed successfully")
            return

        self._update_ui_with_excel_info(excel_files, excel_data)
        if excel_files:
            self._process_first_excel_file(excel_files[0])
        self._reconnect_specification_signals()

    def _on_excel_files_process_error(self, error_msg):
        """主线程：后台任务异常兜底"""
        self.logger.error("Failed to process Excel files: %s", error_msg)
        if hasattr(self.main_window, 'checker_input_xlsx'):
            self.main_window.checker_input_xlsx.set_error(f"Failed to process files: {error_msg}")
        if hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.showMessage("[Error]: Failed to process files")
        self._reconnect_specification_signals()
```

> 说明：`_process_excel_files_task` 是绑定方法，BackgroundWorker 在同进程内直接持有调用（QThread 不 pickle），无需模块级函数。`validate_excel_file` 自身捕获读取异常返回 `(False, msg, None)`；若抛异常，TaskRunner 捕获后走 `error` 信号 → `_on_excel_files_process_error`，比旧版直接抛到 Qt 信号槽更健壮。

- [ ] **Step 4: 运行验证通过**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_data_processor.py -v`
Expected: PASS（新增 6 个 + 既有用例全部通过）。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/main/business_logic/data_processor.py tests/battery_analysis/main/business_logic/test_data_processor.py
git commit -m "feat(p3): 扫描后 Excel 解析移入后台线程，UI 回调主线程（#9）

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: SHA-256 校验和后台化（VersionManager）

**Files:**
- Modify: `src/battery_analysis/main/business_logic/version_manager.py:22-141`
- Test: `tests/battery_analysis/main/business_logic/test_version_manager.py`

**设计：** `get_version` 保持签名与返回（`None`），内部把 SHA-256 计算派发到 `run_in_background`（QThread + BackgroundWorker + `_MainThreadCallback`）。`_calc_checksum_task` 后台读文件算校验和；`_on_checksum_ready` 主线程做 CSV 落盘 + `lineEdit_Version` 更新，并在**任何读取者之前**回写 `self.main_window.sha256_checksum`（时序保证：`analysis_runner.py:173` 与 `set_version` 依赖它随时可用）。`_MainThreadCallback` 复用自 `data_processor`（同包内私有类，P5 收敛 worker 模式时提取公共）。

- [ ] **Step 1: 写失败测试**

`tests/battery_analysis/main/business_logic/test_version_manager.py`：

**(a)** 把 `TestGetVersion` 的两个既有用例改为新的异步调用模式：

```python
class TestGetVersion:
    """get_version()方法测试（P3 改为后台派发后，直接测 task+callback 两个阶段）"""

    def test_reads_existing_times(self, tmp_path):
        """校验和已存在时，读取Times值显示为版本号"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # 创建一个空xlsx文件作为输入
        xlsx_file = input_dir / "test.xlsx"
        xlsx_file.write_bytes(b"dummy excel content")

        create_sha256_csv(output_dir, ["dummy_checksum"], ["3"])

        main_window = MagicMock()
        main_window.lineEdit_InputPath.text.return_value = str(input_dir)
        main_window.lineEdit_OutputPath.text.return_value = str(output_dir)
        main_window.lineEdit_Version = MagicMock()
        main_window.statusBar_BatteryAnalysis = MagicMock()
        main_window._get_service.return_value = None

        # 模拟calc_checksum返回固定值
        with patch('battery_analysis.main.utils.file_utils.FileUtils.calc_checksum',
                   return_value="dummy_checksum"):
            vm = VersionManager(main_window)
            checksum = vm._calc_checksum_task(str(input_dir))
            vm._on_checksum_ready(checksum)

        # 应显示1.3（第一个校验和，Times=3）
        main_window.lineEdit_Version.setText.assert_called_with("1.3")
        # 校验和已回写，供 set_version/analysis_runner 随时读取
        assert main_window.sha256_checksum == "dummy_checksum"

    def test_invalid_times_uses_zero(self, tmp_path):
        """Times值无效时，默认使用0"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        xlsx_file = input_dir / "test.xlsx"
        xlsx_file.write_bytes(b"dummy excel content")

        # Times为空字符串
        create_sha256_csv(output_dir, ["dummy_checksum"], [""])

        main_window = MagicMock()
        main_window.lineEdit_InputPath.text.return_value = str(input_dir)
        main_window.lineEdit_OutputPath.text.return_value = str(output_dir)
        main_window.lineEdit_Version = MagicMock()
        main_window.statusBar_BatteryAnalysis = MagicMock()
        main_window._get_service.return_value = None

        with patch('battery_analysis.main.utils.file_utils.FileUtils.calc_checksum',
                   return_value="dummy_checksum"):
            vm = VersionManager(main_window)
            checksum = vm._calc_checksum_task(str(input_dir))
            vm._on_checksum_ready(checksum)

        # Times为空字符串→转换为0→显示1.0
        main_window.lineEdit_Version.setText.assert_called_with("1.0")
```

**(b)** 追加后台派发与边界用例：

```python
    def test_get_version_dispatches_background_checksum(self):
        """get_version 把 SHA-256 计算派发到后台线程，不阻塞主线程"""
        main_window = MagicMock()
        main_window.lineEdit_InputPath.text.return_value = "/tmp/in"
        main_window.lineEdit_OutputPath.text.return_value = "/tmp/out"
        vm = VersionManager(main_window)
        with patch('os.path.exists', return_value=True), \
             patch.object(vm, 'run_in_background') as mock_run:
            vm.get_version()
        mock_run.assert_called_once()
        args = mock_run.call_args[0]
        assert args[0] == vm._calc_checksum_task
        assert args[1] == vm._on_checksum_ready
        assert args[3] == "/tmp/in"

    def test_get_version_missing_dirs_clears_version(self):
        """输入/输出目录缺失时，直接清空版本号，不启动线程"""
        main_window = MagicMock()
        main_window.lineEdit_InputPath.text.return_value = "/nonexistent/in"
        main_window.lineEdit_OutputPath.text.return_value = "/nonexistent/out"
        main_window.lineEdit_Version = MagicMock()
        vm = VersionManager(main_window)
        with patch('os.path.exists', return_value=False), \
             patch.object(vm, 'run_in_background') as mock_run:
            vm.get_version()
        main_window.lineEdit_Version.setText.assert_called_once_with("")
        mock_run.assert_not_called()

    def test_calc_checksum_task_returns_none_without_xlsx(self, tmp_path):
        """目录内无 xlsx → 任务返回 None（回调据此清空版本号）"""
        (tmp_path / "readme.txt").write_text("hi", encoding='utf-8')
        vm = VersionManager(MagicMock())
        assert vm._calc_checksum_task(str(tmp_path)) is None

    def test_calc_checksum_task_returns_checksum(self, tmp_path):
        """有 xlsx → 返回 FileUtils.calc_checksum 结果"""
        (tmp_path / "a.xlsx").write_bytes(b"dummy")
        vm = VersionManager(MagicMock())
        with patch('battery_analysis.main.utils.file_utils.FileUtils.calc_checksum',
                   return_value="abc123"):
            assert vm._calc_checksum_task(str(tmp_path)) == "abc123"

    def test_on_checksum_ready_none_clears_version(self):
        """回调收到 None（无 xlsx）→ 清空版本号"""
        main_window = MagicMock()
        main_window.lineEdit_Version = MagicMock()
        vm = VersionManager(main_window)
        vm._on_checksum_ready(None)
        main_window.lineEdit_Version.setText.assert_called_once_with("")

    def test_on_checksum_error_logs(self):
        """校验和计算异常 → 记录日志，不崩溃"""
        vm = VersionManager(MagicMock())
        with patch.object(vm.logger, 'error') as mock_error:
            vm._on_checksum_error("boom")
        mock_error.assert_called_once()
```

- [ ] **Step 2: 运行验证失败**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_version_manager.py -v`
Expected: FAIL——`run_in_background` / `_calc_checksum_task` / `_on_checksum_ready` / `_on_checksum_error` 尚不存在（AttributeError）；`TestGetVersion` 两个旧用例改为新调用模式后也会因方法缺失失败。

- [ ] **Step 3: 实现**

`src/battery_analysis/main/business_logic/version_manager.py`：

**(a)** 顶部 import 追加：

```python
import os
import csv
import logging
from pathlib import Path

from PyQt6 import QtCore as QC
from battery_analysis.main.business_logic.background_worker import BackgroundWorker
from battery_analysis.main.business_logic.data_processor import _MainThreadCallback
```

**(b)** `__init__` 追加线程生命周期属性：

```python
        self.main_window = main_window
        self._ctx = ctx
        self.logger = logging.getLogger(__name__)
        self._background_thread = None
        self._background_worker = None
```

**(c)** `get_version`（:34-141 整体）替换为派发器 + 三个新方法 + `run_in_background`/`_cleanup_background_thread`：

```python
    def get_version(self) -> None:
        """
        计算并设置电池分析的版本号

        目录存在性检查在主线程同步完成；SHA-256 校验和计算派发到后台线程，
        完成后由 _on_checksum_ready 在主线程落盘 SHA256.csv 并更新 UI（roadmap #9）。
        """
        strInPutDir = self.main_window.lineEdit_InputPath.text()
        strOutoutDir = self.main_window.lineEdit_OutputPath.text()
        if os.path.exists(strInPutDir) and os.path.exists(strOutoutDir):
            self.run_in_background(
                self._calc_checksum_task,
                self._on_checksum_ready,
                self._on_checksum_error,
                strInPutDir,
            )
        else:
            self.main_window.lineEdit_Version.setText("")

    def _calc_checksum_task(self, strInPutDir, **kwargs):
        """后台线程：计算目录内全部 xlsx 的 SHA-256 校验和（不触碰 UI）。

        目录内无 xlsx 文件时返回 None（回调据此清空版本号）。
        progress_callback 由 TaskRunner 强制注入，此处忽略。
        """
        listAllInXlsx = [strInPutDir + f"/{f}" for f in os.listdir(
            strInPutDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
        if not listAllInXlsx:
            return None
        from battery_analysis.main.utils.file_utils import FileUtils
        return FileUtils.calc_checksum(listAllInXlsx)

    def _on_checksum_ready(self, checksum):
        """主线程：校验和计算完成后的版本号落盘 + UI 更新"""
        if checksum is None:
            # 目录内无 xlsx 文件
            self.main_window.lineEdit_Version.setText("")
            return
        # 时序保证：sha256_checksum 必须随时可用（analysis_runner.py:173、
        # set_version 均读取它），故在任何读取者之前回写。
        self.main_window.sha256_checksum = checksum

        try:
            strOutoutDir = self.main_window.lineEdit_OutputPath.text()
            strCsvPath = strOutoutDir + "/SHA256.csv"

            if os.path.exists(strCsvPath) and os.path.getsize(strCsvPath) != 0:
                listSHA256Reader = []
                f = open(strCsvPath, mode='r', encoding='utf-8')
                csvSHA256Reader = csv.reader(f)
                for row in csvSHA256Reader:
                    listSHA256Reader.append(row)
                f.close()
                # 确保列表长度足够，正确访问CSV行数据
                if len(listSHA256Reader) >= 4:
                    listChecksum = listSHA256Reader[1] if len(listSHA256Reader) > 1 else []
                    listTimes = listSHA256Reader[3] if len(listSHA256Reader) > 3 else []
                else:
                    listChecksum = []
                    listTimes = []

                # 检查当前校验和是否已存在
                current_checksum = checksum
                existing_index = -1
                for i, chk in enumerate(listChecksum):
                    if chk == current_checksum:
                        existing_index = i
                        break

                os.remove(strCsvPath)
                f = open(strCsvPath, mode='w', newline='', encoding='utf-8')
                csvSHA256Writer = csv.writer(f)

                if not listChecksum:
                    # 第一次运行，主版本号从1开始
                    csvSHA256Writer.writerow(["Checksums:"])
                    csvSHA256Writer.writerow([current_checksum])
                    csvSHA256Writer.writerow(["Times:"])
                    csvSHA256Writer.writerow(["0"])
                    self.main_window.lineEdit_Version.setText("1.0")
                elif existing_index >= 0:
                    # 校验和已存在，使用现有的版本号和运行次数
                    intVersionMajor = existing_index + 1
                    try:
                        intVersionMinor = int(listTimes[existing_index]) if existing_index < len(listTimes) and listTimes[existing_index] else 0
                    except (ValueError, IndexError):
                        intVersionMinor = 0

                    csvSHA256Writer.writerow(["Checksums:"])
                    csvSHA256Writer.writerow(listChecksum)
                    csvSHA256Writer.writerow(["Times:"])
                    csvSHA256Writer.writerow(listTimes)
                    self.main_window.lineEdit_Version.setText(
                        f"{intVersionMajor}.{intVersionMinor}")
                else:
                    # 校验和不存在，增加主版本号
                    intVersionMajor = len(listChecksum) + 1
                    intVersionMinor = 0

                    # 将当前校验和添加到列表，作为新的主版本
                    listChecksum.append(current_checksum)
                    listTimes.append("0")

                    csvSHA256Writer.writerow(["Checksums:"])
                    csvSHA256Writer.writerow(listChecksum)
                    csvSHA256Writer.writerow(["Times:"])
                    csvSHA256Writer.writerow(listTimes)
                    self.main_window.lineEdit_Version.setText(
                        f"{intVersionMajor}.{intVersionMinor}")
                f.close()
            else:
                f = open(strCsvPath, mode='w', newline='', encoding='utf-8')
                csvSHA256Writer = csv.writer(f)
                csvSHA256Writer.writerow(["Checksums:"])
                csvSHA256Writer.writerow([checksum])
                csvSHA256Writer.writerow(["Times:"])
                csvSHA256Writer.writerow(["0"])
                f.close()
                self.main_window.lineEdit_Version.setText("1.0")

            # 使用文件服务设置文件隐藏属性
            file_service = self.main_window._get_service("file")
            if file_service:
                file_service.hide_file(strCsvPath)
            else:
                # 降级到直接调用
                try:
                    import win32api
                    import win32con
                    win32api.SetFileAttributes(strCsvPath, win32con.FILE_ATTRIBUTE_HIDDEN)
                except ImportError:
                    self.logger.warning("File service is unavailable; cannot set file hidden attribute")
        except Exception as e:  # pylint: disable=broad-exception-caught
            # 后台派发后不再有 _deferred_init 的 try/except 兜底，这里主动记录
            self.logger.error("Failed to finalize version after checksum: %s", e)

    def _on_checksum_error(self, error_msg):
        """主线程：校验和计算异常兜底"""
        self.logger.error("Failed to compute SHA-256 checksum: %s", error_msg)

    def run_in_background(self, task_func, on_finished, on_error, *args):
        """QThread + BackgroundWorker 执行后台任务，回调经 QueuedConnection 切回主线程"""
        self._cleanup_background_thread()
        self._background_thread = QC.QThread()
        self._background_worker = BackgroundWorker(task_func, *args)
        self._background_worker.moveToThread(self._background_thread)

        self._background_thread.started.connect(self._background_worker.run)
        self._background_worker.finished.connect(self._background_thread.quit)
        self._background_worker.finished.connect(self._background_worker.deleteLater)
        self._background_thread.finished.connect(self._background_thread.deleteLater)
        if on_finished:
            self._background_worker.finished.connect(_MainThreadCallback(on_finished))
        if on_error:
            self._background_worker.error.connect(_MainThreadCallback(on_error))
        self._background_thread.start()

    def _cleanup_background_thread(self):
        if self._background_thread and self._background_thread.isRunning():
            self._background_thread.quit()
            self._background_thread.wait(1000)
            if self._background_thread.isRunning():
                self._background_thread.terminate()
        self._background_thread = None
        self._background_worker = None
```

> 说明：`set_version`（:143-283）不改——它读取 `sha256_checksum_run`（已有缓存），仍同步执行；只有 `get_version` 的校验和计算移到后台。`_MainThreadCallback` 从 `data_processor` 复用；无循环 import（`data_processor` 不依赖 `version_manager`）。

- [ ] **Step 4: 运行验证通过**

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_version_manager.py -v`
Expected: PASS（TestSetVersion 6 个不变 + TestGetVersion 更新后全部通过）。随后跑 `set_version` 相关既有用例确认无回归：

Run: `uv run pytest tests/battery_analysis/main/business_logic/test_version_manager.py -k "SetVersion" -v`
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add src/battery_analysis/main/business_logic/version_manager.py tests/battery_analysis/main/business_logic/test_version_manager.py
git commit -m "feat(p3): SHA-256 校验和计算移入后台线程（#9）

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: 全量回归 + 基准确认 + 提交 PR

**Files:**
- 无源码改动；验证 + 推送

- [ ] **Step 1: 全量测试**

Run: `uv run pytest`
Expected: PASS（当前基线 551 passed / 9 skipped 或以上，无新增失败）。

- [ ] **Step 2: pylint 变更文件**

Run:
```bash
uv run pylint src/battery_analysis/utils/resource_manager.py src/battery_analysis/main/main_window.py src/battery_analysis/main/ui_components/progress_dialog.py src/battery_analysis/main/ui_components/theme_manager.py src/battery_analysis/main/battery_chart_viewer.py src/battery_analysis/main/business_logic/data_processor.py src/battery_analysis/main/business_logic/version_manager.py
```
Expected: 无新增错误（既有告警可接受，但不得引入新的 `E`/`F` 级）。

- [ ] **Step 3: 手动冒烟（真实 GUI 路径）**

Run: `uv run python -c "from battery_analysis.main.business_logic.data_processor import DataProcessor; from battery_analysis.main.business_logic.version_manager import VersionManager; print('imports ok')"`
Expected: `imports ok`（验证 `_MainThreadCallback` 复用无循环 import、PyQt6 导入正常）。

- [ ] **Step 4: 确认变更范围**

Run: `git log --oneline main..HEAD`
Expected: 5 个提交（Task 1-5），各自独立可回退。运行 `git diff main --stat` 确认只动计划内文件。

- [ ] **Step 5: 推送并创建 PR**

```bash
git push -u origin feat/p3-unblock-ui
gh pr create --title "feat(p3): 主线程解阻塞" --body "**P3 主线程解阻塞（roadmap #9/#12/#13）**

- 扫描后 Excel 解析移入后台线程（\`_process_excel_files_task\` + 主线程 \`_on_excel_files_processed\` 回调）
- SHA-256 校验和计算移入后台线程（\`_calc_checksum_task\` + \`_on_checksum_ready\`）
- \`cpu_percent\` 改非阻塞 \`interval=None\` 采样
- \`resizeColumnsToContents\` 150ms 去抖
- 移除 4 处低收益 \`processEvents\`，保留 2 处 splash（启动期绘制必需，已在代码注释注明）

范围决定：\`data_processor.analyze_data\`/\`process_all_excel_files\` 为 GUI 不可达死代码（AnalyzeDataCommand 仅弹状态栏），spec #9 的 analyze_data 项跳过（YAGNI），已记录。

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

> 注：`gh pr merge` 会被 auto mode classifier 拦截，PR 由用户手动合并（既有约定）。

---

## Self-Review

**1. Spec 覆盖：**
- spec #9「扫描后 Excel 解析移入后台 worker」→ Task 4 ✓
- spec #9「SHA-256 校验和移入后台 worker」→ Task 5 ✓
- spec #9「analyze_data 移入后台」→ 记录为死代码跳过（YAGNI），列入计划头「范围决定」✓
- spec #12「移除 progress_dialog/theme_manager/launcher 的 processEvents」→ Task 3 移除 progress_dialog/theme_manager，launcher 保留并注明理由（splash 必需）；额外移除 battery_chart_viewer（unpolish/polish 已重绘）✓
- spec #12「cpu_percent(interval=1) → 非阻塞采样」→ Task 1 ✓
- spec #13「resizeColumnsToContents 首次/数据变化才调用 + 去抖」→ Task 2（_deferred_init 首次同步调用保留，resizeEvent 去抖）✓
- 验收「大文件扫描/报告生成时 UI 不冻结」→ Task 4/5 实现，Task 6 冒烟 ✓

**2. 占位符扫描：** 无 TBD/TODO；每个代码步骤含完整代码。

**3. 类型/签名一致性：**
- `run_in_background` 在 DataProcessor（现有）与 VersionManager（新增）签名一致：`(task_func, on_finished, on_error, *args)`。
- `_process_excel_files_task` 返回 `(excel_files, excel_data, error_files)` 与 `_on_excel_files_processed(result)` 解包一致。
- `_calc_checksum_task` 返回 `checksum | None` 与 `_on_checksum_ready(checksum)` 处理一致。
- 两个 task 函数均带 `**kwargs`（TaskRunner 强制注入 `progress_callback`），与既有 `_scan_excel_files_task` 一致。
- `_MainThreadCallback` 在测试里经 `run_in_background` 调用；TestGetVersion 直接调 task+callback 两个阶段，不经线程，避免测试引入真实 QThread 时序。

**已确认的既有事实（实现时无需再调研）：**
- `_process_excel_files`（data_processor.py:269）唯一调用方是 `_on_scan_finished`（:188），Task 4 删除安全。
- `AnalyzeDataCommand` → `presenter.on_analyze_data()` → `_notify_integrated`，不触达 `data_processor.analyze_data`；`ProcessAllExcelCommand` 未注册——二者死代码。
- `QC` 已在 main_window 顶部 import（`import PyQt6.QtCore as QC`），Task 2 无需新增 import。
- version_manager.py 原本无 Qt import，Task 5 新增 `QC`/`BackgroundWorker`/`_MainThreadCallback`，无循环依赖。
