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


def scan_sorted_ndax(directory: str) -> list[str]:
    """非递归扫描实际 NDAX 文件，统一用于预览、转换、校验和与分析。"""
    with os.scandir(directory) as entries:
        files = [
            entry.name for entry in entries
            if entry.name.lower().endswith(".ndax") and entry.is_file()
        ]
    files.sort(key=natural_sort_key)
    return [os.path.join(directory, f) for f in files]
