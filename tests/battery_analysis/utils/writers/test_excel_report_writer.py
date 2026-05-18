# -*- coding: utf-8 -*-
"""
ExcelReportWriter 单元测试

测试策略：
- mock xlsxwriter.Workbook 避免创建真实文件
- 使用真实的采样数据构造 ExcelReportWriter 实例
- 逐方法测试，重点在数据推导和布局计算
"""

import copy
import math
from unittest.mock import MagicMock, PropertyMock, patch, call

import pytest
import xlsxwriter as xwt

from battery_analysis.utils.writers.excel_report_writer import ExcelReportWriter, _compute_list_cpt, _compute_statistics


# ── Helper ──

@pytest.fixture
def fmts():
    """完整的格式字典，所有写方法需要使用"""
    keys = [
        "result_data", "result_data_italic",
        "overview_stat", "overview_stat_dark", "overview_stat_light", "overview_stat_light_bold",
        "sample_line", "sample_data", "sample_data_bold",
        "sample_data_pct", "sample_data_pct_bold", "sample_data_yellow",
        "word_line", "word_data", "word_data_bold",
        "word_data_pct", "word_data_pct_bold", "word_data_yellow",
        "hyperlink",
    ]
    return {k: MagicMock() for k in keys}


# ── 采样数据 ──

SAMPLE_TEST_INFO = [
    "Coin Cell",           # 0: 电池类型
    "Wind",                # 1: 构造方式
    "LCO",                 # 2: 电池材料
    "ICR18650",            # 3: 规格
    "Ewin",                # 4: 制造商
    "DC2401",              # 5: 批次/日期代码
    "85",                  # 6: Samples Qty
    "25:00:00",            # 7: 温度（含冒号，测试 safe_temperature）
    "1800",                # 8: Datasheet Nominal Capacity
    "1750",                # 9: Calculation Nominal Capacity
    "2",                   # 10: Accelerated Aging
    "Lab-A.Site-1",       # 11: Tester location
    "Sandman",             # 12: Tested By
    "/path/to/test.profile",  # 13: Test Profile
    [100, 200, 500],       # 14: listCurrentLevel
    [2.0, 2.25, 2.5, 2.75],  # 15: listVoltageLevel
    30,                    # 16: 起始版本号 (int)
    1575,                  # 17: Required Usable Capacity
]

SAMPLE_BATTERY_INFO = [
    # listBatteryCharge — 3 batteries × 12 charge values (3 current × 4 voltage)
    [
        [1810, 1790, 1750, 1700,  1620, 1580, 1520, 1480,  1350, 1300, 1250, 1200],
        [1800, 1780, 1740, 1690,  1610, 1570, 1510, 1470,  1340, 1290, 1240, 1190],
        [1820, 1800, 1760, 1710,  1630, 1590, 1530, 1490,  1360, 1310, 1260, 1210],
    ],
    ["BAT-001", "BAT-002", "BAT-003"],  # listBatteryName
    ["2024-01-15 10:00:00", "2024-01-15 14:30:00"],  # listBatteryInfo[2] — date range
]


# ── Fixtures ──

@pytest.fixture
def mock_workbook():
    """mock xlsxwriter.Workbook 和 add_worksheet/set_column/close"""
    wb = MagicMock(spec=xwt.Workbook)
    ws = MagicMock()
    wb.add_worksheet.return_value = ws
    return wb


@pytest.fixture
def writer(tmp_path):
    """构造真实的 ExcelReportWriter 实例，结果路径指向 tmp_path"""
    result_path = str(tmp_path / "results")
    return ExcelReportWriter(
        strResultPath=result_path,
        listTestInfo=copy.deepcopy(SAMPLE_TEST_INFO),
        listBatteryInfo=copy.deepcopy(SAMPLE_BATTERY_INFO),
    )


@pytest.fixture
def writer_coin_cell():
    """Coin Cell 类型的 writer"""
    info = copy.deepcopy(SAMPLE_TEST_INFO)
    info[0] = "Coin Cell"
    return ExcelReportWriter("/tmp/r", info, copy.deepcopy(SAMPLE_BATTERY_INFO))


