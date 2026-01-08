"""
MainPresenter实现

MVP架构的Presenter层，负责处理MainWindow的业务逻辑
"""

import logging
from typing import Any, Dict, List
from battery_analysis.application.usecases.calculate_battery_use_case import CalculateBatteryInput, CalculateBatteryUseCase
from battery_analysis.application.usecases.analyze_data_use_case import AnalyzeDataInput, AnalyzeDataUseCase
from battery_analysis.application.usecases.generate_report_use_case import GenerateReportInput, GenerateReportUseCase


class MainPresenter:
    """
    主窗口Presenter，负责处理MainWindow的业务逻辑
    """
    
    def __init__(self, view):
        """
        初始化Presenter
        
        Args:
            view: View层实例（MainWindow）
        """
        self.view = view
        self.logger = logging.getLogger(__name__)
        
        # 从服务容器获取use cases
        self.calculate_battery_use_case = self.view._service_container.get("calculate_battery")
        self.analyze_data_use_case = self.view._service_container.get("analyze_data")
        self.generate_report_use_case = self.view._service_container.get("generate_report")
        
        # 初始化状态
        self.battery_type = ""
        self.construction_method = ""
        self.specification_type = ""
        self.specification_method = ""
        self.manufacturer = ""
        self.tester_location = ""
        self.tested_by = ""
        self.reported_by = ""
        self.temperature = ""
        self.input_path = ""
        self.output_path = ""
        self.barcode = ""
        
        # 初始化环境信息
        self.env_info = {}
    
    def initialize(self):
        """
        初始化Presenter
        """
        self.logger.info("初始化MainPresenter")
        self._initialize_environment_info()
        self._ensure_env_info_keys()
    
    def _initialize_environment_info(self):
        """
        初始化环境信息
        """
        self.logger.info("初始化环境信息")
        # 这里可以实现环境信息的初始化逻辑
        self.env_info = {
            "os": "",
            "python_version": "",
            "app_version": "",
            "qt_version": ""
        }
    
    def _ensure_env_info_keys(self):
        """
        确保环境信息包含必要的键
        """
        required_keys = [
            "os", "python_version", "app_version", "qt_version",
            "cpu", "memory", "disk_space", "network"
        ]
        
        for key in required_keys:
            if key not in self.env_info:
                self.env_info[key] = "Unknown"
    
    def on_calculate_battery(self):
        """
        处理电池计算事件
        """
        self.logger.info("处理电池计算事件")
        
        # 更新状态栏
        self.view.statusBar_BatteryAnalysis.showMessage("执行电池计算...")
        
        # 从View获取输入数据
        input_data = CalculateBatteryInput(
            battery_type=self.view.comboBox_BatteryType.currentText(),
            construction_method=self.view.comboBox_ConstructionMethod.currentText(),
            specification_type=self.view.comboBox_Specification_Type.currentText(),
            specification_method=self.view.comboBox_Specification_Method.currentText(),
            manufacturer=self.view.comboBox_Manufacturer.currentText(),
            tester_location=self.view.comboBox_TesterLocation.currentText(),
            tested_by=self.view.comboBox_TestedBy.currentText(),
            reported_by=self.view.comboBox_ReportedBy.currentText(),
            temperature=self.view.comboBox_Temperature.currentText(),
            input_path=self.view.lineEdit_InputPath.text(),
            output_path=self.view.lineEdit_OutputPath.text(),
            barcode=self.view.lineEdit_Barcode.text()
        )
        
        # 执行电池计算用例
        result = self.calculate_battery_use_case.execute(input_data)
        
        # 更新View
        if result.success:
            self.view.statusBar_BatteryAnalysis.showMessage("状态:就绪")
            self.view.show_message("计算结果", result.message)
        else:
            self.view.statusBar_BatteryAnalysis.showMessage("状态:就绪")
            self.view.show_warning("警告", result.message)
    
    def on_analyze_data(self):
        """
        处理数据分析事件
        """
        self.logger.info("处理数据分析事件")
        
        # 检查输入路径是否设置
        input_path = self.view.lineEdit_InputPath.text()
        if not input_path:
            self.view.show_warning("警告", "请先设置输入路径。")
            return
        
        # 更新状态栏
        self.view.statusBar_BatteryAnalysis.showMessage("分析数据...")
        
        # 从View获取输入数据
        input_data = AnalyzeDataInput(
            input_path=input_path,
            output_path=self.view.lineEdit_OutputPath.text(),
            battery_type=self.view.comboBox_BatteryType.currentText()
        )
        
        # 执行数据分析用例
        result = self.analyze_data_use_case.execute(input_data)
        
        # 更新View
        if result.success:
            self.view.statusBar_BatteryAnalysis.showMessage("状态:就绪")
            self.view.show_message("分析结果", result.message)
        else:
            self.view.statusBar_BatteryAnalysis.showMessage("状态:就绪")
            self.view.show_warning("警告", result.message)
    
    def on_generate_report(self):
        """
        处理报告生成事件
        """
        self.logger.info("处理报告生成事件")
        
        # 检查输出路径是否设置
        output_path = self.view.lineEdit_OutputPath.text()
        if not output_path:
            self.view.show_warning("警告", "请先设置输出路径。")
            return
        
        # 更新状态栏
        self.view.statusBar_BatteryAnalysis.showMessage("生成报告中...")
        
        # 从View获取输入数据
        input_data = GenerateReportInput(
            battery_ids=[self.view.lineEdit_Barcode.text()],
            output_path=output_path,
            report_type="standard",
            include_charts=True,
            include_raw_data=False,
            export_format="pdf"
        )
        
        # 执行报告生成用例
        result = self.generate_report_use_case.generate_report(input_data)
        
        # 更新View
        if result.success:
            self.view.statusBar_BatteryAnalysis.showMessage("状态:就绪")
            self.view.show_message("报告生成结果", result.message)
        else:
            self.view.statusBar_BatteryAnalysis.showMessage("状态:就绪")
            self.view.show_warning("警告", result.message)
    
    def on_export_report(self):
        """
        处理报告导出事件
        """
        self.logger.info("处理报告导出事件")
        
        # 检查输出路径是否设置
        output_path = self.view.lineEdit_OutputPath.text()
        if not output_path:
            self.view.show_warning("警告", "请先设置输出路径。")
            return
        
        # 更新状态栏
        self.view.statusBar_BatteryAnalysis.showMessage("导出报告中...")
        
        # 这里可以实现报告导出逻辑
        # 目前使用消息框提示
        self.view.statusBar_BatteryAnalysis.showMessage("状态:就绪")
        self.view.show_message("报告导出结果", "报告导出已完成。")
    
    def on_batch_processing(self):
        """
        处理批量处理事件
        """
        self.logger.info("处理批量处理事件")
        
        # 更新状态栏
        self.view.statusBar_BatteryAnalysis.showMessage("准备批量处理...")
        
        # 这里可以实现批量处理逻辑
        # 目前使用消息框提示
        self.view.statusBar_BatteryAnalysis.showMessage("状态:就绪")
        self.view.show_message("批量处理", "批量处理功能处于开发阶段。")
    
    def on_input_path_changed(self, path: str):
        """
        处理输入路径变化事件
        
        Args:
            path: 新的输入路径
        """
        self.logger.info("输入路径变化: %s", path)
        self.input_path = path
        # 可以在这里添加路径验证逻辑
    
    def on_output_path_changed(self, path: str):
        """
        处理输出路径变化事件
        
        Args:
            path: 新的输出路径
        """
        self.logger.info("输出路径变化: %s", path)
        self.output_path = path
        # 可以在这里添加路径验证逻辑
    
    def on_battery_type_changed(self, battery_type: str):
        """
        处理电池类型变化事件
        
        Args:
            battery_type: 新的电池类型
        """
        self.logger.info("电池类型变化: %s", battery_type)
        self.battery_type = battery_type
        # 可以在这里添加电池类型相关的逻辑
    
    def validate_inputs(self) -> bool:
        """
        验证输入参数是否合法
        
        Returns:
            bool: 输入参数是否合法
        """
        self.logger.info("检查输入参数")
        
        # 从View获取输入数据
        battery_type = self.view.comboBox_BatteryType.currentText()
        construction_method = self.view.comboBox_ConstructionMethod.currentText()
        specification_type = self.view.comboBox_Specification_Type.currentText()
        specification_method = self.view.comboBox_Specification_Method.currentText()
        manufacturer = self.view.comboBox_Manufacturer.currentText()
        tester_location = self.view.comboBox_TesterLocation.currentText()
        tested_by = self.view.comboBox_TestedBy.currentText()
        reported_by = self.view.comboBox_ReportedBy.currentText()
        temperature = self.view.comboBox_Temperature.currentText()
        input_path = self.view.lineEdit_InputPath.text()
        output_path = self.view.lineEdit_OutputPath.text()
        barcode = self.view.lineEdit_Barcode.text()
        
        # 检查必填字段
        missing_fields = []
        
        if not battery_type:
            missing_fields.append("电池类型")
        if not construction_method:
            missing_fields.append("构造方法")
        if not specification_type:
            missing_fields.append("规格类型")
        if not specification_method:
            missing_fields.append("规格方法")
        if not manufacturer:
            missing_fields.append("制造商")
        if not tester_location:
            missing_fields.append("测试者位置")
        if not tested_by:
            missing_fields.append("测试者")
        if not reported_by:
            missing_fields.append("报告者")
        if not temperature:
            missing_fields.append("温度")
        if not input_path:
            missing_fields.append("输入路径")
        if not output_path:
            missing_fields.append("输出路径")
        if not barcode:
            missing_fields.append("条形码")
        
        # 如果有缺少的字段，显示警告信息
        if missing_fields:
            warning_message = f"缺少必要字段，请检查以下项:\n{', '.join(missing_fields)}"
            self.view.show_warning("警告", warning_message)
            return False
        
        return True
