# -*- coding: utf-8 -*-
"""
初始化管理器

负责处理主窗口的初始化逻辑，将 12 个初始化步骤整合为 4 个阶段：
  环境准备 → 核心服务 → UI 构建 → 启动完成
"""

import logging

from battery_analysis.main.initialization.initialization_orchestrator import (
    InitializationOrchestrator,
)
from battery_analysis.main.initialization.steps.basic_attributes_step import (
    BasicAttributesInitializationStep,
)
from battery_analysis.main.initialization.steps.services_initialization_step import (
    ServicesInitializationStep,
)
from battery_analysis.main.initialization.steps.environment_initialization_step import (
    EnvironmentInitializationStep,
)
from battery_analysis.main.initialization.steps.ui_setup_step import UISetupStep
from battery_analysis.main.initialization.steps.managers_initialization_step import (
    ManagersInitializationStep,
)
from battery_analysis.main.initialization.steps.processors_initialization_step import (
    ProcessorsInitializationStep,
)
from battery_analysis.main.initialization.steps.handlers_initialization_step import (
    HandlersInitializationStep,
)
from battery_analysis.main.initialization.steps.presenters_initialization_step import (
    PresentersInitializationStep,
)
from battery_analysis.main.initialization.steps.command_manager_initialization_step import (
    CommandManagerInitializationStep,
)
from battery_analysis.main.initialization.steps.language_initialization_step import (
    LanguageInitializationStep,
)
from battery_analysis.main.initialization.steps.styles_initialization_step import (
    StylesInitializationStep,
)
from battery_analysis.main.initialization.steps.battery_config_initialization_step import (
    BatteryConfigInitializationStep,
)

# ── 阶段名称 ──────────────────────────────────────────────
PHASE_ENV_PREP = "Environment Preparation"
PHASE_CORE_SVC = "Core Services"
PHASE_UI_BUILD = "UI Build"
PHASE_LAUNCH = "Startup Complete"


class InitializationManager:
    """
    初始化管理器
    将 12 个初始化步骤按职责划分为 4 个阶段，阶段内同优先级步骤可并行执行
    """

    def __init__(self, main_window):
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._orchestrator = InitializationOrchestrator()
        self._register_all_steps()

    def initialize(self):
        """执行完整的初始化流程"""
        self.logger.info("Starting modular initialization process")
        return self._orchestrator.execute_all(self.main_window)

    def _register_all_steps(self):
        """
        注册所有初始化步骤到 4 个阶段：
          1. 环境准备 — 基础环境（版本、容器、环境检测、样式）
          2. 核心服务 — 业务服务层（管理器、处理器、配置）
          3. UI 构建  — 界面层（控制器上下文、Presenter、命令、语言）
        """

        # ── 阶段 1: 环境准备 ──────────────────────────────
        # 所有步骤无依赖关系，理想并行
        self._orchestrator.register_steps(
            [
                BasicAttributesInitializationStep(),
                ServicesInitializationStep(),
                EnvironmentInitializationStep(),
                StylesInitializationStep(),
            ],
            phase=PHASE_ENV_PREP,
        )

        # ── 阶段 2: 核心服务 ──────────────────────────────
        # 按优先级依次初始化：管理器 → 处理器 → 业务管理器 → 电池配置
        self._orchestrator.register_steps(
            [
                ManagersInitializationStep(),
                ProcessorsInitializationStep(),
                HandlersInitializationStep(),
                BatteryConfigInitializationStep(),
            ],
            phase=PHASE_CORE_SVC,
        )

        # ── 阶段 3: UI 构建 ──────────────────────────────
        # 按优先级依次初始化：UI设置 → Presenter → 命令管理器 → 语言
        self._orchestrator.register_steps(
            [
                UISetupStep(),
                PresentersInitializationStep(),
                CommandManagerInitializationStep(),
                LanguageInitializationStep(),
            ],
            phase=PHASE_UI_BUILD,
        )

        total = self._orchestrator.get_total_steps()
        phases = len(self._orchestrator.get_phases())
        phase_names = " → ".join(self._orchestrator.get_phases().keys())
        self.logger.info(
            "Registered %d initialization steps across %d phases: %s", total, phases, phase_names
        )

    def get_executed_steps(self):
        return self._orchestrator.get_executed_steps()

    def get_total_steps(self):
        return self._orchestrator.get_total_steps()
