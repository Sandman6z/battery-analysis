# -*- coding: utf-8 -*-
"""
UI设置步骤
"""

from battery_analysis.main.initialization.initialization_step import InitializationStep


class UISetupStep(InitializationStep):
    """UI设置步骤"""
    
    def __init__(self):
        """初始化UI设置步骤"""
        super().__init__("ui_setup", priority=40)
    
    def execute(self, main_window) -> bool:
        """
        执行UI设置
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否执行成功
        """
        try:
            # 设置控制器的项目上下文
            try:
                main_controller = main_window._get_controller("main_controller")
                if main_controller and hasattr(main_controller, 'set_project_context'):
                    main_controller.set_project_context(
                        project_path=main_window.path,
                        input_path="",  # 初始empty，后续会更新
                        output_path=""  # 初始empty，后续会更新
                    )
            except (AttributeError, TypeError, ValueError) as e:
                self.logger.warning("Failed to set project context: %s", e)

            main_window.setupUi(main_window)
            self.logger.info("UI设置完成")
            return True
        except Exception as e:
            self.logger.exception("UI设置失败")
            return False
    
    def can_execute(self, main_window) -> bool:
        """
        检查是否可以执行此步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否可以执行
        """
        return True
