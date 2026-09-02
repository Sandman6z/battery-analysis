"""单一版本源。

全工程唯一的版本号来源：pyproject.toml（动态读取）、__init__.__version__、
utils/version.py、构建脚本与 CI 均从这里取值。升级版本时只需修改此文件。
"""

__version__ = "3.1.1"
