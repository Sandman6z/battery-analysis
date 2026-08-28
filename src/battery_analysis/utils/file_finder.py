"""文件扫描与自然排序"""

import os
import re


def natural_sort_key(filename: str) -> list:
    """将文件名按自然顺序排序的 key 函数

    针对格式: BTS83_40_5_4_2818580619_...
    将所有数字段转换为整数进行比较，确保 5_4, 5_5, 5_6... 正确排序
    """
    parts = re.split(r"(\d+)", filename)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def scan_sorted_xlsx(directory: str, exclude_temp: bool = True) -> list[str]:
    """扫描目录中的 xlsx 文件，按自然顺序排序返回完整路径

    Args:
        directory: 目录路径
        exclude_temp: 是否排除 ~$ 开头的临时文件

    Returns:
        排序后的 xlsx 文件完整路径列表
    """
    files = [
        f
        for f in os.listdir(directory)
        if f[-5:] == ".xlsx" and (not exclude_temp or f[:2] != "~$")
    ]
    files.sort(key=natural_sort_key)
    return [os.path.join(directory, f) for f in files]
