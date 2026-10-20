# DeepSeek (Round 1): NDAX→xlsx 为忠实转换；XML 与实测电流存在根本矛盾（-30/-26 vs -60/-30），且分析工具从文件名提取电流而非数据验证，导致 26mA 容量计算可能为零——构成数据正确性风险。

# DeepSeek (Round 1): 三者关系深度取证与分析工具影响评估

## 一、取证结果：三者数据流关系

### 1.1 文件格式确认

**NDAX 文件**（16 个）：ZIP 压缩包，内部包含：

```
NDAX (ZIP)
├── EditStep.xml    — 压缩/编码的工步定义（含 PulseData 脉冲参数）
├── Step.xml        — 压缩/编码的工步数据
├── TestInfo.xml    — 测试元信息（PN、日期等）
├── VersionInfo.xml — 软件版本
└── data.ndc        — 二进制测量数据（电流/电压/时间序列）
```

**xlsx 文件**（16 个）：由 `src/battery_analysis/ndax/converter.py` 从 NDAX 转换生成，忠实转换，不做数据修正。

**XML Profile**（1 个）：BTS 测试软件的输入配置文件，定义测试步骤参数。

### 1.2 数据流链路

```
XML Profile (测试计划/声明)
       ↓ 加载到
Neware BTS Client → 执行测试
       ↓ 产生
NDAX data.ndc (设备实测记录)
       ↓ NewareNDA 库解析
xlsx (转换输出，C 列=电流(A)）
       ↓ 分析工具读取
battery-analysis 软件（输出报告/图表）
```

**核心结论**：xlsx 是 NDAX 的忠实转换结果，NDAX 是设备实测记录，XML 是测试计划。三者中 **NDAX/xlsx 是实测证据链，XML 是计划/声明**。

---

## 二、脉冲电流一致性：根本性矛盾

### 2.1 XML Profile 声明值

```xml
<PulseData Cycle_Count="10" Count="8">
  <Pulse1 Value="0"   Time="59000" />  <!-- 静置 59s -->
  <Pulse2 Value="-30" Time="1000" />   <!-- 30mA，1s -->
  <Pulse3 Value="0"   Time="59000" />  <!-- 静置 59s -->
  <Pulse4 Value="-26" Time="1000" />   <!-- 26mA，1s -->
  <Pulse5 Value="0"   Time="58000" />  <!-- 静置 58s -->
  <Pulse6 Value="-15" Time="2000" />   <!-- 15mA，2s -->
  <Pulse7 Value="0"   Time="55000" />  <!-- 静置 55s -->
  <Pulse8 Value="-6"  Time="5000" />   <!-- 6mA，5s -->
</PulseData>
```

声明电流：**30 / 26 / 15 / 6 mA**（正值=放电方向，XML 用负值表示）

### 2.2 xlsx 实测数据（已确认）

- 实际电流直方图：**-60 / -30 / -15 / -6 mA**
- **无 26mA 脉冲**
- 脉冲数比例 860:860:1720:4300 = **1:1:2:5**
- 对应脉冲宽度：**1s / 1s / 2s / 5s** ✅ 与 XML 一致

### 2.3 矛盾对照表

| 维度 | XML 声明 | xlsx/NDAX 实测 | 是否一致 |
|---|---|---|---|
| 最大脉冲电流 | -30 mA | **-60 mA** | ❌ |
| 第二脉冲电流 | -26 mA | **-30 mA**（非 -26） | ❌ |
| 第三脉冲电流 | -15 mA | -15 mA | ✅ |
| 最小脉冲电流 | -6 mA | -6 mA | ✅ |
| 脉冲宽度 | 1/1/2/5 s | 1/1/2/5 s | ✅ |
| 循环次数 | 10 | 10 | ✅ |
| PN | CP224642A | — | — |
| 日期 | 20240927 | 20260917（文件名） | ❌ |

### 2.4 XML Profile 是旧模板

XML 多处与文件名/实际数据不符：
- **PN**：CP224642A（文件名显示 CF224642T）
- **日期**：20240927（文件名 260917 即 20260917）
- **CC 容量**：Remark 写 "CC 20mAh 2mA"，文件名写 "CC 10mAh 2mA"
- **脉冲电流**：声明 30/26/15/6，实测 60/30/15/6

---

## 三、分析工具影响评估（MiniMax 未涉及的关键发现）

### 3.1 脉冲电流来源：来自文件名，非数据验证

**`src/battery_analysis/main/business_logic/filename_parser.py:49`**：

```python
def extract_pulse_current(filename):
    pulse_current_matches = re.findall(r"\(([\d.]+[-\d.]+)mA", filename)
    if len(pulse_current_matches) == 1:
        pulse_current_values = pulse_current_matches[0].split("-")
        return [float(c.strip()) for c in pulse_current_values]
    return []
```

对文件名 `BTS83_40_9_1_..._DC 260917 QA Test (30-26-15-6mA, CC 10mAh 2mA)_...`：
- 提取结果：**[30.0, 26.0, 15.0, 6.0]**
- **完全来自文件名，不与 xlsx 实际数据交叉验证**

