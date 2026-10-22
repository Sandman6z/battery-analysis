"""主窗口初始化与生命周期

从 main_window.py 拆出（大文件拆分重构）。"""

import logging
import time

import PyQt6.QtCore as QC
import PyQt6.QtGui as QG

from battery_analysis.i18n import _
from battery_analysis.main.application_initializer import ApplicationInitializer
from battery_analysis.main.managers.initialization_manager import (
    PHASE_CORE_SVC,
    PHASE_ENV_PREP,
    PHASE_LAUNCH,
    PHASE_UI_BUILD,
    InitializationManager,
)
from battery_analysis.main.utils import FileUtils
from battery_analysis.main.window_state import MainWindowState
from battery_analysis.ui.styles.theme_settings import load_theme_preference
from battery_analysis.utils.log_manager import get_log_manager, get_logger

logger = logging.getLogger(__name__)


class WindowInitMixin(MainWindowState):
    """延迟初始化、组件获取、图标加载、环境信息、窗口尺寸事件"""

    def _deferred_init(self):
        """窗口显示后执行的全部初始化 — 不再阻塞启动

        4 阶段流程：
          环境准备 → 核心服务 → UI 构建 → 启动完成

        每阶段由 `_prepare_application` / `_run_initialization_pipeline` /
        `_complete_launch_phase` 各自承担，本方法只负责时序与错误兜底。
        """
        t0 = time.time()
        try:
            if not self._prepare_application():
                return

            self._run_initialization_pipeline()
            self._complete_launch_phase()

            elapsed = (time.time() - t0) * 1000
            logger.info("Background initialization completed in %dms", elapsed)
        except Exception as e:
            logger.exception("Background initialization error: %s", e)

    def _prepare_application(self) -> bool:
        """前置准备：日志记录器与全局应用初始化

        Returns:
            bool: False 表示全局初始化失败，后续阶段应跳过
        """
        self.logger = get_logger("main_window")

        initializer = ApplicationInitializer()
        if not initializer.initialize():
            logger.error("Application initialization failed; some features may be unavailable")
            return False
        return True

    def _run_initialization_pipeline(self):
        """阶段 1-3：环境准备 → 核心服务 → UI 构建，并注册语言切换回调"""
        logger.info("─" * 40)
        logger.info(
            "Initialization pipeline: %s → %s → %s",
            PHASE_ENV_PREP,
            PHASE_CORE_SVC,
            PHASE_UI_BUILD,
        )
        init_manager = InitializationManager(self)
        init_manager.initialize()

        # 注册 refresh_texts 回调（语言切换时自动调用）
        if hasattr(self, "language_manager") and self.language_manager:
            self.language_manager.register(self.refresh_texts)

    def _complete_launch_phase(self):
        """阶段 4：UI 后处理、版本号、主题、辅助功能与菜单启用"""
        logger.info("")
        logger.info("▶ Phase [%s]", PHASE_LAUNCH)

        # 4a) UI 后处理（窗口属性、控件填充）
        self.ui_manager.init_window()
        self.ui_manager.init_widget()
        # 连接菜单动作和控制器信号（connect_widget 内部已调用
        # signal_connector.connect_controllers，勿重复调用——重复连接导致弹窗出现两次）
        self.connect_widget()
        if hasattr(self, "pushButton_Run"):
            self.pushButton_Run.setFocus()
        if hasattr(self, "tableWidget_TestInformation"):
            self.tableWidget_TestInformation.resizeColumnsToContents()

        # 4b) 版本号
        self.version_manager.get_version()

        # 4c) 应用保存的主题设置
        try:
            self.theme_manager.set_theme(load_theme_preference())
        except Exception as e:
            logger.warning("Failed to apply saved theme: %s", e)

        # 4d) 非关键 UI 辅助功能／工具提示
        self._lazy_init()

        # 4d) 环境日志（包含 psutil/platform 调用，UI 已可见）
        try:
            lm = get_log_manager()
            if lm:
                lm.log_environment_info()
        except Exception:
            logger.exception("Failed to log environment info")

        logger.info("  Phase [%s] completed ✓", PHASE_LAUNCH)

        # 启用配置菜单（服务已就绪）
        if hasattr(self, "actionConfiguration"):
            logger.debug("Enabling actionConfiguration menu")
            self.actionConfiguration.setEnabled(True)
            logger.debug(
                "actionConfiguration menu enabled: %s", self.actionConfiguration.isEnabled()
            )

    # ------------------------------
    # 服务和控制器获取方法
    # ------------------------------
    def _get_component(self, component_name, component_type="service"):
        logger.debug("_get_component called: %s %s", component_type, component_name)
        cache_dict = self._services if component_type == "service" else self._controllers
        if component_name not in cache_dict:
            logger.debug("%s %s not in cache, fetching...", component_type, component_name)
            try:
                cache_dict[component_name] = self._service_container.get(component_name)
                logger.debug(
                    "Successfully fetched %s %s: %s",
                    component_type,
                    component_name,
                    cache_dict[component_name],
                )
            except Exception as e:
                logger.warning(
                    "Failed to get %s %s: %s", component_type, component_name, e, exc_info=True
                )
                cache_dict[component_name] = None
        else:
            logger.debug(
                "%s %s found in cache: %s",
                component_type,
                component_name,
                cache_dict[component_name],
            )
        return cache_dict[component_name]

    def _get_service(self, service_name):
        return self._get_component(service_name, "service")

    def _get_controller(self, controller_name):
        return self._get_component(controller_name, "controller")

    # ------------------------------
    # 窗口和UI管理方法
    # ------------------------------
    def _load_application_icon(self) -> QG.QIcon:
        try:
            env_detector = getattr(self, "env_detector", None)
            icon_paths = FileUtils.get_icon_paths(
                env_detector, getattr(self, "current_directory", None)
            )
            for icon_path in icon_paths:
                if icon_path.exists():
                    return QG.QIcon(str(icon_path))
            logger.warning(_("App icon not found; using default icon."))
            return QG.QIcon()
        except (OSError, TypeError, ValueError, RuntimeError, ImportError) as e:
            logger.error("Failed to load application icon: %s", e)
            return QG.QIcon()

    # ------------------------------
    # 环境和信息管理方法
    # ------------------------------
    def _initialize_environment_info(self):
        self.environment_manager.initialize_environment_info()

    def _ensure_env_info_keys(self):
        self.environment_manager.ensure_env_info_keys()

    def resizeEvent(self, event):
        """窗口大小改变时的事件处理函数"""
        super().resizeEvent(event)
        if hasattr(self, "tableWidget_TestInformation"):
            if self.tableWidget_TestInformation.rowCount() > 0:
                # 真去抖（roadmap #13）：取消前一个待触发的定时器，只保留最后一次。
                # resizeColumnsToContents 是 O(rows×cols) 重排，
                # 连续 resize 期间只在停止150ms 后执行一次。
                if self._resize_timer is not None:
                    self._resize_timer.stop()
                self._resize_timer = QC.QTimer.singleShot(150, self._resize_table_columns)

    def _resize_table_columns(self):
        """去抖后的列宽自适应（由 resizeEvent 的 QTimer.singleShot 触发）"""
        if hasattr(self, "tableWidget_TestInformation"):
            if self.tableWidget_TestInformation.rowCount() > 0:
                self.tableWidget_TestInformation.resizeColumnsToContents()

    def _lazy_init(self):
        """延迟初始化非关键UI组件（窗口显示后执行）"""
        if self._lazy_init_done:
            return
        self._lazy_init_done = True
        try:
            t0 = time.time()
            # 可访问性设置和工具提示 — 不影响功能
            if hasattr(self, "ui_manager"):
                self.ui_manager.setup_accessibility()
                self.ui_manager.setup_tooltips()
            logger.debug("Deferred initialization completed in %dms", (time.time() - t0) * 1000)
        except Exception as e:
            logger.warning("Deferred initialization failed: %s", e)
