"""电池型号分类工具——根据型号名和容量判断电池类型"""

DEFAULT_CAPACITY_THRESHOLD = 800  # mAh，低于此值为 Coin Cell


def classify_spec(model_name: str, capacity: int = 0) -> str:
    """根据规格型号名和容量判定电池类型

    判定规则：
    1. CR 开头 → Coin Cell
    2. CP 或 CF 开头 → Pouch Cell
    3. 兜底：容量 >= threshold → Pouch Cell，否则 Coin Cell
    """
    upper = model_name.strip().upper()
    if upper.startswith("CR"):
        return "Coin Cell"
    if upper.startswith(("CP", "CF")):
        return "Pouch Cell"
    return "Pouch Cell" if capacity >= DEFAULT_CAPACITY_THRESHOLD else "Coin Cell"


def extract_spec_name(rule: str) -> str:
    """从规则字符串中提取规格型号名（rule 分段第 0 段）"""
    parts = rule.split("/")
    return parts[0].strip() if parts else ""


def extract_capacity(rule: str) -> int:
    """从规则字符串中提取容量（rule 分段第 2 段）"""
    parts = rule.split("/")
    if len(parts) >= 3:
        try:
            return int(parts[2])
        except ValueError:
            return 0
    return 0


def derive_specifications(rules: list) -> dict:
    """从 rules 列表自动派生 specifications 字典

    返回: {"Coin Cell": [...], "Pouch Cell": [...]}，去重、保持首次出现顺序
    """
    specs: dict = {"Coin Cell": [], "Pouch Cell": []}
    seen: set = set()
    for rule in rules:
        spec_name = extract_spec_name(rule)
        if not spec_name or spec_name in seen:
            continue
        seen.add(spec_name)
        capacity = extract_capacity(rule)
        cell_type = classify_spec(spec_name, capacity)
        specs[cell_type].append(spec_name)
    return specs
