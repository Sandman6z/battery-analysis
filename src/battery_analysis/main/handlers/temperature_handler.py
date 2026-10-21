"""温度 UI：类型仅由 NDAX 内嵌配方决定。"""

from enum import Enum


class TemperatureType(Enum):
    ROOM = "Room Temperature"
    FREEZER = "Freezer Temperature"


class TemperatureHandler:
    def __init__(self, main_window=None):
        self.main_window = main_window

    def get_temperature_value(self) -> str:
        temperature_type = self.main_window.comboBox_Temperature.currentText()
        if temperature_type == TemperatureType.FREEZER.value:
            return f"{temperature_type}:{self.main_window.spinBox_Temperature.value()}"
        return temperature_type

    def clear_temperature_ui(self):
        self.main_window.comboBox_Temperature.setCurrentIndex(-1)
        self.main_window.comboBox_Temperature.setEnabled(False)
        self.main_window.spinBox_Temperature.setValue(0)
        self.main_window.spinBox_Temperature.setEnabled(False)

    def update_temperature_ui(self, temperature_type: TemperatureType):
        previous = self.main_window.comboBox_Temperature.currentText()
        self.main_window.comboBox_Temperature.setCurrentText(temperature_type.value)
        self.main_window.comboBox_Temperature.setEnabled(False)
        is_freezer = temperature_type == TemperatureType.FREEZER
        self.main_window.spinBox_Temperature.setEnabled(is_freezer)
        if is_freezer:
            # 配方名不提供实测温度；-20 仅为可编辑的标称默认值。
            if previous != temperature_type.value:
                self.main_window.spinBox_Temperature.setValue(-20)
        else:
            self.main_window.spinBox_Temperature.setValue(0)
        # 扫描和 Run 前复核都从这里更新温度，同时刷新容量，避免沿用常温规则。
        self.main_window.check_construction()

    def on_temperature_type_changed(self):
        self.main_window.spinBox_Temperature.setEnabled(
            self.main_window.comboBox_Temperature.currentText() == TemperatureType.FREEZER.value
        )
