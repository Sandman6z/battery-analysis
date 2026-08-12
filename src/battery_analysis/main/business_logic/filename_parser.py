"""
文件名解析模块

从Excel文件名中提取规格类型、方法、制造商、批次日期码、脉冲电流等信息
"""

import re
import logging

logger = logging.getLogger(__name__)


def set_specification_type(filename, all_spec_types, combo_box):
    """从文件名匹配规格类型"""
    sorted_types = sorted(enumerate(all_spec_types), key=lambda x: len(x[1]), reverse=True)
    for t, spec_type in sorted_types:
        if spec_type in filename:
            combo_box.setCurrentIndex(t)
            return


def set_specification_method(filename, all_spec_methods, combo_box):
    """从文件名匹配规格方法"""
    sorted_methods = sorted(enumerate(all_spec_methods), key=lambda x: len(x[1]), reverse=True)
    for m, method in sorted_methods:
        if method in filename:
            combo_box.setCurrentIndex(m)
            return


def set_manufacturer(filename, combo_box):
    """从文件名匹配制造商"""
    for m in range(combo_box.count()):
        if combo_box.itemText(m) in filename:
            combo_box.setCurrentIndex(m)
            break


def extract_batch_date_code(filename, line_edit):
    """提取批次日期代码，兼容 DC2604、DC(2604) 和 DC (2604) 三种格式"""
    # 匹配 DC 后可选空格、可选括号包裹的字母数字批次码
    batch_date_codes = re.findall(r"DC\s*\(?(\w+)\)?", filename)
    if len(batch_date_codes) == 1:
        line_edit.setText(batch_date_codes[0].strip())


def extract_pulse_current(filename):
    """提取脉冲电流"""
    pulse_current_matches = re.findall(r"\(([\d.]+[-\d.]+)mA", filename)
    if len(pulse_current_matches) == 1:
        pulse_current_values = pulse_current_matches[0].split("-")
        try:
            return [float(c.strip()) for c in pulse_current_values]
        except ValueError:
            return [int(float(c.strip())) for c in pulse_current_values]
    return []


def extract_cc_current(filename):
    """提取恒流电流"""
    cc_current_matches = re.findall(r"mA,(.*?)\)", filename)
    if len(cc_current_matches) == 1:
        cc_current_str = cc_current_matches[0].replace("mAh", "")
        cc_current_values = re.findall(r"([\d.]+)mA", cc_current_str)
        if len(cc_current_values) >= 1:
            return cc_current_values[-1]
    return ""
