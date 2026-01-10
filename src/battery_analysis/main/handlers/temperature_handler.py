"""温度处理类"""
import os
from enum import Enum


class TemperatureType(Enum):
    """温度类型枚举"""
    ROOM = "Room Temperature"
    FREEZER = "Freezer Temperature"


class TemperatureHandler:
    """温度处理类"""
    
    def __init__(self, main_window):
        """
        初始化温度处理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
    
    def detect_temperature_type_from_xml(self, xml_path: str) -> TemperatureType:
        """
        根据XML文件名自动检测温度类型
        
        规则：
        - 文件名中包含"Freezer"（不区分大小写），表示冷冻温度
        - 否则表示常温
        
        Args:
            xml_path: XML文件的完整路径
            
        Returns:
            检测到的温度类型枚举值
        """
        try:
            # 获取文件名
            file_name = os.path.basename(xml_path)
            
            # 根据文件名检测温度类型
            if "Freezer" in file_name.lower():
                return TemperatureType.FREEZER
            else:
                return TemperatureType.ROOM
        except Exception as e:
            self.main_window.logger.warning("检测温度类型时发生错误: %s", e)
            return TemperatureType.ROOM
    
    def get_temperature_value(self) -> str:
        """
        构建温度值字符串
        
        Returns:
            格式化的温度值字符串
        """
        temperature_type = self.main_window.comboBox_Temperature.currentText()
        if temperature_type == TemperatureType.FREEZER.value:
            return f"{temperature_type}:{self.main_window.spinBox_Temperature.value()}"
        else:  # Room Temperature
            return temperature_type
    
    def update_temperature_ui(self, temperature_type: TemperatureType):
        """
        根据温度类型更新UI
        
        Args:
            temperature_type: 温度类型枚举值
        """
        # 设置组合框选中项
        self.main_window.comboBox_Temperature.setCurrentText(temperature_type.value)
        
        # 启用或禁用spinBox
        self.main_window.spinBox_Temperature.setEnabled(
            temperature_type == TemperatureType.FREEZER
        )
    
    def on_temperature_type_changed(self):
        """
        处理温度类型变化事件
        """
        temperature_type = self.main_window.comboBox_Temperature.currentText()
        self.main_window.spinBox_Temperature.setEnabled(
            temperature_type == TemperatureType.FREEZER.value
        )