# Borderless UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove all visible borders from UI components, change background to warm beige `#f5f0e8`, and unify component styling with background-color + rounded corners.

**Architecture:** The UI styling is managed through a 3-layer system: (1) global QSS file (`battery_analyzer.qss`) as the base, (2) inline `setStyleSheet()` calls in `ui_main_window.py` that override QSS, (3) programmatic style application via `StyleManager` and `ThemeManager`. The plan strips layer 2 (inline overrides) and rewrites layer 1 (QSS) with borderless warm-beige styling. Theme color variables in `style_manager.py` and fallback styles in `theme_manager.py` are updated to match.

**Tech Stack:** PyQt6, QSS, Python

**Spec:** `docs/superpowers/specs/2026-05-15-borderless-ui-design.md`

---

### Task 1: Rewrite `battery_analyzer.qss` with borderless warm-beige palette

**Files:**
- Modify: `src/battery_analysis/ui/styles/battery_analyzer.qss`

- [ ] **Step 1: Update color palette — replace all `#f8f9fa`, `#ffffff`, `#e9ecef`, `#495057`, `#212529` with new warm-beige equivalents**

The new palette:

| Role | Old Color | New Color | Applies to |
|---|---|---|---|
| Main background | `#f8f9fa` | `#f5f0e8` | QMainWindow, QWidget |
| Card/surface | `#ffffff` | `#faf7f2` | QGroupBox, card backgrounds |
| Input background | `#ffffff` | `#ede9e3` | QLineEdit, QComboBox, QSpinBox |
| Input hover | — | `#e5e0d8` | hover state |
| Input focus | — | `#ffffff` (+ `2px #27ae60` border) | focus state |
| Border/divider | `#e9ecef` | `#e0d8cc` | dividers, table gridlines |
| Primary text | `#212529` | `#3d3229` | body text |
| Secondary text | `#495057` | `#8a7a6a` | labels, secondary info |
| Accent green | `#27ae60` | `#27ae60` (keep) | title underline, focus border |

- [ ] **Step 2: Remove all `border` declarations from QFrame, QGroupBox, QLineEdit, QComboBox, QSpinBox, QTableWidget, QPushButton (base)**

Replace:

```css
/* Old - QFrame with border */
QFrame {
    border: 1px solid #e9ecef;
    border-radius: 4px;
    background-color: #f8f9fa;
}
```

With:

```css
/* New - QFrame borderless */
QFrame {
    border: none;
    background-color: transparent;
}
```

- [ ] **Step 3: Rewrite QGroupBox to borderless with title underline**

Replace:

```css
QGroupBox {
    font-weight: bold;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 6px;
    background-color: #f8f9fa;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px 0 8px;
    color: #495057;
    background-color: #ffffff;
}
```

With:

```css
QGroupBox {
    border: none;
    border-radius: 0;
    margin-top: 12px;
    padding: 0;
    font-weight: 600;
    font-size: 12px;
    background-color: transparent;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 0;
    padding: 0 0 8px 0;
    color: #3d3229;
    border-bottom: 2px solid #27ae60;
    background-color: transparent;
}
```

- [ ] **Step 4: Rewrite QLineEdit to borderless with warm input background**

Replace:

```css
QLineEdit {
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 5px 8px;
    background-color: #ffffff;
    color: #495057;
    font-size: 11px;
}

QLineEdit:focus {
    border-color: #3498db;
    outline: none;
    background-color: #ffffff;
}

QLineEdit:hover {
    border-color: #adb5bd;
}
```

With:

```css
QLineEdit {
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #ede9e3;
    color: #3d3229;
    font-size: 11px;
}

QLineEdit:hover {
    background-color: #e5e0d8;
}

QLineEdit:focus {
    border: 2px solid #27ae60;
    background-color: #ffffff;
    padding: 6px 10px;  /* account for 2px border */
}
```

- [ ] **Step 5: Rewrite QComboBox to borderless + custom dropdown arrow**

Replace:

```css
QComboBox {
    border: 1px solid #e9ecef;
    border-radius: 3px;
    padding: 4px 8px;
    background-color: #ffffff;
    color: #495057;
    min-width: 80px;
}
```

With:

```css
QComboBox {
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #ede9e3;
    color: #3d3229;
    min-width: 80px;
}

QComboBox:hover {
    background-color: #e5e0d8;
}

QComboBox:focus {
    border: 2px solid #27ae60;
    background-color: #ffffff;
    padding: 6px 10px;
}

QComboBox::drop-down {
    border: none;
    background: transparent;
    width: 24px;
}

QComboBox::down-arrow {
    image: url(:/icons/chevron-down.svg);
    width: 12px;
    height: 12px;
}

QComboBox::down-arrow:on {
    image: url(:/icons/chevron-up.svg);
}
```

