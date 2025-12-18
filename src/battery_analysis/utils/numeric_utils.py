import numpy as np


def np_mean(_listCpt):
    if len(_listCpt) > 0:
        return float(np.mean(_listCpt))
    else:
        return 0


def np_std(_listCpt):
    if len(_listCpt) > 1:
        return float(np.std(_listCpt, ddof=1))
    else:
        return 0


def np_max(_listCpt):
    if len(_listCpt) > 0:
        return float(np.max(_listCpt))
    else:
        return 0


def np_min(_listCpt):
    if len(_listCpt) > 0:
        return float(np.min(_listCpt))
    else:
        return 0


def np_med(_listCpt):
    if len(_listCpt) > 0:
        return float(np.median(_listCpt))
    else:
        return 0
