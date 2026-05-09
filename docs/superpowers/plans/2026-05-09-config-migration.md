# 配置系统重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 移除 `setting.ini` 和 `user_settings.ini`，改为 JSON 文件 (`%APPDATA%/battery-analysis/config.json`) + UI 内置配置管理。

**Architecture:** 新增 `JsonConfigManager` 替代 `IniFileManager`，ConfigService 接口不变，内部委托改为 JSON。ConfigManager 保持 `get_config("Section/Key")` 对外 API 不变，通过键映射表翻译到 JSON 路径。新增 ConfigDialog 供 UI 管理配置。

**Tech Stack:** Python 3.13, PyQt6, json (stdlib)

---

### Task 1: 创建 config_defaults.py — 内置默认数据

**Files:**
- Create: `src/battery_analysis/utils/config_defaults.py`

- [ ] **Step 1: 创建默认数据模块**

该文件提供从现有 setting.ini 提取的默认配置数据，作为首次运行时的种子数据。

```python
# src/battery_analysis/utils/config_defaults.py
"""
配置默认值模块
首次运行时，如果 %APPDATA% 下没有 config.json，则从此模块创建初始数据。
"""

DEFAULT_CONFIG = {
    "version": 1,
    "battery": {
        "types": ["Coin Cell", "Pouch Cell"],
        "constructionMethods": ["Spiral Type", "Laminate Type"],
        "specifications": {
            "Coin Cell": ["CR2450", "CR2450YP", "CR2450PH", "CR2450D", "CR2450HE1", "CR2450HE4"],
            "Pouch Cell": ["CP224642A", "CF583083"]
        },
        "specificationMethods": ["1S1P", "1S2P", "2S1P"],
        "manufacturers": ["ATMT", "EVE", "Omnergy", "Nanfu", "Huiderui", "GP&LB", "HCB"],
        "rules": [
            "CR2450/1S1P/600/550/380/1.0",
            "CR2450D/1S1P/600/550/280/1.0",
            "CR2450HE1/1S1P/600/550/380/1.0",
            "CR2450HE4/1S1P/600/550/280/1.0",
            "CP224642A/1S1P/920/920/80%/5.0",
            "CF583083/1S1P/4000/4000/80%/5.0"
        ],
        "pulseCurrents": [30.0, 26.0, 15.0, 6.0],
        "cutOffVoltages": [2.6, 2.5, 2.4, 2.3, 2.25, 2.2, 2.1, 2.0, 1.8]
    },
    "test": {
        "locations": [
            "CT-4008Q (Qual.), BOE DT",
            "CT-4008Q (QA), BOE DT",
            "CT-4008Q (Qual.), PDI",
            "CT-4008Q (QA), BOE CQ",
            "CT-4008Q (QA), Liba M1",
            "CT-4008Q (QA), Jabil VN",
            "CT-4008Q (HWE), VG Fernitz"
        ],
        "testedBy": [
            "Hall", "Guoying Qi", "Zhaoxuan Zheng", "Xiaoe Wang",
            "Rachel Zhao", "Sandman Zhang", "Maiyue Zhang",
            "Howard Lin", "Kate Zhu", "Sy Tran", "Stefan"
        ],
        "equipment": {}
    },
    "window": {
        "width": 1200,
        "height": 800,
        "maximized": True
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/battery_analysis/utils/config_defaults.py
git commit -m "feat: add config_defaults.py with default configuration data"
```

---

### Task 2: 创建 JsonConfigManager — JSON 配置读写

**Files:**
- Create: `src/battery_analysis/utils/json_config_manager.py`
- Test: (optional, manual test during verification)

- [ ] **Step 1: 创建 JsonConfigManager 类**

```python
# src/battery_analysis/utils/json_config_manager.py
"""
JSON 配置管理器
提供 JSON 配置文件的读取、写入、原子替换功能。
键访问使用点号路径格式，如 "battery.types"。
"""
import json
import os
import tempfile
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class JsonConfigManager:
    """JSON 配置管理器，支持原子写入和键路径访问"""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._loaded = False

    def read_config(self, config_path: str) -> bool:
        """读取 JSON 配置文件"""
        path = Path(config_path)
        if not path.exists():
            logger.warning("配置文件不存在: %s", config_path)
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            self._loaded = True
            logger.info("配置文件读取成功: %s", config_path)
            return True
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.error("配置文件读取失败: %s", e)
            self._data = {}
            self._loaded = False
            return False

    def write_config(self, config_path: str) -> bool:
        """原子写入 JSON 配置文件（写临时文件 → os.replace）"""
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(
                suffix=".tmp",
                prefix="config_",
                dir=os.path.dirname(config_path)
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(self._data, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, config_path)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
            logger.info("配置文件写入成功: %s", config_path)
            return True
        except (IOError, OSError, PermissionError) as e:
            logger.error("配置文件写入失败: %s", e)
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """通过点号路径获取值，如 'battery.types' → ['Coin Cell', ...]
        空字符串返回完整数据字典。"""
        if not self._loaded:
            return default
        if not key_path:
            return self._data
        keys = key_path.split(".")
        value = self._data
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError, IndexError):
            return default

    def set(self, key_path: str, value: Any) -> bool:
        """通过点号路径设置值"""
        keys = key_path.split(".")
        target = self._data
        try:
            for k in keys[:-1]:
                if k not in target or not isinstance(target[k], dict):
                    target[k] = {}
                target = target[k]
            target[keys[-1]] = value
            return True
        except (TypeError, KeyError) as e:
            logger.error("设置配置值失败: %s", e)
            return False

    def get_all(self) -> Dict[str, Any]:
        """获取完整配置数据"""
        return self._data

    def set_defaults(self, defaults: Dict[str, Any]):
        """用默认数据填充（仅当文件初次创建时调用）"""
        self._data = defaults
        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded

    def clear(self):
        self._data = {}
        self._loaded = False
```