- [ ] **Step 6: Rewrite QSpinBox to borderless**

Replace:

```css
QSpinBox {
    border: 1px solid #e9ecef;
    border-radius: 3px;
    padding: 3px 20px 3px 5px;
    background-color: #ffffff;
    color: #495057;
    font-size: 11px;
    height: 22px;
    width: 80px;
}
```

With:

```css
QSpinBox {
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #ede9e3;
    color: #3d3229;
    font-size: 11px;
}

QSpinBox:hover {
    background-color: #e5e0d8;
}

QSpinBox:focus {
    border: 2px solid #27ae60;
    background-color: #ffffff;
    padding: 6px 10px;
}
```

- [ ] **Step 7: Rewrite QTableWidget — remove outer border, keep gridlines**

Replace:

```css
QTableWidget {
    border: 1px solid #e9ecef;
    border-radius: 4px;
    background-color: #f8f9fa;
    gridline-color: #e9ecef;
}
```

With:

```css
QTableWidget {
    border: none;
    border-radius: 8px;
    background-color: transparent;
    gridline-color: #e0d8cc;
}
```

- [ ] **Step 8: Update QPushButton base — remove border, keep rounded corners for default state**

Replace:

```css
QPushButton {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 3px;
    padding: 4px 10px;
    color: #495057;
    font-weight: 500;
    font-size: 10px;
    min-width: 50px;
    min-height: 22px;
}
```

With:

```css
QPushButton {
    background-color: #ede9e3;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    color: #3d3229;
    font-weight: 500;
    font-size: 11px;
}
```

- [ ] **Step 9: Update styled push buttons (gradient buttons) — increase border-radius to 8px**

For all `QPushButton[button-type="*"]`, `QPushButton[data-action="*"]`, `#pushButton_Run`:
- Set `border-radius: 8px` (keep existing gradient colors)
- Keep existing `border-color` declarations for visual structure

- [ ] **Step 10: Remove duplicate style blocks, clean up QSS file**

The QSS file has duplicate blocks for `QLineEdit`, `QPushButton`, `QTabBar`, `QStatusBar`, `QToolBar`. Remove duplicates — keep only the last instance of each selector block.

- [x] **Step 11: Verify syntax — no unbalanced braces or invalid QSS**

Self-review note: All braces balanced, all selectors valid QSS syntax.

---

### Task 2: Remove inline setStyleSheet overrides from `ui_main_window.py`

**Files:**
- Modify: `src/battery_analysis/ui/ui_main_window.py` (WARNING: generated file, changes lost on pyuic6 regeneration)

**Remove the following `setStyleSheet()` calls** — their styling is now handled by the QSS file:

| Line | Widget | What to do |
|---|---|---|
| 85-116 | `comboBox_Temperature` | Remove entire setStyleSheet call |
| 178 | `spinBox_AcceleratedAging` | Keep empty-string setStyleSheet (no-op, harmless) |
| 229+ | `comboBox_Manufacturer` | Remove entire setStyleSheet call |
| 289+ | `lineEdit_BatchDateCode` | Remove entire setStyleSheet call |
| 325+ | `lineEdit_SamplesQty` | Remove entire setStyleSheet call |
| 385+ | `comboBox_BatteryType` | Remove entire setStyleSheet call |
| 451+ | `comboBox_ConstructionMethod` | Remove entire setStyleSheet call |
| 524+ | `comboBox_Specification_Method` | Remove entire setStyleSheet call |
| 573+ | `comboBox_Specification_Type` | Remove entire setStyleSheet call |
| 647+ | `lineEdit_RequiredUseableCapacity` | Remove entire setStyleSheet call |
| 683+ | `lineEdit_CalculationNominalCapacity` | Remove entire setStyleSheet call |
| 718+ | `lineEdit_DatasheetNominalCapacity` | Remove entire setStyleSheet call |
| 745+ | `groupBox_TestConfig` | Remove entire setStyleSheet call |
| 788+ | `lineEdit_TestProfile` | Remove entire setStyleSheet call |
| 852+ | `comboBox_TesterLocation` | Remove entire setStyleSheet call |
| 923+ | `comboBox_TestedBy` | Remove entire setStyleSheet call |
| 1002+ | `lineEdit_InputPath` | Remove entire setStyleSheet call |
| 1058+ | `lineEdit_OutputPath` | Remove entire setStyleSheet call |
| 1086+ | `groupBox_TestInformation` | Remove entire setStyleSheet call |
| 1233+ | `pushButton_Run` | **KEEP** — special gradient button styling |
| 1306+ | `lineEdit_Version` | Remove entire setStyleSheet call |
| 1347+ | `comboBox_ReportedBy` | Remove entire setStyleSheet call |

