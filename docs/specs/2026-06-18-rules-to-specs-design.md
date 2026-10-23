---
name: Rules-Driven Specifications Redesign
description: 将 battery rules 改为行级可编辑列表，使其成为规格型号的数据源，specifications 变为自动生成的只读展示
---

# Rules-Driven Specifications Redesign

## 背景

当前 tools-configuration 中存在数据冗余问题：
- `battery.rules` 中已包含各电池型号的完整参数（容量、方法、电压等）
- `battery.specifications` 独立维护两个列表（Coin Cell / Pouch Cell），与 rules 内容重复
- 新增电池需同时修改两处，容易不一致

## 改动目标

1. **Rules 输入改为行级列表**（类似 Manufacturers 的 QListWidget + +/- 按钮），替代大文本框
2. **Specifications 改为从 Rules 自动解析生成**，只读展示，移除编辑按钮
3. **判定规则**：型号名前缀 `CR` → Coin Cell；`CP/CF` 开头 → Pouch Cell；容量值作为辅助校验

## 实现方案

### 判定逻辑

```
def classify_spec(model_name: str, capacity: int) -> str:
    if model_name.startswith("CR"):
        return "Coin Cell"
    elif model_name.startswith(("CP", "CF")):
        return "Pouch Cell"
    # 兜底：按容量阈值
    return "Pouch Cell" if capacity >= 800 else "Coin Cell"
```

新增电池时只需在 rules 中添加一行，软件自动归类到对应 specification 列表。

### UI 改动

| 组件 | 原实现 | 新实现 |
|------|--------|--------|
| **Rules** | `QPlainTextEdit` 大文本框 | `QGroupBox` + `QListWidget` + +/- 按钮（与 Manufacturers 一致） |
| **Specifications** | `QListWidget` + +/- 编辑按钮 | 移除 +/- 按钮，设置 `flags` 为不可编辑 |

### 数据层改动

- **config_schema.py**：`BatterySchema.specifications` 保持 `Dict[str, List[str]]` 类型但改为 `field(default_factory=dict)`，走 rules 派生
- **config_defaults.py**：移除 `specifications` 字段，启动迁移时自动派生
- **config_dialog.py** `collect_data()`：保存时自动从 rules 计算 specifications 并写入 `_working_data`

### 影响评估

| 消费者 | 影响 | 说明 |
|--------|------|------|
| `validation_manager.py` | 无 | 已从 rules 解析容量 |
| `config_manager.py` | 无 | 仍通过 `BatteryConfig/Rules` 读取 rules |
| `config_manager.py` INI 映射 | 无 | `SpecificationTypeCoinCell` 等 INI 键仍会写入（由派生数据填充） |
| `filename_parser.py` | 无 | 读取 comboBox_Specification_Type 列表，自动派生不受影响 |
| `data_processor.py` | 无 | 同上 |

## 文件改动清单

1. `src/battery_analysis/main/ui_components/config_dialog.py` — 核心改动
2. `src/battery_analysis/utils/config_defaults.py` — 清理 specs 默认值
3. `src/battery_analysis/utils/config_schema.py` — specs 可空

## 未改动

- 配置文件的 JSON 读/写路径不变（key 仍然是 `battery.specifications`）
- ConfigService 层无需修改
- 业务逻辑层（validation_manager, config_manager, etc.）无需修改
