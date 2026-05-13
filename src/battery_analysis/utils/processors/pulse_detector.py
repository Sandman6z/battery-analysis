"""脉冲检测逻辑"""
import logging

logger = logging.getLogger(__name__)


def b_is_in_range(current, standard):
    """检查电流是否在标准值的 +/-5% 范围内（兼容正负数）"""
    return abs(current - standard) <= abs(standard * 0.05)


def is_pulse_step(step_value) -> bool:
    """检查步骤值是否为脉冲步骤"""
    return str(step_value).strip() in ("脉冲", "Pulse")


def detect_pulse_rows(record_df, step_col=1):
    """检测 Record 表中的脉冲行，返回布尔掩码（pd.Series）"""
    step_series = record_df.iloc[:, step_col].astype(str).str.strip()
    return step_series.isin(["脉冲", "Pulse"])
