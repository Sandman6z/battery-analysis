"""data_loader.csv_read 行为测试"""

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
