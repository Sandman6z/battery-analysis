# Rules-Driven Specifications Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 battery rules 从大文本框改为行级列表（类似 manufacturers），并使 specifications 自动从 rules 派生且只读

**Architecture:** 修改 ConfigDialog._BatteryConfigPage 的 UI 组件，添加分类判定函数，在 load_data/collect_data 中自动转换 rules ↔ specifications。保存时 rules 作为唯一数据源，specifications 由其派生。

**Tech Stack:** Python, PyQt6, QListWidget, QGroupBox

---

### Task 1: 添加电池型号分类工具函数

**Files:**
- Create: `src/battery_analysis/utils/battery_classifier.py`
- Modify: `src/battery_analysis/utils/config_defaults.py`

- [ ] **Step 1: 创建电池分类模块**

```python
"""电池型号分类工具——根据型号名和容量判断电池类型"""

DEFAULT_CAPACITY_THRESHOLD = 800  # mAh，低于此值为 Coin Cell


def classify_spec(model_name: str, capacity: int = 0) -> str:
    """根据规格型号名和容量判定电池类型

    判定规则：
    1. CR 开头 → Coin Cell
    2. CP 或 CF 开头 → Pouch Cell
    3. 兜底：容量 >= threshold → Pouch Cell，否则 Coin Cell
    """
    upper = model_name.strip().upper()
    if upper.startswith("CR"):
        return "Coin Cell"
    if upper.startswith(("CP", "CF")):
        return "Pouch Cell"
    return "Pouch Cell" if capacity >= DEFAULT_CAPACITY_THRESHOLD else "Coin Cell"


def extract_spec_name(rule: str) -> str:
    """从规则字符串中提取规格型号名
    
    rule 格式: Model/SpecMethod/Capacity/...
    返回 rule_parts[0]
    """
    parts = rule.split("/")
    return parts[0].strip() if parts else ""


def extract_capacity(rule: str) -> int:
    """从规则字符串中提取容量（rule_parts[2]）"""
    parts = rule.split("/")
    if len(parts) >= 3:
        try:
            return int(parts[2])
        except ValueError:
            return 0
    return 0


def derive_specifications(rules: list) -> dict:
    """从 rules 列表自动派生 specifications 字典
    
    返回: {"Coin Cell": [...], "Pouch Cell": [...]}
    """
    specs: dict = {"Coin Cell": [], "Pouch Cell": []}
    seen: set = set()
    for rule in rules:
        spec_name = extract_spec_name(rule)
        if not spec_name or spec_name in seen:
            continue
        seen.add(spec_name)
        capacity = extract_capacity(rule)
        cell_type = classify_spec(spec_name, capacity)
        specs[cell_type].append(spec_name)
    return specs
```

- [ ] **Step 2: 写测试验证分类逻辑**

Create: `tests/battery_analysis/utils/test_battery_classifier.py`

