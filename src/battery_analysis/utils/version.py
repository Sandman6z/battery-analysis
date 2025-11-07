import setuptools_scm

try:
    # 获取版本号（开发环境）
    __version__ = setuptools_scm.get_version(root='../../..', relative_to=__file__)
except Exception:
    # 作为已安装包获取版本号
    try:
        from importlib.metadata import version
        __version__ = version("battery-analysis")
    except ImportError:
        # 最后回退
        __version__ = "0.0.0"

class Version(object):
    def __init__(self):
        self.version = __version__
