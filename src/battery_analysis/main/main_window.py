# 标准库导入
import os
import re
import csv
import sys
import time
import hashlib
import threading
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 添加项目根目录到Python路径
script_dir = Path(__file__).absolute().parent
project_root = script_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

# 第三方库导入
import PyQt6.QtGui as QG
import PyQt6.QtCore as QC
import PyQt6.QtWidgets as QW
import win32api
import win32con

# 本地模块导入
from battery_analysis.ui import ui_main_window
from battery_analysis.utils import version
from battery_analysis.utils import file_writer
from battery_analysis.utils import battery_analysis


def calc_md5checksum(file_paths):
    md5_hash = hashlib.md5()
    for file_path in file_paths:
        with open(file_path, "rb") as file:
            data = file.read()
            md5_hash.update(data)
    return md5_hash.hexdigest()


class Checker:
    def __init__(self) -> None:
        self.b_check_pass = True
        self.str_error_msg = ""

    def clear(self):
        self.b_check_pass = True
        self.str_error_msg = ""

    def set_error(self, error_msg: str):
        self.b_check_pass = False
        self.str_error_msg = error_msg


class Main(QW.QMainWindow, ui_main_window.Ui_MainWindow, version.Version):
    sigSetVersion = QC.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        version.Version.__init__(self)
        
        self.thread = None
        self.b_has_config = True
        self.checker_battery_type = Checker()
        self.checker_table = Checker()
        self.checker_input_xlsx = Checker()
        self.checker_update_config = Checker()
        self.construction_method = ""
        self.test_information = ""
        self.specification_type = ""
        self.cc_current = ""
        self.md5_checksum = ""
        self.md5_checksum_run = ""
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("bt")

        # 改进的配置文件路径查找逻辑
        # 首先确定基础目录
        if getattr(sys, 'frozen', False):
            # 在exe环境中，使用exe所在目录
            base_dir = Path(sys.executable).parent
        else:
            # 在开发环境中，使用脚本目录推导项目根目录
            script_dir = Path(__file__).absolute().parent
            base_dir = script_dir.parent.parent.parent
        
        # 定义可能的配置文件路径列表
        possible_config_paths = [
            # 1. 首先检查当前工作目录下的config文件夹
            Path.cwd() / "config" / "setting.ini",
            # 2. 检查基础目录下的config文件夹
            base_dir / "config" / "setting.ini",
            # 3. 检查当前工作目录下的setting.ini
            Path.cwd() / "setting.ini",
            # 4. 检查基础目录下的setting.ini
            base_dir / "setting.ini"
        ]
        
        # 遍历所有可能的路径，找到第一个存在的配置文件
        self.config_path = None
        for path in possible_config_paths:
            if path.exists():
                self.config_path = str(path)
                break
        
        project_root = base_dir
        
        # 添加对None值的检查，避免TypeError
        if self.config_path is None or not Path(self.config_path).exists():
            self.b_has_config = False
            # 创建默认配置设置
            self.config = QC.QSettings()
        else:
            self.b_has_config = True
            self.config = QC.QSettings(
                self.config_path, 
                QC.QSettings.Format.IniFormat
            )
        
        self.current_directory = str(project_root)
        self.path = str(project_root)  # 添加缺失的path属性，用于线程参数

        self.setupUi(self)

        self.init_window()
        self.init_widget()

        listPulseCurrent = self.get_config("BatteryConfig/PulseCurrent")
        listCutoffVoltage = self.get_config("BatteryConfig/CutoffVoltage")
        self.listCurrentLevel = [int(listPulseCurrent[c].strip()) for c in range(len(listPulseCurrent))]
        self.listVoltageLevel = [float(listCutoffVoltage[c].strip()) for c in range(len(listCutoffVoltage))]

    def get_config(self, config_key):
        # 获取配置值并处理为列表格式，移除所有DEBUG打印以避免UI卡死
        # 如果没有配置文件，直接返回空列表
        if not self.b_has_config:
            return []
        
        try:
            value = self.config.value(config_key)
            if isinstance(value, list):
                list_value = []
                for item in value:
                    if item != "":
                        list_value.append(item)
            elif isinstance(value, str):
                list_value = [value]
            else:
                list_value = []
            return list_value
        except Exception as e:
            logging.error(f"读取配置 {config_key} 失败: {e}")
            return []

    def init_window(self) -> None:
        # 在窗口标题中显示应用程序名称和版本号
        self.setWindowTitle(f"battery-analyzer v{self.version}")
        # 使用配置目录下的图标文件
        try:
            # 使用实际存在的ico图标文件
            icon_path = Path(self.current_directory) / "config" / "resources" / "icons" / "Icon_BatteryTestGUI.ico"
            if icon_path.exists():
                icon = QG.QIcon(str(icon_path))
            else:
                # 如果文件不存在，使用默认图标
                icon = QG.QIcon()
        except Exception:
            # 捕获所有异常，确保应用能正常启动
            icon = QG.QIcon()
        
        self.setWindowIcon(icon)

    def init_widget(self) -> None:
        if self.b_has_config:
            self.statusBar_BatteryAnalysis.showMessage("status:ok")
            
            self.init_lineedit()
            self.init_combobox()
            self.init_table()
            self.connect_widget()
            
            self.pushButton_Run.setFocus()
        else:
            # @todo: Add error popup windows here
            pass

    def init_lineedit(self) -> None:
        # input limit, only numbers allowed
        reg = QC.QRegularExpression(r"^\d*$")
        validator = QG.QRegularExpressionValidator(self)
        validator.setRegularExpression(reg)
        # self.lineEdit_BatchDateCode.setValidator(validator)
        self.lineEdit_SamplesQty.setValidator(validator)
        # self.lineEdit_Temperature.setValidator(validator)
        self.lineEdit_DatasheetNominalCapacity.setValidator(validator)
        self.lineEdit_CalculationNominalCapacity.setValidator(validator)
        self.lineEdit_RequiredUseableCapacity.setValidator(validator)
        # QSpinBox不需要设置文本验证器，因为它有内置的范围限制

        reg = QC.QRegularExpression(r"^\d+(\.\d+)?$")
        validator = QG.QRegularExpressionValidator(self)
        validator.setRegularExpression(reg)
        self.lineEdit_Version.setValidator(validator)

        self.lineEdit_TestProfile.setText("Not provided")
        self.lineEdit_Temperature.setText("Room Temperature")

    def init_combobox(self) -> None:
        self.comboBox_BatteryType.addItems(self.get_config("BatteryConfig/BatteryType"))
        self.comboBox_ConstructionMethod.addItems(self.get_config("BatteryConfig/ConstructionMethod"))
        self.comboBox_Specification_Type.addItems(self.get_config("BatteryConfig/SpecificationTypeCoinCell"))
        self.comboBox_Specification_Type.addItems(self.get_config("BatteryConfig/SpecificationTypePouchCell"))
        self.comboBox_Specification_Method.addItems(self.get_config("BatteryConfig/SpecificationMethod"))
        self.comboBox_Manufacturer.addItems(self.get_config("BatteryConfig/Manufacturer"))
        self.comboBox_TesterLocation.addItems(self.get_config("TestConfig/TesterLocation"))
        self.comboBox_TestedBy.addItems(self.get_config("TestConfig/TestedBy"))

        self.comboBox_BatteryType.setCurrentIndex(-1)
        self.comboBox_ConstructionMethod.setCurrentIndex(-1)
        self.comboBox_Specification_Type.setCurrentIndex(-1)
        self.comboBox_Specification_Method.setCurrentIndex(-1)
        self.comboBox_Manufacturer.setCurrentIndex(-1)
        self.comboBox_TesterLocation.setCurrentIndex(-1)
        self.comboBox_TestedBy.setCurrentIndex(-1)

        self.comboBox_ConstructionMethod.setEnabled(False)

    def init_table(self) -> None:
        self.config.setValue(
            "TestInformation/DataProcessingPlatforms", 
            f"BatteryAnalysis-DataConverter_V{self.version}.exe"
        )
        # 移除固定列宽设置，改为在resizeEvent中按比例分配
        # 确保表格的最后一列自动拉伸
        self.tableWidget_TestInformation.horizontalHeader().setStretchLastSection(True)

        def set_span_item(item_text: str, row: int, col: int, 
                          row_span: int = 1, col_span: int = 1, 
                          editable: bool = False) -> None:
            # 只有当跨度大于1时才调用setSpan，避免单个单元格跨度的警告
            if row_span > 1 or col_span > 1:
                self.tableWidget_TestInformation.setSpan(row, col, row_span, col_span)
            
            item = QW.QTableWidgetItem(item_text)
            if not editable:
                item.setFlags(QC.Qt.ItemFlag.ItemIsEnabled)
                item.setBackground(QG.QBrush(QG.QColor(242, 242, 242)))
            
            self.tableWidget_TestInformation.setItem(row, col, item)

        set_span_item("Test Equipment", 0, 0, 1, 2)
        set_span_item("", 0, 2, editable=True)

        set_span_item("Software Versions", 1, 0, 3, 1)
        set_span_item("BTS Server Version", 1, 1)
        set_span_item("BTS Client Version", 2, 1)
        set_span_item("TSDA (Data Analysis) Version", 3, 1)
        set_span_item("", 1, 2, editable=True)
        set_span_item("", 2, 2, editable=True)
        set_span_item("", 3, 2, editable=True)

        set_span_item("Middle Machines", 4, 0, 5, 1)
        set_span_item("Model", 4, 1)
        set_span_item("Hardware Version", 5, 1)
        set_span_item("Serial Number", 6, 1)
        set_span_item("Firmware Version", 7, 1)
        set_span_item("Device Type", 8, 1)
        set_span_item("", 4, 2, editable=True)
        set_span_item("", 5, 2, editable=True)
        set_span_item("", 6, 2, editable=True)
        set_span_item("", 7, 2, editable=True)
        set_span_item("", 8, 2, editable=True)

        set_span_item("Test Units", 9, 0, 3, 1)
        set_span_item("Model", 9, 1)
        set_span_item("Hardware Version", 10, 1)
        set_span_item("Firmware Version", 11, 1)
        set_span_item("", 9, 2, editable=True)
        set_span_item("", 9, 3, editable=True)
        set_span_item("", 10, 2, editable=True)
        set_span_item("", 11, 2, editable=True)

        set_span_item("Data Processing Platforms", 12, 0, 1, 2)
        set_span_item(
            self.get_config("TestInformation/DataProcessingPlatforms")[0], 
            12, 2, 
            editable=True
        )
        set_span_item("Reported By", 13, 0, 1, 2)
        set_span_item(
            self.get_config("TestInformation/ReportedBy")[0], 
            13, 2, 
            editable=True
        )

    def connect_widget(self) -> None:
        self.comboBox_BatteryType.currentIndexChanged.connect(self.check_batterytype)
        self.comboBox_Specification_Type.currentIndexChanged.connect(self.check_specification)
        self.comboBox_Specification_Method.currentIndexChanged.connect(self.check_specification)
        self.comboBox_TesterLocation.currentIndexChanged.connect(self.set_table)
        self.lineEdit_InputPath.textChanged.connect(self.get_xlsxinfo)
        self.pushButton_TestProfile.clicked.connect(self.select_testprofile)
        self.pushButton_InputPath.clicked.connect(self.select_inputpath)
        self.pushButton_OutputPath.clicked.connect(self.select_outputpath)
        self.pushButton_Run.clicked.connect(self.run)
        self.sigSetVersion.connect(self.get_version)

    def check_batterytype(self) -> None:
        self.checker_battery_type.clear()
        if self.comboBox_BatteryType.currentText() == "Coin Cell":
            self.comboBox_ConstructionMethod.setEnabled(False)
            self.comboBox_ConstructionMethod.setCurrentIndex(-1)
            self.lineEdit_DatasheetNominalCapacity.setText("")
            self.lineEdit_CalculationNominalCapacity.setText("")
            self.lineEdit_RequiredUseableCapacity.setText("")
            self.comboBox_Specification_Type.currentIndexChanged.disconnect(self.check_specification)
            self.comboBox_Specification_Method.currentIndexChanged.disconnect(self.check_specification)
            self.comboBox_Specification_Type.clear()
            self.comboBox_Specification_Type.addItems(self.get_config("BatteryConfig/SpecificationTypeCoinCell"))
            self.comboBox_Specification_Type.setCurrentIndex(-1)
            self.comboBox_Specification_Type.currentIndexChanged.connect(self.check_specification)
            self.comboBox_Specification_Method.currentIndexChanged.connect(self.check_specification)
            for t in range(self.comboBox_Specification_Type.count()):
                if self.specification_type == self.comboBox_Specification_Type.itemText(t):
                    self.comboBox_Specification_Type.setCurrentIndex(t)
                    break
        elif self.comboBox_BatteryType.currentText() == "Pouch Cell":
            self.comboBox_ConstructionMethod.setEnabled(True)
            for c in range(self.comboBox_ConstructionMethod.count()):
                if self.construction_method == self.comboBox_ConstructionMethod.itemText(c):
                    self.comboBox_ConstructionMethod.setCurrentIndex(c)
                    self.construction_method = ""
                    break
            self.lineEdit_DatasheetNominalCapacity.setText("")
            self.lineEdit_CalculationNominalCapacity.setText("")
            self.lineEdit_RequiredUseableCapacity.setText("")
            self.comboBox_Specification_Type.currentIndexChanged.disconnect(self.check_specification)
            self.comboBox_Specification_Method.currentIndexChanged.disconnect(self.check_specification)
            self.comboBox_Specification_Type.clear()
            self.comboBox_Specification_Type.addItems(self.get_config("BatteryConfig/SpecificationTypePouchCell"))
            self.comboBox_Specification_Type.setCurrentIndex(-1)
            self.comboBox_Specification_Type.currentIndexChanged.connect(self.check_specification)
            self.comboBox_Specification_Method.currentIndexChanged.connect(self.check_specification)
            for t in range(self.comboBox_Specification_Type.count()):
                if self.strSpecificationType == self.comboBox_Specification_Type.itemText(t):
                    self.comboBox_Specification_Type.setCurrentIndex(t)
                    break
        elif self.comboBox_BatteryType.currentText() == "":
            pass
        else:
            self.checker_battery_type.set_error(f"No battery type named {self.comboBox_BatteryType.currentText()}")
            self.statusBar_BatteryAnalysis.showMessage(f"[Error]: No battery type named {self.comboBox_BatteryType.currentText()}")

    def check_specification(self) -> None:
        self.specification_type = self.comboBox_Specification_Type.currentText()
        coin_cell_types = self.get_config("BatteryConfig/SpecificationTypeCoinCell")
        pouch_cell_types = self.get_config("BatteryConfig/SpecificationTypePouchCell")
        
        for coin_type in coin_cell_types:
            if self.specification_type == coin_type:
                self.comboBox_BatteryType.setCurrentIndex(0)
        
        for pouch_type in pouch_cell_types:
            if self.specification_type == pouch_type:
                self.comboBox_BatteryType.setCurrentIndex(1)
            
        specification_method = self.comboBox_Specification_Method.currentText()
        if self.specification_type == "" or specification_method == "":
            return

        rules = self.get_config("BatteryConfig/Rules")
        for rule in rules:
            rule_parts = rule.split("/")
            if rule_parts[0] == self.specification_type:
                if specification_method == rule_parts[1]:
                    self.lineEdit_DatasheetNominalCapacity.setText(f"{rule_parts[2]}")
                    self.lineEdit_CalculationNominalCapacity.setText(f"{rule_parts[3]}")
                    listRequiredUseableCapacityPercentage = re.findall(r"(\d+)%", rule_parts[4])
                    if listRequiredUseableCapacityPercentage != [] and len(listRequiredUseableCapacityPercentage) == 1:
                        self.lineEdit_RequiredUseableCapacity.setText(f"{int(int(rule_parts[3])*int(listRequiredUseableCapacityPercentage[0])/100)}")
                    else:
                        self.lineEdit_RequiredUseableCapacity.setText(f"{rule_parts[4]}")
                else:
                    self.lineEdit_DatasheetNominalCapacity.setText("")
                    self.lineEdit_CalculationNominalCapacity.setText("")
                    self.lineEdit_RequiredUseableCapacity.setText("")
                break
            elif rule_parts[0] in self.specification_type:
                if specification_method == rule_parts[1]:
                    self.lineEdit_DatasheetNominalCapacity.setText(f"{rule_parts[2]}")
                    self.lineEdit_CalculationNominalCapacity.setText(f"{rule_parts[3]}")
                    listRequiredUseableCapacityPercentage = re.findall(r"(\d+)%", rule_parts[4])
                    if listRequiredUseableCapacityPercentage != [] and len(listRequiredUseableCapacityPercentage) == 1:
                        self.lineEdit_RequiredUseableCapacity.setText(f"{int(int(rule_parts[3])*int(listRequiredUseableCapacityPercentage[0])/100)}")
                    else:
                        self.lineEdit_RequiredUseableCapacity.setText(f"{rule_parts[4]}")
                else:
                    self.lineEdit_DatasheetNominalCapacity.setText("")
                    self.lineEdit_CalculationNominalCapacity.setText("")
                    self.lineEdit_RequiredUseableCapacity.setText("")
            else:
                pass

    def set_table(self) -> None:
        self.checker_table.clear()
        # 不再重新创建QSettings实例，而是重新读取配置
        # 这样可以确保使用与初始化时相同的配置文件路径和设置
        self.config.sync()  # 确保配置文件被正确加载
        
        test_information_groups = []
        child_groups = self.config.childGroups()
        
        for group in child_groups:
            if "TestInformation." in group:
                test_information_groups.append(group)

        if not test_information_groups:
            self.checker_table.set_error("No TestInformation in setting.ini")
            self.statusBar_BatteryAnalysis.showMessage("[Error]: No TestInformation in setting.ini")
            return

        self.test_information = ""
        for group in test_information_groups:
            group_parts = group.split(".")
            if len(group_parts) != 3:
                self.checker_table.set_error(f"Wrong TestInformation section format:[{group}] in setting.ini")
                self.statusBar_BatteryAnalysis.showMessage(f"[Error]: Wrong TestInformation section format:[{group}] in setting.ini")
                return
            
            location = group_parts[1]
            laboratory = group_parts[2]
            tester_location = self.comboBox_TesterLocation.currentText().replace(" ", "")
            
            if (laboratory in tester_location) and (location in tester_location):
                self.test_information = group
                break

        if self.test_information == "":
            self.checker_table.set_error("Can't find matched TestInformation section in setting.ini")
            self.statusBar_BatteryAnalysis.showMessage("[Error]: Can't find matched TestInformation section in setting.ini")
            return

        def set_item(item_data, row: int, col: int) -> None:
            item_text = ", ".join(item_data) if item_data else ""
            qt_item = QW.QTableWidgetItem(item_text)
            self.tableWidget_TestInformation.setItem(row, col, qt_item)

        set_item(self.get_config(f"{self.test_information}/TestEquipment"), 0, 2)
        set_item(self.get_config(f"{self.test_information}/SoftwareVersions.BTSServerVersion"), 1, 2)
        set_item(self.get_config(f"{self.test_information}/SoftwareVersions.BTSClientVersion"), 2, 2)
        set_item(self.get_config(f"{self.test_information}/SoftwareVersions.BTSDAVersion"), 3, 2)
        set_item(self.get_config(f"{self.test_information}/MiddleMachines.Model"), 4, 2)
        set_item(self.get_config(f"{self.test_information}/MiddleMachines.HardwareVersion"), 5, 2)
        set_item(self.get_config(f"{self.test_information}/MiddleMachines.SerialNumber"), 6, 2)
        set_item(self.get_config(f"{self.test_information}/MiddleMachines.FirmwareVersion"), 7, 2)
        set_item(self.get_config(f"{self.test_information}/MiddleMachines.DeviceType"), 8, 2)
        set_item(self.get_config(f"{self.test_information}/TestUnits.Model"), 9, 2)
        set_item(self.get_config(f"{self.test_information}/TestUnits.HardwareVersion"), 10, 2)
        set_item(self.get_config(f"{self.test_information}/TestUnits.FirmwareVersion"), 11, 2)

    def get_xlsxinfo(self) -> None:
        self.checker_input_xlsx.clear()
        self.comboBox_Specification_Type.currentIndexChanged.disconnect(self.check_specification)
        self.comboBox_Specification_Method.currentIndexChanged.disconnect(self.check_specification)
        self.comboBox_BatteryType.setCurrentIndex(-1)
        self.comboBox_Specification_Type.clear()
        self.comboBox_Specification_Type.addItems(self.get_config("BatteryConfig/SpecificationTypeCoinCell"))
        self.comboBox_Specification_Type.addItems(self.get_config("BatteryConfig/SpecificationTypePouchCell"))
        self.comboBox_Specification_Type.setCurrentIndex(-1)
        self.comboBox_Specification_Method.clear()
        self.comboBox_Specification_Method.addItems(self.get_config("BatteryConfig/SpecificationMethod"))
        self.comboBox_Specification_Method.setCurrentIndex(-1)
        self.comboBox_Manufacturer.setCurrentIndex(-1)
        self.lineEdit_BatchDateCode.setText("")
        self.lineEdit_SamplesQty.setText("")
        self.lineEdit_DatasheetNominalCapacity.setText("")
        self.lineEdit_CalculationNominalCapacity.setText("")
        self.comboBox_Specification_Type.currentIndexChanged.connect(self.check_specification)
        self.comboBox_Specification_Method.currentIndexChanged.connect(self.check_specification)
        strInDataXlsxDir = self.lineEdit_InputPath.text()
        if strInDataXlsxDir != "":
            listAllInXlsx = [f for f in os.listdir(strInDataXlsxDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            if len(listAllInXlsx) != 0:
                intIndexType = -1
                intIndexMethod = -1
                strSampleInputXlsxTitle = listAllInXlsx[0]
                self.construction_method = ""
                for c in range(self.comboBox_ConstructionMethod.count()):
                    if self.comboBox_ConstructionMethod.itemText(c) in strSampleInputXlsxTitle:
                        self.construction_method = self.comboBox_ConstructionMethod.itemText(c)
                        break
                listAllSpecificationType = self.get_config("BatteryConfig/SpecificationTypeCoinCell") + self.get_config("BatteryConfig/SpecificationTypePouchCell")
                listAllSpecificationMethod = self.get_config("BatteryConfig/SpecificationMethod")
                for t in range(len(listAllSpecificationType)):
                    if f"{listAllSpecificationType[t]}" in strSampleInputXlsxTitle:
                        intIndexType = t
                        break
                for m in range(len(listAllSpecificationMethod)):
                    if f"{listAllSpecificationMethod[m]}" in strSampleInputXlsxTitle:
                        intIndexMethod = m
                        break
                self.comboBox_Specification_Type.setCurrentIndex(intIndexType)
                self.comboBox_Specification_Method.setCurrentIndex(intIndexMethod)
                for m in range(self.comboBox_Manufacturer.count()):
                    if self.comboBox_Manufacturer.itemText(m) in strSampleInputXlsxTitle:
                        self.comboBox_Manufacturer.setCurrentIndex(m)
                listBatchDateCode = re.findall("DC(.*?),", strSampleInputXlsxTitle)
                if len(listBatchDateCode) == 1:
                    self.lineEdit_BatchDateCode.setText(listBatchDateCode[0].strip())
                listPulseCurrentToSplit = re.findall(r"\(([\d.]+[-\d.]+)mA", strSampleInputXlsxTitle)
                if len(listPulseCurrentToSplit) == 1:
                    listPulseCurrent = listPulseCurrentToSplit[0].split("-")
                    try:
                        # 将字符串转换为浮点数，保留小数精度
                        self.listCurrentLevel = [float(c.strip()) for c in listPulseCurrent]
                    except ValueError:
                        # 处理转换失败的情况
                        self.listCurrentLevel = [int(float(c.strip())) for c in listPulseCurrent]
                    self.config.setValue("BatteryConfig/PulseCurrent", listPulseCurrent)
                    # self.listCurrentLevel = [int(listPulseCurrent[c].strip()) for c in range(len(listPulseCurrent))]
                    # self.config.setValue("BatteryConfig/PulseCurrent", listPulseCurrent)

                self.cc_current = ""
                list_cc_current_to_split = re.findall(r"mA,(.*?)\)", strSampleInputXlsxTitle)
                if len(list_cc_current_to_split) == 1:
                    str_cc_current_to_split = list_cc_current_to_split[0].replace("mAh", "")
                    list_cc_current_to_split = re.findall(r"([\d.]+)mA", str_cc_current_to_split)
                    if len(list_cc_current_to_split) >= 1:
                        self.cc_current = list_cc_current_to_split[-1]
                self.lineEdit_SamplesQty.setText(str(len(listAllInXlsx)))
            else:
                self.checker_input_xlsx.set_error("Input path has no data")
            self.statusBar_BatteryAnalysis.showMessage("[Error]: Input path has no data")

    def get_version(self) -> None:
        """
        计算并设置电池分析的版本号
        
        此方法通过分析输入目录中的XLSX文件，计算其MD5校验和，
        然后根据MD5.csv文件中的历史记录确定当前版本号。如果输入文件内容变更，
        版本号会自动增加。
        
        工作流程：
        1. 从UI获取输入和输出目录路径
        2. 检查目录是否存在
        3. 收集输入目录中所有有效的.xlsx文件（排除临时文件）
        4. 计算这些文件的MD5校验和
        5. 读取MD5.csv文件（如果存在）来获取历史记录
        6. 根据MD5校验和匹配确定版本号
        7. 如果找到匹配的MD5，使用对应的版本号；否则创建新版本
        8. 更新MD5.csv文件并设置为隐藏属性
        9. 将版本号显示在UI中
        
        版本号格式：
        - 主版本号：当输入文件内容发生变化时增加
        - 次版本号：同一内容的重复运行计数
        
        错误处理：
        - 如果输入或输出目录不存在，清空版本号显示
        - 如果输入目录中没有XLSX文件，清空版本号显示
        
        返回值：
            None
        """
        strInPutDir = self.lineEdit_InputPath.text()
        strOutoutDir = self.lineEdit_OutputPath.text()
        if os.path.exists(strInPutDir) and os.path.exists(strOutoutDir):
            listAllInXlsx = [strInPutDir + f"/{f}" for f in os.listdir(strInPutDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            if len(listAllInXlsx) == 0:
                self.lineEdit_Version.setText("")
                return
            strCsvMd5Path = strOutoutDir + "/MD5.csv"
            self.md5_checksum = calc_md5checksum(listAllInXlsx)
            if os.path.exists(strCsvMd5Path) and os.path.getsize(strCsvMd5Path) != 0:
                listMD5Reader = []
                f = open(strCsvMd5Path, mode='r', encoding='utf-8')
                csvMD5Reader = csv.reader(f)
                for row in csvMD5Reader:
                    listMD5Reader.append(row)
                f.close()
                [_, listChecksum, _, listTimes] = listMD5Reader

                os.remove(strCsvMd5Path)
                f = open(strCsvMd5Path, mode='w', newline='', encoding='utf-8')
                csvMD5Writer = csv.writer(f)

                if len(listChecksum) == 0:
                    csvMD5Writer.writerow(["Checksums:"])
                    csvMD5Writer.writerow([self.md5_checksum])
                    csvMD5Writer.writerow(["Times:"])
                    csvMD5Writer.writerow(["0"])
                    self.lineEdit_Version.setText("1.0")
                else:
                    intVersionMajor = 1
                    intVersionMinor = 0
                    for c in range(len(listChecksum)):
                        if self.md5_checksum == listChecksum[c]:
                            intVersionMajor = c + 1
                            intVersionMinor = int(listTimes[c])
                            # increase it after executing the whole program
                            break
                        if c == len(listChecksum) - 1:
                            intVersionMajor = c + 2
                            listChecksum.append(self.md5_checksum)
                            listTimes.append("0")
                    csvMD5Writer.writerow(["Checksums:"])
                    csvMD5Writer.writerow(listChecksum)
                    csvMD5Writer.writerow(["Times:"])
                    csvMD5Writer.writerow(listTimes)
                    self.lineEdit_Version.setText(f"{intVersionMajor}.{intVersionMinor}")
                f.close()
            else:
                f = open(strCsvMd5Path, mode='w', newline='', encoding='utf-8')
                csvMD5Writer = csv.writer(f)
                csvMD5Writer.writerow(["Checksums:"])
                csvMD5Writer.writerow([self.md5_checksum])
                csvMD5Writer.writerow(["Times:"])
                csvMD5Writer.writerow(["0"])
                f.close()
                self.lineEdit_Version.setText("1.0")
            win32api.SetFileAttributes(strCsvMd5Path, win32con.FILE_ATTRIBUTE_HIDDEN)
        else:
            self.lineEdit_Version.setText("")

    def select_testprofile(self) -> None:
        self.current_directory, _ = QW.QFileDialog.getOpenFileName(self, "Select Test Profile", self.current_directory, "XML Files(*.xml)")
        if self.current_directory != "":
            self.lineEdit_TestProfile.setText(self.current_directory)
            # 获取Test Profile的父目录
            test_profile_dir = os.path.dirname(self.current_directory)
            # 获取父目录的上级目录（同级目录的根目录）
            parent_dir = os.path.dirname(test_profile_dir)
            # 自动设置input path为同级的2_xlsx文件夹
            input_path = os.path.join(parent_dir, "2_xlsx")
            if os.path.exists(input_path):
                self.lineEdit_InputPath.setText(input_path)
                self.sigSetVersion.emit()
            # 自动设置output path为同级的3_analysis results文件夹
            output_path = os.path.join(parent_dir, "3_analysis results")
            if not os.path.exists(output_path):
                # 如果输出目录不存在，创建它
                os.makedirs(output_path)
            self.lineEdit_OutputPath.setText(output_path)
            self.sigSetVersion.emit()
            # 更新current_directory
            self.current_directory = parent_dir

    def select_inputpath(self) -> None:
        self.current_directory = QW.QFileDialog.getExistingDirectory(self, "Select Input Path", self.current_directory)
        if self.current_directory != "":
            self.lineEdit_InputPath.setText(self.current_directory)
            self.sigSetVersion.emit()
            self.current_directory = self.current_directory + "/../../"

    def select_outputpath(self) -> None:
        self.current_directory = QW.QFileDialog.getExistingDirectory(self, "Select Output Path", self.current_directory)
        if self.current_directory != "":
            self.lineEdit_OutputPath.setText(self.current_directory)
            self.sigSetVersion.emit()
            self.current_directory = self.current_directory + "/../"

    def run(self) -> None:
        if self.checker_battery_type.b_check_pass and self.checker_table.b_check_pass and self.checker_input_xlsx.b_check_pass:
            self.save_table()
            self.init_widgetcolor()
            if self.checkinput():
                self.init_thread()
                if self.thread is not None:
                    """ test_info
                    index 0: Battery Type
                    index 1: Construction Method
                    index 2: Specification_Type
                    index 3: Specification_Method
                    index 4: Manufacturer
                    index 5: Batch/Date Code
                    index 6: Sample Qty  
                    index 7: Temperature
                    index 8: Datasheet Nominal Capacity
                    index 9: Calculation Nominal Capacity
                    index 10: Accelerated Aging
                    index 11: Tester Location
                    index 12: Test By
                    index 13: Test Profile
                    index 14: Pulse Current List
                    index 15: Cut-off Voltage List
                    index 16: Report word version
                    index 17: Required Useable Capacity
                    """
                    test_info = [
                        self.comboBox_BatteryType.currentText(),
                        self.comboBox_ConstructionMethod.currentText(),
                        self.comboBox_Specification_Type.currentText(),
                        self.comboBox_Specification_Method.currentText(),
                        self.comboBox_Manufacturer.currentText(),
                        self.lineEdit_BatchDateCode.text(),
                        self.lineEdit_SamplesQty.text(),
                        self.lineEdit_Temperature.text(),
                        self.lineEdit_DatasheetNominalCapacity.text(),
                        self.lineEdit_CalculationNominalCapacity.text(),
                        str(self.spinBox_AcceleratedAging.value()),
                        self.comboBox_TesterLocation.currentText(),
                        self.comboBox_TestedBy.currentText(),
                        self.lineEdit_TestProfile.text(),
                        self.listCurrentLevel,
                        self.listVoltageLevel,
                        self.lineEdit_Version.text(),
                        self.lineEdit_RequiredUseableCapacity.text()
                    ]
                    self.thread.get_info(self.path, self.lineEdit_InputPath.text(), self.lineEdit_OutputPath.text(), test_info)
                    self.update_config(test_info)
                    if self.checker_update_config.b_check_pass:
                        self.md5_checksum_run = self.md5_checksum
                        self.statusBar_BatteryAnalysis.showMessage("status:ok")
                        self.thread.start()     
        else:
            self.statusBar_BatteryAnalysis.showMessage(f"[Error]: {self.checker_battery_type.str_error_msg} {self.checker_table.str_error_msg} {self.checker_input_xlsx.str_error_msg}")
            self.pushButton_Run.setText("Rerun")
            self.pushButton_Run.setFocus()

    def save_table(self) -> None:
        # set focus on pushButton_Run for saving the input text
        self.pushButton_Run.setFocus()

        def set_item(config_key: str, row: int, col: int):
            list_item_text = self.tableWidget_TestInformation.item(row, col).text().split(",")
            for i in range(len(list_item_text)):
                list_item_text[i] = list_item_text[i].strip()
            if len(list_item_text) == 1:
                self.config.setValue(f"{config_key}", list_item_text[0])
            else:
                self.config.setValue(f"{config_key}", list_item_text)

        if self.test_information != "":
            set_item(f"{self.test_information}/TestEquipment", 0, 2)
            set_item(f"{self.test_information}/SoftwareVersions.BTSServerVersion", 1, 2)
            set_item(f"{self.test_information}/SoftwareVersions.BTSClientVersion", 2, 2)
            set_item(f"{self.test_information}/SoftwareVersions.BTSDAVersion", 3, 2)
            set_item(f"{self.test_information}/MiddleMachines.Model", 4, 2)
            set_item(f"{self.test_information}/MiddleMachines.HardwareVersion", 5, 2)
            set_item(f"{self.test_information}/MiddleMachines.SerialNumber", 6, 2)
            set_item(f"{self.test_information}/MiddleMachines.FirmwareVersion", 7, 2)
            set_item(f"{self.test_information}/MiddleMachines.DeviceType", 8, 2)
            set_item(f"{self.test_information}/TestUnits.Model", 9, 2)
            set_item(f"{self.test_information}/TestUnits.HardwareVersion", 10, 2)
            set_item(f"{self.test_information}/TestUnits.FirmwareVersion", 11, 2)

        set_item("TestInformation/TestEquipment", 0, 2)
        set_item("TestInformation/SoftwareVersions.BTSServerVersion", 1, 2)
        set_item("TestInformation/SoftwareVersions.BTSClientVersion", 2, 2)
        set_item("TestInformation/SoftwareVersions.BTSDAVersion", 3, 2)
        set_item("TestInformation/MiddleMachines.Model", 4, 2)
        set_item("TestInformation/MiddleMachines.HardwareVersion", 5, 2)
        set_item("TestInformation/MiddleMachines.SerialNumber", 6, 2)
        set_item("TestInformation/MiddleMachines.FirmwareVersion", 7, 2)
        set_item("TestInformation/MiddleMachines.DeviceType", 8, 2)
        set_item("TestInformation/TestUnits.Model", 9, 2)
        set_item("TestInformation/TestUnits.HardwareVersion", 10, 2)
        set_item("TestInformation/TestUnits.FirmwareVersion", 11, 2)
        set_item("TestInformation/ReportedBy", 13, 2)

    def init_widgetcolor(self) -> None:
        self.label_BatteryType.setStyleSheet("background-color:")
        self.label_ConstructionMethod.setStyleSheet("background-color:")
        self.label_Specification.setStyleSheet("background-color:")
        self.label_Manufacturer.setStyleSheet("background-color:")
        self.label_BatchDateCode.setStyleSheet("background-color:")
        self.label_SamplesQty.setStyleSheet("background-color:")
        self.label_Temperature.setStyleSheet("background-color:")
        self.label_DatasheetNominalCapacity.setStyleSheet("background-color:")
        self.label_CalculationNominalCapacity.setStyleSheet("background-color:")
        self.label_AcceleratedAging.setStyleSheet("background-color:")
        self.label_RequiredUseableCapacity.setStyleSheet("background-color:")
        self.label_TesterLocation.setStyleSheet("background-color:")
        self.label_TestedBy.setStyleSheet("background-color:")
        self.label_TestProfile.setStyleSheet("background-color:")
        self.label_InputPath.setStyleSheet("background-color:")
        self.label_OutputPath.setStyleSheet("background-color:")
        self.label_Version.setStyleSheet("background-color:")
        self.pushButton_Run.setStyleSheet("background-color:")

    def checkinput(self) -> bool:
        check_pass_flag = True
        warning_info = ["Unknown: "]
        if self.comboBox_BatteryType.currentText() == "":
            check_pass_flag = False
            warning_info.append("Battery Type")
            self.label_BatteryType.setStyleSheet("background-color:red")
        if self.comboBox_BatteryType.currentText() == "Pouch Cell":
            if self.comboBox_ConstructionMethod.currentText() == "":
                check_pass_flag = False
                warning_info.append("Construction Method")
                self.label_ConstructionMethod.setStyleSheet("background-color:red")
        if self.comboBox_Specification_Type.currentText() == "" or self.comboBox_Specification_Method.currentText() == "":
            check_pass_flag = False
            warning_info.append("Specification")
            self.label_Specification.setStyleSheet("background-color:red")
        if self.comboBox_Manufacturer.currentText() == "":
            check_pass_flag = False
            warning_info.append("Manufacturer")
            self.label_Manufacturer.setStyleSheet("background-color:red")
        if self.lineEdit_BatchDateCode.text() == "":
            check_pass_flag = False
            warning_info.append("Batch/Date Code")
            self.label_BatchDateCode.setStyleSheet("background-color:red")
        if self.lineEdit_SamplesQty.text() == "":
            check_pass_flag = False
            warning_info.append("SamplesQty")
            self.label_SamplesQty.setStyleSheet("background-color:red")
        if self.lineEdit_Temperature.text() == "":
            check_pass_flag = False
            warning_info.append("Temperature")
            self.label_Temperature.setStyleSheet("background-color:red")
        if self.lineEdit_DatasheetNominalCapacity.text() == "":
            check_pass_flag = False
            warning_info.append("Datasheet Nominal Capacity")
            self.label_DatasheetNominalCapacity.setStyleSheet("background-color:red")
        if self.lineEdit_CalculationNominalCapacity.text() == "":
            check_pass_flag = False
            warning_info.append("Calculation Nominal Capacity")
            self.label_CalculationNominalCapacity.setStyleSheet("background-color:red")
        # QSpinBox总是有一个值（0-10），所以不需要检查是否为空
        # 但我们仍然可以检查值是否在有效范围内（虽然控件已经限制了）
        aging_value = self.spinBox_AcceleratedAging.value()
        if aging_value < 0 or aging_value > 10:
            check_pass_flag = False
            warning_info.append("Accelerated Aging")
            self.label_AcceleratedAging.setStyleSheet("background-color:red")
        if self.lineEdit_RequiredUseableCapacity.text() == "":
            check_pass_flag = False
            warning_info.append("Required Useable Capacity")
            self.label_RequiredUseableCapacity.setStyleSheet("background-color:red")
        if self.comboBox_TesterLocation.currentText() == "":
            check_pass_flag = False
            warning_info.append("Test Location")
            self.label_TesterLocation.setStyleSheet("background-color:red")
        if self.comboBox_TestedBy.currentText() == "":
            check_pass_flag = False
            warning_info.append("Test By")
            self.label_TestedBy.setStyleSheet("background-color:red")
        if self.lineEdit_TestProfile.text() == "":
            check_pass_flag = False
            warning_info.append("Test Profile")
            self.label_TestProfile.setStyleSheet("background-color:red")
        if self.lineEdit_InputPath.text() == "":
            check_pass_flag = False
            warning_info.append("Input Path")
            self.label_InputPath.setStyleSheet("background-color:red")
        if self.lineEdit_OutputPath.text() == "":
            check_pass_flag = False
            warning_info.append("Output Path")
            self.label_OutputPath.setStyleSheet("background-color:red")
        if self.lineEdit_Version.text() == "":
            check_pass_flag = False
            warning_info.append("Version")
            self.label_Version.setStyleSheet("background-color:red")
        # check_pass_flag = True
        if check_pass_flag:
            self.pushButton_Run.setEnabled(False)
            self.pushButton_Run.setFocus()
        else:
            warning_info_str = warning_info[0]
            for i in range(1, len(warning_info) - 1):
                warning_info_str = warning_info_str + warning_info[i] + ", "
            warning_info_str += warning_info[-1]
            # print(warning_info_str)
            self.statusBar_BatteryAnalysis.showMessage(warning_info_str)
            self.pushButton_Run.setText("Rerun")
            self.pushButton_Run.setFocus()
        return check_pass_flag

    def init_thread(self) -> None:
        self.thread = Thread()
        self.thread.info.connect(self.get_threadinfo)
        self.thread.sigThreadEnd.connect(self.set_version)
        self.thread.sigRenamePath.connect(self.rename_pltPath)

    def get_threadinfo(self, threadstate, stateindex, threadinfo) -> None:
        self.statusBar_BatteryAnalysis.showMessage(threadinfo)
        if threadstate:
            if stateindex == 0:
                self.pushButton_Run.setText("Running.")
            if stateindex == 1:
                self.pushButton_Run.setText("Running..")
            if stateindex == 2:
                self.pushButton_Run.setText("Running...")
            if stateindex == 3:
                self.pushButton_Run.setText("Running....")
        else:
            self.thread.deleteLater()
            if stateindex == 0:
                self.pushButton_Run.setText("Run")
                self.pushButton_Run.setStyleSheet("background-color:#00FF00")
                self.pushButton_Run.setEnabled(True)
            else:
                self.pushButton_Run.setText("Rerun")
                self.pushButton_Run.setStyleSheet("background-color:red")
                self.pushButton_Run.setEnabled(True)

    def set_version(self) -> None:
        # 导入pathlib用于更现代的路径处理
        from pathlib import Path
        
        # 初始化必要的属性如果不存在
        if not hasattr(self, 'md5_checksum_run'):
            self.md5_checksum_run = self.md5_checksum if hasattr(self, 'md5_checksum') else ''
            
        list_md5_reader = []
        output_path_str = self.lineEdit_OutputPath.text()
        
        try:
            # 使用Path对象进行路径处理
            output_path = Path(output_path_str)
            md5_file = output_path / "MD5.csv"
            
            # 检查路径是否有效
            if not output_path_str or not output_path.is_dir():
                self.statusBar_BatteryAnalysis.showMessage(f"[Warning]: Invalid output path: {output_path_str}")
                return
                
            # 读取MD5文件
            if md5_file.exists():
                try:
                    with md5_file.open(mode='r', encoding='utf-8') as f:
                        csv_md5_reader = csv.reader(f)
                        for row in csv_md5_reader:
                            list_md5_reader.append(row)
                except PermissionError:
                    self.statusBar_BatteryAnalysis.showMessage(f"[Warning]: Permission denied reading {md5_file}")
                    return
                except Exception as read_error:
                    self.statusBar_BatteryAnalysis.showMessage(f"[Warning]: Failed to read MD5 file: {str(read_error)}")
                    return
            
            # 处理文件内容
            if len(list_md5_reader) >= 4:
                try:
                    [_, list_checksum, _, list_times] = list_md5_reader
                    
                    # 创建临时文件避免权限问题
                    temp_file = output_path / "MD5_temp.csv"
                    with temp_file.open(mode='w', newline='', encoding='utf-8') as f:
                        csv_md5_writer = csv.writer(f)
                        for c, checksum in enumerate(list_checksum):
                            if self.md5_checksum_run == checksum:
                                version_major = c + 1
                                version_minor = int(list_times[c]) + 1
                                list_times[c] = str(version_minor)
                                if self.md5_checksum_run == getattr(self, 'md5_checksum', ''):
                                    self.lineEdit_Version.setText(f"{version_major}.{version_minor}")
                                break
                        
                        csv_md5_writer.writerow(["Checksums:"])
                        csv_md5_writer.writerow(list_checksum)
                        csv_md5_writer.writerow(["Times:"])
                        csv_md5_writer.writerow(list_times)
                    
                    # 替换原文件
                    if md5_file.exists():
                        try:
                            md5_file.unlink()  # 删除原文件
                        except PermissionError:
                            self.statusBar_BatteryAnalysis.showMessage(f"[Warning]: Cannot remove existing MD5 file, using new location")
                            md5_file = temp_file  # 使用临时文件作为新的MD5文件
                            temp_file = None
                    
                    if temp_file:
                        temp_file.replace(md5_file)  # 替换文件
                    
                    # 尝试设置隐藏属性，但不抛出异常
                    try:
                        win32api.SetFileAttributes(str(md5_file), win32con.FILE_ATTRIBUTE_HIDDEN)
                    except Exception:
                        # 忽略设置隐藏属性失败的错误
                        pass
                except PermissionError:
                    self.statusBar_BatteryAnalysis.showMessage(f"[Warning]: Permission denied writing to {output_path}")
                except Exception as write_error:
                    self.statusBar_BatteryAnalysis.showMessage(f"[Warning]: Failed to write MD5 file: {str(write_error)}")
            else:
                # 如果文件不存在或格式不正确，创建新文件
                try:
                    with md5_file.open(mode='w', newline='', encoding='utf-8') as f:
                        csv_md5_writer = csv.writer(f)
                        csv_md5_writer.writerow(["Checksums:"])
                        csv_md5_writer.writerow([self.md5_checksum_run if self.md5_checksum_run else ""])
                        csv_md5_writer.writerow(["Times:"])
                        csv_md5_writer.writerow(["1"])
                    
                    try:
                        win32api.SetFileAttributes(str(md5_file), win32con.FILE_ATTRIBUTE_HIDDEN)
                    except Exception:
                        pass
                except PermissionError:
                    self.statusBar_BatteryAnalysis.showMessage(f"[Warning]: Cannot create MD5 file in {output_path}")
                except Exception as create_error:
                    self.statusBar_BatteryAnalysis.showMessage(f"[Warning]: Failed to create MD5 file: {str(create_error)}")
                    
        except Exception as e:
            # 捕获所有其他异常但不中断程序
            self.statusBar_BatteryAnalysis.showMessage(f"[Info]: Version tracking skipped: {str(e)}")

    def rename_pltPath(self, strTestDate):
        self.config.setValue("PltConfig/Path", f"{self.lineEdit_OutputPath.text()}/{strTestDate}_V{self.lineEdit_Version.text()}")

    def update_config(self, test_info) -> None:
        # 初始化checker_update_config如果不存在
        if not hasattr(self, 'checker_update_config'):
            self.checker_update_config = Checker()
        self.checker_update_config.clear()
        self.config.setValue("PltConfig/Path", f"{self.lineEdit_OutputPath.text()}/V{test_info[16]}")

        bSetTitle = False
        rules = self.get_config("BatteryConfig/Rules")
        specification_type = self.comboBox_Specification_Type.currentText()
        strPulseCurrent = ""
        for c in range(len(self.listCurrentLevel)):
            strPulseCurrent += f"{self.listCurrentLevel[c]}mA/"
        for rule in rules:
            rule_parts = rule.split("/")
            if self.cc_current == "":
                  self.cc_current = rule_parts[5]
            if rule_parts[0] == specification_type:
                self.config.setValue("PltConfig/Title", f"{test_info[4]} {test_info[2]} {test_info[3]}({test_info[5]}), -{test_info[8]}mAh@{self.cc_current}mA, {strPulseCurrent[:-1]}, {test_info[7]}")
                bSetTitle = True
                break
            elif rule_parts[0] in specification_type:
                self.config.setValue("PltConfig/Title", f"{test_info[4]} {test_info[2]} {test_info[3]}({test_info[5]}), -{test_info[8]}mAh@{self.cc_current}mA, {strPulseCurrent[:-1]}, {test_info[7]}")
                bSetTitle = True
            else:
                pass
        if not bSetTitle:
            self.checker_update_config.set_error("PltTitle")
            self.statusBar_BatteryAnalysis.showMessage(f"[Error]: No rules for {specification_type}")
            
    def resizeEvent(self, event):
        """窗口大小改变时的事件处理函数"""
        # 调用父类的resizeEvent以确保正常的事件处理
        super().resizeEvent(event)
        
        # 调整表格列宽以适应窗口大小
        if hasattr(self, 'tableWidget_TestInformation'):
            # 计算可用宽度（减去边距和滚动条）
            available_width = self.tableWidget_TestInformation.width() - 20
            
            # 设置列宽比例
            # 第0列（15%）
            self.tableWidget_TestInformation.horizontalHeader().resizeSection(0, int(available_width * 0.15))
            # 第1列（25%）
            self.tableWidget_TestInformation.horizontalHeader().resizeSection(1, int(available_width * 0.25))
            # 第2列（剩余空间）
            self.tableWidget_TestInformation.horizontalHeader().resizeSection(2, int(available_width * 0.6))


class Thread(QC.QThread):
    info = QC.pyqtSignal(bool, int, str)
    sigThreadEnd = QC.pyqtSignal()
    sigRenamePath = QC.pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.strPath = ""
        self.strInputPath = ""
        self.strOutputPath = ""
        self.listTestInfo = []
        self.bThreadRun = False
        self.strErrorBattery = ""
        self.strErrorXlsx = ""
        self.strTestDate = ""

    def get_info(self, strPath, strInputPath, strOutputPath, listTestInfo) -> None:
        self.strPath = strPath
        self.strInputPath = strInputPath
        self.strOutputPath = strOutputPath
        self.listTestInfo = listTestInfo

    def run(self) -> None:
        self.bThreadRun = True
        threading.Thread(target=self.signal_running, daemon=True).start()
        if os.path.exists(f"{self.strOutputPath}/V{self.listTestInfo[16]}"):
            shutil.rmtree(f"{self.strOutputPath}/V{self.listTestInfo[16]}")
        os.mkdir(f"{self.strOutputPath}/V{self.listTestInfo[16]}")
        infoBattery = battery_analysis.BatteryAnalysis(strInDataXlsxDir=self.strInputPath,
                                                              strResultPath=self.strOutputPath,
                                                              listTestInfo=self.listTestInfo)
        self.strErrorBattery = infoBattery.UBA_GetErrorLog()
        if self.strErrorBattery == "":
            listBatteryInfo = infoBattery.UBA_GetBatteryInfo()
            try:
                [sy, sm, sd] = listBatteryInfo[2][0].split(" ")[0].split("-")
                self.strTestDate = f"{sy}{sm}{sd}"
            except ValueError:
                self.strTestDate = "00000000"
            if os.path.exists(f"{self.strOutputPath}/{self.strTestDate}_V{self.listTestInfo[16]}"):
                shutil.rmtree(f"{self.strOutputPath}/{self.strTestDate}_V{self.listTestInfo[16]}")
            self.sigRenamePath.emit(self.strTestDate)
            os.rename(f"{self.strOutputPath}/V{self.listTestInfo[16]}", f"{self.strOutputPath}/{self.strTestDate}_V{self.listTestInfo[16]}")
            infoFile = file_writer.FileWriter(strResultPath=self.strOutputPath,
                                                     listTestInfo=self.listTestInfo,
                                                     listBatteryInfo=listBatteryInfo)
            self.strErrorXlsx = infoFile.UFW_GetErrorLog()
            if self.strErrorXlsx != "":
                logging.error(self.strErrorXlsx)
                # shutil.rmtree(f"{self.strOutputPath}/{self.strTestDate}_V{self.listTestInfo[16]}")
            else:
                # 优化ImageMaker启动逻辑：仅查找与 analyzer 同版本的 visualizer
                import sys
                import re
                exe_dir = os.path.dirname(sys.executable)
                build_type = "Debug" if "Debug" in exe_dir else "Release"

                # 从当前运行的 analyzer 可执行文件名中解析版本（形如 battery-analyzer_1_0_1.exe）
                analyzer_exe_name = os.path.basename(sys.executable)
                m = re.search(r"battery-analyzer_(\d+_\d+_\d+)\.exe", analyzer_exe_name, re.IGNORECASE)
                version_us = None
                if m:
                    version_us = m.group(1)
                else:
                    # 回退：从项目版本读取，并转换为下划线格式
                    try:
                        from ..utils.version import Version
                        version_us = Version().version.replace('.', '_')
                    except Exception:
                        version_us = "2_0_0"  # 与项目默认版本保持一致

                # 仅使用与 analyzer 同版本的候选路径
                exe_candidates = [
                    # 可执行文件所在目录（打包/本地运行）
                    os.path.join(exe_dir, f"battery-analysis-visualizer_{version_us}.exe"),
                    # 项目根目录（少数场景可能存在）
                    os.path.join(self.strPath, f"battery-analysis-visualizer_{version_us}.exe"),
                    # 项目构建目录（Debug/Release）
                    os.path.join(self.strPath, "build", build_type, f"battery-analysis-visualizer_{version_us}.exe"),
                ]
                
                exe_executed = False
                for exe_path in exe_candidates:
                    if os.path.exists(exe_path):
                        logging.info(f"启动ImageMaker: {exe_path}")
                        try:
                            # 使用CREATE_NEW_CONSOLE标志启动，以便新窗口中运行
                            subprocess.run(exe_path, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                            exe_executed = True
                            break
                        except Exception as e:
                            logging.error(f"启动失败 {exe_path}: {e}")
                            continue
                
                if not exe_executed:
                    logging.warning("未找到battery-analysis-visualizer可执行文件")
                    logging.info("候选路径:")
                    for path in exe_candidates:
                        logging.info(f"  - {path}: {'存在' if os.path.exists(path) else '不存在'}")
        else:
            logging.error(self.strErrorBattery)
            # shutil.rmtree(f"{self.strOutputPath}/V{self.listTestInfo[16]}")
        self.bThreadRun = False

    def signal_running(self) -> None:
        while self.bThreadRun:
            self.info.emit(True, 0, "status:run")
            time.sleep(0.4)
            self.info.emit(True, 1, "status:run")
            time.sleep(0.4)
            self.info.emit(True, 2, "status:run")
            time.sleep(0.4)
            self.info.emit(True, 3, "status:run")
            time.sleep(0.4)
        if self.strErrorBattery != "":
            self.info.emit(False, 1, self.strErrorBattery)
        else:
            if self.strErrorXlsx != "":
                self.info.emit(False, 2, self.strErrorXlsx)
            else:
                self.info.emit(False, 0, "status:success")
                self.sigThreadEnd.emit()


def main() -> None:
    import warnings
    import matplotlib
    
    # 抑制PyQt5的deprecation warning
    warnings.filterwarnings("ignore", message=".*sipPyTypeDict.*")
    
    # 优化matplotlib配置，避免font cache构建警告
    matplotlib.use('Agg')  # 使用非交互式后端
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans','Liberation Sans']
    
    app = QW.QApplication(sys.argv)
    main = Main()
    # 移除固定窗口大小，允许自由调整
    main.setMinimumSize(970, 885)  # 设置最小尺寸以确保UI元素正常显示
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__': 
    main()