- [ ] **Step 2: Commit**

```bash
git add src/battery_analysis/utils/json_config_manager.py
git commit -m "feat: add JsonConfigManager with atomic JSON read/write"
```

---

### Task 3: 改造 ConfigService — 内部委托改为 JsonConfigManager

**Files:**
- Modify: `src/battery_analysis/main/services/config_service.py`
- Modify: `src/battery_analysis/main/services/config_service_interface.py`

- [ ] **Step 1: 修改接口文档注释（接口签名不变）**

`config_service_interface.py` 的接口签名不变（`get_config_value`, `get_config_value_raw`, 等）。仅更新文档注释反映底层存储已改为 JSON。

- [ ] **Step 2: 改造 ConfigService — 内部使用 JsonConfigManager**

ConfigService 构造函数改为创建 `JsonConfigManager` 替代 `IniFileManager`。

核心变化：
- `load_config()` → 用 `JsonConfigManager.read_config()` 替代 `IniFileManager.read_config()`
- `get_config_value()` → 不再用 INI section/key 格式，用 JSON 点号路径
- `get_config_value_raw()` → 保持返回字符串格式以兼容 ConfigManager（内部将值 JSON 序列化为字符串）
- `save_config()` → 用 `JsonConfigManager.write_config()`
- `clear_cache()` → 简化

```python
# config_service.py 关键改动

def __init__(self):
    BaseService.__init__(self)
    self._config_manager = JsonConfigManager()  # 替换 IniFileManager
    self._config_path = None

def get_config_value(self, key: str, default: Any = None) -> Any:
    """
    获取配置值，key 格式为 JSON 点号路径如 "battery.types"
    """
    try:
        if not self._config_manager.is_loaded():
            self.load_config()
        return self._config_manager.get(key, default)
    except Exception as e:
        self.logger.error("获取配置值失败: %s", e)
        return default

def get_config_value_raw(self, key: str, default: Optional[str] = None) -> Optional[str]:
    """
    获取配置值的原始字符串表示（兼容 ConfigManager 的 get_config）
    """
    try:
        value = self.get_config_value(key, default)
        if isinstance(value, list):
            # 保持旧版兼容：列表转为逗号分隔字符串
            return ", ".join(str(v) for v in value)
        if value is None:
            return None
        return str(value)
    except Exception as e:
        self.logger.error("获取原始配置值失败: %s", e)
        return default

def save_config(self) -> bool:
    try:
        if self._config_path and self._config_manager.is_loaded():
            success = self._config_manager.write_config(str(self._config_path))
            ...
    except Exception as e:
        ...

def load_config(self, config_path: Optional[str] = None, use_cache: bool = True) -> bool:
    """
    从 JSON 文件加载配置。如果文件不存在，从内置默认值创建。
    """
    try:
        if config_path:
            self._config_path = Path(config_path)
        else:
            self._config_path = self._resolve_config_path()

        if not self._config_path or not self._config_path.exists():
            # 首次运行：用默认数据创建
            from battery_analysis.utils.config_defaults import DEFAULT_CONFIG
            self._config_manager.set_defaults(DEFAULT_CONFIG)
            self._config_manager.write_config(str(self._config_path))
            self._loaded = True
            self.logger.info("首次运行，已创建默认配置文件: %s", self._config_path)
            return True

        success = self._config_manager.read_config(str(self._config_path))
        self._loaded = success
        return success
    except Exception as e:
        ...

def _resolve_config_path(self) -> Path:
    """解析配置文件的 %APPDATA% 路径"""
    import os
    appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
    return Path(appdata) / "battery-analysis" / "config.json"

# 删除旧版 find_config_file 方法中的 setting.ini 搜索逻辑
# 简化为直接返回 %APPDATA% 路径
def find_config_file(self, file_name: str = "config.json", use_cache: bool = False) -> Optional[Path]:
    return self._resolve_config_path()
```

- [ ] **Step 3: Commit**

```bash
git add src/battery_analysis/main/services/config_service.py src/battery_analysis/main/services/config_service_interface.py
git commit -m "refactor: switch ConfigService from IniFileManager to JsonConfigManager"
```

---

### Task 4: 改造 ConfigManager — 键映射 + 去掉 INI 方法

**Files:**
- Modify: `src/battery_analysis/main/ui_components/config_manager.py`

- [ ] **Step 1: 添加 INI→JSON 键映射表**

