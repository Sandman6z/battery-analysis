"""初始化实际使用的分析命令。"""

from battery_analysis.main.commands import RunAnalysisCommand


class CommandManager:
    """将运行按钮和分析菜单共用的命令暴露给主窗口。"""

    def __init__(self, main_window):
        self.main_window = main_window
        main_window.run_analysis_command = RunAnalysisCommand(main_window.analysis_runner)
