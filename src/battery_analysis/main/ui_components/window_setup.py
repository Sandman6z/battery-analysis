"""
窗口设置组件

负责主窗口的初始化和设置
"""

import logging
from PyQt6 import QtGui as QG
from PyQt6 import QtWidgets as QW


class WindowSetup:
    """
    窗口设置类，负责主窗口的初始化和设置
    """
    
    def __init__(self, main_window):
        """
        初始化窗口设置
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def init_window(self) -> None:
        """
        初始化窗口
        """
        # 调用父类方法设置窗口标题
        window_title = f"Battery Analyzer v{self.main_window.version}"
        self.main_window.setWindowTitle(window_title)
        
        # 加载应用图标
        self._load_application_icon()
    
    def _load_application_icon(self) -> QG.QIcon:
        """
        加载应用程序图标
        
        Returns:
            应用程序图标
        """
        try:
            # 尝试多个可能的图标路径（优先使用环境检测器，否则使用固定路径）
            icon_paths = []
            
            # 如果环境检测器可用，使用它来解析路径
            if hasattr(self.main_window, 'env_detector') and self.main_window.env_detector:
                icon_paths = [
                    self.main_window.env_detector.get_resource_path("config/resources/icons/Icon_BatteryTestGUI.ico"),
                    self.main_window.env_detector.get_resource_path("resources/icons/Icon_BatteryTestGUI.ico"),
                ]
            
            # 始终尝试相对路径（工程中的图标）
            from pathlib import Path
            icon_paths.extend([
                Path(self.main_window.current_directory) / "config" / "resources" / "icons" / "Icon_BatteryTestGUI.ico",
                Path(self.main_window.current_directory) / "resources" / "icons" / "Icon_BatteryTestGUI.ico",
            ])
            
            # 遍历所有可能的路径，找到第一个存在的
            for icon_path in icon_paths:
                if icon_path.exists():
                    self.logger.debug("找到应用图标: %s", icon_path)
                    app_icon = QG.QIcon(str(icon_path))
                    self.main_window.setWindowIcon(app_icon)
                    return app_icon
            
            # 如果都找不到，使用默认图标
            self.logger.warning("未找到应用图标文件，使用默认图标")
            return QG.QIcon()
        except (OSError, TypeError, ValueError, RuntimeError, ImportError) as e:
            # 捕获所有可能的异常，确保应用能正常启动
            self.logger.error("加载应用图标失败: %s", e)
            return QG.QIcon()
    
    def toggle_toolbar_safe(self) -> None:
        """
        安全地切换工具栏的显示/隐藏状态
        """
        if hasattr(self.main_window, 'actionShow_Toolbar') and hasattr(self.main_window, 'toolBar'):
            self.main_window.toolBar.setVisible(self.main_window.actionShow_Toolbar.isChecked())
        elif hasattr(self.main_window, 'toolBar'):
            # 如果没有actionShow_Toolbar，只是切换显示状态
            self.main_window.toolBar.setVisible(not self.main_window.toolBar.isVisible())
    
    def toggle_statusbar_safe(self) -> None:
        """
        安全地切换状态栏的显示/隐藏状态
        """
        if hasattr(self.main_window, 'actionShow_Statusbar') and hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.setVisible(
                self.main_window.actionShow_Statusbar.isChecked())
        elif hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            # 如果没有actionShow_Statusbar，只是切换显示状态
            self.main_window.statusBar_BatteryAnalysis.setVisible(
                not self.main_window.statusBar_BatteryAnalysis.isVisible())
    
    def setup_menu_shortcuts(self) -> None:
        """
        设置菜单快捷键
        """
        self.logger.warning("setup_menu_shortcuts 已迁移到 MenuManager")
    
    def init_widgetcolor(self) -> None:
        """
        初始化部件颜色
        """
        # 初始化UI部件颜色
        try:
            self.main_window.lineEdit_InputPath.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_OutputPath.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_version.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_testDate.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_testTime.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_Barcode.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_SerialNumber.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_BatchNumber.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_LotNumber.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_ManufactureDate.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_BatteryDate.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_BatteryModel.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_ChemicalSystem.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_Capacity.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_DesignVoltage.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_RatedVoltage.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_DischargeCurrent.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_DischargeVoltage.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_ChargeCurrent.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_CellType.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_CellNumber.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_ConnectionType.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_Manufacturer.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_Assembler.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_Tester.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_InspectionType.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_InspectionCriteria.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_TestEquipment.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_TestSoftware.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_TestOperator.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_TestLocation.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_AmbientTemperature.setStyleSheet("background-color: #ffffff;")
            self.main_window.lineEdit_Humidity.setStyleSheet("background-color: #ffffff;")
        except (AttributeError, TypeError, RuntimeError) as e:
            self.logger.error("初始化部件颜色失败: %s", e)