@pytest.fixture
def writer_pouch_cell():
    """Pouch Cell 类型的 writer"""
    info = copy.deepcopy(SAMPLE_TEST_INFO)
    info[0] = "Pouch Cell"
    return ExcelReportWriter("/tmp/r", info, copy.deepcopy(SAMPLE_BATTERY_INFO))


# ── __init__ ──

class TestInit:
    """构造函数测试"""

    def test_derives_current_and_voltage_levels(self, writer):
        assert writer.listCurrentLevel == [100, 200, 500]
        assert writer.listVoltageLevel == [2.0, 2.25, 2.5, 2.75]
        assert writer.intCurrentLevelNum == 3
        assert writer.intVoltageLevelNum == 4

    def test_derives_file_current_type_string(self, writer):
        assert writer.strFileCurrentType == "100-200-500"

    def test_derives_battery_info(self, writer):
        assert writer.intBatteryNum == 3
        assert writer.listBatteryName == ["BAT-001", "BAT-002", "BAT-003"]
        assert len(writer.listBatteryCharge) == 3

    def test_derives_png_paths(self, writer):
        assert len(writer.listPngPath) == 3
        for i, level in enumerate([100, 200, 500]):
            assert f"{level}mA" in writer.listPngPath[i]
            assert "UseableCapacityOverCutoffVoltage" in writer.listPngPath[i]

    def test_result_xlsx_path_includes_temperature_safe(self, writer):
        assert "25_00_00" in writer.strResultXlsxPath
        assert writer.strResultXlsxPath.endswith(".xlsx")

    def test_sample_xlsx_path(self, writer):
        assert "Sample_" in writer.strSampleXlsxPath
        assert writer.strSampleXlsxPath.endswith(".xlsx")

    def test_report_word_path(self, writer):
        assert writer.strReportWordPath.endswith(".docx")
        assert "Ewin" in writer.strReportWordPath
        assert "LCO" in writer.strReportWordPath
        assert "DC2401" in writer.strReportWordPath

    def test_temperature_colon_replaced_safely(self):
        """冒号在文件名中被替换为下划线"""
        info = copy.deepcopy(SAMPLE_TEST_INFO)
        info[7] = "45:30:15"
        w = ExcelReportWriter("/tmp/r", info, copy.deepcopy(SAMPLE_BATTERY_INFO))
        assert "45_30_15" in w.strResultXlsxPath
        assert "45_30_15" in w.strSampleXlsxPath


# ── _create_formats ──

class TestCreateFormats:
    """格式创建测试"""

    def test_returns_dict_with_all_keys(self, writer, mock_workbook):
        fmts = writer._create_formats(mock_workbook, mock_workbook)
        expected_keys = [
            "result_data", "result_data_italic",
            "overview_stat", "overview_stat_dark", "overview_stat_light", "overview_stat_light_bold",
            "sample_line", "sample_data", "sample_data_bold",
            "sample_data_pct", "sample_data_pct_bold", "sample_data_yellow",
            "word_line", "word_data", "word_data_bold",
            "word_data_pct", "word_data_pct_bold", "word_data_yellow",
            "hyperlink",
        ]
        for key in expected_keys:
            assert key in fmts, f"Missing format key: {key}"


# ── _write_overview_header ──

class TestWriteOverviewHeader:
    """Overview 表头测试"""

    def test_writes_header_lines(self, writer):
        ws = MagicMock()
        writer._write_overview_header(ws)
        assert ws.write.call_count == 12  # 12 header lines

    def test_header_contains_key_info(self, writer):
        ws = MagicMock()
        writer._write_overview_header(ws)
        text_calls = [c[0][2] for c in ws.write.call_args_list]
        assert any("#BATTERY CHARACTERISTICS" in t for t in text_calls)
        assert any("LCO" in t for t in text_calls)
        assert any("ICR18650" in t for t in text_calls)
        assert any("Ewin" in t for t in text_calls)


# ── _write_result_columns ──

