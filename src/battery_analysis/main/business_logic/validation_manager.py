"""
验证管理模块

这个模块负责处理所有输入验证逻辑，包括：
- 版本号格式验证
- 输入路径验证
- 必填字段验证
- 电池类型验证
- 规格验证
"""

import logging
import PyQt6.QtCore as QC
import PyQt6.QtWidgets as QW
from battery_analysis.i18n.language_manager import _


class ValidationManager:
    """
    验证管理器，负责处理所有输入验证逻辑
    """
    
    def __init__(self, main_window):
        """
        初始化验证管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def validate_version(self) -> None:
        """
        验证版本号格式并提供实时反馈
        """
        version_text = self.main_window.lineEdit_Version.text()
        regex = QC.QRegularExpression(r"^\d+(\.\d+){0,2}$")
        if version_text and not regex.match(version_text).hasMatch():
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                f"{_('warning', '警告')}: {_('version_format_invalid', '版本号格式不正确，应为 x.y.z 格式')}")
            # 设置错误样式
            self.main_window.lineEdit_Version.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            # 重置样式
            self.main_window.lineEdit_Version.setStyleSheet("")
            # 如果所有验证都通过，显示正常状态
            if self.main_window.checker_battery_type.b_check_pass:
                self.main_window.statusBar_BatteryAnalysis.showMessage("status:ok")
    
    def validate_input_path(self) -> None:
        """
        验证输入路径是否存在
        """
        import os
        path = self.main_window.lineEdit_InputPath.text()
        if path and not os.path.exists(path):
            self.main_window.statusBar_BatteryAnalysis.showMessage(f"{_('warning', '警告')}: {_('input_path_not_exists', '输入路径不存在')}")
            self.main_window.lineEdit_InputPath.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            self.main_window.lineEdit_InputPath.setStyleSheet("")
            # 如果所有验证都通过，显示正常状态
            if self.main_window.checker_battery_type.b_check_pass:
                self.main_window.statusBar_BatteryAnalysis.showMessage("status:ok")
    
    def validate_required_fields(self) -> None:
        """
        验证必填字段是否为空
        """
        empty_fields = []

        if not self.main_window.lineEdit_SamplesQty.text():
            empty_fields.append("样品数量")
            self.main_window.lineEdit_SamplesQty.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            self.main_window.lineEdit_SamplesQty.setStyleSheet("")

        if not self.main_window.lineEdit_DatasheetNominalCapacity.text():
            empty_fields.append("标称容量")
            self.main_window.lineEdit_DatasheetNominalCapacity.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            self.main_window.lineEdit_DatasheetNominalCapacity.setStyleSheet("")

        if not self.main_window.lineEdit_CalculationNominalCapacity.text():
            empty_fields.append("计算容量")
            self.main_window.lineEdit_CalculationNominalCapacity.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            self.main_window.lineEdit_CalculationNominalCapacity.setStyleSheet("")

        if not self.main_window.lineEdit_RequiredUseableCapacity.text():
            empty_fields.append("可用容量")
            self.main_window.lineEdit_RequiredUseableCapacity.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;")
        else:
            self.main_window.lineEdit_RequiredUseableCapacity.setStyleSheet("")

        if empty_fields:
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                f"{_('warning', '警告')}: {_('required_fields_empty', '以下必填字段为空')}: {', '.join(empty_fields)}")
        else:
            # 如果所有验证都通过，显示正常状态
            if self.main_window.checker_battery_type.b_check_pass:
                self.main_window.statusBar_BatteryAnalysis.showMessage("status:ok")
    
    def check_batterytype(self) -> None:
        """
        检查电池类型并更新相关UI组件
        """
        self.main_window.checker_battery_type.clear()
        if self.main_window.comboBox_BatteryType.currentText() == "Coin Cell":
            self.main_window.comboBox_ConstructionMethod.setEnabled(False)
            self.main_window.comboBox_ConstructionMethod.setCurrentIndex(-1)
            self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
            self.main_window.lineEdit_CalculationNominalCapacity.setText("")
            self.main_window.lineEdit_RequiredUseableCapacity.setText("")
            self.main_window.comboBox_Specification_Type.currentIndexChanged.disconnect(
                self.main_window.check_specification)
            self.main_window.comboBox_Specification_Method.currentIndexChanged.disconnect(
                self.main_window.check_specification)
            self.main_window.comboBox_Specification_Type.clear()
            self.main_window.comboBox_Specification_Type.addItems(
                self.main_window.get_config("BatteryConfig/SpecificationTypeCoinCell"))
            self.main_window.comboBox_Specification_Type.setCurrentIndex(-1)
            self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
                self.main_window.check_specification)
            self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
                self.main_window.check_specification)
            for t in range(self.main_window.comboBox_Specification_Type.count()):
                if self.main_window.specification_type == self.main_window.comboBox_Specification_Type.itemText(t):
                    self.main_window.comboBox_Specification_Type.setCurrentIndex(t)
                    break
        elif self.main_window.comboBox_BatteryType.currentText() == "Pouch Cell":
            self.main_window.comboBox_ConstructionMethod.setEnabled(True)
            for c in range(self.main_window.comboBox_ConstructionMethod.count()):
                if self.main_window.construction_method == self.main_window.comboBox_ConstructionMethod.itemText(c):
                    self.main_window.comboBox_ConstructionMethod.setCurrentIndex(c)
                    self.main_window.construction_method = ""
                    break
            self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
            self.main_window.lineEdit_CalculationNominalCapacity.setText("")
            self.main_window.lineEdit_RequiredUseableCapacity.setText("")
            self.main_window.comboBox_Specification_Type.currentIndexChanged.disconnect(
                self.main_window.check_specification)
            self.main_window.comboBox_Specification_Method.currentIndexChanged.disconnect(
                self.main_window.check_specification)
            self.main_window.comboBox_Specification_Type.clear()
            self.main_window.comboBox_Specification_Type.addItems(
                self.main_window.get_config("BatteryConfig/SpecificationTypePouchCell"))
            self.main_window.comboBox_Specification_Type.setCurrentIndex(-1)
            self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
                self.main_window.check_specification)
            self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
                self.main_window.check_specification)
            for t in range(self.main_window.comboBox_Specification_Type.count()):
                if self.main_window.specification_type == self.main_window.comboBox_Specification_Type.itemText(t):
                    self.main_window.comboBox_Specification_Type.setCurrentIndex(t)
                    break
        elif not self.main_window.comboBox_BatteryType.currentText():
            pass
        else:
            self.main_window.checker_battery_type.set_error(
                f"No battery type named {self.main_window.comboBox_BatteryType.currentText()}")
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                f"[Error]: No battery type named {self.main_window.comboBox_BatteryType.currentText()}")
    
    def check_specification(self) -> None:
        """
        检查规格并更新相关UI组件
        """
        self.main_window.specification_type = self.main_window.comboBox_Specification_Type.currentText()
        coin_cell_types = self.main_window.get_config(
            "BatteryConfig/SpecificationTypeCoinCell")
        pouch_cell_types = self.main_window.get_config(
            "BatteryConfig/SpecificationTypePouchCell")

        for coin_type in coin_cell_types:
            if self.main_window.specification_type == coin_type:
                self.main_window.comboBox_BatteryType.setCurrentIndex(0)

        for pouch_type in pouch_cell_types:
            if self.main_window.specification_type == pouch_type:
                self.main_window.comboBox_BatteryType.setCurrentIndex(1)

        specification_method = self.main_window.comboBox_Specification_Method.currentText()
        if not self.main_window.specification_type or not specification_method:
            return

        rules = self.main_window.get_config("BatteryConfig/Rules")
        for rule in rules:
            rule_parts = rule.split("/")
            if rule_parts[0] == self.main_window.specification_type:
                if specification_method == rule_parts[1]:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText(
                        f"{rule_parts[2]}")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText(
                        f"{rule_parts[3]}")
                    import re
                    listRequiredUseableCapacityPercentage = re.findall(
                        r"(\d+)%", rule_parts[4])
                    if (listRequiredUseableCapacityPercentage != []
                            and len(listRequiredUseableCapacityPercentage) == 1):
                        nominal_capacity = int(rule_parts[3])
                        percentage = int(
                            listRequiredUseableCapacityPercentage[0])
                        required_capacity = int(
                            nominal_capacity * percentage / 100)
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{required_capacity}")
                    else:
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{rule_parts[4]}")
                else:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText("")
                    self.main_window.lineEdit_RequiredUseableCapacity.setText("")
                break
            elif rule_parts[0] in self.main_window.specification_type:
                if specification_method == rule_parts[1]:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText(
                        f"{rule_parts[2]}")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText(
                        f"{rule_parts[3]}")
                    import re
                    listRequiredUseableCapacityPercentage = re.findall(
                        r"(\d+)%", rule_parts[4])
                    if (listRequiredUseableCapacityPercentage != []
                            and len(listRequiredUseableCapacityPercentage) == 1):
                        nominal_capacity = int(rule_parts[3])
                        percentage = int(
                            listRequiredUseableCapacityPercentage[0])
                        required_capacity = int(
                            nominal_capacity * percentage / 100)
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{required_capacity}")
                    else:
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{rule_parts[4]}")
                else:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText("")
                    self.main_window.lineEdit_RequiredUseableCapacity.setText("")
            else:
                pass
    
    def checkinput(self) -> bool:
        """
        检查所有输入是否完整有效
        
        Returns:
            bool: 输入是否通过验证
        """
        check_pass_flag = True
        warning_info = ["Unknown: "]
        if not self.main_window.comboBox_BatteryType.currentText():
            check_pass_flag = False
            warning_info.append("Battery Type")
            self.main_window.label_BatteryType.setStyleSheet("background-color:red")
        if self.main_window.comboBox_BatteryType.currentText() == "Pouch Cell":
            if not self.main_window.comboBox_ConstructionMethod.currentText():
                check_pass_flag = False
                warning_info.append("Construction Method")
                self.main_window.label_ConstructionMethod.setStyleSheet(
                    "background-color:red")
        if (not self.main_window.comboBox_Specification_Type.currentText()
                or not self.main_window.comboBox_Specification_Method.currentText()):
            check_pass_flag = False
            warning_info.append("Specification")
            self.main_window.label_Specification.setStyleSheet("background-color:red")
        if not self.main_window.comboBox_Manufacturer.currentText():
            check_pass_flag = False
            warning_info.append("Manufacturer")
            self.main_window.label_Manufacturer.setStyleSheet("background-color:red")
        if not self.main_window.lineEdit_BatchDateCode.text():
            check_pass_flag = False
            warning_info.append("Batch/Date Code")
            self.main_window.label_BatchDateCode.setStyleSheet("background-color:red")
        if not self.main_window.lineEdit_SamplesQty.text():
            check_pass_flag = False
            warning_info.append("SamplesQty")
            self.main_window.label_SamplesQty.setStyleSheet("background-color:red")
        if not self.main_window.comboBox_Temperature.currentText():
            check_pass_flag = False
            warning_info.append("Temperature")
            self.main_window.label_Temperature.setStyleSheet("background-color:red")
        if not self.main_window.lineEdit_DatasheetNominalCapacity.text():
            check_pass_flag = False
            warning_info.append("Datasheet Nominal Capacity")
            self.main_window.label_DatasheetNominalCapacity.setStyleSheet(
                "background-color:red")
        if not self.main_window.lineEdit_CalculationNominalCapacity.text():
            check_pass_flag = False
            warning_info.append("Calculation Nominal Capacity")
            self.main_window.label_CalculationNominalCapacity.setStyleSheet(
                "background-color:red")
        # QSpinBox总是有一个值（0-10），所以不需要检查是否为空
        # 但我们仍然可以检查值是否在有效范围内（虽然控件已经限制了）
        aging_value = self.main_window.spinBox_AcceleratedAging.value()
        if aging_value < 0 or aging_value > 10:
            check_pass_flag = False
            warning_info.append("Accelerated Aging")
            self.main_window.label_AcceleratedAging.setStyleSheet("background-color:red")
        if not self.main_window.lineEdit_RequiredUseableCapacity.text():
            check_pass_flag = False
            warning_info.append("Required Useable Capacity")
            self.main_window.label_RequiredUseableCapacity.setStyleSheet(
                "background-color:red")
        if not self.main_window.comboBox_TesterLocation.currentText():
            check_pass_flag = False
            warning_info.append("Test Location")
            self.main_window.label_TesterLocation.setStyleSheet("background-color:red")
        if not self.main_window.comboBox_TestedBy.currentText():
            check_pass_flag = False
            warning_info.append("Test By")
            self.main_window.label_TestedBy.setStyleSheet("background-color:red")
        if not self.main_window.comboBox_ReportedBy.currentText():
            check_pass_flag = False
            warning_info.append("Reported By")
            # 注意：Reported By没有对应的label，所以不需要设置样式
        if not self.main_window.lineEdit_TestProfile.text():
            check_pass_flag = False
            warning_info.append("Test Profile")
            self.main_window.label_TestProfile.setStyleSheet("background-color:red")
        if not self.main_window.lineEdit_InputPath.text():
            check_pass_flag = False
            warning_info.append("Input Path")
            self.main_window.label_InputPath.setStyleSheet("background-color:red")
        if not self.main_window.lineEdit_OutputPath.text():
            check_pass_flag = False
            warning_info.append("Output Path")
            self.main_window.label_OutputPath.setStyleSheet("background-color:red")
        if not self.main_window.lineEdit_Version.text():
            check_pass_flag = False
            warning_info.append("Version")
            self.main_window.label_Version.setStyleSheet("background-color:red")
        
        if check_pass_flag:
            self.main_window.pushButton_Run.setEnabled(False)
            self.main_window.pushButton_Run.setFocus()
        else:
            warning_info_str = warning_info[0]
            for i in range(1, len(warning_info) - 1):
                warning_info_str = warning_info_str + warning_info[i] + ", "
            warning_info_str += warning_info[-1]
            self.main_window.statusBar_BatteryAnalysis.showMessage(warning_info_str)
            self.main_window.pushButton_Run.setText("Rerun")
            self.main_window.pushButton_Run.setFocus()
        return check_pass_flag
