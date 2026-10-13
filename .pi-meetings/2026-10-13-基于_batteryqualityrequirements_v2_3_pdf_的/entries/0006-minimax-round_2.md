# MiniMax (Round 2): 重新定优先级：QNOM 分档表矛盾为 P0；冷陈三口径同步为 P1；发现 fallback 路径在期望格不在档位时仍有静默单条件判断问题；单样本格 µ-2σ 语义矛盾被全部四人忽视；提出 3 个新盲区。

# MiniMax Round 2：挑战与深化——重新定优先级 + 三个被遗漏的盲区

## 〇、阅读说明

Round 1 我提了 9 项创意盲区，GPT 做了全局俯瞰，DeepSeek 做了逐条 PDF 比对，GLM 做了纠偏与务实核查。本轮我从"四人是否互相说漏了"和"代码是否还有没说出口的假设"两个角度切入。

---

## 一、对 GLM 纠偏 DeepSeek 的确认与深化

GLM 正确指出 DeepSeek 的"fallback 丢失最小值检查"已过时。当前 `report_coordinator.py:165-176` 确实在 `build_expectations` 返回 `[]` 时，构造了 legacy `Expectation` 对象并交给 `evaluate_expectations` 执行双条件（`sample_ok` + `stat_ok`）。DeepSeek 的描述基于过期代码。

**但 GLM 没有说完**——这个"legacy 构造 Expectation"路径在以下场景仍会触发静默单条件降级，值得补充：

> 当 `build_expectations` 返回非空，但 `evaluate_expectations` 因期望格不在实测档位而 `verdicts = []` 时，`report_coordinator.py:178-188` 走的是 `listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate`——**单条件，阈值是 required/QNOM 比例，不是 PDF 绝对期望值**，且**没有任何日志或 Remarks 标注**。这是 GLM 发现 B 的完整场景。

确认：GLM 的 B 项（冷冻三口径不同步导致 verdicts=[] → legacy 单点判定）优先级应为 🔴 高，修复方案加一条——`report_coordinator.py:183` 的单条件分支需加 `logger.warning`，并让 Remarks 注明 `"legacy single-point judgment used"`。

---

## 二、GLM 发现 A（QNOM 分档表矛盾）与我 Round 1 问题 2 的合并深化

GLM 的发现 A（分档表与 PDF 摘录矛盾）与我 Round 1 的问题 2（QNOM 临界值落在哪一档）是同一问题的两个侧面——现已合并确认。

**验证：实际代码**（`pulse_currents.py:46-53`）：

```python
_POUCH_CAPACITY_BANDS = (
    (1200, [30, 26, 15, 6]),
    (2000, [60, 30, 15, 6]),
    (3000, [100, 60, 30, 15, 6]),
)
# QNOM >= 3000: 150/100/60/30/15/6
```

docstring：`1200 <= QNOM < 2000`、`2000 <= QNOM < 3000`、`QNOM >= 3000`。

代码用 `capacity_mah < upper_limit` 遍历，取第一个满足的档——即：
- QNOM=1199 → 第一档（30mA）
- QNOM=1200 → **第二档（60mA）** ← 边界落在第二档
- QNOM=1999 → 第二档（60mA）
- QNOM=2000 → **第三档（100mA）** ← 边界落在第三档
- QNOM=3000 → 第四档（150mA）

**但 PDF 2026-09-23 摘录中**：
- 2000 ≤ QNOM < 3000 → 150/100/60/30（无 15/6）
- QNOM ≥ 3000 → 7 级（500/250/100/60/30/15/6）

且摘录**没有 1200–2000 档**（代码凭空多出一档）。这意味着：
1. **QNOM=1200** 代码判入 60mA 档，PDF 可能要求入 30mA 档（如果 PDF 用 `< 1200` + `1200 ≤ QNOM < 2000` 而非 `< 1200` + `< 2000`）
2. **QNOM=2000** 代码判入 100mA 档，PDF 摘录似乎说入 150mA 档
3. **摘录中 1200–2000 区间的缺失**是最关键的问题——这个档是代码自己发明的，没有 PDF 来源

**优先级重新排序**：这是整个会议中**唯一能导致系统性判定格选错的源头性错误**，排在 P0。修复成本（30 分钟导出 PDF 重比对）远低于风险（所有 QNOM 落入 1200–2000/2000–3000 边界的 Pouch 电池判定全部错位）。