class TestWriteResultColumns:
    """结果表列名测试"""

    def test_writes_battery_label(self, writer, fmts):
        ws = MagicMock()
        writer._write_result_columns(ws, fmts)
        ws.write.assert_any_call(2, 0, "Battery", fmts['result_data'])

    def test_writes_stat_row_labels(self, writer, fmts):
        ws = MagicMock()
        writer._write_result_columns(ws, fmts)
        labels = [c[0][2] for c in ws.write.call_args_list]
        for label in ("Mean(μ)", "Median", "Std. Var.(σ)", "μ-3σ", "μ-2σ", "μ+2σ", "μ+3σ", "Minimum", "Maximum"):
            assert label in labels, f"Missing stat label: {label}"

    def test_writes_current_level_headers(self, writer, fmts):
        ws = MagicMock()
        writer._write_result_columns(ws, fmts)
        text_calls = [c[0][2] for c in ws.write.call_args_list]
        for level in ["100mA", "200mA", "500mA"]:
            assert level in text_calls

    def test_writes_voltage_level_headers(self, writer, fmts):
        ws = MagicMock()
        writer._write_result_columns(ws, fmts)
        text_calls = [c[0][2] for c in ws.write.call_args_list]
        for volt in ["2.0V", "2.25V", "2.5V", "2.75V"]:
            assert volt in text_calls


# ── _write_battery_data ──

class TestWriteBatteryData:
    """电池数据写入测试"""

    def test_writes_all_battery_names(self, writer, fmts):
        ws = MagicMock()
        writer._write_battery_data(ws, fmts)
        names_written = [c[0][2] for c in ws.write.call_args_list if isinstance(c[0][2], str) and c[0][2].startswith("BAT-")]
        assert names_written == ["BAT-001", "BAT-002", "BAT-003"]

    def test_writes_charge_data(self, writer, fmts):
        ws = MagicMock()
        writer._write_battery_data(ws, fmts)
        # 每个电池 12 个 charge 值 = 36 次 write 调用
        charge_writes = [c for c in ws.write.call_args_list if not isinstance(c[0][2], str)]
        assert len(charge_writes) == 3 * 12  # all charge values written


# ── _write_result_statistics ──

class TestWriteResultStatistics:
    """统计值写入测试"""

    @pytest.fixture
    def stats(self):
        return {
            'mean': [[1800]*4, [1600]*4, [1400]*4],
            'med': [[1805]*4, [1605]*4, [1405]*4],
            'std': [[10]*4, [8]*4, [9]*4],
            'mm3s': [[1770]*4, [1576]*4, [1373]*4],
            'mm2s': [[1780]*4, [1584]*4, [1382]*4],
            'mp2s': [[1820]*4, [1616]*4, [1418]*4],
            'mp3s': [[1830]*4, [1624]*4, [1427]*4],
            'min': [[1790]*4, [1580]*4, [1390]*4],
            'max': [[1810]*4, [1620]*4, [1410]*4],
        }

    def test_writes_all_stat_rows(self, writer, stats, fmts):
        ws = MagicMock()
        writer._write_result_statistics(ws, stats, fmts)
        # 9 stat rows × 3 current × 4 voltage = 108
        assert len(ws.write.call_args_list) == 108


# ── _prepare_sample_content ──

