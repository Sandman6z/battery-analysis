"""
应用异常体系

分层异常类，替代全局只有一个 BatteryAnalysisException 的状况。
每层异常继承自 BaseAppException，携带 error_code 用于 UI 层展示。
"""


class BaseAppException(Exception):
    """所有应用异常的基类。"""

    def __init__(self, message: str, error_code: int = 500):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


# ── 数据层 ────────────────────────────────────────────────────


class DataException(BaseAppException):
    """数据读取/写入相关错误。"""

    def __init__(self, message: str, error_code: int = 400):
        super().__init__(message, error_code)


class FileNotFoundException(DataException):
    def __init__(self, path: str):
        super().__init__(f"File not found: {path}", 404)


class FileFormatException(DataException):
    """Excel/CSV/XML 格式不符合预期。"""

    def __init__(self, detail: str = "", error_code: int = 422):
        super().__init__(f"File format error: {detail}", error_code)


class ConfigException(BaseAppException):
    """配置相关错误。"""

    def __init__(self, message: str, error_code: int = 500):
        super().__init__(f"Configuration error: {message}", error_code)


# ── 分析引擎层 ────────────────────────────────────────────────


class AnalysisException(BaseAppException):
    """电池分析引擎错误。"""

    def __init__(self, message: str, error_code: int = 500):
        super().__init__(message, error_code)


class ValidationException(BaseAppException):
    """输入数据验证失败。"""

    def __init__(self, message: str, error_code: int = 422):
        super().__init__(f"Validation failed: {message}", error_code)


# ── 应用/UI 层 ────────────────────────────────────────────────


class ServiceException(BaseAppException):
    """服务不可用或初始化失败。"""

    def __init__(self, service_name: str, detail: str = ""):
        msg = f"Service '{service_name}' unavailable"
        if detail:
            msg += f": {detail}"
        super().__init__(msg, 503)


class InitializationException(BaseAppException):
    """应用初始化阶段失败。"""

    def __init__(self, component: str, detail: str = ""):
        msg = f"Component '{component}' initialization failed"
        if detail:
            msg += f": {detail}"
        super().__init__(msg, 500)


# ── 保持向后兼容 ──────────────────────────────────────────────


# BatteryAnalysisException 仍然可用，只是现在继承自 BaseAppException
class BatteryAnalysisException(BaseAppException):
    """已弃用 — 请使用更具体的异常子类。"""

    def __init__(self, message: str, error_code: int = 500):
        super().__init__(message, error_code)
