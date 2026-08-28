"""VersionManager单元测试"""

import csv
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from battery_analysis.main.business_logic.version_manager import VersionManager


@pytest.fixture
def version_manager():
    """创建一个带有mock主窗口的VersionManager实例"""
    main_window = MagicMock()
    main_window.lineEdit_InputPath = MagicMock()
    main_window.lineEdit_InputPath.text.return_value = ""
    main_window.lineEdit_OutputPath = MagicMock()
    main_window.lineEdit_OutputPath.text.return_value = ""
    main_window.lineEdit_Version = MagicMock()
    main_window.sha256_checksum = ""
    main_window.sha256_checksum_run = ""
    main_window.statusBar_BatteryAnalysis = MagicMock()
    main_window._get_service.return_value = None
    return VersionManager(main_window)


def create_sha256_csv(tmp_path: Path, checksums: list, times: list):
    """在tmp_path下创建测试用SHA256.csv文件"""
    csv_path = tmp_path / "SHA256.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Checksums:"])
        writer.writerow(checksums)
        writer.writerow(["Times:"])
        writer.writerow(times)
    return csv_path


class TestSetVersion:
    """set_version()方法测试"""

    def test_increments_times_from_0_to_1(self, tmp_path):
        """校验和存在时，Times从0递增到1，版本号显示1.1"""
        csv_path = create_sha256_csv(tmp_path, ["abc123"], ["0"])
        main_window = MagicMock()
        main_window.lineEdit_OutputPath.text.return_value = str(tmp_path)
        main_window.sha256_checksum_run = "abc123"
        main_window.lineEdit_Version = MagicMock()
        main_window.statusBar_BatteryAnalysis = MagicMock()
        main_window._get_service.return_value = None

        vm = VersionManager(main_window)
        vm.set_version()

        # 验证Times已递增
        with open(csv_path, encoding="utf-8") as f:
            reader = list(csv.reader(f))
        assert reader[3] == ["1"]
        # 验证UI已更新
        main_window.lineEdit_Version.setText.assert_called_once_with("1.1")

    def test_increments_from_1_to_2(self, tmp_path):
        """连续调用set_version，Times从1递增到2"""
        csv_path = create_sha256_csv(tmp_path, ["abc123"], ["1"])
        main_window = MagicMock()
        main_window.lineEdit_OutputPath.text.return_value = str(tmp_path)
        main_window.sha256_checksum_run = "abc123"
        main_window.lineEdit_Version = MagicMock()
        main_window.statusBar_BatteryAnalysis = MagicMock()
        main_window._get_service.return_value = None

        vm = VersionManager(main_window)
        vm.set_version()

        with open(csv_path, encoding="utf-8") as f:
            reader = list(csv.reader(f))
        assert reader[3] == ["2"]
        main_window.lineEdit_Version.setText.assert_called_once_with("1.2")

    def test_multiple_checksums_updates_only_matching(self, tmp_path):
        """多个校验和时，只递增匹配的那个，其他不受影响"""
        create_sha256_csv(tmp_path, ["abc123", "def456", "ghi789"], ["5", "3", "7"])
        main_window = MagicMock()
        main_window.lineEdit_OutputPath.text.return_value = str(tmp_path)
        main_window.sha256_checksum_run = "def456"
        main_window.lineEdit_Version = MagicMock()
        main_window.statusBar_BatteryAnalysis = MagicMock()
        main_window._get_service.return_value = None

        vm = VersionManager(main_window)
        vm.set_version()

        csv_path = tmp_path / "SHA256.csv"
        with open(csv_path, encoding="utf-8") as f:
            reader = list(csv.reader(f))
        # def456是第二个checksum（索引1），Times应从3变成4
        assert reader[3] == ["5", "4", "7"]
        # major=matching_index+1=2, times=4 → "2.4"
        main_window.lineEdit_Version.setText.assert_called_once_with("2.4")

    def test_checksum_not_found(self, tmp_path):
        """校验和不存在时，文件不变，版本号不更新"""
        csv_path = create_sha256_csv(tmp_path, ["abc123"], ["1"])
        original_content = csv_path.read_text(encoding="utf-8")

        main_window = MagicMock()
        main_window.lineEdit_OutputPath.text.return_value = str(tmp_path)
        main_window.sha256_checksum_run = "nonexistent"
        main_window.lineEdit_Version = MagicMock()
        main_window.statusBar_BatteryAnalysis = MagicMock()
        main_window._get_service.return_value = None

        vm = VersionManager(main_window)
        with patch.object(vm.logger, "warning") as mock_warning:
            vm.set_version()

        # 文件内容不变
        assert csv_path.read_text(encoding="utf-8") == original_content
        # 发出警告
        mock_warning.assert_called_once()
        # UI版本号不更新
        main_window.lineEdit_Version.setText.assert_not_called()

    def test_output_path_invalid(self, tmp_path):
        """输出路径无效时，set_version不执行写入"""
        main_window = MagicMock()
        main_window.lineEdit_OutputPath.text.return_value = "/nonexistent/path"
        main_window.sha256_checksum_run = "abc123"
        main_window.lineEdit_Version = MagicMock()
        main_window.statusBar_BatteryAnalysis = MagicMock()
        main_window._get_service.return_value = None

        vm = VersionManager(main_window)
        vm.set_version()

        main_window.lineEdit_Version.setText.assert_not_called()

    def test_creates_file_if_not_exists(self, tmp_path):
        """SHA256.csv不存在时，以Times=1创建新文件"""
        main_window = MagicMock()
        main_window.lineEdit_OutputPath.text.return_value = str(tmp_path)
        main_window.sha256_checksum_run = "abc123"
        main_window.lineEdit_Version = MagicMock()
        main_window.statusBar_BatteryAnalysis = MagicMock()
        main_window._get_service.return_value = None

        # 模拟win32api可用
        with patch("win32api.SetFileAttributes"):
            vm = VersionManager(main_window)
            # 确保hasattr检查通过
            vm.main_window = main_window
            vm.set_version()

        csv_path = tmp_path / "SHA256.csv"
        assert csv_path.exists()
        with open(csv_path, encoding="utf-8") as f:
            reader = list(csv.reader(f))
        assert reader[1] == ["abc123"]
        assert reader[3] == ["1"]


