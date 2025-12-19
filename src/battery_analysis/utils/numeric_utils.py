"""
数值计算工具函数模块

提供基于numpy的数值计算函数，处理空列表等边界情况
"""

import numpy as np

def np_mean(_listCpt):
    if len(_listCpt) > 0:
        return float(np.mean(_listCpt))
    return 0


def np_std(_listCpt):
    if len(_listCpt) > 1:
        return float(np.std(_listCpt, ddof=1))
    return 0


def np_max(_listCpt):
    if len(_listCpt) > 0:
        return float(np.max(_listCpt))
    return 0


def np_min(_listCpt):
    if len(_listCpt) > 0:
        return float(np.min(_listCpt))
    return 0


def np_med(_listCpt):
    if len(_listCpt) > 0:
        return float(np.median(_listCpt))
    return 0
