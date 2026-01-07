"""
温度检测工具模块

根据XML文件名自动检测温度类型
"""
import os
import logging


def detect_temperature_type_from_xml(xml_path: str) -> str:
    """
    根据XML文件名自动检测温度类型
    
    规则：
    - 文件名中包含"Freezer"（不区分大小写），表示冷冻温度
    - 否则表示常温
    
    Args:
        xml_path: XML文件的完整路径
        
    Returns:
        str: "Freezer Temperature" 或 "Room Temperature"
    """
    try:
        # 获取文件名
        file_name = os.path.basename(xml_path)
        
        # 检查文件名中是否包含"freezer"（不区分大小写）
        if "freezer" in file_name.lower():
            return "Freezer Temperature"
        
        # 默认常温
        return "Room Temperature"
        
    except (AttributeError, ValueError) as e:
        logging.warning("检测温度类型时发生错误: %s", e)
        return "Room Temperature"


def is_freezer_temperature(xml_path: str) -> bool:
    """
    检查XML文件是否对应冷冻温度测试
    
    Args:
        xml_path: XML文件的完整路径
        
    Returns:
        bool: True表示冷冻温度，False表示常温
    """
    return detect_temperature_type_from_xml(xml_path) == "Freezer Temperature"


def is_room_temperature(xml_path: str) -> bool:
    """
    检查XML文件是否对应常温测试
    
    Args:
        xml_path: XML文件的完整路径
        
    Returns:
        bool: True表示常温，False表示冷冻温度
    """
    return detect_temperature_type_from_xml(xml_path) == "Room Temperature"
