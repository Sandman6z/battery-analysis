"""PDF §7.1.1 / §6.2.11 golden expectations（从 BatteryQualityRequirements_v2.3 直接转录）

本文件是"事实源"快照：所有值来自 PDF 原文（pdftotext 导出后逐条核对），
带出处行号，**不从代码常量抄录**。测试断言实现输出 == 这里的 golden 值，
因此任何实现侧漂移（分档、比例、override、判定格）都会被测试捕获。

出处：BatteryQualityRequirements_v2.3.pdf → pdftotext -layout 导出的纯文本行号
（bqr.txt，2884 行）。行号在 SOURCE 中注明，便于 PDF 改版后重导出核对。
"""

# ── §7.1.1.3–.10 脉冲电流分档（bqr.txt:1290-1310, 1470-1487, 1645-1662, 1820-1843）──
# 每档格式：(QNOM 上限 mAh，档位序列)，语义 "1200mAh ≤ QNOM < 2000mAh"
# 上限开闭由 §7.1.1 标题的 "<" 决定：QNOM < 1200 / 1200≤QNOM<2000 / 2000≤QNOM<3000 / ≥3000
GOLDEN_POUCH_BANDS = (
    # §7.1.1.3/.4  QNOM < 1200mAh：30/26/15/6（Pause Period 1-4，bqr:1296-1303）
    (1200, (30, 26, 15, 6)),
    # §7.1.1.5/.6  1200 ≤ QNOM < 2000mAh：60/30/15/6（bqr:1476-1483）
    (2000, (60, 30, 15, 6)),
    # §7.1.1.7/.8  2000 ≤ QNOM < 3000mAh：100/60/30/15/6（bqr:1648-1659）
    (3000, (100, 60, 30, 15, 6)),
)
# §7.1.1.9/.10  QNOM ≥ 3000mAh：150/100/60/30/15/6（bqr:1823-1839）
GOLDEN_POUCH_LARGE_BAND = (150, 100, 60, 30, 15, 6)

# 分档边界探针：(capacity, 期望档位) —— 上限不含、下限含
GOLDEN_POUCH_BAND_PROBES = (
    (1199, (30, 26, 15, 6)),
    (1200, (60, 30, 15, 6)),  # 边界切入第二档
    (1999, (60, 30, 15, 6)),
    (2000, (100, 60, 30, 15, 6)),
    (2999, (100, 60, 30, 15, 6)),
    (3000, GOLDEN_POUCH_LARGE_BAND),
    (5000, GOLDEN_POUCH_LARGE_BAND),
)

# ── §7.1.1.1/.2 Coin Cell（bqr.txt:1080-1091, 1175-1186, 1212-1224）──
GOLDEN_COIN = {
    # 常温：脉冲 30/26/15/6，期望 >380mAh to 2.25V at 30mA
    "room": {"currents": (30, 26, 15, 6), "threshold_mah": 380, "judgment_current_ma": 30.0},
    # 冷冻单体：脉冲 15/13/7.5/3，期望 >280mAh to 2.25V at 15mA for single cell
    "freezer_single": {
        "currents": (15, 13, 7.5, 3),
        "threshold_mah": 280,
        "judgment_current_ma": 15.0,
    },
    # 冷冻 1S2P：脉冲 30/26/15/6（与常温同档），期望 >280mAh to 2.25V at 30mA for 1S2P pack
    "freezer_1s2p": {
        "currents": (30, 26, 15, 6),
        "threshold_mah": 280,
        "judgment_current_ma": 30.0,
    },
}

# ── §7.1.1.11 CP583083 "Hermes"（bqr.txt:1935, 2015-2024）──
# 脉冲 5 档：500/250/100/50/25（Pause Period 1-5，bqr:2015-2019）
GOLDEN_HERMES_PULSE_CURRENTS = (500, 250, 100, 50, 25)
# Expected Usable Q 四格（bqr:2021-2024）：(截止电压, 电流, 阈值 mAh)
GOLDEN_HERMES_EXPECTATIONS = (
    (2.25, 500, 3000),
    (2.25, 100, 3600),
    (2.5, 500, 2600),
    (2.5, 100, 3200),
)
# 型号匹配关键字：PDF 型号 CP583083，"Hermes" 为昵称；CF 前缀为拼写兼容
GOLDEN_HERMES_SPEC_KEYWORD = "583083"

# ── 构造比例（§7.1.1.3–.10 Expected Usable Q 行，bqr.txt:1309, 1396, 1483, 1570, 1659, 1748, 1839, 1930）──
# Spiral  ">85% of Qnom to 2.25V at <最高档>"
# Laminate ">75% of Qnom to 2.25V at <最高档>"
GOLDEN_CONSTRUCTION_RATIO = {"spiral": 0.85, "laminate": 0.75}
# 中文构造关键词（实现侧兼容；PDF 用英文 Generic Spiral/Laminate Type）
GOLDEN_CONSTRUCTION_RATIO_ZH = {"螺旋": 0.85, "叠片": 0.75}

# ── 截止电压档位（§7.1.1.x 各表 Cut-Off Voltages）──
# 标准（Coin/Pouch 各档一致，bqr:1306-1307）
GOLDEN_CUTOFF_VOLTAGES = (2.4, 2.3, 2.25, 2.2, 2.0, 1.8)
# Hermes 7 档（bqr:2017-2018）
GOLDEN_HERMES_CUTOFF_VOLTAGES = (2.5, 2.4, 2.3, 2.25, 2.2, 2.0, 1.8)

# ── §6.2.11 判定双条件（bqr.txt:936-944）──
# ① no single measured sample must have a usable capacity of less than the
#    specified expected usable capacity
# ② for the statistical results, the µ - 2 value ... must be higher than the
#    specified usable capacity
# 注：② 是严格 "higher than"（>，非 ≥）；①是 "less than 才不合格"（≥ 合格）
GOLDEN_DUAL_CONDITION = {"sample_cmp": ">=", "mu2sigma_cmp": ">"}
# "if not specified otherwise, the highest specified pulse current value should
#  be used to calculate the usable capacity"（bqr:940）→ 判定格电流 = 档位[0]
GOLDEN_JUDGMENT_CURRENT = "highest_in_band"

# ── 规则行换算（§6.2.11 示例 "percentage of the nominal capacitance"，bqr:937-939）──
# dual percent 规则 "85%|75%"：spiral 取 group(1)，laminate 取 group(2)
GOLDEN_RULE_PERCENT_SAMPLES = (
    # (rule 行, construction, 期望百分比)
    ("XYZ1430/1S1P/1500/1500/85%|75%/5", "Spiral Type", 85),
    ("XYZ1430/1S1P/1500/1500/85%|75%/5", "Laminate Type", 75),
    ("CR2450/1S1P/600/550/380/1.0", "", 0),  # 绝对值规则无百分比
)
