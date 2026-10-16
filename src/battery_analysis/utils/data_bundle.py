"""进程内 DataFrame bundle 缓存（裁决⑥：ndax→分析内存直传）。

xlsx 中间格式本质是三张表（cycle/step/record）的序列化。转换端把三表
内存形态（与 read_xlsx_sheets 返回结构一致：文件名行 + 表头行 + 数据行）
按 xlsx 路径注册到本缓存；分析端 read_xlsx_sheets 先查缓存命中即直传，
未命中回落磁盘读取（纯 xlsx 工作流、进程重启后回落，行为完全兼容）。

注意：转换在 ProcessPool 子进程内执行时，子进程注册对父进程不可见——
父进程必须在 as_completed 回收结果时重新 register（见 convert_batch /
ConvertWorker）。
"""

import os
from collections import OrderedDict
from typing import NamedTuple

import pandas as pd


class DataBundle(NamedTuple):
    """三表内存形态，顺序与 read_xlsx_sheets 返回值一致。"""

    cycle: pd.DataFrame
    step: pd.DataFrame
    record: pd.DataFrame


class _BundleCache:
    """路径（normcase+abspath）→ DataBundle，LRU 上限 64。"""

    def __init__(self) -> None:
        self._cache: OrderedDict[str, DataBundle] = OrderedDict()

    @staticmethod
    def _key(path) -> str:
        return os.path.normcase(os.path.abspath(str(path)))

    def register(self, xlsx_path, bundle: DataBundle) -> None:
        """注册（或覆盖）某 xlsx 路径对应的内存 bundle；超出容量淘汰最旧。"""
        key = self._key(xlsx_path)
        self._cache[key] = bundle
        self._cache.move_to_end(key)
        while len(self._cache) > 64:
            self._cache.popitem(last=False)

    def get(self, xlsx_path) -> DataBundle | None:
        """查询 bundle；未命中返回 None（调用方回落磁盘读取）。"""
        return self._cache.get(self._key(xlsx_path))

    def clear(self) -> None:
        """清空缓存（测试/需要强制走磁盘时用）。"""
        self._cache.clear()


bundle_cache = _BundleCache()