- [ ] **Step 1: Remove all QComboBox green-border inline stylesheets**

For each of: `comboBox_Temperature`, `comboBox_Manufacturer`, `comboBox_BatteryType`, `comboBox_ConstructionMethod`, `comboBox_Specification_Method`, `comboBox_Specification_Type`, `comboBox_TesterLocation`, `comboBox_TestedBy`, `comboBox_ReportedBy` — remove the `setStyleSheet("""...""")` call entirely.

- [ ] **Step 2: Remove all QLineEdit green-border inline stylesheets**

For each of: `lineEdit_BatchDateCode`, `lineEdit_SamplesQty`, `lineEdit_RequiredUseableCapacity`, `lineEdit_CalculationNominalCapacity`, `lineEdit_DatasheetNominalCapacity`, `lineEdit_TestProfile`, `lineEdit_InputPath`, `lineEdit_OutputPath`, `lineEdit_Version` — remove the `setStyleSheet("""...""")` call entirely.

- [ ] **Step 3: Remove QGroupBox inline stylesheets**

For `groupBox_TestConfig` (line 745) and `groupBox_TestInformation` (line 1086) — remove the `setStyleSheet()` call.

- [ ] **Step 4: Verify `pushButton_Run` style is preserved**

Confirm `pushButton_Run.setStyleSheet(...)` at line 1233 is still present with its gradient styling.

---

### Task 3: Remove white-background overrides from `window_setup.py`

**Files:**
- Modify: `src/battery_analysis/main/ui_components/window_setup.py`

- [ ] **Step 1: Remove entire `init_widgetcolor()` method body** (lines 107-147)

The method sets `background-color: #ffffff` on 26 QLineEdit widgets. Since the new QSS handles input backgrounds, these inline overrides are unnecessary and would conflict.

Replace with a no-op or remove the method and its call site:

```python
def init_widgetcolor(self) -> None:
    """初始化部件颜色 — no longer needed, handled by QSS"""
    pass
```

- [ ] **Step 2: Find and verify the call site**

Search `main_window.py` or `launcher.py` for `init_widgetcolor()` call and verify it won't error (no-op method is fine).

---

### Task 4: Update style_manager.py theme variables

**Files:**
- Modify: `src/battery_analysis/ui/styles/style_manager.py`

- [ ] **Step 1: Update `get_style_variables()` method — update color values for all themes**

New modern theme defaults:

```python
"modern": {
    "primary_color": "#27ae60",
    "secondary_color": "#27ae60",
    "warning_color": "#f39c12",
    "error_color": "#e74c3c",
    "background_color": "#f5f0e8",
    "surface_color": "#faf7f2",
    "text_color": "#3d3229",
    "border_color": "#e0d8cc"
}
```

- [ ] **Step 2: Update dark theme color replacement map in `_load_available_styles()`** (lines 64-69)

The dark theme replaces old colors with dark equivalents. Update replacements:

```python
# Old replacements (for old pale palette):
dark_style = dark_style.replace("#f8f9fa", "#2c3e50")  # background
dark_style = dark_style.replace("#ffffff", "#34495e")  # surface
dark_style = dark_style.replace("#212529", "#ecf0f1")  # text
dark_style = dark_style.replace("#495057", "#bdc3c7")  # secondary text
dark_style = dark_style.replace("#e9ecef", "#4a5f7a")  # border

# New replacements (for warm beige palette):
dark_style = dark_style.replace("#f5f0e8", "#2c3e50")  # background
dark_style = dark_style.replace("#faf7f2", "#34495e")  # surface
dark_style = dark_style.replace("#ede9e3", "#3a4a5e")  # input background
dark_style = dark_style.replace("#e5e0d8", "#405060")  # input hover
dark_style = dark_style.replace("#3d3229", "#ecf0f1")  # text
dark_style = dark_style.replace("#8a7a6a", "#bdc3c7")  # secondary text
dark_style = dark_style.replace("#e0d8cc", "#4a5f7a")  # divider/border
```

- [ ] **Step 3: Update high_contrast, blue, green theme replacement maps** (lines 81-106)

