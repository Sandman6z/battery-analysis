# User (Feedback after Round 1): 提供了 BatteryQualityRequirements_v2.3 测试标准 PDF，代码逻辑应基于此标准。

# 测试标准关键信息（BatteryQualityRequirements_v2.3）

## 不同电池类型的脉冲电流配置

### CR2450 (Standard/Freezer) — 4级脉冲
| Pulse Current | 持续时间 | Pause |
|---|---|---|
| 30mA | 1s | 59s |
| 26mA | 1s | 59s |
| 15mA | 2s | 58s |
| 6mA | 5s | 55s |
- Cut-Off Voltages: 2.4V, 2.3V, 2.25V, 2.2V, 2.0V, 1.8V

### Generic Pouch QNOM < 1200mAh — 4级脉冲
同 CR2450 配置

### Generic Pouch 2000mAh ≤ QNOM < 3000mAh — 4级脉冲
| Pulse Current | 持续时间 | Pause |
|---|---|---|
| 150mA | 1s | 59s |
| 100mA | 1s | 59s |
| 60mA | 1s | 59s |
| 30mA | 1s | 59s |
- Cut-Off Voltages: 2.5V, 2.4V, 2.3V, 2.25V, 2.2V, 2.0V, 1.8V

### Generic Pouch QNOM ≥ 3000mAh — 7级脉冲
| Pulse Current | 持续时间 | Pause |
|---|---|---|
| 500mA | 1s | 59s |
| 250mA | 1s | 59s |
| 100mA | 1s | 59s |
| 60mA | 1s | 59s |
| 30mA | 1s | 59s |
| 15mA | 2s | 58s |
| 6mA | 5s | 55s |
- Cut-Off Voltages: 2.5V, 2.4V, 2.3V, 2.25V, 2.2V, 2.0V, 1.8V

### CP305050 / CF583083 等 — 6级脉冲
| Pulse Current | 持续时间 | Pause |
|---|---|---|
| 100mA | 1s | 59s |
| 60mA | 1s | 59s |
| 30mA | 1s | 59s |
| 15mA | 2s | 58s |
| 6mA | 5s | 55s |

## 测试流程结构
1. **Pre-Discharge**: 0mAh（部分场景有预放电）
2. **Constant Current Load Period**: 恒流放电（如1mA for 10h = 10mAh）
3. **Recovery Period**: 10min
4. **Nr. of Pulse Bursts**: 10次脉冲簇
5. 每个Pulse Burst包含所有脉冲等级，从高到低依次施加

## 统计要求
- 每个 (pulse current, cut-off voltage) 组合记录 usable capacity
- 计算: Mean µ, Median, Std σ, µ±2σ, µ±3σ, Min, Max
- **µ - 2σ 必须高于指定的 usable capacity 要求**（约96%正态分布达标）

## 当前代码配置对比
- config_defaults.py: `pulseCurrents: [30.0, 26.0, 15.0, 6.0]` — 仅覆盖 CR2450/小容量
- config_defaults.py: `cutOffVoltages: [2.6, 2.5, 2.4, 2.3, 2.25, 2.2, 2.1, 2.0, 1.8]` — 包含标准中不存在的 2.6V 和 2.1V
- 大容量 pouch 需要 7 级脉冲，当前配置只支持 4 级