```python
# 在 ConfigManager 类中新增
_INI_TO_JSON_KEY = {
    "BatteryConfig/BatteryType": "battery.types",
    "BatteryConfig/ConstructionMethod": "battery.constructionMethods",
    "BatteryConfig/SpecificationTypeCoinCell": "battery.specifications.Coin Cell",
    "BatteryConfig/SpecificationTypePouchCell": "battery.specifications.Pouch Cell",
    "BatteryConfig/SpecificationMethod": "battery.specificationMethods",
    "BatteryConfig/Manufacturer": "battery.manufacturers",
    "BatteryConfig/Rules": "battery.rules",
    "BatteryConfig/PulseCurrent": "battery.pulseCurrents",
    "BatteryConfig/CutOffVoltage": "battery.cutOffVoltages",
    "TestConfig/TesterLocation": "test.locations",
    "TestConfig/TestedBy": "test.testedBy",
}
```

- [ ] **Step 2: 改造 get_config 方法**

```python
def get_config(self, config_key: str) -> List[str]:
    """
    获取配置值。支持旧版 "Section/Key" 格式（自动映射到 JSON 路径）
    和 JSON 点号路径格式。
    """
    if not self.b_has_config or not self._config_service:
        return []

    try:
        # 尝试键映射
        json_key = self._INI_TO_JSON_KEY.get(config_key, config_key)
        value = self._config_service.get_config_value(json_key)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            # 可能还是旧格式，尝试逗号拆分
            return [v.strip().strip('"') for v in value.split(",") if v.strip()]
        return [str(value)]
    except Exception as e:
        logging.error("读取配置 %s 失败: %s", config_key, e)
        return []
```

- [ ] **Step 3: 清理 ConfigManager 中的 INI 相关方法**

删除或清空以下方法体：
- `save_user_settings()` — 不再需要（原逻辑写入 `user_settings.ini`）
- `rename_pltPath()` — 已为空实现，删除
- `update_config()` — 简化，去掉 INI 写入逻辑（只保留内存中的规则匹配）
- `_parse_list_value()` — 不再需要（基于 JSON 的列表直接返回），可以删除
- `reload_config()` — 简化

删除 `UserSettingsManager` 的依赖和 `user_settings_path` 相关逻辑。

- [ ] **Step 4: 清空 save_user_settings 方法**

```python
def save_user_settings(self):
    """用户偏好已不再持久化，此方法保留为空以兼容调用"""
    pass
```

- [ ] **Step 5: Commit**

```bash
git add src/battery_analysis/main/ui_components/config_manager.py
git commit -m "refactor: ConfigManager uses JSON key mapping, remove user_settings methods"
```

---

### Task 5: 修改 main_window.py — get_config 使用 ConfigService 直接获取

**Files:**
- Modify: `src/battery_analysis/main/main_window.py`

- [ ] **Step 1: 清理 ConfigManager 的 user_settings 调用**

检查 `main_window.py` 中是否有调用 `config_manager.save_user_settings()` 的地方，改为跳过或删除。

搜索 `save_settings` 方法并删除其内容中的 user_settings_manager 调用：

```python
# 找到类似这样的方法并简化
def save_settings(self):
    """保存设置 — 不再持久化 UI 选择状态"""
    self.statusBar_BatteryAnalysis.showMessage("设置已保存")
```

- [ ] **Step 2: 添加 show_config_dialog 方法**

```python
def show_config_dialog(self):
    """打开配置管理对话框"""
    from battery_analysis.main.ui_components.config_dialog import ConfigDialog
    dialog = ConfigDialog(self)
    if dialog.exec() == QW.QDialog.DialogCode.Accepted:
        self.statusBar_BatteryAnalysis.showMessage("配置已保存")
        # 重新加载配置并刷新 UI
        self.config_manager.reload_config()
        self.ui_manager.init_combobox()
```

- [ ] **Step 3: Commit**

```bash
git add src/battery_analysis/main/main_window.py
git commit -m "feat: add show_config_dialog method to MainWindow"
```

---

### Task 6: 修改 .ui 文件 — 添加 actionConfiguration 菜单项

**Files:**
- Modify: `src/battery_analysis/ui/resources/ui_battery_analysis.ui`
- Modify: Regenerate `src/battery_analysis/ui/ui_main_window.py`

- [ ] **Step 1: 在 .ui 文件中添加 action**

在 `<widget class="QMenu" name="menuTools">` 的最后一个 `<addaction name="separator"/>` 后面，添加：

```xml
    <addaction name="separator"/>
    <addaction name="actionConfiguration"/>
   </widget>
```

在 `<action name="actionBatteryChartViewer">` 块之后（其他 action 定义的后面），添加 action 定义：

```xml
  <action name="actionConfiguration">
   <property name="text">
    <string>Configuration</string>
   </property>
  </action>
```

- [ ] **Step 2: 用 pyuic6 重新生成 ui_main_window.py**

```bash
.\.venv\Scripts\pyuic6 .\src\battery_analysis\ui\resources\ui_battery_analysis.ui -o .\src\battery_analysis\ui\ui_main_window.py
```

