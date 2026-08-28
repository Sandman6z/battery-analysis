import logging

from battery_analysis.main.commands.base import Command


class RunAnalysisCommand(Command):
    """
    运行电池分析命令
    """

    def __init__(self, analysis_runner):
        """
        初始化运行分析命令

        Args:
            analysis_runner: 分析运行器实例
        """
        self.analysis_runner = analysis_runner

    def execute(self):
        """
        执行运行分析命令
        """
        try:
            self.analysis_runner.run_analysis()
            return True
        except Exception as e:
            logging.error(f"Failed to run analysis: {e!s}")
            return False


class CalculateBatteryCommand(Command):
    """
    计算电池命令
    """

    def __init__(self, presenter):
        """
        初始化计算电池命令

        Args:
            presenter: Presenter实例
        """
        self.presenter = presenter

    def execute(self):
        """
        执行计算电池命令
        """
        try:
            self.presenter.on_calculate_battery()
            return True
        except Exception as e:
            logging.error(f"Failed to calculate battery: {e!s}")
            return False