class TestPrepareSampleContent:
    """样本表内容准备测试"""

    @pytest.fixture
    def stats(self):
        return {
            'mean': [[1800, 1790, 1750, 1700], [1620, 1580, 1520, 1480], [1350, 1300, 1250, 1200]],
            'med': [[1800, 1780, 1740, 1690], [1610, 1570, 1510, 1470], [1340, 1290, 1240, 1190]],
            'std': [[10, 10, 10, 10], [10, 10, 10, 10], [10, 10, 10, 10]],
            'mm3s': [[1770, 1760, 1720, 1670], [1590, 1550, 1490, 1450], [1320, 1270, 1220, 1170]],
            'mm2s': [[1780, 1770, 1730, 1680], [1600, 1560, 1500, 1460], [1330, 1280, 1230, 1180]],
            'mp2s': [[1820, 1810, 1770, 1720], [1640, 1600, 1540, 1500], [1370, 1320, 1270, 1220]],
            'mp3s': [[1830, 1820, 1780, 1730], [1650, 1610, 1550, 1510], [1380, 1330, 1280, 1230]],
            'min': [[1790, 1780, 1740, 1690], [1610, 1570, 1510, 1470], [1340, 1290, 1240, 1190]],
            'max': [[1810, 1800, 1760, 1710], [1630, 1590, 1530, 1490], [1360, 1310, 1260, 1210]],
        }

    def test_identifies_max_current_position(self, writer, stats):
        sample = writer._prepare_sample_content(stats)
        assert sample['intPosiMaxmA'] == 2  # 500mA is max

    def test_identifies_2_25v_position(self, writer, stats):
        sample = writer._prepare_sample_content(stats)
        assert sample['intPosi2V25'] == 1  # 2.25V is index 1

    def test_test_profile_start_line_for_coin_cell(self, writer_coin_cell, stats):
        sample = writer_coin_cell._prepare_sample_content(stats)
        assert sample['intTestProfileStartLine'] == 3

    def test_test_profile_start_line_for_pouch_cell(self, writer_pouch_cell, stats):
        sample = writer_pouch_cell._prepare_sample_content(stats)
        assert sample['intTestProfileStartLine'] == 4

    def test_actual_measured_capacity_length(self, writer, stats):
        sample = writer._prepare_sample_content(stats)
        # intVoltageLevelNum * 2
        assert sample['intActualMeasuredCapacityLength'] == 8

    def test_str_content_includes_test_info(self, writer, stats):
        sample = writer._prepare_sample_content(stats)
        content = sample['listStrContent']
        assert content[0] == "Coin Cell"
        assert content[1] == "LCO-ICR18650"
        assert content[2] == "Ewin"
        assert content[3] == "Wind"

    def test_result_pass_when_mm2s_meets_requirement(self, writer, stats):
        """Required 1575, mm2s at 500mA/2.25V = 1280, 1280/1750 = 73% < 1575/1750=90% => Fail"""
        sample = writer._prepare_sample_content(stats)
        # 1575/1750 = 90%, mm2s[2][1] = 1280, 1280/1750 ≈ 73.1%
        assert sample['listStrContent'][17] == "Fail"

    def test_result_pass_when_mm2s_meets_requirement(self, writer, stats):
        """修改 required capacity 很低，确保 pass"""
        info = copy.deepcopy(SAMPLE_TEST_INFO)
        info[17] = 100  # Required Usable Capacity = 100
        w = ExcelReportWriter("/tmp/r", info, copy.deepcopy(SAMPLE_BATTERY_INFO))
        sample = w._prepare_sample_content(stats)
        assert sample['listStrContent'][17] == "Pass"

    def test_str_content_includes_date_range(self, writer, stats):
        sample = writer._prepare_sample_content(stats)
        date_str = sample['listStrContent'][14]
        assert "15.01.2024" in date_str  # format: dd.mm.yyyy

    def test_str_items_contains_all_labels(self, writer, stats):
        sample = writer._prepare_sample_content(stats)
        items = sample['listStrItems']
        assert items[0] == "Battery Type"
        assert "Actual Measured Capacity" in items[13]
        assert items[19] == "Remarks"


# ── _insert_images ──

class TestInsertImages:
    """图像插入测试"""

    def test_inserts_one_image_per_current_level(self, writer):
        ws = MagicMock()
        writer._insert_images(ws)
        assert ws.insert_image.call_count == writer.intCurrentLevelNum

    def test_insert_image_with_scaling(self, writer):
        ws = MagicMock()
        writer._insert_images(ws)
        for call_args in ws.insert_image.call_args_list:
            args = call_args[0]
            # insert_image(row, col, filename, options_dict)
            options = args[3] if len(args) >= 4 else {}
            assert 'x_scale' in options
            assert 'y_scale' in options


