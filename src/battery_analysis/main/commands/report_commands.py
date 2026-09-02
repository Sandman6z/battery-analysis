import logging

from battery_analysis.main.commands.base import Command


class ExportReportCommand(Command):
    """
    导出报告命令
    """

    def __init__(self, presenter):
        """
        初始化导出报告命令

        Args:
            presenter: Presenter实例
        """
        self.presenter = presenter

    def execute(self):
        """
        执行导出报告命令
        """
        try:
            self.presenter.on_export_report()
            return True
        except Exception as e:
            logging.error(f"Failed to export report: {e!s}")
            return False


class GenerateReportCommand(Command):
    """
    生成报告命令
    """

    def __init__(self, presenter):
        """
        初始化生成报告命令

        Args:
            presenter: Presenter实例
        """
        self.presenter = presenter

    def execute(self):
        """
        执行生成报告命令
        """
        try:
            self.presenter.on_generate_report()
            return True
        except Exception as e:
            logging.error(f"Failed to generate report: {e!s}")
            return False


class BatchProcessingCommand(Command):
    """
    批量处理命令
    """

    def __init__(self, presenter):
        """
        初始化批量处理命令

        Args:
            presenter: Presenter实例
        """
        self.presenter = presenter

    def execute(self):
        """
        执行批量处理命令
        """
        try:
            self.presenter.on_batch_processing()
            return True
        except Exception as e:
            logging.error(f"Failed to batch process: {e!s}")
            return False