验证生成的文件包含 `actionConfiguration` 定义和 `menuTools` 中的引用。

- [ ] **Step 3: Commit**

```bash
git add src/battery_analysis/ui/resources/ui_battery_analysis.ui src/battery_analysis/ui/ui_main_window.py
git commit -m "feat: add Configuration action to Tools menu in .ui"
```

---

### Task 7: 连接菜单信号 — menu_manager.py

**Files:**
- Modify: `src/battery_analysis/main/ui_components/menu_manager.py`

- [ ] **Step 1: 在 connect_menu_actions 中添加配置管理入口**

在 `connect_menu_actions()` 方法的 "工具菜单功能连接" 区域之后添加：

```python
# 配置管理连接
if hasattr(self.main_window, 'actionConfiguration'):
    self.main_window.actionConfiguration.triggered.connect(
        self.main_window.show_config_dialog)
```

- [ ] **Step 2: 在 setup_menu_shortcuts 中添加 tooltip**

在工具菜单快捷键和工具提示区域添加：

```python
if hasattr(self.main_window, 'actionConfiguration'):
    self.main_window.actionConfiguration.setToolTip(
        _("tooltip_configuration", "配置管理系统数据字典"))
```

- [ ] **Step 3: Commit**

```bash
git add src/battery_analysis/main/ui_components/menu_manager.py
git commit -m "feat: wire up Configuration action signal in MenuManager"
```

---

### Task 8: 创建 ConfigDialog — 配置管理界面（一次性全量实现）

**Files:**
- Create: `src/battery_analysis/main/ui_components/config_dialog.py`

- [ ] **Step 1: 创建配置管理对话框**

该文件较大，分为三个主要区域：Battery Config、Test Config、Equipment。此处给出左侧分类、右侧编辑器的完整框架。