class TestGetVersion:
    """get_version()方法测试（P3 改为后台派发后，直接测 task+callback 两个阶段）"""

    def test_reads_existing_times(self, tmp_path):
        """校验和已存在时，读取Times值显示为版本号"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # 创建一个空xlsx文件作为输入
        xlsx_file = input_dir / "test.xlsx"
        xlsx_file.write_bytes(b"dummy excel content")

        create_sha256_csv(output_dir, ["dummy_checksum"], ["3"])

        main_window = MagicMock()
        main_window.lineEdit_InputPath.text.return_value = str(input_dir)
        main_window.lineEdit_OutputPath.text.return_value = str(output_dir)
        main_window.lineEdit_Version = MagicMock()
        main_window.statusBar_BatteryAnalysis = MagicMock()
        main_window._get_service.return_value = None

        # 模拟calc_checksum返回固定值
        with patch(
            "battery_analysis.main.utils.file_utils.FileUtils.calc_checksum",
            return_value="dummy_checksum",
        ):
            vm = VersionManager(main_window)
            vm._checksum_generation = 1
            checksum = vm._calc_checksum_task(str(input_dir))
            vm._on_checksum_ready(checksum, generation=1)

        # 应显示1.3（第一个校验和，Times=3）
        main_window.lineEdit_Version.setText.assert_called_with("1.3")
        # 校验和已回写，供 set_version/analysis_runner 随时读取
        assert main_window.sha256_checksum == "dummy_checksum"

    def test_invalid_times_uses_zero(self, tmp_path):
        """Times值无效时，默认使用0"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        xlsx_file = input_dir / "test.xlsx"
        xlsx_file.write_bytes(b"dummy excel content")

        # Times为空字符串
        create_sha256_csv(output_dir, ["dummy_checksum"], [""])

        main_window = MagicMock()
        main_window.lineEdit_InputPath.text.return_value = str(input_dir)
        main_window.lineEdit_OutputPath.text.return_value = str(output_dir)
        main_window.lineEdit_Version = MagicMock()
        main_window.statusBar_BatteryAnalysis = MagicMock()
        main_window._get_service.return_value = None

        with patch(
            "battery_analysis.main.utils.file_utils.FileUtils.calc_checksum",
            return_value="dummy_checksum",
        ):
            vm = VersionManager(main_window)
            vm._checksum_generation = 1
            checksum = vm._calc_checksum_task(str(input_dir))
            vm._on_checksum_ready(checksum, generation=1)

        # Times为空字符串→转换为0→显示1.0
        main_window.lineEdit_Version.setText.assert_called_with("1.0")

    def test_get_version_dispatches_background_checksum(self):
        """get_version 校验通过 → bump generation + cancel_all + 派发后台校验和任务"""
        main_window = MagicMock()
        main_window.lineEdit_InputPath.text.return_value = "/tmp/in"
        main_window.lineEdit_OutputPath.text.return_value = "/tmp/out"
        vm = VersionManager(main_window)
        vm._task_manager = MagicMock()
        with patch("os.path.exists", return_value=True), patch.object(vm, "_run_async") as mock_run:
            vm.get_version()
        assert vm._checksum_generation == 1
        vm._task_manager.cancel_all.assert_called_once()
        mock_run.assert_called_once()
        task_func, on_finished, on_error, input_dir = mock_run.call_args[0]
        assert task_func == vm._calc_checksum_task
        assert input_dir == "/tmp/in"
        # 回调是 closure：转发到同名方法并携带代次
        with patch.object(vm, "_on_checksum_ready") as mock_ready:
            on_finished("abc123")
        mock_ready.assert_called_once_with("abc123", 1)
        with patch.object(vm, "_on_checksum_error") as mock_error:
            on_error("boom")
        mock_error.assert_called_once_with("boom", 1)

    def test_calc_checksum_task_absorbs_progress_callback_kwarg(self, tmp_path):
        """TaskRunner 注入的 progress_callback 经 **kwargs 吸收，不影响计算"""
        (tmp_path / "a.xlsx").write_bytes(b"dummy")
        vm = VersionManager(MagicMock())
        with patch(
            "battery_analysis.main.utils.file_utils.FileUtils.calc_checksum", return_value="abc123"
        ):
            result = vm._calc_checksum_task(str(tmp_path), progress_callback=lambda pct, msg: None)
        assert result == "abc123"

    def test_on_checksum_ready_discards_stale_result(self):
        """旧代次 → 丢弃校验和结果，不落盘不更新版本号"""
        main_window = MagicMock()
        main_window.lineEdit_InputPath.text.return_value = "/new/dir"
        main_window.lineEdit_OutputPath.text.return_value = "/tmp/out"
        main_window.lineEdit_Version = MagicMock()
        vm = VersionManager(main_window)
        vm._checksum_generation = 5
        with patch.object(vm.logger, "info") as mock_info:
            vm._on_checksum_ready("stale_checksum", generation=4)
        mock_info.assert_called_once()
        main_window.lineEdit_Version.setText.assert_not_called()

    def test_stale_checksum_generation_is_discarded(self):
        """旧代次校验和结果被丢弃（守卫拦截，UI 零访问）"""
        vm = VersionManager()
        vm.main_window = MagicMock()
        vm._checksum_generation = 3
        vm._on_checksum_ready(None, generation=2)
        vm.main_window.assert_not_called()  # 守卫在触碰 main_window 前 return

    def test_get_version_missing_dirs_clears_version(self):
        """输入/输出目录缺失时，清空版本号并推进代次/取消在途任务"""
        main_window = MagicMock()
        main_window.lineEdit_InputPath.text.return_value = "/nonexistent/in"
        main_window.lineEdit_OutputPath.text.return_value = "/nonexistent/out"
        main_window.lineEdit_Version = MagicMock()
        vm = VersionManager(main_window)
        vm._task_manager = MagicMock()
        with (
            patch("os.path.exists", return_value=False),
            patch.object(vm, "_run_async") as mock_run,
        ):
            vm.get_version()
        main_window.lineEdit_Version.setText.assert_called_once_with("")
        # 目录失效也推进代次并取消在途任务，防旧代次结果误接受（I-1 回归修复）
        assert vm._checksum_generation == 1
        vm._task_manager.cancel_all.assert_called_once()
        mock_run.assert_not_called()

    def test_stale_checksum_after_missing_dirs_is_discarded(self):
        """I-1 回归：目录失效后旧代次结果到达 → 守卫丢弃，不复活版本号"""
        main_window = MagicMock()
        main_window.lineEdit_InputPath.text.return_value = "/now/invalid/in"
        main_window.lineEdit_OutputPath.text.return_value = "/now/invalid/out"
        main_window.lineEdit_Version = MagicMock()
        vm = VersionManager(main_window)
        vm._task_manager = MagicMock()
        vm._checksum_generation = 1  # gen 1 校验和任务在途
        with (
            patch("os.path.exists", return_value=False),
            patch.object(vm, "_run_async") as mock_run,
        ):
            vm.get_version()
        # 目录失效 → 推进到 gen 2，版本号清空，不派发新任务
        assert vm._checksum_generation == 2
        main_window.lineEdit_Version.setText.assert_called_once_with("")
        mock_run.assert_not_called()
        # 旧代次（gen 1）结果此刻到达 → 守卫丢弃，版本号保持清空不被复活
        with patch.object(vm.logger, "info") as mock_info:
            vm._on_checksum_ready("stale_checksum", generation=1)
        mock_info.assert_called_once()
        main_window.lineEdit_Version.setText.assert_called_once_with("")

    def test_calc_checksum_task_returns_none_without_xlsx(self, tmp_path):
        """目录内无 xlsx → 任务返回 None（回调据此清空版本号）"""
        (tmp_path / "readme.txt").write_text("hi", encoding="utf-8")
        vm = VersionManager(MagicMock())
        assert vm._calc_checksum_task(str(tmp_path)) is None

    def test_calc_checksum_task_returns_checksum(self, tmp_path):
        """有 xlsx → 返回 FileUtils.calc_checksum 结果"""
        (tmp_path / "a.xlsx").write_bytes(b"dummy")
        vm = VersionManager(MagicMock())
        with patch(
            "battery_analysis.main.utils.file_utils.FileUtils.calc_checksum", return_value="abc123"
        ):
            assert vm._calc_checksum_task(str(tmp_path)) == "abc123"

    def test_on_checksum_ready_none_clears_version(self):
        """回调收到 None（无 xlsx）→ 清空版本号"""
        main_window = MagicMock()
        main_window.lineEdit_Version = MagicMock()
        vm = VersionManager(main_window)
        vm._checksum_generation = 1
        vm._on_checksum_ready(None, generation=1)
        main_window.lineEdit_Version.setText.assert_called_once_with("")
        # 目录切换为无 xlsx 时，校验和缓存也应清空
        assert main_window.sha256_checksum == ""

    def test_on_checksum_error_logs(self):
        """校验和计算异常 → 记录日志，不崩溃"""
        vm = VersionManager(MagicMock())
        vm._checksum_generation = 1
        with patch.object(vm.logger, "error") as mock_error:
            vm._on_checksum_error("boom", generation=1)
        mock_error.assert_called_once()

    def test_on_checksum_error_discards_stale_result(self):
        """旧代次 → 错误兜底同样丢弃"""
        vm = VersionManager(MagicMock())
        vm._checksum_generation = 5
        with patch.object(vm.logger, "error") as mock_error:
            vm._on_checksum_error("boom", generation=4)
        mock_error.assert_not_called()
