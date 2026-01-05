"""
验证重构后的代码是否能正常工作
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("正在导入重构后的模块...")
    from battery_analysis.main.main_window import Main
    print("✅ 成功导入Main类")
    
    print("\n正在导入管理器类...")
    from battery_analysis.main.ui_manager import UIManager
    from battery_analysis.main.config_manager import ConfigManager
    from battery_analysis.main.menu_manager import MenuManager
    from battery_analysis.main.dialog_manager import DialogManager
    from battery_analysis.main.progress_dialog import ProgressDialog
    print("✅ 成功导入所有管理器类")
    
    print("\n重构验证通过！所有模块都能成功导入。")
    print("\n重构总结：")
    print("1. 将ProgressDialog类移到了单独的文件中")
    print("2. 创建了UI管理器类(UIManager)，负责UI初始化和设置")
    print("3. 创建了配置管理器类(ConfigManager)，负责配置文件的读取和写入")
    print("4. 创建了菜单管理器类(MenuManager)，负责菜单和工具栏的管理")
    print("5. 创建了对话框管理器类(DialogManager)，负责各种对话框的处理")
    print("6. 重构了Main类，使其成为核心协调者")
    
    print("\n建议：")
    print("1. 进一步重构Main类，将更多功能委托给相应的管理器")
    print("2. 运行完整的测试套件，确保功能正常")
    print("3. 进行集成测试，验证各个组件之间的协作是否正常")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
