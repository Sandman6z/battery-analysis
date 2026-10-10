# GLM (Round 2): 基于测试标准的务实重评估：配置按电池类型自动切换的可执行方案


# GLM Round 2：基于测试标准的务实重评估

## 一、先认错：Round 1 我低估了问题

Round 1 我说"核心流程够用，最值得做的是加诊断可见性"。这话在**没有测试标准**的前提下是合理的——如果所有电池都用同一套脉冲配置，确实只需要修修边界、加加日志。

但用户提供了 BatteryQualityRequirements_v2.3 之后，情况变了。**这不是"边界处理"的问题，是"基础配置假设错了"的问题。**

| 维度 | Round 1 的假设 | 测试标准的现实 |
|------|--------------|--------------|
| 脉冲电流 | 全局 `[30,26,15,6]` mA | 4种电池类型，电流从 6mA 到 500mA 跨两个数量级 |
| 脉冲等级数 | 固定 4 级 | 4级/6级/7级不等 |
| 截止电压 | 全局 `[2.6,2.5,...,1.8]` | 不同电池类型有不同电压集合，且 2.6V 和 2.1V 在标准中**不存在** |
| 脉冲持续时间 | 代码完全没用 | 标准中明确要求（1s/2s/5s），是重要的诊断维度 |

**核心问题**：当前代码用一套配置处理所有电池类型，但标准定义了**至少 4 种不同的脉冲方案**。

---

## 二、务实评估：哪些改进是真正值得做的？

### 不值得做的（DeepSeek 和 MiniMax 的部分提案）

| 提案 | 为什么不做 |
|------|-----------|
| 聚类自适应脉冲发现（MiniMax 提案 A）| 过度设计。标准已经定义了精确的脉冲参数，不需要"猜"。聚类算法引入不确定性、调试难度、依赖。**用查表替代算法是工程正道。** |
| 策略模式重构 | 只有 4 种配置，一个 dict 查表就够了。策略模式要写 4 个类 + 工厂 + 注册表，这是用 8 分钟解决 2 分钟的问题。 |
| 事件溯源/调试时间线 | 好主意，但 ROI 太低。先把配置搞对，再考虑花哨的调试工具。 |
| 自适应容差（MiniMax 提案 C）| 当前 ±5% 在所有电池类型下都适用，标准没有对不同电池类型指定不同容差。别修没坏的东西。 |

### 值得做的（按 ROI 排序）

#### 改进 1（P0）：脉冲配置按电池类型自动切换

**这是本轮最关键的改进。**

现状：`config_defaults.py` 硬编码 `[30,26,15,6]` 和 `[2.6,2.5,...,1.8]`，所有电池共用。

方案：**查表映射**。利用现有 `battery_classifier.classify_spec()` 和规格名做精确匹配。

```python
# 新增：pulse_config_registry.py（或直接放在 config_defaults.py 里）

from dataclasses import dataclass

@dataclass(frozen=True)
class PulseConfig:
    currents: tuple[float, ...]     # 脉冲电流等级 (mA)
    cut_off_voltages: tuple[float, ...]  # 截止电压 (V)
    pulse_durations: tuple[int, ...]     # 每级持续时间 (s)，来自标准
    pause_durations: tuple[int, ...]     # 每级暂停时间 (s)，来自标准

# 精确匹配优先，然后按容量区间兜底
PULSE_REGISTRY: dict[str, PulseConfig] = {
    # --- CR2450 系列（Coin Cell）---
    "CR2450": PulseConfig(
        currents=(30, 26, 15, 6),
        cut_off_voltages=(2.4, 2.3, 2.25, 2.2, 2.0, 1.8),
        pulse_durations=(1, 1, 2, 5),
        pause_durations=(59, 59, 58, 55),
    ),
    "CR2450D": ...,  # 同 CR2450
    "CR2450HE1": ...,
    "CR2450HE4": ...,
    
    # --- Pouch Cell 按容量分档 ---
    # 用 "Pouch_<1200" / "Pouch_2000-3000" / "Pouch_>=3000" 作为 key
    # 具体规格名查不到时，用 capacity 匹配这些区间
}

def get_pulse_config(spec_name: str, capacity_mah: int) -> PulseConfig:
    """根据规格名和容量返回对应的脉冲配置"""
    # 精确匹配
    if spec_name in PULSE_REGISTRY:
        return PULSE_REGISTRY[spec_name]
    # 按容量兜底（Pouch Cell）
    if capacity_mah < 1200:
        return PULSE_REGISTRY["Pouch_<1200"]
    elif capacity_mah < 3000:
        return PULSE_REGISTRY["Pouch_2000-3000"]
    else:
        return PULSE_REGISTRY["Pouch_>=3000"]
```

**为什么这个方案务实：**
- 不改架构，只是把硬编码的 list 换成查表
- `battery_classifier.py` 已经能从规则字符串提取 `spec_name` 和 `capacity`（`extract_spec_name()`、`extract_capacity()`）
- UI 层已有 `comboBox_SpecificationType` 和容量输入框，数据已经存在
- 向后兼容：用户手动编辑 pulseCurrents 时仍然优先使用用户配置