# ── _write_overview_statistics ──

class TestWriteOverviewStatistics:
    """Overview 统计表测试"""

    @pytest.fixture
    def stats(self):
        return {
            'mean': [[1800, 1790, 1750, 1700], [1620, 1580, 1520, 1480], [1350, 1300, 1250, 1200]],
            'med': [[1795, 1785, 1745, 1695], [1615, 1575, 1515, 1475], [1345, 1295, 1245, 1195]],
            'std': [[10, 10, 10, 10], [10, 10, 10, 10], [10, 10, 10, 10]],
            'mm3s': [[1770, 1760, 1720, 1670], [1590, 1550, 1490, 1450], [1320, 1270, 1220, 1170]],
            'mm2s': [[1780, 1770, 1730, 1680], [1600, 1560, 1500, 1460], [1330, 1280, 1230, 1180]],
            'mp2s': [[1820, 1810, 1770, 1720], [1640, 1600, 1540, 1500], [1370, 1320, 1270, 1220]],
            'mp3s': [[1830, 1820, 1780, 1730], [1650, 1610, 1550, 1500], [1380, 1330, 1280, 1230]],
            'min': [[1790, 1780, 1740, 1690], [1610, 1570, 1510, 1470], [1340, 1290, 1240, 1190]],
            'max': [[1810, 1800, 1760, 1710], [1630, 1590, 1530, 1490], [1360, 1310, 1260, 1210]],
        }

    def test_writes_statistical_results_title(self, writer, stats, fmts):
        ws = MagicMock()
        writer._write_overview_statistics(ws, stats, fmts)
        ws.write.assert_any_call(13, 0, "Statisticals Results", fmts['overview_stat_dark'])

    def test_writes_voltage_headers(self, writer, stats, fmts):
        ws = MagicMock()
        writer._write_overview_statistics(ws, stats, fmts)
        assert ws.write_rich_string.call_count >= 4  # 4 voltage levels + 3 current levels

    def test_uses_custom_start_line(self, writer, stats, fmts):
        ws = MagicMock()
        writer._write_overview_statistics(ws, stats, fmts, wsOverviewStatisticalStartLine=5)
        ws.write.assert_any_call(5, 0, "Statisticals Results", fmts['overview_stat_dark'])


# ── _write_sample_excel ──

class TestWriteSampleExcel:
    """Sample Excel 工作表写入测试"""

    @pytest.fixture
    def stats(self):
        return {
            'mean': [[1800, 1790, 1750, 1700], [1620, 1580, 1520, 1480], [1350, 1300, 1250, 1200]],
            'med': [[1795, 1785, 1745, 1695], [1615, 1575, 1515, 1475], [1345, 1295, 1245, 1195]],
            'std': [[10, 10, 10, 10], [10, 10, 10, 10], [10, 10, 10, 10]],
            'mm3s': [[1770, 1760, 1720, 1670], [1590, 1550, 1490, 1450], [1320, 1270, 1220, 1170]],
            'mm2s': [[1780, 1770, 1730, 1680], [1600, 1560, 1500, 1460], [1330, 1280, 1230, 1180]],
            'mp2s': [[1820, 1810, 1770, 1720], [1640, 1600, 1540, 1500], [1370, 1320, 1270, 1220]],
            'mp3s': [[1830, 1820, 1780, 1730], [1650, 1610, 1550, 1500], [1380, 1330, 1280, 1230]],
            'min': [[1790, 1780, 1740, 1690], [1610, 1570, 1510, 1470], [1340, 1290, 1240, 1190]],
            'max': [[1810, 1800, 1760, 1710], [1630, 1590, 1530, 1490], [1360, 1310, 1260, 1210]],
        }

    @pytest.fixture
    def sample(self, writer, stats):
        return writer._prepare_sample_content(stats)

    def test_writes_content_to_correct_rows(self, writer, sample, stats, fmts):
        ws = MagicMock()
        writer._write_sample_excel(ws, sample, stats, fmts)
        # Must have written something
        assert ws.write.call_count > 0 or ws.merge_range.call_count > 0

    def test_includes_battery_info_in_content(self, writer, sample, stats, fmts):
        ws = MagicMock()
        writer._write_sample_excel(ws, sample, stats, fmts)
        content_calls = [c[0][2] for c in ws.write.call_args_list if not isinstance(c[0][2], (int, float))]
        assert "LCO-ICR18650" in content_calls
        assert "Wind" in content_calls


