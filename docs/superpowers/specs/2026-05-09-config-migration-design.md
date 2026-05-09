# 配置系统重构：INI 迁移为 JSON + UI 内置管理

## 概述

移除 `setting.ini` 和 `user_settings.ini` 两个外部配置文件，改为 JSON 文件 + 应用内置 UI 管理的配置系统。文件存储在 `%APPDATA%/battery-analysis/config.json`，运行时在内存中操作。

## 设计原则

1. **配置即数据**：配置项是应用的数据字典，不是用户该手动编辑的文件
2. **UI 即入口**：所有配置修改通过应用界面完成
3. **零外部依赖**：打包后的 exe 不再需要附带 `setting.ini`
4. **向下不兼容**：旧 INI 文件不迁移，保留不动供用户手动删除

## 数据模型

将两个 INI 文件合并为一个 JSON，去掉运行时状态和 UI 偏好：

```jsonc
{
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
    "testers": [
      "Hall", "Guoying Qi", "Zhaoxuan Zheng", "Xiaoe Wang",
      "Rachel Zhao", "Sandman Zhang", "Maiyue Zhang",
      "Howard Lin", "Kate Zhu", "Sy Tran", "Stefan"
    ],
    "equipment": {
      "BOEDT.Qual": {
        "testEquipment": "NEWARE Battery Testing System CT-4008Q",
        "softwareVersions": {
          "btsServer": "BTS Server(R3)-8.0.0.323 (2023.05.31)",
          "btsClient": "BTS Client 8.0.0.516(2023.05.31)",
          "btsda": "BTSDA 8.0.0.502(2023.05.31)"
        },
        "middleMachines": {
          "model": "CT-ZWJ-4'S-T-1U",
          "hardwareVersion": "B01-BTS-ZWJ-4.36T",
          "serialNumber": "T2302-370530",
          "firmwareVersion": "4S_2.15.6.0_20220517_095718",
          "deviceType": "BTS82"
        },
        "testUnits": {
          "model": "CT-4008Q-5V100mA-HWX, CT-4008Q-5V6A-S1",
          "hardwareVersion": "B01-BTS-XWJ-M-7.B.19QSn",
          "firmwareVersion": "M04310100_220818_094651_FD4F1"
        }
      },
      // BOEDT.QA / PDI.Qual / BOECQ.QA / LibaM1.QA / JabilVN.QA / VGFernitz.HWE
      // 全量数据见现有 setting.ini [TestInformation.*] 段，结构同上
    }
  },
  "window": {
    "width": 1200,
    "height": 800,
    "maximized": true
  }
}
```

### 变化对照

| 原 INI | 新 JSON | 说明 |
|--------|---------|------|
| `BatteryConfig` | `battery` | 结构调整，`SpecificationType*` 合并为 `specifications` 对象 |
| `TestConfig` | `test` | `TesterLocation`/`TestedBy` 改为数组 |
| `TestInformation.*` | `test.equipment` | 6 个地点统一 schema |
| `PltConfig` | 移除 | Path/Title 不再持久化 |
| `user_settings.ini` | 移除 | 窗口大小记住(唯一真正有用的偏好) |
| — | `window` | 新增，记录窗口状态 |

## 存储

- **路径**：`%APPDATA%/battery-analysis/config.json`
- **写入策略**：写临时文件 → `os.replace()` 原子替换原文件（防止崩溃丢数据）
- **启动逻辑**：
  1. 检查文件是否存在
  2. 不存在 → 从内置默认值创建
  3. 存在 → 读取到内存，校验 schema
  4. 整个会话期间操作内存
  5. 用户点"保存"才写回文件

## 配置管理 UI

新增对话框，入口位于菜单 **Tools → Configuration**。

### 入口修改

- **`ui_battery_analysis.ui`**：`menuTools` 的 separator 后加 `actionConfiguration`
- **`ui_main_window.py`**：`pyuic6` 重新生成
- **`menu_manager.py`**：`actionConfiguration.triggered.connect` 到主窗口
- **`main_window.py`**：新增 `show_config_dialog` 方法

### 对话框布局

左侧三个分类，右侧当前分类的编辑器：

1. **Battery Config** — 电池类型、构造方式、规格型号(按类型分组)、规格方式、制造商、Rules(文本框)、脉冲电流、截止电压
2. **Test Config** — 测试地点、测试人员列表
3. **Equipment** — 6 个地点设备参数的表格 + 编辑对话框，可增删

底部按钮：**Reset Defaults** / **Save** / **Cancel**

### 设备信息编辑

表格列出所有地点，点某一行弹出详细编辑对话框包含 TestEquipment、SoftwareVersions、MiddleMachines、TestUnits 四组字段。

## 代码改造

### 新增文件
- `utils/json_config_manager.py` — `JsonConfigManager` 类
- `utils/config_defaults.py` — 内置默认数据
- `ui_components/config_dialog.py` — 配置管理对话框

### 修改文件
- `services/config_service.py` — 内部改为委托 `JsonConfigManager`
- `services/config_service_interface.py` — 接口不变
- `ui_components/config_manager.py` — 去掉 INI 相关方法
- `ui_components/menu_manager.py` — 连接 actionConfiguration 信号
- `main/main_window.py` — 新增 `show_config_dialog`
- `ui/resources/ui_battery_analysis.ui` — 新增 actionConfiguration

### 删除文件
- `user_settings_manager.py`（功能由 JSON 替代）

### 构建修改
- `scripts/build.py`：去掉 `--add-data config`，去掉 `setting.ini` 生成逻辑，设置 `%APPDATA%` 路径

## 不兼容说明

- 旧 `config/setting.ini` 文件不再读取，保留不动
- 首次运行自动创建 `%APPDATA%/battery-analysis/config.json`（含全量默认数据）
- 旧文件用户手动删除即可

## 实施顺序

1. **阶段 1 — 存储层**：`json_config_manager.py` + `config_defaults.py`，改 `config_service.py`
2. **阶段 2 — UI 配置管理**：`.ui` → `pyuic6`，`config_dialog.py`，菜单入口
3. **阶段 3 — 清理**：删旧文件方法，改 `build.py`
4. **阶段 4 — 验证**：首次运行、CRUD、打包测试

## 体积影响

- 引入 `json`（stdlib）：**0 KB**
- 移除 INI 文件 + PyInstaller `--add-data`：**约 -0.5 KB**（实际无意义）
- 净效果：exe 体积不变
