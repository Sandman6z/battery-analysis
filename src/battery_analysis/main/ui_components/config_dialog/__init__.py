"""配置管理对话框包

由原单文件 config_dialog.py 拆分而来（大文件拆分重构）。
对外仍暴露原有的导入路径：`from ...ui_components.config_dialog import ConfigDialog`
"""

from battery_analysis.main.ui_components.config_dialog.constants import (
    RULE_COLUMNS,
    SPEC_METHOD_COL,
)
from battery_analysis.main.ui_components.config_dialog.dialog import ConfigDialog
from battery_analysis.main.ui_components.config_dialog.list_editor import _ListEditor
from battery_analysis.main.ui_components.config_dialog.rules_editor import _RulesEditor

__all__ = [
    "RULE_COLUMNS",
    "SPEC_METHOD_COL",
    "ConfigDialog",
    "_ListEditor",
    "_RulesEditor",
]
