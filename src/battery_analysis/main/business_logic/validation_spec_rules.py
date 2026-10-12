"""电池类型与规格验证规则（从 validation_manager.py 拆出）

check_batterytype / check_specification 及其辅助查询。"""

from battery_analysis.utils.pulse_currents import required_useable_capacity_from_rule


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

        # 按规则匹配填充容量字段（含 85%|75% 构造相关换算）
        self._apply_specification_rules()

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

    def _clear_spec_rule_fields(self) -> None:
        """清空「标称 / 计算 / 要求可用容量」三个字段"""
        self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
        self.main_window.lineEdit_CalculationNominalCapacity.setText("")
        self.main_window.lineEdit_RequiredUseableCapacity.setText("")

    def _fill_spec_rule_fields(self, rule_parts: list) -> None:
        """按规则第 3–5 段填充容量字段

        第 5 段（要求可用容量）支持绝对值（"380"）、单百分比（"80%"）与
        构造相关双百分比（"85%|75%" = 螺旋/叠片，按当前构造方法选取，
        对齐 BatteryQualityRequirements_v2.3 §7.1.1.3–.10）。
        """
        self.main_window.lineEdit_DatasheetNominalCapacity.setText(f"{rule_parts[2]}")
        self.main_window.lineEdit_CalculationNominalCapacity.setText(f"{rule_parts[3]}")
        required = required_useable_capacity_from_rule(
            "/".join(rule_parts),
            self.main_window.comboBox_ConstructionMethod.currentText(),
        )
        if required is not None:
            self.main_window.lineEdit_RequiredUseableCapacity.setText(f"{required}")
        else:
            self.main_window.lineEdit_RequiredUseableCapacity.setText(f"{rule_parts[4]}")

    def _apply_specification_rules(self) -> None:
        """按当前规格/成组方式匹配规则并填充容量字段

        仅做规则匹配与字段填充：不改电池类型/规格下拉框、不联动温度，
        供 check_specification 与 check_construction 共用。
        """
        spec = self.main_window.comboBox_Specification_Type.currentText()
        method = self.main_window.comboBox_Specification_Method.currentText()
        if not spec or not method:
            return
        rules = self.main_window.config_manager.get_config("BatteryConfig/Rules") or []
        for rule in rules:
            rule_parts = str(rule).split("/")
            if len(rule_parts) < 5:
                continue
            if rule_parts[0] == spec:
                if method == rule_parts[1]:
                    self._fill_spec_rule_fields(rule_parts)
                else:
                    self._clear_spec_rule_fields()
                break
            elif rule_parts[0] in spec:
                if method == rule_parts[1]:
                    self._fill_spec_rule_fields(rule_parts)
                else:
                    self._clear_spec_rule_fields()
            else:
                pass

    def check_construction(self) -> None:
        """构造方法变化 → 重算「要求可用容量」

        Pouch Cell 规则第 5 段为双百分比（螺旋 85% / 叠片 75%，
        §7.1.1.3–.10），构造方法改变时按新构造重新换算。
        不触碰电池类型/规格下拉框与温度设置，避免递归回调。
        """
        self._apply_specification_rules()

    def _get_types_requiring_construction(self) -> list:
        """返回需要填写构造方法的电池类型名称列表。

        业务约定：仅 Pouch Cell（软包电池）需要填写构造方法；
        Coin Cell（纽扣电池）不需要，且下拉框禁用。
        """
        return ["Pouch Cell"]