```python
"""测试电池分类工具"""

import pytest
from battery_analysis.utils.battery_classifier import (
    classify_spec,
    extract_spec_name,
    extract_capacity,
    derive_specifications,
    DEFAULT_CAPACITY_THRESHOLD,
)


class TestClassifySpec:
    def test_cr_prefix_is_coin_cell(self):
        assert classify_spec("CR2450", 600) == "Coin Cell"

    def test_cr_without_capacity_is_coin_cell(self):
        assert classify_spec("CR2450") == "Coin Cell"

    def test_cp_prefix_is_pouch_cell(self):
        assert classify_spec("CP224642A", 920) == "Pouch Cell"

    def test_cf_prefix_is_pouch_cell(self):
        assert classify_spec("CF583083", 4000) == "Pouch Cell"

    def test_lower_case_input(self):
        assert classify_spec("cr2450", 600) == "Coin Cell"
        assert classify_spec("cp305050", 2000) == "Pouch Cell"

    def test_fallback_by_capacity_above_threshold(self):
        name = "XYZ9999"  # 无 CR/CP/CF 前缀
        assert classify_spec(name, DEFAULT_CAPACITY_THRESHOLD + 1) == "Pouch Cell"

    def test_fallback_by_capacity_below_threshold(self):
        name = "XYZ100"
        assert classify_spec(name, DEFAULT_CAPACITY_THRESHOLD - 1) == "Coin Cell"

    def test_fallback_zero_capacity_coin(self):
        assert classify_spec("UNKNOWN", 0) == "Coin Cell"


class TestExtractSpecName:
    def test_first_part_of_rule(self):
        assert extract_spec_name("CR2450/1S1P/600/550/380/1.0") == "CR2450"

    def test_empty_string(self):
        assert extract_spec_name("") == ""

    def test_single_part(self):
        assert extract_spec_name("CR2450") == "CR2450"


class TestExtractCapacity:
    def test_third_part_of_rule(self):
        assert extract_capacity("CR2450/1S1P/600/550/380/1.0") == 600

    def test_not_a_number(self):
        assert extract_capacity("CR2450/1S1P/abc/550/380/1.0") == 0

    def test_too_few_parts(self):
        assert extract_capacity("CR2450/1S1P") == 0


class TestDeriveSpecifications:
    def test_mixed_rules(self):
        rules = [
            "CR2450/1S1P/600/550/380/1.0",
            "CR2450D/1S1P/600/550/280/1.0",
            "CP224642A/1S1P/920/920/80%/5.0",
            "CF583083/1S1P/4000/4000/80%/5.0",
            "CP305050/1S1P/2000/2000/80%/1.0",
        ]
        result = derive_specifications(rules)
        assert "CR2450" in result["Coin Cell"]
        assert "CR2450D" in result["Coin Cell"]
        assert "CP224642A" in result["Pouch Cell"]
        assert "CF583083" in result["Pouch Cell"]
        assert "CP305050" in result["Pouch Cell"]

    def test_duplicate_specs_are_deduplicated(self):
        rules = [
            "CR2450/1S1P/600/550/380/1.0",
            "CR2450/1S2P/600/550/380/1.0",
        ]
        result = derive_specifications(rules)
        assert result["Coin Cell"].count("CR2450") == 1

    def test_empty_rules(self):
        assert derive_specifications([]) == {"Coin Cell": [], "Pouch Cell": []}
```

- [ ] **Step 3: 运行测试确保通过**

```bash
cd /c/Users/boe/Documents/EwinDT/battery-analysis
python -m pytest tests/battery_analysis/utils/test_battery_classifier.py -v
```
Expected: 所有测试通过

- [ ] **Step 4: 提交**

```bash
git add src/battery_analysis/utils/battery_classifier.py tests/battery_analysis/utils/test_battery_classifier.py
git commit -m "feat: add battery classifier utility for spec→type deduction"
```

---

### Task 2: 修改 ConfigDialog — Rules 改为行级列表，Specs 改为自动派生只读

**Files:**
- Modify: `src/battery_analysis/main/ui_components/config_dialog.py`

- [ ] **Step 1: 在 _BatteryConfigPage 顶部添加分类工具导入**

```python
from battery_analysis.utils.battery_classifier import derive_specifications, classify_spec, extract_spec_name, extract_capacity
```
插入位置在现有 import 块末尾（第15行后）。

- [ ] **Step 2: 替换 Specifications 区域 — 移除编辑按钮，设为只读**

找到第 137-161 行（specifications 的 tab widget 和按钮部分），替换为：

```python
        # 规格型号（从 Rules 自动派生，只读展示）
        self._spec_page = QW.QTabWidget()
        self._spec_coin = QW.QListWidget()
        self._spec_coin.setMinimumHeight(130)
        self._spec_coin.setSelectionMode(QW.QAbstractItemView.SelectionMode.NoSelection)
        self._spec_pouch = QW.QListWidget()
        self._spec_pouch.setMinimumHeight(130)
        self._spec_pouch.setSelectionMode(QW.QAbstractItemView.SelectionMode.NoSelection)
        self._spec_page.addTab(self._spec_coin, "Coin Cell")
        self._spec_page.addTab(self._spec_pouch, "Pouch Cell")
        self._spec_page.setMinimumHeight(180)
        spec_group = QW.QGroupBox("Specifications")
        spec_vbox = QW.QVBoxLayout(spec_group)
        spec_vbox.addWidget(self._spec_page)
        # 无 +/- 按钮 — 只读展示
        layout.addRow(spec_group)
```

