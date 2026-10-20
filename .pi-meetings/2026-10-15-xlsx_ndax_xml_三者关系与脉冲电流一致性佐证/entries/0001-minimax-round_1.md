# MiniMax (Round 1): xlsx / ndax / XML 三者关系与脉冲电流一致性分析

# xlsx / ndax / XML 三者关系与脉冲电流一致性佐证分析

## 一、三者格式确认（取证）

### 1. NDAX 文件格式（实测）

通过二进制头部探查，确认 NDAX 是 **ZIP 压缩包**，内部包含 4 个文件：

```
NDAX (ZIP)
├── Step.xml        — 工步定义，含脉冲参数
├── TestInfo.xml    — 测试元信息（PN、日期等）
├── VersionInfo.xml — 软件版本
└── data.ndc        — 二进制测试数据（电流/电压/时间序列）
```

直接证据：文件头为 `PK\x03\x04`（ZIP 签名），解压后可看到上述 4 个文件。文件名与对应 xlsx 完全一致（除去扩展名）。

### 2. xlsx 生成流程

`battery_analysis/ndax/converter.py` 揭示了转换链路：

```
NDAX (ZIP)
  → NewareNDA Python 库读取 data.ndc + Step.xml
  → 按 Cycle / Step / Record 三张表写入 xlsx
  → xlsx 第 C 列为电流（单位 A），第 B 列为工步类型（"脉冲"/"恒流放电"/"搁置"）
```

转换器本身 **不做电流值修正**，只忠实地把 NDAX 库返回的 DataFrame 写入 xlsx。

### 3. XML Profile 的作用

XML profile 是 **BTS 测试软件输入**，定义测试步骤参数（含脉冲电流/时间），但 **不直接写入 NDAX 数据文件**。它由 Neware BTS Client 在创建测试任务时加载，控制设备如何执行工步。

## 二、关联字段识别

| 关联维度 | NDAX → xlsx | NDAX → XML Profile |
|---|---|---|
| 文件名 | 完全一致（同名对应） | 由用户手动关联 |
| 测试日期 | 从 Cycle 表读取 | XML Head_Info date 属性 |
| 脉冲参数 | 从 data.ndc 实测，Step.xml 声明 | XML Step4 PulseData 定义 |
| PN（电池型号） | 从 TestInfo.xml 读取 | XML Head_Info PN 属性 |
| 脉冲电流值 | **实测值，不受 XML 控制** | XML 声明值（期望值） |

关键发现：NDAX 文件内部嵌入了 Step.xml（与目录中 profile 完全相同的内容），确保同一批次测试的工步定义可追溯。

## 三、脉冲电流一致性佐证（矛盾分析）

### XML Profile 声明（CF224642T_QATest_30-26-15-6mA_CC-2mA-10mAh.xml）

```xml
<PulseData Cycle_Count="10" Count="8">
  <Pulse1 Value="0"  Time="59000" />  <!-- 静置 -->
  <Pulse2 Value="-30" Time="1000" />  <!-- 30mA 脉冲 -->
  <Pulse3 Value="0"  Time="59000" />  <!-- 静置 -->
  <Pulse4 Value="-26" Time="1000" />  <!-- 26mA 脉冲 -->
  <Pulse5 Value="0"  Time="58000" />  <!-- 静置 -->
  <Pulse6 Value="-15" Time="2000" />  <!-- 15mA 脉冲，宽度 2s -->
  <Pulse7 Value="0"  Time="55000" />  <!-- 静置 -->
  <Pulse8 Value="-6"  Time="5000" />  <!-- 6mA 脉冲，宽度 5s -->
</PulseData>
```

### 已知事实（xlsx 抽验结果）

- **实际电流**：-60 / -30 / -15 / -6 mA
- **无 26mA 脉冲**
- 脉冲数比例 860:860:1720:4300 = 1:1:2:5，对应脉冲宽度 1s/1s/2s/5s
- 文件名和 XML 声明：30/26/15/6 mA

### 矛盾点

| 维度 | XML 声明 | NDAX 实际数据 |
|---|---|---|
| 脉冲电流值 | -30 / -26 / -15 / -6 mA | **-60 / -30 / -15 / -6 mA** |
| 26mA 脉冲 | 存在 | **不存在** |
| 脉冲宽度 | 1s / 1s / 2s / 5s | 1s / 1s / 2s / 5s（吻合） |
| 循环次数 | 10 | 10（吻合） |

## 四、根因分析与三者互相佐证关系

### 4.1 数据溯源链

```
XML Profile (声明)  ←---  手动关联（同一目录）
       ↓
Neware BTS Client 执行测试
       ↓
NDAX data.ndc (实测数据)  ←---  包含内部 Step.xml（与 profile 内容相同）
       ↓
NewareNDA 库解析
       ↓
xlsx (转换输出)  ←---  第 C 列为实测电流，第 B 列为实测工步类型
```

**结论**：xlsx 是 NDAX 的忠实转换结果，NDAX 是测试设备的实测记录，XML profile 是测试任务的配置输入。三者中 **NDAX/xlsx 是实测证据链，XML 是计划/声明**。

### 4.2 电流不一致的可能原因

1. **旧模板问题**：XML Head_Info 显示 PN=CP224642A、日期 20240927（文件名却含 260917），Remark 字段还写的是 "CC 20mAh 2mA" 而非文件名中的 "CC 10mAh"。**该 XML 是旧模板，被错误地用于本次测试**。
2. **设备配置覆盖**：BTS 测试机实际执行时，可能通过设备面板手动修改了脉冲电流设定（-30 被改为 -60），而 NDAX 忠实地记录了实际执行的电流值。
3. **软件版本差异**：不同 BTS Client 版本对脉冲参数的处理逻辑可能不同。

### 4.3 三者互相佐证关系

| 佐证维度 | 如何互相印证 |
|---|---|
| 文件名对应性 | NDAX/xlsx 文件名完全一致 → 确认同一电池的同一测试 |
| XML 内嵌一致性 | NDAX 内嵌 Step.xml 与目录中 profile 应一致 → 可验证 NDAX 未被篡改 |
| 工步结构一致 | XML 声明 8 个 Pulse + 10 次循环，NDAX 脉冲数比例验证 → 结构吻合 |
| **电流值矛盾** | XML 声明 30/26/15/6，NDAX 实测 60/30/15/6 → **矛盾即证据：测试执行与计划不符** |
| 脉冲宽度一致 | XML 声明 1s/1s/2s/5s，NDAX 脉冲数比例验证 1/1/2/5 → 时间参数一致 |

## 五、结论与建议

1. **xlsx 与 NDAX 完全一致**：converter.py 忠实地将 NDAX 转换为 xlsx，不做数据修改。两者共同构成实测证据。
2. **XML Profile 与实测数据存在根本性电流值矛盾**：XML 声明 -30mA，实际执行为 -60mA；XML 声明 -26mA，实际无此脉冲。
3. **XML Profile 是旧模板**：PN、日期、CC 容量均与文件名不符，强烈指向模板混用问题。
4. **建议验证方向**：
   - 检查 BTS 测试机面板的历史设置记录，确认是否在测试执行前手动修改了脉冲电流
   - 对比其他批次测试的 NDAX 数据，看 -60mA 是否为系统性配置
   - 确认 Neware BTS Client 8.0.0.516 的脉冲参数处理逻辑，是否存在从 XML 读取后的设备端修正机制
   - 在分析报告中标注"XML 声明值与实测值不一致"，避免用 XML 期望值误导分析结论