---

## 三、我 Round 1 问题 3 被四人全部忽视——这是本轮最重要的补充

### 单样本 µ-2σ 语义矛盾：为什么没人提

四人中，DeepSeek 提到了"单样本 std=0，µ-2σ 失去独立意义"（中优先级），我 Round 1 提到了"值恰好等于 threshold 时 sample_ok=True 但 stat_ok=False"的矛盾。但没有一个人把这个矛盾推进到**它实际上是一个合规性漏洞**。

**完整场景**：

样本数据：n=1，值=380mAh，threshold=380mAh

```
sample_ok = (380 >= 380 - 1e-6) = True   # 单样本 ≥ 期望 → Pass
stat_ok   = (380 > 380)             = False  # µ-2σ 不"严格高于" → Fail
```

**PDF §6.2.11 原文**："no single measured sample must have a usable capacity **less than** the specified expected usable capacity" AND "the µ-2σ value ... must be **higher than** the specified usable capacity"。

两个条件都要求报告为"符合"。但代码在此场景下输出 Fail——因为单样本的 µ-2σ = 样本值，严格"高于"要求样本值 > 阈值。这在字面意义上是 PDF 的字面意思，但语义上：
- 若 PDF 意图是"样本代表的质量稳定性足以覆盖到 threshold"，那么 n=1 时，µ-2σ=样本值，样本值=threshold 应该判 Pass
- 若 PDF 意图是"µ-2σ 是一个独立于单样本的统计保证"，那么 n=1 时 µ-2σ 无法提供统计保证，样本值=threshold 判 Fail 是合理的

**PDF 没有明确 n=1 的处理方式，这是设计缺陷，不是实现缺陷。** 但代码选择了"Fail"这一边，而没有在报告里注明"单样本，统计保证不足"。

**为什么其他四人没提**：DeepSeek 提到但标记为"中优先级无建议"；GLM 完全没提；GPT 和我的 Round 1 都只停留在"矛盾"描述，没有追问"这个 Fail 结论对产线意味着什么"。

**实际影响**：CR2450 冷冻型 threshold=280mAh，若实测值恰好是 280mAh（极罕见但可能），所有电池判 Fail。但最小值检查通过了（280 >= 280），用户看到的是一个"似乎合格的电池被统计检查拒绝"的困惑报告。

**修复方向**（两条路二选一）：
- A：在 `statistics_utils.py` 对 n=1 返回 `mu2sigma=None`，`evaluate_expectations` 对 `mu2sigma is None` 输出 `"stat_ok=N/A (single sample)"`，由人判断
- B：在报告 Remarks 里注明"single sample, statistical criterion not applicable"

---

## 四、三个新盲区（其他四人完全没提）

### 盲区 N1：legacy fallback 的 µ-2σ 计算用的是实测最高电流档，而非 PDF 指定档

`report_coordinator.py:178-188` 的 legacy fallback 路径：

```python
if listMM2S[intPosiMaxmA][intPosi2V25] / intQnomCapacity >= intPassRate:
    strResult = "Pass"
```

这里用的是**实测数据中的最高电流档**（`intPosiMaxmA`），而不是 PDF 对该 profile 规定的判定电流。举例：
- Pouch Cell QNOM=2500，PDF 规定 100mA 档，但实测文件只有 30mA 测试
- legacy fallback 用 `listMM2S[30mA index][2.25V]` 判断
- 30mA 档的 µ-2σ 通常远高于 100mA 档（放电更慢，容量更大）
- **结论：legacy fallback 更容易让不合格电池 Pass**

这与 GLM 的发现 B 场景结合——当冷冻三口径不同步导致 verdicts=[] 时，走的是这个偏向宽松的 legacy 路径。GLM 发现了同步问题，但我补充了"即使触发 legacy，它本身也比 PDF 标准宽松"。

### 盲区 N2：PDF 没有规定 µ-2σ 的分母，legacy 路径和 `evaluate_expectations` 用了不同的分母

- `evaluate_expectations`（新路径）：`stat_ok = mu2sigma > threshold_mah`（阈值直接来自 PDF，是 mAh 绝对值）
- legacy fallback（`report_coordinator.py:178`）：`mu2sigma / intQnomCapacity >= intPassRate`（阈值是 required/QNOM 比例）

