"""电池类型与规格验证规则（从 validation_manager.py 拆出）

check_batterytype / check_specification 及其辅助查询。"""

import re


class ValidationSpecRulesMixin:
    """电池类型、规格（Specification）、施工方式相关验证"""

    def check_batterytype(self) -> None:
        """
        检查电池类型并更新相关UI组件
        """
        self.main_window.checker_battery_type.clear()
        current_type = self.main_window.comboBox_BatteryType.currentText()

        if not current_type:
            # 未选择电池类型 → 禁用相关控件
            self.main_window.comboBox_ConstructionMethod.setEnabled(False)
            self.main_window.comboBox_ConstructionMethod.setCurrentIndex(-1)
            self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
            self.main_window.lineEdit_CalculationNominalCapacity.setText("")
            self.main_window.lineEdit_RequiredUseableCapacity.setText("")
            try:
                self.main_window.comboBox_Specification_Type.currentIndexChanged.disconnect(
                    self.main_window.check_specification
                )
                self.main_window.comboBox_Specification_Method.currentIndexChanged.disconnect(
                    self.main_window.check_specification
                )
            except (TypeError, AttributeError):
                pass
            self.main_window.comboBox_Specification_Type.clear()
            self.main_window.comboBox_Specification_Type.setEnabled(False)
            self.main_window.comboBox_Specification_Method.setEnabled(False)
            self.main_window.comboBox_Specification_Type.setCurrentIndex(-1)
            self.main_window.comboBox_Specification_Method.setCurrentIndex(-1)
            self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
                self.main_window.check_specification
            )
            self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
                self.main_window.check_specification
            )
            return

        # 构造方法：仅需要的电池类型（如 Pouch Cell）启用，其他类型禁用并清空
        requires_construction = current_type in self._get_types_requiring_construction()
        self.main_window.comboBox_ConstructionMethod.setEnabled(requires_construction)
        self.main_window.comboBox_ConstructionMethod.setCurrentIndex(-1)
        # 将文件名解析到的构造方法设置到下拉框（仅需要的类型）
        if requires_construction and self.main_window.construction_method:
            for c in range(self.main_window.comboBox_ConstructionMethod.count()):
                if (
                    self.main_window.construction_method
                    == self.main_window.comboBox_ConstructionMethod.itemText(c)
                ):
                    self.main_window.comboBox_ConstructionMethod.setCurrentIndex(c)
                    self.main_window.construction_method = ""
                    break
        self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
        self.main_window.lineEdit_CalculationNominalCapacity.setText("")
        self.main_window.lineEdit_RequiredUseableCapacity.setText("")
        try:
            self.main_window.comboBox_Specification_Type.currentIndexChanged.disconnect(
                self.main_window.check_specification
            )
            self.main_window.comboBox_Specification_Method.currentIndexChanged.disconnect(
                self.main_window.check_specification
            )
        except (TypeError, AttributeError):
            pass
        self.main_window.comboBox_Specification_Type.clear()
        self.main_window.comboBox_Specification_Type.addItems(self._get_all_specifications())
        self.main_window.comboBox_Specification_Type.setEnabled(True)
        self.main_window.comboBox_Specification_Method.setEnabled(True)
        self.main_window.comboBox_Specification_Type.setCurrentIndex(-1)
        # 先恢复选中项（信号仍断开，不会触发 check_specification）
        for t in range(self.main_window.comboBox_Specification_Type.count()):
            if (
                self.main_window.specification_type
                == self.main_window.comboBox_Specification_Type.itemText(t)
            ):
                self.main_window.comboBox_Specification_Type.setCurrentIndex(t)
                break
        # 再重连信号
        self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
            self.main_window.check_specification
        )
        self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
            self.main_window.check_specification
        )

    def _get_all_specifications(self) -> list:
        """从配置中获取所有规格型号（不分电池类型）"""
        coin = (
            self.main_window.config_manager.get_config("BatteryConfig/SpecificationTypeCoinCell")
            or []
        )
        pouch = (
            self.main_window.config_manager.get_config("BatteryConfig/SpecificationTypePouchCell")
            or []
        )
        return coin + pouch

    def check_specification(self) -> None:
        """
        检查规格并更新相关UI组件
        """
        self.main_window.specification_type = (
            self.main_window.comboBox_Specification_Type.currentText()
        )
        # 规格 → 电池类型映射表（配置驱动，不硬编码索引）
        type_spec_pairs = [
            (
                "Coin Cell",
                self.main_window.config_manager.get_config(
                    "BatteryConfig/SpecificationTypeCoinCell"
                )
                or [],
            ),
            (
                "Pouch Cell",
                self.main_window.config_manager.get_config(
                    "BatteryConfig/SpecificationTypePouchCell"
                )
                or [],
            ),
        ]

        # 临时断开 BatteryType 信号，避免递归触发 check_batterytype
        try:
            self.main_window.comboBox_BatteryType.currentIndexChanged.disconnect(
                self.main_window.check_batterytype
            )
        except (TypeError, AttributeError):
            pass

        # 根据当前选中的规格自动匹配电池类型（按文本值，非索引）
        for type_name, spec_list in type_spec_pairs:
            if self.main_window.specification_type in spec_list:
                for i in range(self.main_window.comboBox_BatteryType.count()):
                    if self.main_window.comboBox_BatteryType.itemText(i) == type_name:
                        self.main_window.comboBox_BatteryType.setCurrentIndex(i)
                        break
                break

        self.main_window.comboBox_BatteryType.currentIndexChanged.connect(
            self.main_window.check_batterytype
        )

        # 显式执行 check_batterytype 以确保 UI 状态更新
        # （setCurrentIndex 在信号断开期间执行，不会自动触发回调）
        self.main_window.check_batterytype()

        specification_method = self.main_window.comboBox_Specification_Method.currentText()
        if not self.main_window.specification_type or not specification_method:
            return

        rules = self.main_window.config_manager.get_config("BatteryConfig/Rules")
        for rule in rules:
            rule_parts = rule.split("/")
            if rule_parts[0] == self.main_window.specification_type:
                if specification_method == rule_parts[1]:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText(f"{rule_parts[2]}")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText(f"{rule_parts[3]}")
                    listRequiredUseableCapacityPercentage = re.findall(r"(\d+)%", rule_parts[4])
                    if (
                        listRequiredUseableCapacityPercentage != []
                        and len(listRequiredUseableCapacityPercentage) == 1
                    ):
                        nominal_capacity = int(rule_parts[3])
                        percentage = int(listRequiredUseableCapacityPercentage[0])
                        required_capacity = int(nominal_capacity * percentage / 100)
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{required_capacity}"
                        )
                    else:
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{rule_parts[4]}"
                        )
                else:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText("")
                    self.main_window.lineEdit_RequiredUseableCapacity.setText("")
                break
            elif rule_parts[0] in self.main_window.specification_type:
                if specification_method == rule_parts[1]:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText(f"{rule_parts[2]}")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText(f"{rule_parts[3]}")
                    listRequiredUseableCapacityPercentage = re.findall(r"(\d+)%", rule_parts[4])
                    if (
                        listRequiredUseableCapacityPercentage != []
                        and len(listRequiredUseableCapacityPercentage) == 1
                    ):
                        nominal_capacity = int(rule_parts[3])
                        percentage = int(listRequiredUseableCapacityPercentage[0])
                        required_capacity = int(nominal_capacity * percentage / 100)
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{required_capacity}"
                        )
                    else:
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{rule_parts[4]}"
                        )
                else:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText("")
                    self.main_window.lineEdit_RequiredUseableCapacity.setText("")
            else:
                pass

        # 根据 required useable capacity 自动判定温度类型
        # 但如果温度已从XML文件名设置，则跳过容量检测，避免覆盖
        if not self._temperature_set_from_xml:
            capacity_text = self.main_window.lineEdit_RequiredUseableCapacity.text()
            if capacity_text:
                try:
                    capacity_value = int(capacity_text)
                    self.main_window.temperature_handler.set_temperature_by_capacity(capacity_value)
                except ValueError:
                    pass

    def _get_types_requiring_construction(self) -> list:
        """返回需要填写构造方法的电池类型名称列表。

        业务约定：仅 Pouch Cell（软包电池）需要填写构造方法；
        Coin Cell（纽扣电池）不需要，且下拉框禁用。
        """
        return ["Pouch Cell"]
