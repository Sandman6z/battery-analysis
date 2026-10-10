"""
BatteryChartViewer 适配器模块

将现有的 BatteryChartViewer 包装为实现 IVisualizer 接口的类。
从 visualizer_factory.py 中拆出（大文件拆分重构）。
"""

import logging
import os

from battery_analysis.main.interfaces.ivisualizer import IVisualizer


class BatteryChartViewerWrapper(IVisualizer):
    """
    BatteryChartViewer的适配器类

    将现有的BatteryChartViewer包装为实现IVisualizer接口的类
    """

    def __init__(self, data_path: str | None = None):
        """
        初始化适配器

        Args:
            data_path: 可选的数据路径
        """
        self.logger = logging.getLogger(__name__)

        # 延迟导入，避免 import visualizer_factory 时触发 matplotlib 等 heavy 导入
        from battery_analysis.main.battery_chart_viewer import BatteryChartViewer

        self._viewer = BatteryChartViewer(data_path=None, auto_search=False)
        self._config = {}

        # 如果提供了有效的数据路径，先设置路径但不自动加载
        if data_path and os.path.exists(data_path):
            self._viewer.set_data_path(data_path)
            # 不自动加载数据，由调用者决定何时加载

    def _load_data_at(self, data_path: str, success_msg: str) -> None:
        """在指定目录上加载数据，并按统一话术记录日志。"""
        self._viewer.set_data_path(data_path)
        if self._viewer.load_data():
            self._viewer.loaded_data = True
            self.logger.info(success_msg)
        else:
            self.logger.warning("Data loading failed")

    def _load_data_from_xml_path(self, xml_path: str) -> None:
        """按 XML 路径定位分析结果目录并加载数据。

        embed_to_widget 与 show_figure 原本各有一份几乎相同、但兜底分支
        不一致的实现（见 docs/refactor-findings.md #1），现统一为此实现。

        流程：XML 转绝对路径 → 上一级目录（回退 XML 所在目录）中找分析结果
        目录 → 最新子目录的 Info_Image.csv → 兜底遍历其他子目录 → 兜底直接
        在分析结果目录根下找 csv。
        """
        # 确保XML路径是绝对路径
        if not os.path.isabs(xml_path):
            xml_path = os.path.abspath(xml_path)

        # 检查XML路径是否存在
        if not os.path.exists(xml_path):
            self.logger.warning("XML file does not exist: %s", xml_path)

        # 获取XML所在目录
        test_profile_dir = os.path.dirname(xml_path)

        # 检查XML所在目录是否存在
        if not os.path.exists(test_profile_dir):
            self.logger.warning("XML directory does not exist: %s", test_profile_dir)

        # 获取XML所在目录的上一级目录
        parent_dir = os.path.dirname(test_profile_dir)

        # 检查XML上一级目录是否存在
        if not os.path.exists(parent_dir):
            self.logger.warning("XML parent directory does not exist: %s", parent_dir)

        # 定义可能的分析结果目录名称
        analysis_dir_names = [
            "3_analysis results",
            "analysis results",
            "Analysis Results",
            "3_Analysis Results",
        ]

        # 尝试在XML上一级目录中寻找分析结果目录
        analysis_results_dir = None
        for dir_name in analysis_dir_names:
            analysis_dir = os.path.join(parent_dir, dir_name)
            if os.path.exists(analysis_dir):
                analysis_results_dir = analysis_dir
                break

        # 如果在XML上一级目录中没有找到，尝试在XML所在目录中寻找
        if not analysis_results_dir:
            for dir_name in analysis_dir_names:
                analysis_dir = os.path.join(test_profile_dir, dir_name)
                if os.path.exists(analysis_dir):
                    analysis_results_dir = analysis_dir
                    break

        if not analysis_results_dir:
            self.logger.warning("Analysis results directory not found")
            return

        # 检查分析结果目录是否存在
        if not os.path.exists(analysis_results_dir):
            self.logger.warning(
                "Analysis results directory does not exist: %s", analysis_results_dir
            )
            return

        # 获取子目录列表
        try:
            subdirs = [
                d
                for d in os.listdir(analysis_results_dir)
                if os.path.isdir(os.path.join(analysis_results_dir, d))
            ]

            if not subdirs:
                self.logger.warning("No subdirectories in the analysis results directory")
                # 尝试直接在分析结果目录中寻找Info_Image.csv文件
                info_image_csv = os.path.join(analysis_results_dir, "Info_Image.csv")
                if os.path.exists(info_image_csv):
                    self._load_data_at(
                        analysis_results_dir,
                        "Successfully loaded data from analysis results directory",
                    )
                return

            # 按修改时间排序，获取最新的子目录
            latest_dir = max(
                subdirs,
                key=lambda d: os.path.getmtime(os.path.join(analysis_results_dir, d)),
            )
            latest_dir_path = os.path.join(analysis_results_dir, latest_dir)

            # 检查最新目录中是否有Info_Image.csv文件
            info_image_csv = os.path.join(latest_dir_path, "Info_Image.csv")
            if os.path.exists(info_image_csv):
                self._load_data_at(latest_dir_path, "Successfully loaded data from XML path")
                return

            self.logger.warning("Info_Image.csv file not found in the latest version directory")
            # 尝试在分析结果目录的其他子目录中寻找Info_Image.csv文件
            for subdir in subdirs:
                subdir_path = os.path.join(analysis_results_dir, subdir)
                info_image_csv = os.path.join(subdir_path, "Info_Image.csv")
                if os.path.exists(info_image_csv):
                    self._load_data_at(
                        subdir_path, "Successfully loaded data from another subdirectory"
                    )
                    break
        except Exception as e:
            self.logger.error("Error processing analysis results directory: %s", e)

    def embed_to_widget(
        self, parent_widget, data_path: str | None = None, xml_path: str | None = None
    ):
        """
        将图表嵌入到指定的 QWidget 中

        Args:
            parent_widget: 父 QWidget
            data_path: 可选的数据路径
            xml_path: 可选的XML文件路径

        Returns:
            tuple: (fig, canvas, filter_checkbox, scroll_area, battery_checkboxes) 或 None
        """
        try:
            # 重置viewer状态
            self._viewer.loaded_data = False

            # 只有当提供了XML路径或数据路径时才加载数据
            if xml_path is not None and xml_path:
                self._load_data_from_xml_path(xml_path)

            # 如果提供了数据路径，加载数据
            elif data_path is not None:
                self._load_data_at(data_path, "Successfully loaded data from data path")
            # 嵌入图表到父控件
            result = self._viewer.embed_to_widget(parent_widget)
            return result

        except (ImportError, TypeError, ValueError, OSError) as e:
            self.logger.error("Error embedding chart: %s", e)
            return None

    def show_figure(self, data_path: str | None = None, xml_path: str | None = None) -> bool:
        """
        显示图表

        Args:
            data_path: 可选的数据路径
            xml_path: 可选的XML文件路径

        Returns:
            bool: 是否成功显示
        """
        try:
            # 重置viewer状态
            self._viewer.loaded_data = False

            # 只有当提供了XML路径或数据路径时才加载数据
            if xml_path is not None and xml_path:
                self._load_data_from_xml_path(xml_path)

            # 如果提供了数据路径，加载数据
            elif data_path is not None:
                self._load_data_at(data_path, "Successfully loaded data from data path")

            # 其他情况（没有提供XML路径或数据路径），不加载任何数据，直接显示无数据
            # 不设置loaded_data，让_viewer在plt_figure时显示无数据

            # 创建可视化
            success = self._viewer.plt_figure()
            if not success:
                self.logger.warning("Chart display failed")

            return success
        except (ImportError, TypeError, ValueError, OSError) as e:
            self.logger.error("Error displaying chart: %s", e)
            return False

    def load_data(self, data_path: str) -> bool:
        """
        加载数据

        Args:
            data_path: 数据路径

        Returns:
            bool: 是否成功加载数据
        """
        try:
            self._viewer.set_data_path(data_path)
            success = self._viewer.load_data()
            if not success:
                self._viewer.loaded_data = False
                self.logger.warning("Data loading failed: %s", data_path)
            else:
                self._viewer.loaded_data = True

            return success
        except (TypeError, ValueError, OSError) as e:
            self.logger.error("Error loading data: %s", e)
            self._viewer.loaded_data = False
            return False

    def clear_data(self) -> None:
        """
        清除所有数据，回到初始状态
        """
        try:
            self._viewer.loaded_data = False
            self._viewer.listPlt = []
            self._viewer.listBatteryName = []
            self._viewer.listBatteryNameSplit = []
            self._viewer.intBatteryNum = 0

            # 清除数据路径
            self._viewer.strPltPath = None
            self._viewer.strInfoImageCsvPath = None
        except (TypeError, AttributeError, OSError) as e:
            self.logger.error("Error clearing data: %s", e)

    def is_data_loaded(self) -> bool:
        """
        检查是否有数据已加载

        Returns:
            bool: 是否已加载数据
        """
        return getattr(self._viewer, "loaded_data", False)

    def get_status_info(self) -> dict:
        """
        获取状态信息

        Returns:
            dict: 状态信息字典
        """
        return {
            "data_loaded": self.is_data_loaded(),
            "battery_count": getattr(self._viewer, "intBatteryNum", 0),
            "data_path": getattr(self._viewer, "strPltPath", None),
            "config": self._config.copy(),
        }

    def set_config(self, config: dict) -> None:
        """
        设置配置

        Args:
            config: 配置字典
        """
        self._config.update(config)
        self.logger.debug("Configuration updated: %s", config)

    def get_config(self) -> dict:
        """
        获取当前配置

        Returns:
            dict: 当前配置字典
        """
        return self._config.copy()

    @property
    def viewer(self) -> "BatteryChartViewer":  # noqa: F821 延迟 import，pyflakes 误报
        """
        获取原始的viewer实例

        Returns:
            BatteryChartViewer: 原始viewer实例
        """
        return self._viewer
