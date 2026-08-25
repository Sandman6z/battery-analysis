import logging

from battery_analysis.main.commands.base import Command


class AnalyzeDataCommand(Command):
    """
    分析数据命令
    """

    def __init__(self, presenter):
        """
        初始化分析数据命令

        Args:
            presenter: Presenter实例
        """
        self.presenter = presenter

    def execute(self):
        """
        执行分析数据命令
        """
        try:
            self.presenter.on_analyze_data()
            return True
        except Exception as e:
            logging.error(f"Failed to analyze data: {str(e)}")
            return False
