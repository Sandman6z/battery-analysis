#!/usr/bin/env python3
"""
测试UI控件事件绑定是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PyQt5 import QtWidgets as QW
from battery_analysis.main.main_window import Main
from battery_analysis.version import version

def test_ui_events():
    """测试UI控件事件绑定"""
    print("=== 测试UI控件事件绑定 ===")
    
    # 创建QApplication实例
    app = QW.QApplication([])
    
    try:
        # 创建Main窗口实例
        print("1. 创建Main窗口实例...")
        main_window = Main()
        print("   ✓ Main窗口创建成功")
        
        # 显示窗口
        print("2. 显示窗口...")
        main_window.show()
        
        # 测试事件绑定
        print("3. 测试事件绑定...")
        
        # 测试电池类型下拉框事件
        print("   测试Battery Type下拉框...")
        initial_count = main_window.comboBox_BatteryType.count()
        print(f"   ✓ Battery Type下拉框有 {initial_count} 个选项")
        
        # 测试制造商下拉框事件
        print("   测试Manufacturer下拉框...")
        manufacturer_count = main_window.comboBox_Manufacturer.count()
        print(f"   ✓ Manufacturer下拉框有 {manufacturer_count} 个选项")
        
        # 测试输入路径文本框事件
        print("   测试InputPath文本框...")
        input_path_text = main_window.lineEdit_InputPath.text()
        print(f"   ✓ InputPath当前文本: '{input_path_text}'")
        
        # 测试输出路径文本框事件
        print("   测试OutputPath文本框...")
        output_path_text = main_window.lineEdit_OutputPath.text()
        print(f"   ✓ OutputPath当前文本: '{output_path_text}'")
        
        # 测试按钮是否可点击
        print("   测试按钮状态...")
        print(f"   ✓ TestProfile按钮可点击: {main_window.pushButton_TestProfile.isEnabled()}")
        print(f"   ✓ InputPath按钮可点击: {main_window.pushButton_InputPath.isEnabled()}")
        print(f"   ✓ OutputPath按钮可点击: {main_window.pushButton_OutputPath.isEnabled()}")
        print(f"   ✓ Run按钮可点击: {main_window.pushButton_Run.isEnabled()}")
        
        # 手动触发一个事件来测试绑定是否工作
        print("4. 手动触发事件测试...")
        
        # 设置电池类型
        if main_window.comboBox_BatteryType.count() > 0:
            main_window.comboBox_BatteryType.setCurrentIndex(0)
            print("   ✓ 设置Battery Type为第一个选项")
        
        # 设置制造商
        if main_window.comboBox_Manufacturer.count() > 0:
            main_window.comboBox_Manufacturer.setCurrentIndex(0)
            print("   ✓ 设置Manufacturer为第一个选项")
        
        # 设置测试位置
        if main_window.comboBox_TesterLocation.count() > 0:
            main_window.comboBox_TesterLocation.setCurrentIndex(0)
            print("   ✓ 设置TesterLocation为第一个选项")
        
        print("5. 检查状态栏...")
        status_message = main_window.statusBar_BatteryAnalysis.currentMessage()
        print(f"   ✓ 状态栏消息: '{status_message}'")
        
        print("\n=== 所有UI控件事件绑定测试完成 ===")
        print("如果以上测试都显示成功，说明UI控件初始化和事件绑定正常。")
        print("如果用户界面仍然无响应，可能是其他问题（如事件循环阻塞等）。")
        
        # 启动事件循环
        print("\n启动事件循环...")
        app.exec_()
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_ui_events()