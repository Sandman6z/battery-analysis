"""
测试主窗口UI模块的功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from battery_analysis.main.main_window import Main


@pytest.fixture
def app():
    """创建QApplication实例"""
    return QApplication([])


class TestMainWindow:
    """测试主窗口类"""
    
    def setup_method(self):
        """设置测试环境"""
        # 模拟初始化管理器，避免实际初始化过程
        with patch('battery_analysis.main.main_window.InitializationManager') as mock_init_manager:
            # 创建模拟的初始化管理器实例
            mock_init_instance = Mock()
            mock_init_manager.return_value = mock_init_instance
            
            # 模拟初始化方法
            mock_init_instance.initialize = Mock()
            
            # 创建主窗口实例
            self.main_window = Main()
            
            # 模拟必要的属性和方法
            self.main_window.ui_manager = Mock()
            self.main_window.ui_manager.init_window = Mock()
            self.main_window.ui_manager.init_widget = Mock()
            self.main_window.ui_manager.connect_widget = Mock()
            
            self.main_window.menu_manager = Mock()
            self.main_window.menu_manager.connect_menu_actions = Mock()
            self.main_window.menu_manager.setup_menu_shortcuts = Mock()
            self.main_window.menu_manager.update_statusbar_messages = Mock()
            self.main_window.menu_manager.toggle_toolbar_safe = Mock()
            self.main_window.menu_manager.toggle_statusbar_safe = Mock()
            
            self.main_window.dialog_manager = Mock()
            self.main_window.dialog_manager.handle_exit = Mock()
            self.main_window.dialog_manager.handle_about = Mock()
            self.main_window.dialog_manager.show_preferences = Mock()
            self.main_window.dialog_manager.show_online_help = Mock()
            
            self.main_window.config_manager = Mock()
            self.main_window.config_manager.get_config = Mock(return_value=[])
            self.main_window.config_manager.save_user_settings = Mock()
            self.main_window.config_manager.save_settings = Mock()
            
            self.main_window.validation_manager = Mock()
            self.main_window.validation_manager.validate_version = Mock()
            self.main_window.validation_manager.validate_input_path = Mock()
            self.main_window.validation_manager.validate_required_fields = Mock()
            self.main_window.validation_manager.check_batterytype = Mock()
            self.main_window.validation_manager.check_specification = Mock()
            self.main_window.validation_manager.checkinput = Mock(return_value=True)
            
            self.main_window.environment_manager = Mock()
            self.main_window.environment_manager.initialize_environment_info = Mock()
            self.main_window.environment_manager.ensure_env_info_keys = Mock()
            
            self.main_window.visualization_manager = Mock()
            self.main_window.visualization_manager.run_visualizer = Mock()
            self.main_window.visualization_manager.show_visualizer_error = Mock()
            
            self.main_window.test_profile_manager = Mock()
            self.main_window.test_profile_manager.select_testprofile = Mock()
            
            self.main_window.path_manager = Mock()
            self.main_window.path_manager.select_inputpath = Mock()
            self.main_window.path_manager.select_outputpath = Mock()
            
            self.main_window.report_manager = Mock()
            self.main_window.report_manager.open_report = Mock()
            self.main_window.report_manager.open_report_path = Mock()
            self.main_window.report_manager.show_analysis_complete_dialog = Mock()
            
            self.main_window.theme_manager = Mock()
            self.main_window.theme_manager.set_theme = Mock()
            
            self.main_window.help_manager = Mock()
            self.main_window.help_manager.show_user_manual = Mock()
            
            self.main_window.temperature_handler = Mock()
            self.main_window.temperature_handler.on_temperature_type_changed = Mock()
            
            self.main_window.data_processor = Mock()
            self.main_window.data_processor.get_xlsxinfo = Mock()
            
            self.main_window.version_manager = Mock()
            self.main_window.version_manager.get_version = Mock()
            
            self.main_window.table_manager = Mock()
            self.main_window.table_manager.set_table = Mock()
            self.main_window.table_manager.save_table = Mock()
            
            # 模拟命令对象
            self.main_window.calculate_battery_command = Mock()
            self.main_window.calculate_battery_command.execute = Mock()
            
            self.main_window.analyze_data_command = Mock()
            self.main_window.analyze_data_command.execute = Mock()
            
            self.main_window.generate_report_command = Mock()
            self.main_window.generate_report_command.execute = Mock()
            
            self.main_window.batch_processing_command = Mock()
            self.main_window.batch_processing_command.execute = Mock()
            
            self.main_window.export_report_command = Mock()
            self.main_window.export_report_command.execute = Mock()
            
            self.main_window.run_analysis_command = Mock()
            self.main_window.run_analysis_command.execute = Mock()
            
            # 模拟其他必要属性
            self.main_window.pushButton_Run = Mock()
            self.main_window.pushButton_Run.setFocus = Mock()
            self.main_window.signal_connector = Mock()
            self.main_window.signal_connector.progress_dialog = Mock()
            self.main_window.version = "1.0.0"
    
    def test_init_window(self):
        """测试窗口初始化"""
        # 调用初始化方法
        self.main_window.init_window()
        
        # 验证ui_manager的init_window方法被调用
        self.main_window.ui_manager.init_window.assert_called_once()
    
    def test_init_widget(self):
        """测试部件初始化"""
        # 调用初始化方法
        self.main_window.init_widget()
        
        # 验证ui_manager的init_widget方法被调用
        self.main_window.ui_manager.init_widget.assert_called_once()
        # 验证Run按钮获得焦点
        self.main_window.pushButton_Run.setFocus.assert_called_once()
    
    def test_load_application_icon(self):
        """测试加载应用程序图标"""
        with patch('battery_analysis.main.main_window.FileUtils') as mock_file_utils, \
             patch('battery_analysis.main.main_window.QG.QIcon') as mock_qicon:
            # 设置模拟返回值
            mock_file_utils.get_icon_paths = Mock(return_value=[])
            mock_qicon.return_value = Mock()
            
            # 调用方法
            icon = self.main_window._load_application_icon()
            
            # 验证方法被调用
            mock_file_utils.get_icon_paths.assert_called_once()
            mock_qicon.assert_called_once()
    
    def test_on_language_changed(self):
        """测试语言切换"""
        with patch('battery_analysis.main.main_window._') as mock_gettext:
            # 设置模拟返回值
            mock_gettext.side_effect = lambda x, y=None: y if y else x
            
            # 调用方法
            self.main_window._on_language_changed('en')
            
            # 验证方法被调用
            self.main_window._update_ui_texts.assert_called_once()
            self.main_window._update_statusbar_messages.assert_called_once()
            self.main_window._refresh_dialogs.assert_called_once()
    
    def test_handle_exit(self):
        """测试退出处理"""
        # 调用方法
        self.main_window.handle_exit()
        
        # 验证dialog_manager的handle_exit方法被调用
        self.main_window.dialog_manager.handle_exit.assert_called_once()
    
    def test_handle_about(self):
        """测试关于对话框"""
        # 调用方法
        self.main_window.handle_about()
        
        # 验证dialog_manager的handle_about方法被调用
        self.main_window.dialog_manager.handle_about.assert_called_once()
    
    def test_show_preferences(self):
        """测试显示首选项对话框"""
        # 调用方法
        self.main_window.show_preferences()
        
        # 验证dialog_manager的show_preferences方法被调用
        self.main_window.dialog_manager.show_preferences.assert_called_once()
    
    def test_on_preferences_applied(self):
        """测试首选项应用"""
        # 调用方法
        self.main_window.on_preferences_applied()
        # 验证方法执行（无异常）
        assert True
    
    def test_toggle_toolbar_safe(self):
        """测试安全切换工具栏"""
        # 调用方法
        self.main_window.toggle_toolbar_safe()
        
        # 验证menu_manager的toggle_toolbar_safe方法被调用
        self.main_window.menu_manager.toggle_toolbar_safe.assert_called_once()
    
    def test_toggle_statusbar_safe(self):
        """测试安全切换状态栏"""
        # 调用方法
        self.main_window.toggle_statusbar_safe()
        
        # 验证menu_manager的toggle_statusbar_safe方法被调用
        self.main_window.menu_manager.toggle_statusbar_safe.assert_called_once()
    
    def test_show_user_manual(self):
        """测试显示用户手册"""
        # 调用方法
        self.main_window.show_user_manual()
        
        # 验证help_manager的show_user_manual方法被调用
        self.main_window.help_manager.show_user_manual.assert_called_once()
    
    def test_show_online_help(self):
        """测试显示在线帮助"""
        # 调用方法
        self.main_window.show_online_help()
        
        # 验证dialog_manager的show_online_help方法被调用
        self.main_window.dialog_manager.show_online_help.assert_called_once()
    
    def test_calculate_battery(self):
        """测试电池计算"""
        # 调用方法
        self.main_window.calculate_battery()
        
        # 验证命令执行
        self.main_window.calculate_battery_command.execute.assert_called_once()
    
    def test_analyze_data(self):
        """测试数据分析"""
        # 调用方法
        self.main_window.analyze_data()
        
        # 验证命令执行
        self.main_window.analyze_data_command.execute.assert_called_once()
    
    def test_generate_report(self):
        """测试生成报告"""
        # 调用方法
        self.main_window.generate_report()
        
        # 验证命令执行
        self.main_window.generate_report_command.execute.assert_called_once()
    
    def test_run_visualizer(self):
        """测试运行可视化工具"""
        # 调用方法
        test_xml_path = "test.xml"
        self.main_window.run_visualizer(test_xml_path)
        
        # 验证可视化管理器的run_visualizer方法被调用
        self.main_window.visualization_manager.run_visualizer.assert_called_once_with(test_xml_path)
    
    def test_batch_processing(self):
        """测试批量处理"""
        # 调用方法
        self.main_window.batch_processing()
        
        # 验证命令执行
        self.main_window.batch_processing_command.execute.assert_called_once()
    
    def test_save_settings(self):
        """测试保存设置"""
        # 调用方法
        self.main_window.save_settings()
        
        # 验证config_manager的save_user_settings方法被调用
        self.main_window.config_manager.save_user_settings.assert_called_once()
    
    def test_export_report(self):
        """测试导出报告"""
        # 调用方法
        self.main_window.export_report()
        
        # 验证命令执行
        self.main_window.export_report_command.execute.assert_called_once()
    
    def test_set_theme(self):
        """测试设置主题"""
        # 调用方法
        test_theme = "dark"
        self.main_window.set_theme(test_theme)
        
        # 验证theme_manager的set_theme方法被调用
        self.main_window.theme_manager.set_theme.assert_called_once_with(test_theme)
    
    def test_validate_version(self):
        """测试验证版本"""
        # 调用方法
        self.main_window.validate_version()
        
        # 验证validation_manager的validate_version方法被调用
        self.main_window.validation_manager.validate_version.assert_called_once()
    
    def test_validate_input_path(self):
        """测试验证输入路径"""
        # 调用方法
        self.main_window.validate_input_path()
        
        # 验证validation_manager的validate_input_path方法被调用
        self.main_window.validation_manager.validate_input_path.assert_called_once()
    
    def test_check_batterytype(self):
        """测试检查电池类型"""
        # 调用方法
        self.main_window.check_batterytype()
        
        # 验证validation_manager的check_batterytype方法被调用
        self.main_window.validation_manager.check_batterytype.assert_called_once()
    
    def test_check_specification(self):
        """测试检查规格"""
        # 调用方法
        self.main_window.check_specification()
        
        # 验证validation_manager的check_specification方法被调用
        self.main_window.validation_manager.check_specification.assert_called_once()
    
    def test_select_testprofile(self):
        """测试选择测试配置文件"""
        # 调用方法
        self.main_window.select_testprofile()
        
        # 验证test_profile_manager的select_testprofile方法被调用
        self.main_window.test_profile_manager.select_testprofile.assert_called_once()
    
    def test_select_inputpath(self):
        """测试选择输入路径"""
        # 调用方法
        self.main_window.select_inputpath()
        
        # 验证path_manager的select_inputpath方法被调用
        self.main_window.path_manager.select_inputpath.assert_called_once()
    
    def test_select_outputpath(self):
        """测试选择输出路径"""
        # 调用方法
        self.main_window.select_outputpath()
        
        # 验证path_manager的select_outputpath方法被调用
        self.main_window.path_manager.select_outputpath.assert_called_once()
    
    def test_run(self):
        """测试运行分析"""
        # 调用方法
        self.main_window.run()
        
        # 验证命令执行
        self.main_window.run_analysis_command.execute.assert_called_once()
    
    def test_get_xlsxinfo(self):
        """测试获取Excel文件信息"""
        # 调用方法
        self.main_window.get_xlsxinfo()
        
        # 验证data_processor的get_xlsxinfo方法被调用
        self.main_window.data_processor.get_xlsxinfo.assert_called_once()
    
    def test_get_version(self):
        """测试获取版本"""
        # 调用方法
        self.main_window.get_version()
        
        # 验证version_manager的get_version方法被调用
        self.main_window.version_manager.get_version.assert_called_once()
    
    def test_on_temperature_type_changed(self):
        """测试温度类型变化处理"""
        # 调用方法
        test_index = 1
        self.main_window.on_temperature_type_changed(test_index)
        
        # 验证temperature_handler的on_temperature_type_changed方法被调用
        self.main_window.temperature_handler.on_temperature_type_changed.assert_called_once()
    
    def test_checkinput(self):
        """测试检查输入"""
        # 调用方法
        result = self.main_window.checkinput()
        
        # 验证validation_manager的checkinput方法被调用
        self.main_window.validation_manager.checkinput.assert_called_once()
        # 验证返回值
        assert result is True
    
    def test_rename_pltPath(self):
        """测试重命名图表路径"""
        # 调用方法
        test_date = "2024-01-01"
        self.main_window.rename_pltPath(test_date)
        
        # 验证config_manager的rename_pltPath方法被调用
        self.main_window.config_manager.rename_pltPath.assert_called_once_with(test_date)
    
    def test_update_config(self):
        """测试更新配置"""
        # 调用方法
        test_info = {"TestDate": "2024-01-01"}
        self.main_window.update_config(test_info)
        
        # 验证config_manager的update_config方法被调用
        self.main_window.config_manager.update_config.assert_called_once_with(test_info)