- [ ] **Step 3: 替换 Rules 文本框为 QListWidget（类似 Manufacturers）**

找到第 172-177 行（Rules 的 QPlainTextEdit），替换为：

```python
        # Rules（行级列表，和 Manufacturers 一致）
        self._list_rules = self._make_list_group("Rules")
        layout.addRow(self._list_rules)
```

- [ ] **Step 4: 修改 load_data — specs 从 rules 自动派生**

找到 `load_data` 方法，将 specs 填充改为：

```python
    def load_data(self, data: dict):
        """从数据填充页面"""
        self._fill_list(self._list_types, data.get("types", []))
        self._fill_list(self._list_construction, data.get("constructionMethods", []))
        # Specifications 从 Rules 自动派生（只读展示）
        rules = data.get("rules", [])
        self._fill_rules_list(self._list_rules, rules)
        self._refresh_specs_from_rules(rules)
        self._fill_list(self._list_spec_method, data.get("specificationMethods", []))
        self._fill_list(self._list_mfrs, data.get("manufacturers", []))
        self._fill_list(self._list_pulse, [str(v) for v in data.get("pulseCurrents", [])])
        self._fill_list(self._list_voltage, [str(v) for v in data.get("cutOffVoltages", [])])
```

同时添加辅助方法：

```python
    def _fill_rules_list(self, group_or_lw, items: list):
        """填充 Rules 列表（规则项通常较长，方便阅读）"""
        lw = group_or_lw if isinstance(group_or_lw, QW.QListWidget) else group_or_lw.findChild(QW.QListWidget)
        if lw is None:
            return
        lw.clear()
        for item in items:
            li = QW.QListWidgetItem(str(item))
            li.setFlags(li.flags() | QC.Qt.ItemFlag.ItemIsEditable)
            lw.addItem(li)

    def _refresh_specs_from_rules(self, rules: list):
        """从 rules 重新计算 specifications 并刷新只读列表"""
        self._spec_coin.clear()
        self._spec_pouch.clear()
        specs = derive_specifications(rules)
        for spec in specs.get("Coin Cell", []):
            item = QW.QListWidgetItem(spec)
            item.setFlags(item.flags() & ~QC.Qt.ItemFlag.ItemIsEditable)
            self._spec_coin.addItem(item)
        for spec in specs.get("Pouch Cell", []):
            item = QW.QListWidgetItem(spec)
            item.setFlags(item.flags() & ~QC.Qt.ItemFlag.ItemIsEditable)
            self._spec_pouch.addItem(item)
```

- [ ] **Step 5: Rules 的 add/remove 按钮联动 spec 刷新**

需要 hook rules 列表的变更事件，在添加/删除规则后自动刷新 specs。修改 `__init__` 中对 rules 列表的初始化：

在电池页面 `__init__` 中，创建 rules 列表后连接信号。添加一个方法来处理变更。

找到 `_make_list_group` 的使用点，在 rules 列表创建后添加信号连接。

在 `__init__` 中找到：
```python
        # Rules（行级列表，和 Manufacturers 一致）
        self._list_rules = self._make_list_group("Rules")
        layout.addRow(self._list_rules)
```

后面追加：
```python
        # Rules 变更时自动刷新 Specifications
        rules_list = self._list_rules.findChild(QW.QListWidget)
        if rules_list:
            rules_list.model().rowsInserted.connect(self._on_rules_changed)
            rules_list.model().rowsRemoved.connect(self._on_rules_changed)
            rules_list.model().dataChanged.connect(self._on_rules_changed)
```

```python
    def _on_rules_changed(self):
        """Rules 列表发生变更时重新生成 Specifications"""
        rules = self._read_list(self._list_rules)
        self._refresh_specs_from_rules(rules)
```

- [ ] **Step 6: 修改 collect_data — specs 从 rules 派生**

