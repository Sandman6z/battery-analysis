#!/usr/bin/env python3
"""
调试PyInstaller可执行文件的问题
"""

import os
import sys
import traceback

def test_main_window():
    """测试主窗口初始化"""
    print("=== 测试主窗口初始化 ===")
    try:
        # 测试导入
        print("1. 测试导入...")
        from src.battery_analysis.ui import ui_main_window
        print("   ✅ UI模块导入成功")
        
        from src.battery_analysis.utils import version
        print("   ✅ Version模块导入成功")
        
        from src.battery_analysis.main.main_window import Main
        print("   ✅ Main类导入成功")
        
        # 测试配置读取
        print("2. 测试配置读取...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        config_path = os.path.join(project_root, "config", "setting.ini")
        print(f"   配置路径: {config_path}")
        print(f"   配置文件存在: {os.path.exists(config_path)}")
        
        if os.path.exists(config_path):
            import PyQt5.QtCore as QC
            config = QC.QSettings(config_path, QC.QSettings.IniFormat)
            print("   ✅ 配置对象创建成功")
        
        # 测试版本信息
        print("3. 测试版本信息...")
        version_info = version.Version()
        print(f"   版本号: {version_info.version}")
        
        print("4. 测试完成，所有组件正常！")
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        print("详细错误:")
        traceback.print_exc()
        return False

def test_pyinstaller_environment():
    """测试PyInstaller环境"""
    print("\n=== 测试PyInstaller环境 ===")
    
    # 检查是否为打包环境
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        print("1. 检测到PyInstaller打包环境")
        print(f"   临时目录: {sys._MEIPASS}")
    else:
        print("1. 检测到开发环境（未打包）")
    
    # 检查当前工作目录
    print(f"2. 当前工作目录: {os.getcwd()}")
    
    # 检查可执行文件位置
    print(f"3. 可执行文件位置: {sys.executable}")
    
    # 检查相对路径
    exe_dir = os.path.dirname(sys.executable)
    print(f"4. 可执行文件目录: {exe_dir}")
    
    # 检查配置文件是否存在
    exe_config_path = os.path.join(exe_dir, "config", "setting.ini")
    print(f"5. exe目录配置路径: {exe_config_path}")
    print(f"6. exe目录配置存在: {os.path.exists(exe_config_path)}")

def main():
    print("开始诊断PyInstaller可执行文件问题...")
    
    # 测试组件
    test_result = test_main_window()
    
    # 测试环境
    test_pyinstaller_environment()
    
    print("\n=== 诊断结果 ===")
    if test_result:
        print("✅ 所有组件测试通过")
        print("问题可能出在PyInstaller的依赖配置上")
    else:
        print("❌ 组件测试失败")

if __name__ == "__main__":
    main()