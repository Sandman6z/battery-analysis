# -*- coding: utf-8 -*-
"""
初始化协调器

负责管理和执行所有初始化步骤，实现模块化初始化流程
"""

import logging
import concurrent.futures
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
        
        # 按优先级分组步骤
        priority_groups = {}
        for step in sorted_steps:
            if step.get_priority() not in priority_groups:
                priority_groups[step.get_priority()] = []
            priority_groups[step.get_priority()].append(step)
        
        # 执行所有步骤
        all_success = True
        executed_count = 0
        failed_count = 0
        
        # 按优先级顺序执行每组步骤
        for priority in sorted(priority_groups.keys()):
            steps_in_group = priority_groups[priority]
            self.logger.debug("执行优先级组: %d, 包含步骤: %d个", priority, len(steps_in_group))
            
            # 过滤出可以执行的步骤
            executable_steps = [step for step in steps_in_group if step.can_execute(main_window)]
            
            if not executable_steps:
                self.logger.debug("跳过优先级组: %d (无步骤可执行)", priority)
                continue
            
            # 如果只有一个步骤，直接执行
            if len(executable_steps) == 1:
                step = executable_steps[0]
                self._execute_step(step, main_window)
                if step.get_name() in self._executed_steps:
                    if self._executed_steps[step.get_name()]:
                        executed_count += 1
                    else:
                        failed_count += 1
                        all_success = False
            else:
                # 并行执行多个步骤
                self.logger.info("并行执行步骤: %s", ", ".join([step.get_name() for step in executable_steps]))
                
                # 使用线程池并行执行
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # 提交所有任务
                    future_to_step = {executor.submit(self._execute_step, step, main_window): step for step in executable_steps}
                    
                    # 获取结果
                    for future in concurrent.futures.as_completed(future_to_step):
                        step = future_to_step[future]
                        try:
                            future.result()
                            if step.get_name() in self._executed_steps:
                                if self._executed_steps[step.get_name()]:
                                    executed_count += 1
                                else:
                                    failed_count += 1
                                    all_success = False
                        except Exception as e:
                            self.logger.exception("获取步骤执行结果异常: %s", step.get_name())
                            failed_count += 1
                            all_success = False
        
        self.logger.info("初始化流程完成 - 成功: %d, 失败: %d, 总计: %d", 
                       executed_count, failed_count, executed_count + failed_count)
        
        return all_success
    
    def _execute_step(self, step: InitializationStep, main_window) -> None:
        """
        执行单个初始化步骤
        
        Args:
            step: 初始化步骤
            main_window: 主窗口实例
        """
        self.logger.debug("准备执行步骤: %s (优先级: %d)", step.get_name(), step.get_priority())
        
        try:
            # 执行步骤
            success = step.execute(main_window)
            self._executed_steps[step.get_name()] = success
            
            if success:
                self.logger.info("步骤执行成功: %s", step.get_name())
            else:
                self.logger.error("步骤执行失败: %s", step.get_name())
                
        except Exception as e:
            self.logger.exception("步骤执行异常: %s", step.get_name())
            self._executed_steps[step.get_name()] = False
    
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
