# -*- coding: utf-8 -*-
"""
初始化协调器

负责管理和执行所有初始化步骤，实现模块化初始化流程
"""

import logging
from typing import List, Dict, Any, Optional
from battery_analysis.main.initialization.initialization_step import InitializationStep


class InitializationOrchestrator:
    """初始化协调器，负责管理和执行初始化步骤"""
    
    def __init__(self):
        """初始化协调器"""
        self.logger = logging.getLogger(__name__)
        self._steps: List[InitializationStep] = []
        self._executed_steps: Dict[str, bool] = {}
    
    def register_step(self, step: InitializationStep) -> None:
        """
        注册初始化步骤
        
        Args:
            step: 初始化步骤实例
        """
        self.logger.debug("注册初始化步骤: %s (优先级: %d)", step.get_name(), step.get_priority())
        self._steps.append(step)
    
    def register_steps(self, steps: List[InitializationStep]) -> None:
        """
        批量注册初始化步骤
        
        Args:
            steps: 初始化步骤列表
        """
        for step in steps:
            self.register_step(step)
    
    def execute_all(self, main_window) -> bool:
        """
        执行所有初始化步骤
        
        Args:
            main_window: 主窗口实例
            
        Returns:
            是否所有步骤都执行成功
        """
        self.logger.info("开始执行初始化流程")
        
        # 按优先级排序步骤
        sorted_steps = sorted(self._steps)
        
        # 执行所有步骤
        all_success = True
        executed_count = 0
        failed_count = 0
        
        for step in sorted_steps:
            self.logger.debug("准备执行步骤: %s (优先级: %d)", step.get_name(), step.get_priority())
            
            # 检查是否可以执行
            if not step.can_execute(main_window):
                self.logger.warning("跳过步骤: %s (条件不满足)", step.get_name())
                continue
            
            try:
                # 执行步骤
                success = step.execute(main_window)
                self._executed_steps[step.get_name()] = success
                
                if success:
                    self.logger.info("步骤执行成功: %s", step.get_name())
                    executed_count += 1
                else:
                    self.logger.error("步骤执行失败: %s", step.get_name())
                    failed_count += 1
                    all_success = False
                    
            except Exception as e:
                self.logger.exception("步骤执行异常: %s", step.get_name())
                self._executed_steps[step.get_name()] = False
                failed_count += 1
                all_success = False
        
        self.logger.info("初始化流程完成 - 成功: %d, 失败: %d, 总计: %d", 
                       executed_count, failed_count, executed_count + failed_count)
        
        return all_success
    
    def get_step(self, name: str) -> Optional[InitializationStep]:
        """
        根据名称获取初始化步骤
        
        Args:
            name: 步骤名称
            
        Returns:
            初始化步骤实例，或None
        """
        for step in self._steps:
            if step.get_name() == name:
                return step
        return None
    
    def get_executed_steps(self) -> Dict[str, bool]:
        """
        获取已执行步骤的结果
        
        Returns:
            已执行步骤的结果字典，键为步骤名称，值为是否成功
        """
        return self._executed_steps.copy()
    
    def get_total_steps(self) -> int:
        """
        获取总步骤数
        
        Returns:
            总步骤数
        """
        return len(self._steps)
    
    def get_pending_steps(self) -> List[InitializationStep]:
        """
        获取未执行的步骤
        
        Returns:
            未执行的步骤列表
        """
        pending = []
        for step in self._steps:
            if step.get_name() not in self._executed_steps:
                pending.append(step)
        return pending
    
    def clear(self) -> None:
        """
        清空所有已注册的步骤和执行结果
        """
        self._steps.clear()
        self._executed_steps.clear()
