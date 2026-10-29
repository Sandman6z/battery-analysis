"""实际使用的配置、分析与报告异常，携带供界面展示的错误码。"""


class BaseAppException(Exception):
    """所有应用异常的基类。"""

    def __init__(self, message: str, error_code: int = 500):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class ConfigException(BaseAppException):
    """配置相关错误。"""

    def __init__(self, message: str, error_code: int = 500):
        super().__init__(f"Configuration error: {message}", error_code)


class BatteryAnalysisException(BaseAppException):
    """电池分析与报告生成错误。"""

    def __init__(self, message: str, error_code: int = 500):
        super().__init__(message, error_code)
