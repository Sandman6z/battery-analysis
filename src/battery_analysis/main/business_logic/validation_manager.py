"""
验证管理模块

这个模块负责处理所有输入验证逻辑，包括：
- 版本号格式验证
- 输入路径验证
- 必填字段验证
- 电池类型验证
- 规格验证
"""

import logging
import os
import re

import PyQt6.QtCore as QC

from battery_analysis.i18n.language_manager import _
from battery_analysis.main.business_logic.validation_feedback import ValidationFeedbackMixin
from battery_analysis.main.business_logic.validation_fields import ValidationFieldsMixin
from battery_analysis.main.business_logic.validation_spec_rules import ValidationSpecRulesMixin
from battery_analysis.utils.input_validator import FieldValues, InputValidator, ValidationResult


class ValidationManager(ValidationFieldsMixin, ValidationSpecRulesMixin, ValidationFeedbackMixin):
    """验证管理器（骨架类）

    原 697 行大文件按职责拆分，本文件保留 __init__ 与类入口：
    - validation_fields      版本号/路径/必填字段/InputValidator 校验
    - validation_spec_rules  电池类型、规格、施工方式验证
    - validation_feedback    checkinput 主流程与字段级 UI 反馈
    """

    def __init__(self, main_window=None):
        """
        初始化验证管理器

        Args:
            main_window: 主窗口实例（旧接口）
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._temperature_set_from_xml = False  # 标志：温度是否已从XML文件名设置