```python
    def collect_data(self):
        """将页面数据写回 _working_data"""
        battery = self._dialog._working_data.setdefault("battery", {})
        battery["types"] = self._read_list(self._list_types)
        battery["constructionMethods"] = self._read_list(self._list_construction)
        # Specifications 从 Rules 自动派生，不直接从 UI 读取
        rules = self._read_list(self._list_rules)
        battery["specifications"] = derive_specifications(rules)
        battery["specificationMethods"] = self._read_list(self._list_spec_method)
        battery["manufacturers"] = self._read_list(self._list_mfrs)
        battery["rules"] = rules
        battery["pulseCurrents"] = self._parse_float_list(self._read_list(self._list_pulse))
        battery["cutOffVoltages"] = self._parse_float_list(self._read_list(self._list_voltage))
```

- [ ] **Step 7: 提交**

```bash
git add src/battery_analysis/main/ui_components/config_dialog.py
git commit -m "refactor: rules as list widget, specs auto-derived and read-only"
```

---

### Task 3: 更新 config_defaults.py — 清理 specs 默认值

**Files:**
- Modify: `src/battery_analysis/utils/config_defaults.py`

- [ ] **Step 1: 移除硬编码的 specifications 列表**

在 `DEFAULT_CONFIG["battery"]` 中找到：
```python
        "specifications": {
            "Coin Cell": ["CR2450", "CR2450YP", "CR2450PH", "CR2450D", "CR2450HE1", "CR2450HE4"],
            "Pouch Cell": ["CP224642A", "CF583083", "CP305050"]
        },
```
替换为：
```python
        "specifications": {},  # 从 rules 自动派生，启动时填充
```

- [ ] **Step 2: 同步更新 rules 默认数据**

确保 rules 默认数据是最新的（CP305050 容量改为 2000）—— 当前已经是 20，需要改成 2000：

```python
        "rules": [
            "CR2450/1S1P/600/550/380/1.0",
            "CR2450D/1S1P/600/550/280/1.0",
            "CR2450HE1/1S1P/600/550/380/1.0",
            "CR2450HE4/1S1P/600/550/280/1.0",
            "CP224642A/1S1P/920/920/80%/5.0",
            "CF583083/1S1P/4000/4000/80%/5.0",
            "CP305050/1S1P/2000/2000/80%/1.0",
        ],
```

- [ ] **Step 3: 提交**

```bash
git add src/battery_analysis/utils/config_defaults.py
git commit -m "refactor: remove hardcoded specs defaults, fix CP305050 capacity to 2000"
```

---

### Task 4: 更新 config_schema.py — specifications 可空

**Files:**
- Modify: `src/battery_analysis/utils/config_schema.py`

- [ ] **Step 1: 将 specifications 默认值改为空 dict**

在 `BatterySchema` 中找到：
```python
    specifications: Dict[str, List[str]] = field(default_factory=dict)
```
已经是正确的（当前代码就是这个）。确认不需要改动。

- [ ] **Step 2: 检查是否有验证 warnings 需要调整**

`BatterySchema` 目前没有对 specifications 的非空验证，所以此文件无需修改。

- [ ] **Step 3: 跳过——无需修改此文件**

---

### Task 5: 完整集成自测

- [ ] **Step 1: 运行所有已有测试确保没有回归**

```bash
cd /c/Users/boe/Documents/EwinDT/battery-analysis
python -m pytest tests/ -v 2>&1 | head -100
```
Expected: 所有已有测试通过（新分类器测试也在内）

- [ ] **Step 2: 手动检查代码逻辑闭环**

检查场景：
1. 加载旧配置（有 specs 数据）→ rules 优先，specs 被覆盖
2. 加载新配置（specs 为空）→ 从 rules 自动生成
3. 添加新 rule → specs 自动刷新
4. 删除 rule → specs 自动移除对应型号
5. 编辑 rule 中的型号名 → specs 刷新
6. 保存时 specs 跟随 rules 派生

- [ ] **Step 3: 最终提交**

```bash
git add -A
git commit -m "feat: complete rules-driven specifications redesign"
```
