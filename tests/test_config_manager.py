#!/usr/bin/env python3
"""
测试配置管理器的get_config方法
"""

import logging
from pathlib import Path
from battery_analysis.main.ui_components.config_manager import ConfigManager
import PyQt6.QtCore as QC
import PyQt6.QtWidgets as QW

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MockMainWindow:
    """模拟Main窗口类，用于测试ConfigManager"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def _get_service(self, service_name):
        """模拟获取服务的方法"""
        return None

def test_get_config():
    """测试get_config方法"""
    # 创建QApplication实例，这是Qt所需的
    app = QW.QApplication([])
    
    # 创建模拟的Main窗口实例
    main_window = MockMainWindow()
    
    # 创建配置管理器实例
    config_manager = ConfigManager(main_window)
    
    # 测试获取TesterLocation配置
    tester_locations = config_manager.get_config('TestConfig/TesterLocation')
    print('Tester locations:', tester_locations)
    print('Number of tester locations:', len(tester_locations))
    
    # 测试获取其他配置
    battery_types = config_manager.get_config('BatteryConfig/BatteryType')
    print('Battery types:', battery_types)
    print('Number of battery types:', len(battery_types))
    
    # 测试获取不存在的配置
    non_existent = config_manager.get_config('NonExistent/ConfigKey')
    print('Non-existent config:', non_existent)
    print('Number of non-existent config:', len(non_existent))

if __name__ == '__main__':
    test_get_config()
