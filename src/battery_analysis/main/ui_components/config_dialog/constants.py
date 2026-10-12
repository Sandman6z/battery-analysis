"""配置对话框共享常量（Rules 表格列定义）"""

RULE_COLUMNS = [
    "Specification",
    "Spec Method",
    "Datasheet Capacity",
    "Calculation Capacity",
    "Required Useable Capacity",
    "CC Current (mA)",
]

# Rules 表格中 Spec Method 列的下拉框（可选项来自 battery.specificationMethods）
SPEC_METHOD_COL = RULE_COLUMNS.index("Spec Method")
