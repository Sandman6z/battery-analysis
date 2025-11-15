import os
import tomllib
import sys

class Version(object):
    def __init__(self):
        # 改进的版本号读取逻辑，兼容开发和打包环境
        try:
            # 首先检查是否在PyInstaller打包环境中
            if getattr(sys, 'frozen', False):
                # 在打包环境中，尝试从exe目录查找pyproject.toml
                exe_dir = os.path.dirname(sys.executable)
                exe_pyproject_path = os.path.join(exe_dir, "pyproject.toml")
                
                if os.path.exists(exe_pyproject_path):
                    with open(exe_pyproject_path, "rb") as f:
                        pyproject_data = tomllib.load(f)
                    self.version = pyproject_data.get("project", {}).get("version", "1.0.1")
                    print(f"Version read from exe directory pyproject.toml: {self.version}", file=sys.stderr)
                else:
                    # 如果exe目录下没有pyproject.toml，使用硬编码版本
                    self.version = "1.0.1"
                    print(f"Using hardcoded version in PyInstaller environment: {self.version}", file=sys.stderr)
            else:
                # 在开发环境中，尝试从pyproject.toml读取版本号
                # 获取项目根目录（假设这个文件位于src/battery_analysis/utils/下）
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
                pyproject_path = os.path.join(project_root, "pyproject.toml")
                
                # 检查文件是否存在
                if not os.path.exists(pyproject_path):
                    raise FileNotFoundError(f"pyproject.toml not found at: {pyproject_path}")
                
                # 读取pyproject.toml
                with open(pyproject_path, "rb") as f:
                    pyproject_data = tomllib.load(f)
                
                # 获取版本号
                self.version = pyproject_data.get("project", {}).get("version", "1.0.1")
                print(f"Version read from pyproject.toml: {self.version}", file=sys.stderr)
                
        except Exception as e:
            # 如果读取失败，使用默认版本号
            print(f"Error reading version: {e}", file=sys.stderr)
            self.version = "1.0.1"  # 使用一致的默认版本号
            print(f"Using default version: {self.version}", file=sys.stderr)
