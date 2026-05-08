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
            logging.error(f"分析数据失败: {str(e)}")
            return False


class ProcessExcelCommand(Command):
    """
    处理Excel文件命令
    """

    def __init__(self, data_processor, file_path):
        """
        初始化处理Excel文件命令

        Args:
            data_processor: 数据处理器实例
            file_path: Excel文件路径
        """
        self.data_processor = data_processor
        self.file_path = file_path

    def execute(self):
        """
        执行处理Excel文件命令
        """
        try:
            return self.data_processor.process_excel_with_pandas(self.file_path)
        except Exception as e:
            logging.error(f"处理Excel文件失败: {str(e)}")
            return {}


class ProcessAllExcelCommand(Command):
    """
    批量处理Excel文件命令
    """

    def __init__(self, data_processor, directory):
        """
        初始化批量处理Excel文件命令

        Args:
            data_processor: 数据处理器实例
            directory: 包含Excel文件的目录
        """
        self.data_processor = data_processor
        self.directory = directory

    def execute(self):
        """
        执行批量处理Excel文件命令
        """
        try:
            return self.data_processor.process_all_excel_files(self.directory)
        except Exception as e:
            logging.error(f"批量处理Excel文件失败: {str(e)}")
            return []


class GetXlsxInfoCommand(Command):
    """
    获取Excel文件信息命令
    """

    def __init__(self, data_processor):
        """
        初始化获取Excel文件信息命令

        Args:
            data_processor: 数据处理器实例
        """
        self.data_processor = data_processor

    def execute(self):
        """
        执行获取Excel文件信息命令
        """
        try:
            self.data_processor.get_xlsxinfo()
            return True
        except Exception as e:
            logging.error(f"获取Excel文件信息失败: {str(e)}")
            return False


class SaveTableCommand(Command):
    """
    保存表格数据命令
    """

    def __init__(self, data_processor):
        """
        初始化保存表格数据命令

        Args:
            data_processor: 数据处理器实例
        """
        self.data_processor = data_processor

    def execute(self):
        """
        执行保存表格数据命令
        """
        try:
            self.data_processor.save_table()
            return True
        except Exception as e:
            logging.error(f"保存表格数据失败: {str(e)}")
            return False


class UpdateConfigCommand(Command):
    """
    更新配置命令
    """

    def __init__(self, data_processor, test_info):
        """
        初始化更新配置命令

        Args:
            data_processor: 数据处理器实例
            test_info: 测试信息
        """
        self.data_processor = data_processor
        self.test_info = test_info

    def execute(self):
        """
        执行更新配置命令
        """
        try:
            self.data_processor.update_config(self.test_info)
            return True
        except Exception as e:
            logging.error(f"更新配置失败: {str(e)}")
            return False


class CheckInputCommand(Command):
    """
    检查输入命令
    """

    def __init__(self, battery_calculator):
        """
        初始化检查输入命令

        Args:
            battery_calculator: 电池计算器实例
        """
        self.battery_calculator = battery_calculator

    def execute(self):
        """
        执行检查输入命令
        """
        try:
            return self.battery_calculator.check_input()
        except Exception as e:
            logging.error(f"检查输入失败: {str(e)}")
            return False


class HandleDataErrorCommand(Command):
    """
    处理数据错误命令
    """

    def __init__(self, data_processor, error_msg):
        """
        初始化处理数据错误命令

        Args:
            data_processor: 数据处理器实例
            error_msg: 错误信息
        """
        self.data_processor = data_processor
        self.error_msg = error_msg

    def execute(self):
        """
        执行处理数据错误命令
        """
        try:
            self.data_processor.handle_data_error_recovery(self.error_msg)
            return True
        except Exception as e:
            logging.error(f"处理数据错误失败: {str(e)}")
            return False
