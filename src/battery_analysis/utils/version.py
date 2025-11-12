import os
import tomllib
import sys

class Version(object):
    def __init__(self):
        # 尝试从pyproject.toml读取版本号
        try:
            # 获取项目根目录（假设这个文件位于src/battery_analysis/utils/下）
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            
            # 读取pyproject.toml
            with open(os.path.join(project_root, "pyproject.toml"), "rb") as f:
                pyproject_data = tomllib.load(f)
            
            # 获取版本号
            self.version = pyproject_data.get("project", {}).get("version", "0.0.0")
            # 添加调试信息
            print(f"Version read from pyproject.toml: {self.version}", file=sys.stderr)
        except Exception as e:
            # 如果读取失败，使用默认版本号
            print(f"Error reading version: {e}", file=sys.stderr)
            self.version = "0.0.0"
