#!/usr/bin/env python3
"""
重写battery_chart_viewer.py中的__init__方法
"""
import re

def rewrite_init():
    file_path = "src/battery_analysis/main/battery_chart_viewer.py"
    
    print(f"重写 {file_path} 中的__init__方法...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到__init__方法的位置并替换
        init_pattern = r'class PlotConfig:.*?def __init__\(self, data_path=None\):.*?self\.config=configparser\.ConfigParser\(\)'
        
        replacement = '''    class PlotConfig:
        """
        Chart configuration class for storing configurable chart parameters
        
        Attributes:
        axis_default: Default axis range [xmin, xmax, ymin, ymax]
        axis_special: Axis range under special rules [xmin, xmax, ymin, ymax]
        """
        pass

    def __init__(self, data_path=None):
        """
        Initialize BatteryChartViewer class, set default configuration and load user configuration
        
        Initialize chart parameters, read configuration file, and set default values. If configuration file does not exist,
        use hardcoded default values.

        Args:
            data_path: Optional, specify the directory path to load data
        """
        self.config = configparser.ConfigParser()

        # Initialize language manager
        self.language_manager = get_language_manager()
        self.language_manager.language_changed.connect(self._on_language_changed)'''
        
        content = re.sub(init_pattern, replacement, content, flags=re.DOTALL)
        
        # 修复更多的缩进和空格问题
        content = re.sub(r'self\.config=configparser\.ConfigParser\(\)', 'self.config = configparser.ConfigParser()', content)
        content = re.sub(r'self\.language_manager=get_language_manager\(\)', 'self.language_manager = get_language_manager()', content)
        content = re.sub(r'self\.language_manager\.language_changed\.connect\(self\._on_language_changed\)', 
                        'self.language_manager.language_changed.connect(self._on_language_changed)', content)
        
        # 修复变量赋值
        content = re.sub(r'if\s+not\s+self\.config\.has_section\(\"PltConfig\"\)', 
                        'if not self.config.has_section("PltConfig")', content)
        content = re.sub(r'self\.config\.add_section\(\"PltConfig\"\)', 
                        'self.config.add_section("PltConfig")', content)
        content = re.sub(r'current_dir=Path\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)', 
                        'current_dir = Path(os.path.dirname(os.path.abspath(__file__)))', content)
        content = re.sub(r'self\.project_root=current_dir\.parent\.parent', 
                        'self.project_root = current_dir.parent.parent', content)
        content = re.sub(r'self\.path=self\.project_root', 'self.path = self.project_root', content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("__init__方法重写完成")
        return True
        
    except Exception as e:
        print(f"重写过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    rewrite_init()