两个路径用**不同量纲**做判断：新路径比较 mAh 绝对值，legacy 路径比较百分比。当 required ≠ QNOM × 比例时，两条路径对同一数据的判定可能相反。例如：QNOM=3000，ratio=0.85，required=2550。legacy 用 2550/3000=85%；新路径直接用 2550mAh。数值相同，但如果 required 字段被人为改过（见 GPT R2），两条路径会给出不同答案。

### 盲区 N3：测试覆盖了 Hermes 走 legacy 逻辑，但没验证 legacy 结论的正确性

`test_hermes_expectation_outside_levels_uses_legacy_logic` 只验证"触发了 legacy 逻辑"，不验证"legacy 逻辑对 Hermes 来说结论是什么"。若 Hermes 文件只有 30mA 档（没有 500/100mA），legacy 用 30mA 数据判断 Hermes 是否合格——这个结论在工程上是否合理，没有任何测试。

---

## 五、对四人共识区的挑战与回应

**四人共识**：
1. 核心判定公式（双条件、严格大于）实现正确 ✅
2. 2.25V 精确比较风险存在 ✅（四人全认）
3. 冷冻三口径同步问题存在 ✅（GLM B + 我 Round 1 问题 7）

**挑战点**：

- **"构造方法英文匹配"只是中优先级**（GLM E）——我认为应该是高优先级。UI 有 i18n 目录，`locale/` 存在，一旦 UI 推出中文版，所有 Pouch Cell 的构造方法字段将无法匹配，100% 的 Pouch Cell 判定会静默回退到 legacy。不是说"可能"踩雷，而是"只要中文化就必然"踩雷。

- **"Hermes 期望值硬编码"**（GPT R6, GLM F）四人列为低/中——我认为应该提升。§7.1.1.11 的 4 个值（3000/3600/2600/3200）是硬编码常量，没有任何外部配置或其他来源可查。如果 PDF 更新这 4 个值，需要改代码+测试，而没有任何配置文件驱动。这意味着"规则来源的唯一性"（GLM 的核心关切）在这里完全失效。

---

## 六、Round 2 改进优先级（推翻/修正四人排序）

| 优先级 | 项目 | 修正理由 |
|--------|------|----------|
| **P0** | PDF §7.1.1 全表重导出 + QNOM 分档表比对（GLM A + 我的 QNOM 边界） | 唯一系统性源头错误；所有 1200/2000/3000 边界档位的判定都可能错位 |
| **P0** | 冷冻三口径统一 + 兜底路径日志（GLM B + legacy 结论宽松性补充） | 静默降级到错误标准，且 legacy 比 PDF 标准更宽松 |
| **P1** | 2.25V 容差匹配 + 未找到告警（GLM C） | 精确比较 + index 0 默认静默错位 |
| **P1** | 单样本 µ-2σ 语义矛盾（我的 Round 1 问题 3，他人完全忽视） | n=1 且样本值=threshold 时，双条件一个 Pass 一个 Fail，报告无说明 |
| **P1** | Hermes 测试只验证路径不验证结论（盲区 N3） | 当前测试让有缺陷的 legacy 路径变成了"通过测试的正确逻辑" |
| **P2** | 构造方法中文化雷（GLM E，我提升优先级） | i18n 存在时必然踩雷 |
| **P2** | Hermes 期望值外置到配置（GPT R6, GLM F，我提升优先级） | 规则来源唯一性原则在此处完全失效 |
| **P2** | 空样本格误报 Fail（GLM D） | "没测到"报成"不合格" |
| **P3** | 补全 Pouch Cell 自动化测试（我的 Round 1 问题 1） | 防止 build_expectations 回归 |
| **P3** | µ-2σ 计算 ddof 假设（我的 Round 1 问题 9） | 低样本量下偏乐观，登记即可 |

---

## 七、一句话行动项（用户决策点）

1. **必须**：用 pdftotext 重导出 §7.1.1 全表，裁定 `_POUCH_CAPACITY_BANDS` 与 PDF 是否一致，1200–2000 档是否有 PDF 来源
2. **必须**：在 `report_coordinator.py:183` 加 `logger.warning`，Remarks 标注 "legacy single-point judgment used"
3. **建议**：`build_expectations` 增加 `is_freezer` 参数，接受调用方传入的冷冻标识，而非自己重新从 required 字段推断
4. **建议**：单样本场景的 `stat_ok` 返回 None 或在 Remarks 里注明"single sample, statistical criterion not independently verified"
