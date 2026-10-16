"""裁决⑥ DataFrame 直传测试：转换注册 bundle → read_xlsx_sheets 命中 → 未命中回退磁盘。"""

import pandas as pd
import pytest

import battery_analysis.ndax.converter as conv
from battery_analysis.ndax.converter import convert_one
from battery_analysis.utils.data_bundle import DataBundle, bundle_cache
from battery_analysis.utils.readers.xlsx_reader import read_xlsx_sheets


def _fake_df() -> pd.DataFrame:
    return pd.DataFrame({
        "Cycle": [1, 1, 2],
        "Step": [2, 4, 4],
        "Status": ["CC_DChg", "Pulse", "Pulse"],
        "Current(mA)": [-30.0, -26.0, -15.0],
        "Voltage": [3.5, 3.4, 3.3],
        "Charge_Capacity(mAh)": [10.0, 12.0, 14.0],
        "Discharge_Capacity(mAh)": [8.0, 11.0, 13.5],
        "Timestamp": ["2025-06-10 10:00:00", "2025-06-10 10:05:00", "2025-06-10 10:10:00"],
    })


@pytest.fixture
def converted(tmp_path, monkeypatch):
    monkeypatch.setattr(conv.nda, "read", lambda *a, **kw: _fake_df())
    ndax_path = tmp_path / "sample.ndax"
    ndax_path.write_bytes(b"\x00")
    xlsx_path = tmp_path / "sample.xlsx"
    bundle_cache.clear()
    out = convert_one(ndax_path, xlsx_path)
    yield out, xlsx_path
    bundle_cache.clear()


class TestBundleRegistration:

    def test_convert_one_returns_path(self, converted):
        _out, xlsx_path = converted
        assert _out == str(xlsx_path)
        assert xlsx_path.exists()

    def test_bundle_registered_and_matches_disk(self, converted):
        out, xlsx_path = converted
        mem = read_xlsx_sheets(out)
        bundle_cache.clear()  # 清掉后走磁盘
        disk = read_xlsx_sheets(str(xlsx_path))
        for mem_df, disk_df in zip(mem, disk):
            pd.testing.assert_frame_equal(
                mem_df.reset_index(drop=True), disk_df.reset_index(drop=True),
                check_dtype=False,
            )
        # battery_name 兼容：行0 列0（文件名行）在直传与磁盘两侧语义一致
        assert mem[0].iloc[0, 0] == disk[0].iloc[0, 0] == "sample.ndax"


class TestBundleResolver:

    def test_miss_returns_none(self, tmp_path):
        assert bundle_cache.get(tmp_path / "nope.xlsx") is None

    def test_path_key_is_case_insensitive_dir(self, tmp_path):
        bundle = DataBundle(
            cycle=pd.DataFrame([[None]]), step=pd.DataFrame([[None]]), record=pd.DataFrame([[None]]),
        )
        key = tmp_path / "a.xlsx"
        bundle_cache.register(key, bundle)
        alt = tmp_path / "A.xlsx"  # Windows 大小写不敏感路径
        import os
        if os.path.normcase("A") == os.path.normcase("a"):
            assert bundle_cache.get(alt) is bundle

    def test_clear(self, tmp_path):
        bundle_cache.register(tmp_path / "a.xlsx", DataBundle(
            pd.DataFrame(), pd.DataFrame(), pd.DataFrame()))
        bundle_cache.clear()
        assert bundle_cache.get(tmp_path / "a.xlsx") is None

    def test_disk_read_still_works_without_bundle(self, converted):
        _out, xlsx_path = converted
        bundle_cache.clear()
        cycle_df, step_df, record_df = read_xlsx_sheets(str(xlsx_path))
        assert len(cycle_df) >= 3 and len(step_df) >= 3 and len(record_df) >= 5