```python
# src/battery_analysis/main/ui_components/config_dialog.py
"""
配置管理对话框
提供左侧分类列表、右侧编辑器的 UI，用于管理应用的数据字典配置。
"""

import logging
from typing import Any, Dict, List, Optional
from PyQt6 import QtWidgets as QW
from PyQt6 import QtCore as QC
from PyQt6 import QtGui as QG

from battery_analysis.i18n.language_manager import _
from battery_analysis.utils.config_defaults import DEFAULT_CONFIG


class ConfigDialog(QW.QDialog):
    """配置管理主对话框"""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._config_service = main_window._get_service("config")

        # 从 ConfigService 加载当前数据（深拷贝，取消保存才写回）
        import copy
        self._working_data = copy.deepcopy(self._config_service.get_config_value(""))

        self.setWindowTitle(_("config_dialog_title", "Configuration"))
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        """设置对话框布局"""
        layout = QW.QHBoxLayout(self)

        # 左侧分类列表
        self._category_list = QW.QListWidget()
        self._category_list.setMaximumWidth(180)
        self._category_list.addItems([
            _("cat_battery", "Battery Config"),
            _("cat_test", "Test Config"),
            _("cat_equipment", "Equipment"),
        ])
        self._category_list.currentRowChanged.connect(self._on_category_changed)

        # 右侧堆叠面板
        self._stack = QW.QStackedWidget()

        # 三个面板
        self._page_battery = _BatteryConfigPage(self)
        self._page_test = _TestConfigPage(self)
        self._page_equipment = _EquipmentPage(self)

        self._stack.addWidget(self._page_battery)   # index 0
        self._stack.addWidget(self._page_test)       # index 1
        self._stack.addWidget(self._page_equipment)  # index 2

        # 按钮栏
        btn_layout = QW.QHBoxLayout()
        btn_reset = QW.QPushButton(_("reset_defaults", "Reset Defaults"))
        btn_reset.clicked.connect(self._on_reset_defaults)
        btn_save = QW.QPushButton(_("save", "Save"))
        btn_save.clicked.connect(self._on_save)
        btn_cancel = QW.QPushButton(_("cancel", "Cancel"))
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)

        # 主布局
        left_widget = QW.QWidget()
        left_layout = QW.QVBoxLayout(left_widget)
        left_layout.addWidget(self._category_list)
        left_layout.addStretch()

        right_widget = QW.QWidget()
        right_layout = QW.QVBoxLayout(right_widget)
        right_layout.addWidget(self._stack)
        right_layout.addLayout(btn_layout)

        layout.addWidget(left_widget)
        layout.addWidget(right_widget, 1)

    def _on_category_changed(self, index: int):
        """切换左侧分类"""
        self._stack.setCurrentIndex(index)

    def _on_reset_defaults(self):
        """重置为默认值"""
        reply = QW.QMessageBox.question(
            self, _("confirm_reset", "Reset Defaults"),
            _("confirm_reset_msg", "Reset all configuration to default values? This cannot be undone."),
            QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No
        )
        if reply == QW.QMessageBox.StandardButton.Yes:
            import copy
            self._working_data = copy.deepcopy(DEFAULT_CONFIG)
            self._populate_data()

    def _on_save(self):
        """保存配置并关闭"""
        try:
            # 从各页面收集数据
            self._page_battery.collect_data()
            self._page_test.collect_data()
            self._page_equipment.collect_data()

            # 写回 ConfigService
            self._config_service.load_config(use_cache=False)
            # 逐项写入工作数据
            for section_key, value in self._flatten_dict(self._working_data):
                self._config_service.set_config_value(section_key, value)
            self._config_service.save_config()
            self.accept()
        except Exception as e:
            self.logger.error("保存配置失败: %s", e)
            QW.QMessageBox.critical(
                self, _("error", "Error"),
                f"{_('save_failed', 'Failed to save configuration')}: {e}"
            )

    def _populate_data(self):
        """用 _working_data 填充各页面"""
        self._page_battery.load_data(self._working_data.get("battery", {}))
        self._page_test.load_data(self._working_data.get("test", {}))
        self._page_equipment.load_data(self._working_data.get("test", {}).get("equipment", {}))

    @staticmethod
    def _flatten_dict(d: dict, parent_key: str = "") -> list:
        """将嵌套字典展开为 [(key_path, value), ...]"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(ConfigDialog._flatten_dict(v, new_key))
            else:
                items.append((new_key, v))
        return items


class _BatteryConfigPage(QW.QWidget):
    """电池配置编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog
        self._fields: Dict[str, QW.QListWidget] = {}

        layout = QW.QFormLayout(self)

        def _make_list_editor(items: list, layout_item_label: str) -> QW.QListWidget:
            """创建标签列表编辑器：QListWidget + Add/Remove 按钮"""
            group = QW.QGroupBox(layout_item_label)
            vbox = QW.QVBoxLayout(group)
            lw = QW.QListWidget()
            lw.setAlternatingRowColors(True)
            btn_row = QW.QHBoxLayout()
            btn_add = QW.QPushButton("+")
            btn_add.setFixedWidth(30)
            btn_remove = QW.QPushButton("×")
            btn_remove.setFixedWidth(30)
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            btn_row.addStretch()
            vbox.addWidget(lw)
            vbox.addLayout(btn_row)

            btn_add.clicked.connect(lambda: self._add_list_item(lw))
            btn_remove.clicked.connect(lambda: self._remove_list_item(lw))
            return group  # 包装在 QGroupBox 中

        # 电池类型
        self._list_types = _make_list_editor([], "Battery Types")
        layout.addRow(self._list_types)

        # 构造方式
        self._list_construction = _make_list_editor([], "Construction Methods")
        layout.addRow(self._list_construction)

        # 规格型号（按类型分组：Coin Cell / Pouch Cell）
        self._spec_page = QW.QTabWidget()
        self._spec_coin = QW.QListWidget()
        self._spec_pouch = QW.QListWidget()
        self._spec_page.addTab(self._spec_coin, "Coin Cell")
        self._spec_page.addTab(self._spec_pouch, "Pouch Cell")
        spec_group = QW.QGroupBox("Specifications")
        spec_vbox = QW.QVBoxLayout(spec_group)
        spec_vbox.addWidget(self._spec_page)
        spec_btn_row = QW.QHBoxLayout()
        btn_add_spec = QW.QPushButton("+")
        btn_remove_spec = QW.QPushButton("×")
        spec_btn_row.addWidget(btn_add_spec)
        spec_btn_row.addWidget(btn_remove_spec)
        spec_btn_row.addStretch()
        spec_vbox.addLayout(spec_btn_row)
        btn_add_spec.clicked.connect(lambda: self._add_list_item(
            self._spec_page.currentWidget()))
        btn_remove_spec.clicked.connect(lambda: self._remove_list_item(
            self._spec_page.currentWidget()))
        layout.addRow(spec_group)

        # 规格方式
        self._list_spec_method = _make_list_editor([], "Specification Methods")
        layout.addRow(self._list_spec_method)

        # 制造商
        self._list_mfrs = _make_list_editor([], "Manufacturers")
        layout.addRow(self._list_mfrs)

        # Rules（文本框）
        self._text_rules = QW.QPlainTextEdit()
        self._text_rules.setPlaceholderText(
            "One rule per line, format: Type/Method/Capacity/MinCapacity/Required%/Voltage")
        layout.addRow("Rules:", self._text_rules)

        # 脉冲电流
        self._list_pulse = _make_list_editor([], "Pulse Currents")
        layout.addRow(self._list_pulse)

        # 截止电压
        self._list_voltage = _make_list_editor([], "Cut-off Voltages")
        layout.addRow(self._list_voltage)

    def _add_list_item(self, lw):
        """在列表末尾添加可编辑项"""
        item = QW.QListWidgetItem("")
        item.setFlags(item.flags() | QC.Qt.ItemFlag.ItemIsEditable)
        lw.addItem(item)
        lw.editItem(item)

    def _remove_list_item(self, lw):
        """删除选中项"""
        for item in lw.selectedItems():
            lw.takeItem(lw.row(item))

    def load_data(self, data: dict):
        """从数据填充页面"""
        self._fill_list(self._list_types, data.get("types", []))
        self._fill_list(self._list_construction, data.get("constructionMethods", []))
        self._fill_list(self._spec_coin, data.get("specifications", {}).get("Coin Cell", []))
        self._fill_list(self._spec_pouch, data.get("specifications", {}).get("Pouch Cell", []))
        self._fill_list(self._list_spec_method, data.get("specificationMethods", []))
        self._fill_list(self._list_mfrs, data.get("manufacturers", []))
        self._text_rules.setPlainText("\n".join(data.get("rules", [])))
        self._fill_list(self._list_pulse, [str(v) for v in data.get("pulseCurrents", [])])
        self._fill_list(self._list_voltage, [str(v) for v in data.get("cutOffVoltages", [])])

    def _fill_list(self, lw, items: list):
        lw.clear()
        for item in items:
            li = QW.QListWidgetItem(str(item))
            li.setFlags(li.flags() | QC.Qt.ItemFlag.ItemIsEditable)
            lw.addItem(li)

    def _read_list(self, lw) -> list:
        return [lw.item(i).text().strip() for i in range(lw.count()) if lw.item(i).text().strip()]

    def collect_data(self):
        """将页面数据写回 _working_data"""
        battery = self._dialog._working_data.setdefault("battery", {})
        battery["types"] = self._read_list(self._list_types)
        battery["constructionMethods"] = self._read_list(self._list_construction)
        battery["specifications"] = {
            "Coin Cell": self._read_list(self._spec_coin),
            "Pouch Cell": self._read_list(self._spec_pouch),
        }
        battery["specificationMethods"] = self._read_list(self._list_spec_method)
        battery["manufacturers"] = self._read_list(self._list_mfrs)
        battery["rules"] = [r.strip() for r in self._text_rules.toPlainText().split("\n") if r.strip()]
        battery["pulseCurrents"] = [float(v) for v in self._read_list(self._list_pulse)]
        battery["cutOffVoltages"] = [float(v) for v in self._read_list(self._list_voltage)]


class _TestConfigPage(QW.QWidget):
    """测试配置编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog

        layout = QW.QFormLayout(self)
        self._list_locations = self._make_list_widget("Tester Locations")
        self._list_tested_by = self._make_list_widget("Tested By")
        layout.addRow(self._list_locations)
        layout.addRow(self._list_tested_by)

    def _make_list_widget(self, title: str) -> QW.QGroupBox:
        group = QW.QGroupBox(title)
        vbox = QW.QVBoxLayout(group)
        lw = QW.QListWidget()
        lw.setAlternatingRowColors(True)
        btn_row = QW.QHBoxLayout()
        btn_add = QW.QPushButton("+")
        btn_add.setFixedWidth(30)
        btn_remove = QW.QPushButton("×")
        btn_remove.setFixedWidth(30)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch()
        vbox.addWidget(lw)
        vbox.addLayout(btn_row)
        btn_add.clicked.connect(lambda: self._add_item(lw))
        btn_remove.clicked.connect(lambda: self._remove_item(lw))
        return group

    def _add_item(self, lw):
        item = QW.QListWidgetItem("")
        item.setFlags(item.flags() | QC.Qt.ItemFlag.ItemIsEditable)
        lw.addItem(item)
        lw.editItem(item)

    def _remove_item(self, lw):
        for item in lw.selectedItems():
            lw.takeItem(lw.row(item))

    def _fill_list(self, lw, items: list):
        lw.clear()
        for item in items:
            li = QW.QListWidgetItem(str(item))
            li.setFlags(li.flags() | QC.Qt.ItemFlag.ItemIsEditable)
            lw.addItem(li)

    def _read_list(self, obj) -> list:
        """从 QGroupBox 或直接 QListWidget 读取"""
        if isinstance(obj, QW.QGroupBox):
            lw = obj.findChild(QW.QListWidget)
            if lw:
                return [lw.item(i).text().strip() for i in range(lw.count()) if lw.item(i).text().strip()]
        return []

    def load_data(self, data: dict):
        self._fill_list(self._list_locations.findChild(QW.QListWidget), data.get("locations", []))
        self._fill_list(self._list_tested_by.findChild(QW.QListWidget), data.get("testedBy", []))

    def collect_data(self):
        test = self._dialog._working_data.setdefault("test", {})
        test["locations"] = self._read_list(self._list_locations)
        test["testedBy"] = self._read_list(self._list_tested_by)


class _EquipmentPage(QW.QWidget):
    """设备信息编辑页面"""

    def __init__(self, parent_dialog):
        super().__init__()
        self._dialog = parent_dialog
        self._data: Dict[str, dict] = {}

        layout = QW.QVBoxLayout(self)

        # 表格
        self._table = QW.QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Location", "Test Equipment", "Model"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QW.QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.doubleClicked.connect(self._on_edit_row)

        btn_row = QW.QHBoxLayout()
        btn_add = QW.QPushButton("+ Add Location")
        btn_remove = QW.QPushButton("× Remove")
        btn_edit = QW.QPushButton("Edit")
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_remove)
        btn_row.addWidget(btn_edit)
        btn_row.addStretch()

        btn_add.clicked.connect(self._on_add_location)
        btn_remove.clicked.connect(self._on_remove_location)
        btn_edit.clicked.connect(self._on_edit_selected)

        layout.addWidget(self._table)
        layout.addLayout(btn_row)

    def load_data(self, data: dict):
        self._data = data
        self._refresh_table()

    def _refresh_table(self):
        self._table.setRowCount(0)
        for loc_key, info in self._data.items():
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QW.QTableWidgetItem(loc_key))
            self._table.setItem(row, 1, QW.QTableWidgetItem(
                info.get("testEquipment", "")))
            self._table.setItem(row, 2, QW.QTableWidgetItem(
                info.get("testUnits", {}).get("model", "")))

    def _on_edit_row(self, index):
        self._edit_location(index.row())

    def _on_edit_selected(self):
        rows = self._table.selectionModel().selectedRows()
        if rows:
            self._edit_location(rows[0].row())

    def _edit_location(self, row: int):
        loc_key = self._table.item(row, 0).text()
        info = self._data.get(loc_key, {})
        dialog = _EquipmentEditDialog(loc_key, info, self)
        if dialog.exec():
            new_key, new_info = dialog.get_data()
            if new_key != loc_key:
                del self._data[loc_key]
            self._data[new_key] = new_info
            self._refresh_table()

    def _on_add_location(self):
        dialog = _EquipmentEditDialog("", {}, self)
        if dialog.exec():
            key, info = dialog.get_data()
            if key and key not in self._data:
                self._data[key] = info
                self._refresh_table()

    def _on_remove_location(self):
        rows = self._table.selectionModel().selectedRows()
        for index in sorted(rows, reverse=True):
            loc_key = self._table.item(index.row(), 0).text()
            self._data.pop(loc_key, None)
        self._refresh_table()

    def collect_data(self):
        self._dialog._working_data.setdefault("test", {})["equipment"] = self._data


class _EquipmentEditDialog(QW.QDialog):
    """设备信息编辑对话框"""

    def __init__(self, loc_key: str, data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Equipment Info" if loc_key else "Add Equipment Info")
        self.setMinimumWidth(500)

        layout = QW.QVBoxLayout(self)

        form = QW.QFormLayout()

        self._edit_key = QW.QLineEdit(loc_key)
        form.addRow("Location Key:", self._edit_key)

        self._edit_equipment = QW.QLineEdit(data.get("testEquipment", ""))
        form.addRow("Test Equipment:", self._edit_equipment)

        # Software Versions
        sv = data.get("softwareVersions", {})
        self._edit_sv_server = QW.QLineEdit(sv.get("btsServer", ""))
        self._edit_sv_client = QW.QLineEdit(sv.get("btsClient", ""))
        self._edit_sv_da = QW.QLineEdit(sv.get("btsda", ""))
        form.addRow("BTS Server:", self._edit_sv_server)
        form.addRow("BTS Client:", self._edit_sv_client)
        form.addRow("BTSDA:", self._edit_sv_da)

        # Middle Machines
        mm = data.get("middleMachines", {})
        self._edit_mm_model = QW.QLineEdit(mm.get("model", ""))
        self._edit_mm_hw = QW.QLineEdit(mm.get("hardwareVersion", ""))
        self._edit_mm_sn = QW.QLineEdit(mm.get("serialNumber", ""))
        self._edit_mm_fw = QW.QLineEdit(mm.get("firmwareVersion", ""))
        self._edit_mm_dt = QW.QLineEdit(mm.get("deviceType", ""))
        form.addRow("MM Model:", self._edit_mm_model)
        form.addRow("MM HW Ver:", self._edit_mm_hw)
        form.addRow("MM S/N:", self._edit_mm_sn)
        form.addRow("MM FW Ver:", self._edit_mm_fw)
        form.addRow("MM Device Type:", self._edit_mm_dt)

        # Test Units
        tu = data.get("testUnits", {})
        self._edit_tu_model = QW.QLineEdit(tu.get("model", ""))
        self._edit_tu_hw = QW.QLineEdit(tu.get("hardwareVersion", ""))
        self._edit_tu_fw = QW.QLineEdit(tu.get("firmwareVersion", ""))
        form.addRow("TU Model:", self._edit_tu_model)
        form.addRow("TU HW Ver:", self._edit_tu_hw)
        form.addRow("TU FW Ver:", self._edit_tu_fw)

        layout.addLayout(form)

        btn_layout = QW.QHBoxLayout()
        btn_ok = QW.QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QW.QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_data(self) -> tuple:
        key = self._edit_key.text().strip()
        info = {
            "testEquipment": self._edit_equipment.text().strip(),
            "softwareVersions": {
                "btsServer": self._edit_sv_server.text().strip(),
                "btsClient": self._edit_sv_client.text().strip(),
                "btsda": self._edit_sv_da.text().strip(),
            },
            "middleMachines": {
                "model": self._edit_mm_model.text().strip(),
                "hardwareVersion": self._edit_mm_hw.text().strip(),
                "serialNumber": self._edit_mm_sn.text().strip(),
                "firmwareVersion": self._edit_mm_fw.text().strip(),
                "deviceType": self._edit_mm_dt.text().strip(),
            },
            "testUnits": {
                "model": self._edit_tu_model.text().strip(),
                "hardwareVersion": self._edit_tu_hw.text().strip(),
                "firmwareVersion": self._edit_tu_fw.text().strip(),
            },
        }
        return key, info
```

