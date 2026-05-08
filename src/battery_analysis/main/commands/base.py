from abc import ABC, abstractmethod


class Command(ABC):
    """
    命令基类，定义了命令执行的接口
    """

    @abstractmethod
    def execute(self):
        """
        执行命令

        Returns:
            bool: 命令执行是否成功
        """
        pass
