"""data_loader.csv_read 行为测试"""

from unittest.mock import Mock

from battery_analysis.main.visualization.data_loader import DataLoaderMixin


class _StubDataLoader(DataLoaderMixin):
    """最小 DataLoader 实现，覆盖 csv_read 依赖的钩子"""

    def __init__(self, csv_path):
        self.strInfoImageCsvPath = str(csv_path)
        self.strPltPath = str(csv_path.parent)
        self.listBatteryName = ["Battery_1"]
        self.intCurrentLevelNum = 1
        self.intBatteryNum = 0
        self.last_data_path = None
        self.listPlt = [[0, 1, True, 2, 3, 4]]
        self.processed_rows = 0

    def _initialize_data_structures(self):
        self.listPlt = [[0, 1, True, 2, 3, 4]]

    def _process_csv_data(self, csvreader):
        self.processed_rows = sum(1 for _ in csvreader)

    def _parse_battery_names(self):
        pass

    def _filter_all_data(self):
        pass


class TestCsvRead:
    def test_processes_all_rows(self, tmp_path):
        csv_path = tmp_path / "Info_Image.csv"
        csv_path.write_text("\n".join(f"{i},0,0,0,0" for i in range(20)), encoding="utf-8")
        loader = _StubDataLoader(csv_path)
        loader.csv_read()
        assert loader.processed_rows == 20
        assert loader.intBatteryNum == 1

    def test_rejects_too_few_rows(self, tmp_path):
        csv_path = tmp_path / "Info_Image.csv"
        csv_path.write_text("a,b,c\n", encoding="utf-8")
        loader = _StubDataLoader(csv_path)
        loader.csv_read()
        assert loader.intBatteryNum == 0


class TestGetPulseCurrentLevel:
    """_get_pulse_current_level 兜底行为（默认值来自 config_defaults）"""

    def test_falls_back_to_config_defaults(self, tmp_path):
        from battery_analysis.utils.config_defaults import DEFAULT_CONFIG

        loader = _StubDataLoader(tmp_path / "Info_Image.csv")
        result = loader._get_pulse_current_level()
        assert result == list(DEFAULT_CONFIG["battery"]["pulseCurrents"])
        assert result == [30, 26, 15, 6]  # 30.0 == 30，档位一致

    def test_uses_configured_values(self, tmp_path):
        loader = _StubDataLoader(tmp_path / "Info_Image.csv")
        svc = Mock()
        svc.get_config_value.return_value = [7, 12]
        loader._config_service = svc
        assert loader._get_pulse_current_level() == [7, 12]
        svc.get_config_value.assert_called_once_with("battery.pulseCurrents", [30, 26, 15, 6])

    def test_invalid_config_falls_back(self, tmp_path):
        loader = _StubDataLoader(tmp_path / "Info_Image.csv")
        svc = Mock()
        svc.get_config_value.side_effect = ValueError("bad")
        loader._config_service = svc
        assert loader._get_pulse_current_level() == [30, 26, 15, 6]

    def test_empty_config_falls_back(self, tmp_path):
        loader = _StubDataLoader(tmp_path / "Info_Image.csv")
        svc = Mock()
        svc.get_config_value.return_value = []
        loader._config_service = svc
        assert loader._get_pulse_current_level() == [30, 26, 15, 6]


class TestSpecListsDeriveFromRules:
    """listCoinCell/listPouchCell 由 battery.rules 派生，不再读 battery.specifications"""

    def test_derived_from_rules(self, tmp_path):
        loader = _StubDataLoader(tmp_path / "Info_Image.csv")
        svc = Mock()

        def _fake_get(key, default=None):
            if key == "battery.rules":
                return [
                    "CR2450/1S1P/600/550/380/1.0",
                    "CF583083/1S1P/4000/4000/80%/5.0",
                ]
            return default

        svc.get_config_value.side_effect = _fake_get
        loader._config_service = svc
        loader._read_configurations()
        assert loader.listCoinCell == ["CR2450"]
        assert loader.listPouchCell == ["CF583083"]

    def test_no_service_gives_empty_lists(self, tmp_path):
        loader = _StubDataLoader(tmp_path / "Info_Image.csv")
        loader._read_configurations()
        assert loader.listCoinCell == []
        assert loader.listPouchCell == []


class TestFilterDataEmptyLevel:
    """filter_data 空档位防御：某电池行无数据时返回空列表，不崩溃且索引对齐"""

    def test_empty_row_returns_empty_and_aligned(self, tmp_path):
        loader = _StubDataLoader(tmp_path / "Info_Image.csv")
        charge = [[1, 2, 3], [], [4, 5, 6]]
        voltage = [[4.2, 4.1, 4.0], [], [3.9, 3.8, 3.7]]

        filtered_charge, filtered_voltage = loader.filter_data(charge, voltage)

        assert len(filtered_charge) == 3
        assert filtered_charge[1] == []
        assert filtered_voltage[1] == []
        assert len(filtered_charge[0]) > 0
        assert len(filtered_charge[2]) > 0

    def test_all_rows_empty(self, tmp_path):
        loader = _StubDataLoader(tmp_path / "Info_Image.csv")
        filtered_charge, filtered_voltage = loader.filter_data([[], []], [[], []])
        assert filtered_charge == [[], []]
        assert filtered_voltage == [[], []]
