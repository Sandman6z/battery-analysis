from unittest.mock import Mock, patch

import pytest

from battery_analysis.utils.data_bundle import DataBundle, bundle_cache
from battery_analysis.utils.exceptions import BatteryAnalysisException
from battery_analysis.utils.processors.battery_analysis import BatteryAnalysis
from battery_analysis.utils.readers.xlsx_reader import read_xlsx_sheets


class TestBatteryAnalysis:
    def test_uba_get_test_date_from_excel(self, sample_xlsx_with_test_date):
        """UBA_GetTestDateFromExcel 应委托 extract_test_date_from_xls 返回 YYYYMMDD"""
        analysis = Mock(spec=BatteryAnalysis)
        analysis.UBA_GetTestDateFromExcel = BatteryAnalysis.UBA_GetTestDateFromExcel.__get__(
            analysis
        )
        result = analysis.UBA_GetTestDateFromExcel(str(sample_xlsx_with_test_date))
        assert result == "20250610"

    def test_str_compare_date(self):
        # 测试日期比较方法
        date1 = "2025-01-01 12:00:00"
        date2 = "2025-01-02 12:00:00"

        # 直接调用静态方法，不经过 Mock
        result = BatteryAnalysis._str_compare_date(date1, date2, True)
        assert result == date1

        result = BatteryAnalysis._str_compare_date(date1, date2, False)
        assert result == date2

    def test_parallel_process_file_normalizes_read_failure(self, sample_xlsx):
        """read_xlsx_sheets 失败时应归一化为 BatteryAnalysisException，而非走 xlrd 回退"""
        args = (str(sample_xlsx), [500, 1000], [3.0, 4.0])
        with (
            patch(
                "battery_analysis.utils.processors.battery_analysis.read_xlsx_sheets",
                side_effect=ValueError("simulated corrupt file"),
            ),
            pytest.raises(BatteryAnalysisException, match="Failed to read Excel file"),
        ):
            BatteryAnalysis._parallel_process_file(args)


class TestInProcessBundlePath:
    """裁决⑥ 进程内直传：bundle 路径必须与磁盘路径产出完全一致。

    用 object.__new__ 绕过 __init__（其会自动 run() 写 CSV），只手动装配
    _process_bundles_in_process / run 分支所需的属性。
    """

    LEVELS = [4.0]
    VOLTS = [4.2, 3.8, 2.5]

    @staticmethod
    def _bare_analysis(xlsx_paths, levels, volts):
        analysis = object.__new__(BatteryAnalysis)
        analysis.listAllInXlsx = [str(p) for p in xlsx_paths]
        analysis.listCurrentLevel = levels
        analysis.listVoltageLevel = volts
        analysis._progress_callback = None
        return analysis

    def test_analyze_frames_matches_parallel_process_file(self, sample_xlsx):
        """抽出的 _analyze_frames 与旧 _parallel_process_file（读盘后调它）一致"""
        disk = BatteryAnalysis._parallel_process_file(
            (str(sample_xlsx), self.LEVELS, self.VOLTS)
        )
        cycle_df, step_df, record_df = read_xlsx_sheets(str(sample_xlsx))
        frames = BatteryAnalysis._analyze_frames(
            str(sample_xlsx), cycle_df, step_df, record_df, self.LEVELS, self.VOLTS
        )
        assert disk == frames

    def test_process_bundles_in_process_equals_disk_path(self, sample_xlsx):
        """内存 bundle 路径结果 == 磁盘路径结果（直传不改变分析输出）"""
        cycle_df, step_df, record_df = read_xlsx_sheets(str(sample_xlsx))
        bundle = DataBundle(cycle=cycle_df, step=step_df, record=record_df)
        analysis = self._bare_analysis([sample_xlsx], self.LEVELS, self.VOLTS)

        in_process = analysis._process_bundles_in_process([bundle])
        disk = BatteryAnalysis._parallel_process_file(
            (str(sample_xlsx), self.LEVELS, self.VOLTS)
        )

        assert len(in_process) == 1
        assert in_process[0] == disk

    def test_registered_bundle_is_found_by_run_dispatch(self, sample_xlsx):
        """注册后 bundle_cache.get 能命中，run() 的 all-hit 分支判定为真"""
        cycle_df, step_df, record_df = read_xlsx_sheets(str(sample_xlsx))
        bundle_cache.clear()
        try:
            bundle_cache.register(
                sample_xlsx, DataBundle(cycle=cycle_df, step=step_df, record=record_df)
            )
            got = bundle_cache.get(sample_xlsx)
            assert got is not None
            # 复刻 run() 分支判定式：全部命中 → 进程内
            paths = [str(sample_xlsx)]
            bundles = [bundle_cache.get(p) for p in paths]
            assert all(b is not None for b in bundles)
        finally:
            bundle_cache.clear()

    def test_unregistered_path_falls_back_to_disk_dispatch(self, sample_xlsx):
        """未注册 → bundle_cache.get 返回 None → run() 回退磁盘路径"""
        bundle_cache.clear()
        try:
            bundles = [bundle_cache.get(str(sample_xlsx))]
            assert not all(b is not None for b in bundles)
        finally:
            bundle_cache.clear()

    def test_process_bundles_skips_failing_file(self, sample_xlsx, tmp_path):
        """单文件分析失败时跳过并继续，全部失败才抛异常（对齐子进程语义）"""
        cycle_df, step_df, record_df = read_xlsx_sheets(str(sample_xlsx))
        good = DataBundle(cycle=cycle_df, step=step_df, record=record_df)
        bad = DataBundle(
            cycle=cycle_df.iloc[:0], step=step_df.iloc[:0], record=record_df.iloc[:0]
        )  # 空表 → insufficient data rows
        analysis = self._bare_analysis(["bad.xlsx", sample_xlsx], self.LEVELS, self.VOLTS)

        results = analysis._process_bundles_in_process([bad, good])
        assert len(results) == 1  # 坏的被跳过，好的保留

        all_bad = self._bare_analysis(["bad.xlsx"], self.LEVELS, self.VOLTS)
        with pytest.raises(BatteryAnalysisException, match="All files failed"):
            all_bad._process_bundles_in_process([bad])
