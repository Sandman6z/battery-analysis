# -*- coding: utf-8 -*-
"""
现代化UI样式系统

提供统一的样式管理解决方案
"""

from .style_manager import (
    StyleManager, 
    style_manager, 
    apply_modern_theme,
    create_styled_button,
    create_styled_groupbox
)

__all__ = [
    'StyleManager',
    'style_manager', 
    'apply_modern_theme',
    'create_styled_button',
    'create_styled_groupbox'
]