- [ ] **Step 2: Commit**

```bash
git add src/battery_analysis/main/ui_components/config_dialog.py
git commit -m "feat: add ConfigDialog with battery/test/equipment management UI"
```

---

### Task 9: 修复 data_loader.py 的 ConfigParser 直接依赖

**Files:**
- Modify: `src/battery_analysis/main/visualization/data_loader.py`

- [ ] **Step 1: 替换 ConfigParser 为 ConfigService 调用**

`data_loader.py` 中的 `DataLoaderMixin` 直接使用 `configparser.ConfigParser` 读取 setting.ini。需要改为通过 ConfigService 获取 Rules。

```python
# _read_rules_configuration 方法改造前：
def _read_rules_configuration(self):
    try:
        if (self.config.has_section("BatteryConfig")
                and self.config.has_option("BatteryConfig", "Rules")):
            listRules = self.config.get("BatteryConfig", "Rules").split(",")
            self._process_rules(listRules)
    except configparser.Error as e:
        logger.error(...)

# 改造后：
def _read_rules_configuration(self):
    try:
        from battery_analysis.main.services.config_service import ConfigService
        service = ConfigService()
        service.load_config()
        listRules = service.get_config_value("battery.rules", [])
        self._process_rules(listRules)
    except Exception as e:
        logger.warning("读取Rules配置出错: %s，使用默认maxXaxis", e)
```