# ── _write_sample_word ──

class TestWriteSampleWord:
    """Sample Word 工作表写入测试"""

    @pytest.fixture
    def stats(self):
        return {
            'mean': [[1800]*4, [1600]*4, [1400]*4],
            'med': [[1795]*4, [1615]*4, [1345]*4],
            'std': [[10]*4, [10]*4, [10]*4],
            'mm3s': [[1770]*4, [1590]*4, [1320]*4],
            'mm2s': [[1780]*4, [1600]*4, [1330]*4],
            'mp2s': [[1820]*4, [1640]*4, [1370]*4],
            'mp3s': [[1830]*4, [1650]*4, [1380]*4],
            'min': [[1790]*4, [1610]*4, [1340]*4],
            'max': [[1810]*4, [1630]*4, [1360]*4],
        }

    @pytest.fixture
    def sample(self, writer, stats):
        return writer._prepare_sample_content(stats)

    def test_writes_content(self, writer, sample, stats, fmts):
        ws = MagicMock()
        writer._write_sample_word(ws, sample, stats, fmts)
        assert ws.write.call_count > 0 or ws.merge_range.call_count > 0


# ── write() 主入口 ──

class TestWriteMain:
    """write() 主入口测试"""

    @patch("xlsxwriter.Workbook")
    def test_creates_two_workbooks(self, mock_wb_class, writer):
        mock_wb = MagicMock()
        mock_wb_class.return_value = mock_wb
        writer.write()
        # Should create 2 workbooks (result + sample)
        assert mock_wb_class.call_count == 2

    @patch("xlsxwriter.Workbook")
    def test_adds_four_worksheets(self, mock_wb_class, writer):
        mock_wb = MagicMock()
        mock_wb_class.return_value = mock_wb
        writer.write()
        # Result workbook: overview + result, Sample workbook: word + excel
        assert mock_wb.add_worksheet.call_count == 4

    @patch("xlsxwriter.Workbook")
    def test_closes_both_workbooks(self, mock_wb_class, writer):
        mock_wb = MagicMock()
        mock_wb_class.return_value = mock_wb
        writer.write()
        assert mock_wb.close.call_count == 2

    @patch("xlsxwriter.Workbook")
    def test_accepts_precomputed_stats(self, mock_wb_class, writer):
        mock_wb = MagicMock()
        mock_wb_class.return_value = mock_wb
        # Match writer dimensions: 3 current × 4 voltage
        stats = {
            'mean': [[1800]*4, [1600]*4, [1400]*4],
            'med': [[1795]*4, [1595]*4, [1395]*4],
            'std': [[10]*4, [8]*4, [9]*4],
            'mm3s': [[1770]*4, [1576]*4, [1373]*4],
            'mm2s': [[1780]*4, [1584]*4, [1382]*4],
            'mp2s': [[1820]*4, [1616]*4, [1418]*4],
            'mp3s': [[1830]*4, [1624]*4, [1427]*4],
            'min': [[1790]*4, [1580]*4, [1390]*4],
            'max': [[1810]*4, [1620]*4, [1410]*4],
        }
        writer.write(list_cpt=None, stats=stats)


# ── 向后兼容别名 ──

class TestBackwardsCompatibilityAliases:
    """模块级 _compute_list_cpt / _compute_statistics 别名测试"""

    def test_compute_list_cpt_aliased(self):
        from battery_analysis.utils.writers.statistics_utils import compute_list_cpt
        assert _compute_list_cpt is compute_list_cpt

    def test_compute_statistics_aliased(self):
        from battery_analysis.utils.writers.statistics_utils import compute_statistics
        assert _compute_statistics is compute_statistics
