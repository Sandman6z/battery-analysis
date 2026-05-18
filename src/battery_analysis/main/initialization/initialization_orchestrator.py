# -*- coding: utf-8 -*-
"""
初始化协调器

负责管理和执行所有初始化步骤，支持按阶段分组的模块化初始化流程。
阶段顺序执行，阶段内步骤按优先级排序（同优先级可并行）。
"""

import logging
import concurrent.futures
from typing import Dict, List, Optional, Tuple
from battery_analysis.main.initialization.initialization_step import InitializationStep


class InitializationOrchestrator:
    """初始化协调器，支持按阶段分组管理初始化步骤"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._phases: Dict[str, List[InitializationStep]] = {}
        self._phase_order: List[str] = []
        self._executed_steps: Dict[str, bool] = {}

    def register_step(self, step: InitializationStep, phase: str) -> None:
        """
        注册初始化步骤到指定阶段

        Args:
            step: 初始化步骤实例
            phase: 阶段名称
        """
        if phase not in self._phases:
            self._phases[phase] = []
            self._phase_order.append(phase)
        self._phases[phase].append(step)

    def register_steps(self, steps: List[InitializationStep], phase: str) -> None:
        """
        批量注册初始化步骤到指定阶段

        Args:
            steps: 初始化步骤列表
            phase: 阶段名称
        """
        for step in steps:
            self.register_step(step, phase)

    def execute_all(self, main_window) -> bool:
        """
        按阶段顺序执行所有初始化步骤

        Args:
            main_window: 主窗口实例

        Returns:
            是否所有步骤都执行成功
        """
        self.logger.info("=" * 50)
        self.logger.info("开始执行初始化流程")

        all_success = True
        total_executed = 0
        total_failed = 0

        for phase_name in self._phase_order:
            steps = self._phases.get(phase_name, [])
            if not steps:
                continue

            self.logger.info("")
            self.logger.info("▶ 阶段 [%s] — %d 个步骤", phase_name, len(steps))

            success, executed, failed = self._execute_phase(phase_name, steps, main_window)
            if not success:
                all_success = False
            total_executed += executed
            total_failed += failed

        self.logger.info("")
        self.logger.info("=" * 50)
        self.logger.info("初始化完成 — 成功: %d, 失败: %d, 阶段: %d",
                         total_executed, total_failed, len(self._phase_order))
        return all_success

    def _execute_phase(self, phase_name: str, steps: List[InitializationStep],
                       main_window) -> Tuple[bool, int, int]:
        """
        执行单个阶段内的所有步骤（按优先级分组，同优先级并行）

        Args:
            phase_name: 阶段名称
            steps: 步骤列表
            main_window: 主窗口实例

        Returns:
            (是否全部成功, 成功数, 失败数)
        """
        # 按优先级分组（同优先级步骤可并行执行）
        priority_groups: Dict[int, List[InitializationStep]] = {}
        for step in steps:
            p = step.get_priority()
            if p not in priority_groups:
                priority_groups[p] = []
            priority_groups[p].append(step)

        phase_success = True
        phase_executed = 0
        phase_failed = 0

        # 按优先级顺序执行每组
        for priority in sorted(priority_groups.keys()):
            group = [s for s in priority_groups[priority] if s.can_execute(main_window)]
            if not group:
                continue

            if len(group) == 1:
                self._execute_step(group[0], main_window)
            else:
                self._execute_parallel(group, main_window)

            for step in group:
                if self._executed_steps.get(step.get_name(), False):
                    phase_executed += 1
                else:
                    phase_failed += 1
                    phase_success = False

        status = "全部成功 ✓" if phase_success else f"成功 {phase_executed}, 失败 {phase_failed} ⚠"
        self.logger.info("  阶段 [%s] %s", phase_name, status)
        return phase_success, phase_executed, phase_failed

    def _execute_step(self, step: InitializationStep, main_window) -> None:
        """执行单个初始化步骤"""
        try:
            success = step.execute(main_window)
            self._executed_steps[step.get_name()] = success
            if success:
                self.logger.debug("  ✓ %s", step.get_name())
            else:
                self.logger.error("  ✗ %s", step.get_name())
        except Exception as e:
            self.logger.exception("步骤执行异常: %s", step.get_name())
            self._executed_steps[step.get_name()] = False

    def _execute_parallel(self, steps: List[InitializationStep], main_window) -> None:
        """并行执行一组步骤"""
        step_names = [s.get_name() for s in steps]
        self.logger.info("  并行执行: %s", ", ".join(step_names))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_step = {
                executor.submit(self._execute_step, step, main_window): step
                for step in steps
            }
            for future in concurrent.futures.as_completed(future_to_step):
                try:
                    future.result()
                except Exception as e:
                    step = future_to_step[future]
                    self.logger.exception("获取步骤执行结果异常: %s", step.get_name())

    # ── 查询与维护 ──────────────────────────────────────

    def get_step(self, name: str) -> Optional[InitializationStep]:
        """根据名称查找步骤"""
        for step_list in self._phases.values():
            for step in step_list:
                if step.get_name() == name:
                    return step
        return None

    def get_executed_steps(self) -> Dict[str, bool]:
        """获取已执行步骤的结果"""
        return self._executed_steps.copy()

    def get_total_steps(self) -> int:
        """获取所有阶段的总步骤数"""
        return sum(len(steps) for steps in self._phases.values())

    def get_pending_steps(self) -> List[InitializationStep]:
        """获取所有阶段中未执行的步骤"""
        pending = []
        for step_list in self._phases.values():
            for step in step_list:
                if step.get_name() not in self._executed_steps:
                    pending.append(step)
        return pending

    def get_phases(self) -> Dict[str, List[InitializationStep]]:
        """获取所有阶段及其步骤"""
        return {name: list(steps) for name, steps in self._phases.items()}

    def clear(self) -> None:
        """清空所有阶段的步骤和执行结果"""
        self._phases.clear()
        self._phase_order.clear()
        self._executed_steps.clear()
