# -*- coding: utf-8 -*-
"""
验证工具模块
提供验证状态管理功能
"""


class Checker:
    """
    验证状态管理器
    用于跟踪验证结果和错误信息
    """
    
    def __init__(self) -> None:
        self.b_check_pass = True
        self.str_error_msg = ""

    def clear(self):
        """清除验证状态"""
        self.b_check_pass = True
        self.str_error_msg = ""

    def set_error(self, error_msg: str):
        """设置验证错误信息
        
        Args:
            error_msg: 错误信息字符串
        """
        self.b_check_pass = False
        self.str_error_msg = error_msg