```python
# High contrast (old colors → new warm beige palette equivalents):
high_contrast_style = high_contrast_style.replace("#f5f0e8", "#ffffff")
high_contrast_style = high_contrast_style.replace("#faf7f2", "#ffffff")
high_contrast_style = high_contrast_style.replace("#ede9e3", "#ffffff")
high_contrast_style = high_contrast_style.replace("#3d3229", "#000000")
high_contrast_style = high_contrast_style.replace("#e0d8cc", "#000000")
high_contrast_style = high_contrast_style.replace("#27ae60", "#0000ff")

# Blue theme:
blue_style = blue_style.replace("#f5f0e8", "#e3f2fd")
blue_style = blue_style.replace("#faf7f2", "#ffffff")
blue_style = blue_style.replace("#ede9e3", "#e8eaf6")
blue_style = blue_style.replace("#3d3229", "#1565c0")
blue_style = blue_style.replace("#8a7a6a", "#2196f3")
blue_style = blue_style.replace("#e0d8cc", "#bbdefb")

# Green theme:
green_style = green_style.replace("#f5f0e8", "#e8f5e8")
green_style = green_style.replace("#faf7f2", "#ffffff")
green_style = green_style.replace("#ede9e3", "#e0f0e0")
green_style = green_style.replace("#3d3229", "#2e7d32")
green_style = green_style.replace("#8a7a6a", "#43a047")
green_style = green_style.replace("#e0d8cc", "#c8e6c9")
```

---

### Task 5: Update theme_manager.py fallback dark stylesheet

**Files:**
- Modify: `src/battery_analysis/main/ui_components/theme_manager.py`

- [ ] **Step 1: Update dark fallback stylesheet in `set_theme()`** (lines 131-169)

The fallback is only used when `style_manager.apply_global_style()` fails. Update to borderless style:

```python
dark_stylesheet = """QWidget {
    background-color: #2b2b2b;
    color: #cccccc;
}
QMenuBar {
    background-color: #2b2b2b;
    color: #cccccc;
}
QMenu {
    background-color: #3a3a3a;
    color: #cccccc;
}
QMenu::item:selected {
    background-color: #555555;
}
QPushButton {
    background-color: #4a4a4a;
    border: none;
    border-radius: 8px;
    color: #cccccc;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #555555;
}
QLineEdit, QComboBox, QTextEdit, QSpinBox {
    background-color: #3a3a3a;
    border: none;
    border-radius: 8px;
    color: #cccccc;
    padding: 8px 12px;
}
QTableWidget {
    background-color: #3a3a3a;
    color: #cccccc;
    alternate-background-color: #4a4a4a;
    border: none;
}
QHeaderView::section {
    background-color: #4a4a4a;
    color: #cccccc;
}
QGroupBox {
    border: none;
    color: #cccccc;
}
QGroupBox::title {
    color: #cccccc;
    border-bottom: 2px solid #27ae60;
    padding-bottom: 8px;
}
QFrame {
    border: none;
    background: transparent;
}
"""
```

---

### Task 6: Verify and validate

- [ ] **Step 1: Run the application to verify the UI loads without errors**

Run: `python src/battery_analysis/main/launcher.py` (or appropriate entry point)

Check: No exceptions on startup, main window renders with warm beige background.

- [ ] **Step 2: Visual check — verify all component types have borderless styling**

Check each: QLineEdit, QComboBox, QSpinBox, QGroupBox, QFrame, QPushButton, QTableWidget — none should have visible borders.

- [ ] **Step 3: Verify error validation styling still works**

The validation_manager sets red error styles (`background-color: #FFDDDD; border: 1px solid #FF6666;`) via inline setStyleSheet. This should still work since inline styles override QSS. Manually trigger validation errors to confirm.

- [ ] **Step 4: Test theme switching**

Switch to Dark Theme, verify colors adapt correctly.

- [x] **Step 5: Commit**

```bash
git add src/battery_analysis/ui/styles/battery_analyzer.qss
git add src/battery_analysis/ui/ui_main_window.py
git add src/battery_analysis/main/ui_components/window_setup.py
git add src/battery_analysis/ui/styles/style_manager.py
git add src/battery_analysis/main/ui_components/theme_manager.py
git add docs/superpowers/specs/2026-05-15-borderless-ui-design.md
git commit -m "feat: borderless UI with warm beige palette

Remove all component borders, replace with background-color + rounded corners.
Change main background to warm beige #f5f0e8 for eye comfort.
Remove inline style overrides from ui_main_window.py.
Update style_manager theme variables and dark theme fallback.
"
```
