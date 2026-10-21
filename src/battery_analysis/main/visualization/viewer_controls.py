"""查看器窗口级控件：菜单栏、文件操作按钮、帮助文本、About 对话框

从 interaction_controls.py 拆出（大文件拆分重构）。
"""

import datetime
import logging
import traceback

import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from battery_analysis.utils.version import Version

logger = logging.getLogger(__name__)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 本 Mixin 通过 self 隐式使用兄弟 Mixin 与汇总类的方法/属性；
    # 将 self 标注为汇总类 InteractionControlsMixin，IDE 才能静态看出这些依赖。
    from battery_analysis.main.visualization.interaction_controls import (
        InteractionControlsMixin,
    )


class ViewerControlsMixin:
    """查看器窗口级交互（依赖 ButtonFactoryMixin 的 _create_modern_toggle_group）"""

    def _add_help_text(self: "InteractionControlsMixin", fig):
        """添加帮助文本到图表右上角"""
        try:
            fig.text(
                0.98, 0.85, "Tip: Hover over a data point to view details", fontsize=7, ha="right"
            )
            fig.text(
                0.98,
                0.78,
                "Shortcuts: Scroll to zoom, drag to pan, right-click to reset view",
                fontsize=7,
                ha="right",
            )
            logger.info("Help text added successfully")
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("Error adding help text: %s", e)

    def _add_file_operation_buttons(self: "InteractionControlsMixin", fig):
        """添加文件操作按钮区域（打开文件和退出按钮）"""
        try:
            ax_file = fig.add_axes([0.001, 0.90, 0.17, 0.062])
            ax_file.set_xlim(0, 1)
            ax_file.set_ylim(0, 1)
            ax_file.axis("off")

            buttons_config = [
                {"text": "Open", "callback": lambda: self._open_file_dialog(), "initial": False},
                {"text": "Exit", "callback": lambda: self._close_viewer(), "initial": False},
            ]

            self.file_button_states = self._create_modern_toggle_group(
                ax_file, 0.02, 0.15, 0.96, 0.7, buttons_config
            )

            logger.info("Modern file operation button area added successfully")
        except (ValueError, TypeError, AttributeError) as e:
            logger.error("Error creating file operation buttons: %s", e)

    def _add_menu_bar(self: "InteractionControlsMixin", fig) -> bool:
        """为图表添加菜单栏，成功返回 True，无独立窗口时返回 False。"""
        try:
            logger.info("Starting to add PyQt6 menubar")

            manager = fig.canvas.manager
            if not manager or not hasattr(manager, "window"):
                logger.warning(
                    "Unable to obtain matplotlib window manager, skipping menubar addition"
                )
                return False

            if hasattr(manager.window, "menuBar"):
                self._apply_window_modern_style(manager.window)

                menubar = manager.window.menuBar()
                self._apply_menubar_style(menubar)

                file_menu = menubar.addMenu("File")
                self._apply_menu_style(file_menu)

                open_action = file_menu.addAction("Open")
                open_action.setProperty("menu_action", "open")

                def on_open_clicked():
                    logger.info("Open menu item clicked")
                    self._open_file_dialog()

                open_action.triggered.connect(on_open_clicked)

                file_menu.addSeparator()

                exit_action = file_menu.addAction("Exit")
                exit_action.setProperty("menu_action", "exit")

                def on_exit_clicked():
                    logger.info("Exit menu item clicked, closing visualizer window")
                    if self.current_fig is not None:
                        plt.close(self.current_fig)
                        self.current_fig = None
                        logger.info("Visualizer window closed")
                    else:
                        logger.warning("No visualizer window is currently open")

                exit_action.triggered.connect(on_exit_clicked)

                help_menu = menubar.addMenu("Help")
                self._apply_menu_style(help_menu)

                about_action = help_menu.addAction("About")
                about_action.setProperty("menu_action", "about")

                def on_about_clicked():
                    logger.info("About menu item clicked")
                    self._show_about_dialog()

                about_action.triggered.connect(on_about_clicked)
                logger.info("PyQt6 menubar added successfully")
                return True
            else:
                raise RuntimeError("Window does not support a menu bar")

        except ImportError as e:
            raise ImportError(
                f"PyQt6 dependency missing: {e}. Please ensure PyQt6 is installed correctly"
            )
        except (AttributeError, TypeError, RuntimeError) as e:
            raise RuntimeError(f"Menu bar initialization failed: {e}") from e

    def _open_file_dialog(self: "InteractionControlsMixin"):
        """打开文件对话框，允许用户选择数据文件

        失败场景（对话框打不开、数据加载失败）给用户可见提示，
        用户主动取消只记 debug 日志不打扰。
        """
        try:
            try:
                data_dir = QFileDialog.getExistingDirectory(
                    None,
                    "Select Data Directory",
                    self.strPltPath or ".",
                    QFileDialog.Option.ShowDirsOnly,
                )
            except (ImportError, AttributeError, TypeError, RuntimeError) as qt_error:
                logger.error("Qt file dialog failed: %s", qt_error)
                QMessageBox.warning(None, "Open Data", "Failed to open the file dialog.")
                return

            if not data_dir:
                # 用户主动取消选择：正常操作，不弹提示
                logger.debug("File dialog cancelled by user")
                return

            logger.info("User selected data directory: %s", data_dir)
            self.set_data_path(data_dir)
            if self.load_data():
                self._cleanup_matplotlib_state()
                if self.current_fig is not None:
                    plt.close(self.current_fig)
                    self.current_fig = None
                self.plt_figure()
            else:
                logger.error("Data loading failed, cannot display chart")
                QMessageBox.warning(
                    None, "Load Data", "Failed to load data from the selected directory."
                )
        except (AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
            logger.error("Error opening file dialog: %s", e)
            traceback.print_exc()

    def _show_about_dialog(self: "InteractionControlsMixin"):
        """显示About对话框"""
        try:
            try:
                current_time = datetime.datetime.now().strftime("%Y")
            except (ImportError, OSError, ValueError) as e:
                logger.warning("Failed to get current year: %s", e)
                current_time = "2024"

            try:
                version_obj = Version()
                version_info = f"v{version_obj.version}"
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning("Unable to get version info, using default version: %s", e)
                version_info = "v2.0.0"

            about_text = f"""Battery Analysis Tool
Version: {version_info}

Battery test data visualization and analysis application
Supports importing multiple data formats and generating charts

Features:
• Import data from CSV files
• Interactive chart display and operation
• Toggle between filtered and unfiltered data
• Battery selection and channel control
• Hover to show detailed information

Developer: Ewin Battery Analysis Team
Copyright: © {current_time} MIT License

Thank you for using Battery Analysis Tool!"""

            msg_box = QMessageBox()
            msg_box.setWindowTitle("About")
            msg_box.setText(about_text)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()

            logger.info("About dialog displayed")
        except (AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
            logger.error("Failed to display About dialog: %s", e)
            try:
                version_obj = Version()
                fallback_version = f"v{version_obj.version}"
            except (ImportError, AttributeError, TypeError):
                fallback_version = "v2.1.2"

    def _close_viewer(self: "InteractionControlsMixin"):
        """关闭viewer窗口"""
        try:
            logger.info("File operation button: Exit clicked, closing visualizer window")
            if self.current_fig is not None:
                plt.close(self.current_fig)
                self.current_fig = None
                logger.info("Visualizer window closed")
            else:
                logger.warning("No visualizer window is currently open")
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.error("Error closing viewer window: %s", e)