同时清理 `_load_config_file` 方法中的 ConfigParser 逻辑——如果不再需要可以直接删除或简化。

- [ ] **Step 2: Commit**

```bash
git add src/battery_analysis/main/visualization/data_loader.py
git commit -m "fix: replace direct ConfigParser usage with ConfigService in DataLoaderMixin"
```

---

### Task 10: 删除 user_settings_manager.py 和旧 INI 依赖

**Files:**
- Delete: `src/battery_analysis/main/user_settings_manager.py`
- Modify: `src/battery_analysis/main/ui_components/config_manager.py`（去掉 UserSettingsManager 引用）

- [ ] **Step 1: 删除 user_settings_manager.py**

```bash
git rm src/battery_analysis/main/user_settings_manager.py
```

- [ ] **Step 2: 清理 config_manager.py 中对 UserSettingsManager 的引用**

去掉 import、初始化、以及所有相关调用。

- [ ] **Step 3: 清理 ui_manager.py 中 load_user_settings 的调用**

在 `ui_manager.py` 中，找到并删除调用 `load_user_settings()` 和设置用户偏好的代码段（`init_combobox` 方法末尾以及 `_connect_signals` 中的加载逻辑）。

```python
# 删掉类似这样的内容（在 init_combobox 末尾）：
if self.main_window.config_manager.user_settings_manager:
    user_config = self.main_window.config_manager.user_settings_manager.load_user_settings()
    if user_config:
        # ... 恢复 combobox 选中项等
```