### 3.2 匹配逻辑：±5% 容差

**`src/battery_analysis/utils/processors/pulse_matcher.py:85`**：

```python
neg_levels = [-float(level) for level in listCurrentLevel]  # [30,26,15,6] → [-30,-26,-15,-6]
for c_idx, neg_level in enumerate(neg_levels):
    tolerance = abs(neg_level * 0.05)
    in_range = np.abs(cur_ma - neg_level) <= tolerance
```

- 目标：-26 mA ±5% = [-27.3, -24.7] mA
- 实际数据：-60 mA
- 匹配结果：|-60 - (-26)| = 34 > 1.3 → **不匹配！**

### 3.3 灾难性后果：26mA 容量为零

| 分析电流档 | 目标值 | 实际匹配 | 匹配数据行数 | 容量结果 |
|---|---|---|---|---|
| 30 mA | -30 mA ±5% | -30 mA ✅ | 860 行 | **正常** |
| 26 mA | -26 mA ±5% | **无匹配** | **0 行** | **零或空** |
| 15 mA | -15 mA ±5% | -15 mA ✅ | 1720 行 | **正常** |
| 6 mA | -6 mA ±5% | -6 mA ✅ | 4300 行 | **正常** |

**`Info_Plot.json` 报告 `current_levels: [30, 26, 15, 6]`**——这是从文件名读取的声明值，不是数据验证结果。报告中的 "26mA 可用容量" 实际上是 **零**（因为无数据点匹配 -26mA）。

**图片文件 `Image_UseableCapacityOverCutoffVoltage26mALoad.png`** 显示的 "26mA" 容量曲线实际为空或异常。

### 3.4 根因：无电流值交叉验证

分析工具的完整链路：

1. `filename_parser.extract_pulse_current()` 从文件名提取 [30, 26, 15, 6]
2. `data_processor._verify_pulse_currents()` 对比文件名值与查表值（两者都基于型号规格，非数据）
3. `match_pulse_levels()` 用文件名值匹配实际数据（±5% 容差）
4. **从未将 xlsx 实际电流直方图与声明值进行交叉验证**

---

## 四、脉冲电流真实来源的可能性

对照 `src/battery_analysis/utils/pulse_currents.py` 中的档位表：

| 电池类型 | QNOM 范围 | 期望档位 |
|---|---|---|
| Coin Cell CR2450 标准 | — | **30 / 26 / 15 / 6** |
| Pouch Cell | < 1200mAh | **30 / 26 / 15 / 6** |
| Pouch Cell | 1200-2000mAh | **60 / 30 / 15 / 6** |
| Pouch Cell | 2000-3000mAh | **100 / 60 / 30 / 15 / 6** |
| Pouch Cell | ≥ 3000mAh | **150 / 100 / 60 / 30 / 15 / 6** |

实测数据 **60 / 30 / 15 / 6 mA** 恰好匹配 **Pouch Cell 1200-2000mAh 档**！

但规则 `CP224642A/1S1P/920/920/85%|75%/2` 显示 QNOM=920mAh，属于 `< 1200mAh` 档（应为 30/26/15/6）。

这说明实际测试可能：
1. 使用了 Pouch Cell 的档位配置（60/30/15/6）而不是 Coin Cell 的（30/26/15/6）
2. 或者 BTS 设备端被手动修改了脉冲电流参数

---

## 五、三者互相佐证关系总结

| 佐证维度 | 如何互相印证 |
|---|---|
| **文件名对应** | NDAX/xlsx 文件名完全一致 → 确认同一电池同一测试 |
| **结构一致性** | XML 声明 8 脉冲×10 循环，xlsx 脉冲数比例 1:1:2:5 → 工步结构吻合 |
| **时间参数** | XML 脉冲宽度 1/1/2/5s，xlsx 比例 860:860:1720:4300=1:1:2:5 → 完全一致 |
| **电流值矛盾** | XML 声明 -30/-26，实测 -60/-30 → **矛盾即证据：执行与计划不符** |
| **旧模板** | XML PN/日期/CC 容量均与文件名不符 → 模板混用 |

---

## 六、风险评估与建议

### 高风险
1. **报告中 "26mA 容量" 数据为空或错误**——需要检查所有使用此数据的报告
2. **分析工具无电流数据验证机制**——任何文件名与数据不符都会静默产生错误结果
3. **Info_Plot.json 和分析图表引用不存在的电流档**

### 建议
1. **短期**：对已出报告检查 "26mA" 列数据是否为零/异常，必要时修正
2. **中期**：在分析工具中增加 **电流直方图自动检测**，将数据中实际出现的电流峰值与文件名声明值交叉验证，不一致时强制告警
3. **长期**：将脉冲电流档位从"文件名优先"改为"数据驱动+文件名参考"，提高鲁棒性
4. **验证**：用 NewareNDA 库直接读取 NDAX 的 data.ndc，确认原始二进制数据中电流值是否确实为 -60/-30/-15/-6（排除转换环节问题）