#### 改进 2（P0）：修正 cutOffVoltages 默认值

当前默认值包含 `2.6V` 和 `2.1V`，这两个值在测试标准中**不存在**。

**务实做法**：
- 标准中只有 CR2450 和小容量 Pouch 共用同一套电压：`(2.4, 2.3, 2.25, 2.2, 2.0, 1.8)`
- 大容量 Pouch 增加 `2.5V`
- 最大容量 Pouch 还增加 `2.5V`（同上）

所以 `2.6V` 和 `2.1V` 应该从默认值中**删除**。如果用户有特殊需求，可以在配置对话框中手动添加。

**风险评估**：如果现有用户已经依赖 2.6V/2.1V 的存在（比如他们的测试协议确实包含这些电压），删除会影响分析。**建议**：只修改新安装的默认值，不修改已存在的 config.json。

#### 改进 3（P1）：filename_parser 扩展——提取电池型号

当前 `extract_pulse_current` 只提取电流值，不提取电池型号。但文件名通常包含型号信息：

- `CR2450(30-26-15-6mA,2000mAh)` → 型号 = `CR2450`
- `CP305050(150-100-60-30mA,2000mAh)` → 型号 = `CP305050`
- `CF583083(500-250-100-60-30-15-6mA,4000mAh)` → 型号 = `CF583083`

**方案**：在 `filename_parser.py` 中新增 `extract_battery_model()`：

```python
def extract_battery_model(filename: str) -> str:
    """从文件名提取电池型号（括号前的部分）"""
    match = re.match(r"^([A-Za-z0-9]+)\(", filename)
    return match.group(1) if match else ""
```

然后用 `battery_classifier.classify_spec(model, capacity)` 判断类型，再查 `PULSE_REGISTRY`。

**成本**：10 行代码。**收益**：文件名解析 → 电池类型 → 脉冲配置，全链路自动化。

#### 改进 4（P1）：pulse_durations 写入输出

标准中每个脉冲等级有不同持续时间（1s/2s/5s）。当前代码完全忽略了这个维度。

**务实做法**：
- 先把 `pulse_durations` 存入 `PulseConfig`，随配置传递
- 在 `Info_Plot.json` 中输出 `pulse_durations` 字段
- **暂不做**脉冲波形分析、持续时间校验——那是 Round 3 的事

#### 改进 5（Round 1 遗留，仍然值得做）：诊断可见性

Round 1 的提案仍然成立：
- `detect_pulse_rows` 返回空时记录 unique step values
- 异常消息包含诊断信息
- 步骤名常量化

但优先级要让位给 P0（配置自动切换）。

---

## 三、执行路径（务实版）

### 第一阶段：配置查表（1-2天）
1. 创建 `PulseConfig` dataclass 和 `PULSE_REGISTRY` 查表
2. 修改 `config_defaults.py`：按电池类型提供不同默认值
3. 修改 `BatteryConfigInitializationStep`：根据当前选中的规格类型和容量，调用 `get_pulse_config()` 设置 `listCurrentLevel` 和 `listVoltageLevel`
4. **兼容性**：如果 config.json 中用户已手动设置了 pulseCurrents，优先使用用户配置

### 第二阶段：文件名自动识别（0.5天）
5. `filename_parser.extract_battery_model()` 提取型号
6. 在 `data_processor.py` 中：提取型号 → 查表 → 自动填充 pulseCurrents/cutOffVoltages
7. 在 UI 中显示"已自动匹配为 XXX 配置"的提示

### 第三阶段：诊断可见性（0.5天）
8. Round 1 的诊断改进（日志 + 异常消息 + 常量化）
9. 在 Info_Plot.json 中输出 pulse_durations

### 不做
- ❌ 聚类算法
- ❌ 策略模式
- ❌ 自适应容差
- ❌ 脉冲波形分析
- ❌ listTestInfo 重构为 dataclass（改动面太大，排技术债）

---

## 四、风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| 用户已有 config.json 中的配置与新默认值冲突 | 只改新安装默认值；已有 config 不动 |
| 文件名不含型号信息（用户改了名） | fallback 到 UI 下拉框选择的规格类型 |
| 标准更新导致 PULSE_REGISTRY 过期 | 把 PULSE_REGISTRY 放在配置文件而非代码中，方便非开发人员更新 |
| 7 级脉冲（≥3000mAh Pouch）导致数据结构变化 | 现有嵌套列表 `[c][v]` 天然支持任意级数，无需改结构 |

---

## 五、一句话总结

**Round 1 我说"加诊断就够了"，现在我修正：配置按电池类型自动切换是 P0，诊断可见性是 P1。实现方式是查表映射，不是策略模式也不是聚类算法——用最简单的方式解决最根本的问题。**
