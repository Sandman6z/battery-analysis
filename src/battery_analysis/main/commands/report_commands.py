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
            logging.error(f"导出报告失败: {str(e)}")
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
            logging.error(f"生成报告失败: {str(e)}")
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
            logging.error(f"批量处理失败: {str(e)}")
            return False


class SaveSettingsCommand(Command):
    """
    保存设置命令
    """

    def __init__(self, main_window):
        """
        初始化保存设置命令

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window

    def execute(self):
        """
        执行保存设置命令
        """
        try:
            # 直接调用Main类中的save_settings方法
            self.main_window.save_settings()
            return True
        except Exception as e:
            logging.error(f"保存设置失败: {str(e)}")
            return False