这些选择持久化已经被设计移除，启动时 combobox 全部无选中。

- [ ] **Step 4: Commit**

```bash
git rm src/battery_analysis/main/user_settings_manager.py
git add src/battery_analysis/main/ui_components/config_manager.py
git add src/battery_analysis/main/ui_components/ui_manager.py
git commit -m "refactor: remove user_settings_manager and all user preference persistence"
```

---

### Task 11: 修改 build.py — 去掉外部配置文件依赖

**Files:**
- Modify: `scripts/build.py`

- [ ] **Step 1: 去掉 `--add-data config`**

在 `_build_pyinstaller_args` 方法中，找到 `'--add-data', f'{self.project_root / "config"};config'` 这一行并删除。

- [ ] **Step 2: 去掉 INI 创建逻辑**

在 `move_programs` 方法中，删除从 `project_root / "config" / "setting.ini"` 读取内容、修改 PltConfig、写回 `build_dir / "setting.ini"` 的全部代码块。

- [ ] **Step 3: Commit**

```bash
git add scripts/build.py
git commit -m "build: remove external config dependency, config now managed via %APPDATA%"
```

---

### Task 12: 验证测试

- [ ] **Step 1: 运行应用，验证首次启动自动创建 config.json**

```bash
# 确保没有旧配置文件干扰
rm -f "$APPDATA/battery-analysis/config.json"
uv run python -m src.battery_analysis.main.main_window
```

验证：
- 应用正常启动，无报错
- `%APPDATA%/battery-analysis/config.json` 已创建
- 所有 combobox 正常填充

- [ ] **Step 2: 验证配置管理 UI**

- Tools → Configuration 打开配置对话框
- 修改 Battery Config 中的电池类型、规格等
- 点 Save
- 重启应用，验证修改已生效

- [ ] **Step 3: 验证 Release 打包**

```bash
python -m scripts.build Release
```

验证：
- 打包成功
- 生成的 exe 目录 **没有** `setting.ini`
- exe 可正常运行（首次运行自动创建 config.json）

- [ ] **Step 4: 最终 commit**

```bash
git add -A
git commit -m "chore: final cleanup after config migration"
```
