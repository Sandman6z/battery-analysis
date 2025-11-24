import os
import re
import csv
import sys
import time
import base64
import shutil
import hashlib
import threading
import subprocess

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import PyQt6.QtGui as QG
import PyQt6.QtCore as QC
import PyQt6.QtWidgets as QW

import win32api, win32con

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
        self.bCheckPass = True
        self.strErrorMsg = ""

    def clear(self):
        self.bCheckPass = True
        self.strErrorMsg = ""

    def setError(self, strErrorMsg: str):
        self.bCheckPass = False
        self.strErrorMsg = strErrorMsg


class Main(QW.QMainWindow, ui_main_window.Ui_MainWindow, version.Version):
    sigSetVersion = QC.pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        version.Version.__init__(self)
        self.thread = None
        self.bHasConfig = True
        self.checkerBatteryType = Checker()
        self.checkerTable = Checker()
        self.checkerInputXlsx = Checker()
        self.checkerUpdateConfig = Checker()
        self.strConstructionMethod = ""
        self.strTestInformation = ""
        self.strSpecificationType = ""
        self.strCCCurrent = ""
        self.strMd5Checksum = ""
        self.strMd5ChecksumRun = ""
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("bt")

        # 改进的配置文件路径查找逻辑
        # 首先确定基础目录
        if getattr(sys, 'frozen', False):
            # 在exe环境中，使用exe所在目录
            base_dir = os.path.dirname(sys.executable)
        else:
            # 在开发环境中，使用脚本目录推导项目根目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        
        # 定义可能的配置文件路径列表
        possible_config_paths = [
            # 1. 首先检查当前工作目录下的config文件夹
            os.path.join(os.getcwd(), "config", "setting.ini"),
            # 2. 检查基础目录下的config文件夹
            os.path.join(base_dir, "config", "setting.ini"),
            # 3. 检查当前工作目录下的setting.ini
            os.path.join(os.getcwd(), "setting.ini"),
            # 4. 检查基础目录下的setting.ini
            os.path.join(base_dir, "setting.ini")
        ]
        
        # 遍历所有可能的路径，找到第一个存在的配置文件
        self.config_path = None
        for path in possible_config_paths:
            if os.path.exists(path):
                self.config_path = path
                break
        
        project_root = base_dir
        
        # 添加对None值的检查，避免TypeError
        if self.config_path is None or not os.path.exists(self.config_path):
            self.bHasConfig = False
            # 创建默认配置设置
            self.config = QC.QSettings()
        else:
            self.bHasConfig = True
            self.config = QC.QSettings(self.config_path, QC.QSettings.Format.IniFormat)
        self.current_directory = project_root
        self.path = project_root  # 添加缺失的path属性，用于线程参数

        self.setupUi(self)

        self.init_window()
        self.init_widget()

        listPulseCurrent = self.get_config("BatteryConfig/PulseCurrent")
        listCutoffVoltage = self.get_config("BatteryConfig/CutoffVoltage")
        self.listCurrentLevel = [int(listPulseCurrent[c].strip()) for c in range(len(listPulseCurrent))]
        self.listVoltageLevel = [float(listCutoffVoltage[c].strip()) for c in range(len(listCutoffVoltage))]

    def get_config(self, strValue):
        # 获取配置值并处理为列表格式，移除所有DEBUG打印以避免UI卡死
        # 如果没有配置文件，直接返回空列表
        if not self.bHasConfig:
            return []
        
        try:
            value = self.config.value(strValue)
            if type(value) == list:
                listValue = []
                for v in range(len(value)):
                    if value[v] != "":
                        listValue.append(value[v])
            elif type(value) == str:
                listValue = [value]
            else:
                listValue = []
            return listValue
        except Exception as e:
            print(f"读取配置 {strValue} 失败: {e}")
            return []                    

    def init_window(self) -> None:
        # 在窗口标题中显示应用程序名称和版本号
        self.setWindowTitle(f"battery-analyzer v{self.version}")
        # 使用配置目录下的图标文件
        try:
            # 使用实际存在的ico图标文件
            icon_path = os.path.join(self.current_directory, "config", "resources", "icons", "Icon_BatteryTestGUI.ico")
            if os.path.exists(icon_path):
                icon = QG.QIcon(icon_path)
            else:
                # 如果文件不存在，使用默认图标
                icon = QG.QIcon()
        except Exception:
            # 捕获所有异常，确保应用能正常启动
            icon = QG.QIcon()
        
        self.setWindowIcon(icon)

    def init_widget(self) -> None:
        if self.bHasConfig:
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
        self.config.setValue("TestInformation/DataProcessingPlatforms", f"BatteryAnalysis-DataConverter_V{self.version}.exe")
        # 移除固定列宽设置，改为在resizeEvent中按比例分配
        # 确保表格的最后一列自动拉伸
        self.tableWidget_TestInformation.horizontalHeader().setStretchLastSection(True)

        def setSpanItem(_strItem: str, _intRow: int, _intCol: int, _intRowLengthDown: int = 1, _intColLengthRight: int = 1, _bEditable: bool = False) -> None:
            # 只有当跨度大于1时才调用setSpan，避免单个单元格跨度的警告
            if _intRowLengthDown > 1 or _intColLengthRight > 1:
                self.tableWidget_TestInformation.setSpan(_intRow, _intCol, _intRowLengthDown, _intColLengthRight)
            _item = QW.QTableWidgetItem(_strItem)
            if not _bEditable:
                _item.setFlags(QC.Qt.ItemFlag.ItemIsEnabled)
                _item.setBackground(QG.QBrush(QG.QColor(242, 242, 242)))
            self.tableWidget_TestInformation.setItem(_intRow, _intCol, _item)

        setSpanItem("Test Equipment", 0, 0, 1, 2)
        setSpanItem("", 0, 2, _bEditable=True)

        setSpanItem("Software Versions", 1, 0, 3, 1)
        setSpanItem("BTS Server Version", 1, 1)
        setSpanItem("BTS Client Version", 2, 1)
        setSpanItem("TSDA (Data Analysis) Version", 3, 1)
        setSpanItem("", 1, 2, _bEditable=True)
        setSpanItem("", 2, 2, _bEditable=True)
        setSpanItem("", 3, 2, _bEditable=True)

        setSpanItem("Middle Machines", 4, 0, 5, 1)
        setSpanItem("Model", 4, 1)
        setSpanItem("Hardware Version", 5, 1)
        setSpanItem("Serial Number", 6, 1)
        setSpanItem("Firmware Version", 7, 1)
        setSpanItem("Device Type", 8, 1)
        setSpanItem("", 4, 2, _bEditable=True)
        setSpanItem("", 5, 2, _bEditable=True)
        setSpanItem("", 6, 2, _bEditable=True)
        setSpanItem("", 7, 2, _bEditable=True)
        setSpanItem("", 8, 2, _bEditable=True)

        setSpanItem("Test Units", 9, 0, 3, 1)
        setSpanItem("Model", 9, 1)
        setSpanItem("Hardware Version", 10, 1)
        setSpanItem("Firmware Version", 11, 1)
        setSpanItem("", 9, 2, _bEditable=True)
        setSpanItem("", 9, 3, _bEditable=True)
        setSpanItem("", 10, 2, _bEditable=True)
        setSpanItem("", 11, 2, _bEditable=True)

        setSpanItem("Data Processing Platforms", 12, 0, 1, 2)
        setSpanItem(self.get_config("TestInformation/DataProcessingPlatforms")[0], 12, 2, _bEditable=True)
        setSpanItem("Reported By", 13, 0, 1, 2)
        setSpanItem(self.get_config("TestInformation/ReportedBy")[0], 13, 2, _bEditable=True)

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
        self.checkerBatteryType.clear()
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
                if self.strSpecificationType == self.comboBox_Specification_Type.itemText(t):
                    self.comboBox_Specification_Type.setCurrentIndex(t)
                    break
        elif self.comboBox_BatteryType.currentText() == "Pouch Cell":
            self.comboBox_ConstructionMethod.setEnabled(True)
            for c in range(self.comboBox_ConstructionMethod.count()):
                if self.strConstructionMethod == self.comboBox_ConstructionMethod.itemText(c):
                    self.comboBox_ConstructionMethod.setCurrentIndex(c)
                    self.strConstructionMethod = ""
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
            self.checkerBatteryType.setError(f"No battery type named {self.comboBox_BatteryType.currentText()}")
            self.statusBar_BatteryAnalysis.showMessage(f"[Error]: No battery type named {self.comboBox_BatteryType.currentText()}")

    def check_specification(self) -> None:
        self.strSpecificationType = self.comboBox_Specification_Type.currentText()
        listSpecificationTypeCoinCell = self.get_config("BatteryConfig/SpecificationTypeCoinCell")
        listSpecificationTypePouchCell = self.get_config("BatteryConfig/SpecificationTypePouchCell")
        for c in range(len(listSpecificationTypeCoinCell)):
            if self.strSpecificationType == listSpecificationTypeCoinCell[c]:
                self.comboBox_BatteryType.setCurrentIndex(0)
        for p in range(len(listSpecificationTypePouchCell)):
            if self.strSpecificationType == listSpecificationTypePouchCell[p]:
                self.comboBox_BatteryType.setCurrentIndex(1)
            
        specification_method = self.comboBox_Specification_Method.currentText()
        if self.strSpecificationType == "" or specification_method == "":
            return

        setRule = self.get_config("BatteryConfig/Rules")
        for r in range(len(setRule)):
            listRule = list(setRule[r].split("/"))
            if listRule[0] == self.strSpecificationType:
                if specification_method == listRule[1]:
                    self.lineEdit_DatasheetNominalCapacity.setText(f"{listRule[2]}")
                    self.lineEdit_CalculationNominalCapacity.setText(f"{listRule[3]}")
                    listRequiredUseableCapacityPercentage = re.findall(r"(\d+)%", listRule[4])
                    if listRequiredUseableCapacityPercentage != [] and len(listRequiredUseableCapacityPercentage) == 1:
                        self.lineEdit_RequiredUseableCapacity.setText(f"{int(int(listRule[3])*int(listRequiredUseableCapacityPercentage[0])/100)}")
                    else:
                        self.lineEdit_RequiredUseableCapacity.setText(f"{listRule[4]}")
                else:
                    self.lineEdit_DatasheetNominalCapacity.setText("")
                    self.lineEdit_CalculationNominalCapacity.setText("")
                    self.lineEdit_RequiredUseableCapacity.setText("")
                break
            elif listRule[0] in self.strSpecificationType:
                if specification_method == listRule[1]:
                    self.lineEdit_DatasheetNominalCapacity.setText(f"{listRule[2]}")
                    self.lineEdit_CalculationNominalCapacity.setText(f"{listRule[3]}")
                    listRequiredUseableCapacityPercentage = re.findall(r"(\d+)%", listRule[4])
                    if listRequiredUseableCapacityPercentage != [] and len(listRequiredUseableCapacityPercentage) == 1:
                        self.lineEdit_RequiredUseableCapacity.setText(f"{int(int(listRule[3])*int(listRequiredUseableCapacityPercentage[0])/100)}")
                    else:
                        self.lineEdit_RequiredUseableCapacity.setText(f"{listRule[4]}")
                else:
                    self.lineEdit_DatasheetNominalCapacity.setText("")
                    self.lineEdit_CalculationNominalCapacity.setText("")
                    self.lineEdit_RequiredUseableCapacity.setText("")
            else:
                pass

    def set_table(self) -> None:
        self.checkerTable.clear()
        # 不再重新创建QSettings实例，而是重新读取配置
        # 这样可以确保使用与初始化时相同的配置文件路径和设置
        self.config.sync()  # 确保配置文件被正确加载
        
        # DEBUG: 打印set_table方法中的配置读取信息
        
        
        listTestInformation = []
        listChildGroups = self.config.childGroups()
        
        for c in range(len(listChildGroups)):
            if "TestInformation." in listChildGroups[c]:
                listTestInformation.append(listChildGroups[c])

        if len(listTestInformation) == 0:
            self.checkerTable.setError("No TestInformation in setting.ini")
            self.statusBar_BatteryAnalysis.showMessage("[Error]: No TestInformation in setting.ini")
            return

        self.strTestInformation = ""
        for t in range(len(listTestInformation)):
            listTestInformationSplit = listTestInformation[t].split(".")
            if not len(listTestInformationSplit) == 3:
                self.checkerTable.setError(f"Wrong TestInformation section format:[{listTestInformation[t]}] in setting.ini")
                self.statusBar_BatteryAnalysis.showMessage(f"[Error]: Wrong TestInformation section format:[{listTestInformation[t]}] in setting.ini")
                return
            else:
                strLocation = listTestInformationSplit[1]
                strLaboratory = listTestInformationSplit[2]
                strTesterLocation = self.comboBox_TesterLocation.currentText().replace(" ", "")
                if (strLaboratory in strTesterLocation) and (strLocation in strTesterLocation):
                    self.strTestInformation = listTestInformation[t]
                    break

        if self.strTestInformation == "":
            self.checkerTable.setError("Can't find matched TestInformation section in setting.ini")
            self.statusBar_BatteryAnalysis.showMessage("[Error]: Can't find matched TestInformation section in setting.ini")
            return

        def setItem(_Item, _intRow: int, _intCol: int) -> None:
            _strItem = ""
            for i in range(len(_Item)):
                _strItem = _strItem + _Item[i] + ", "
            _strItem = _strItem[:-2]
            _qtItem = QW.QTableWidgetItem(_strItem)
            self.tableWidget_TestInformation.setItem(_intRow, _intCol, _qtItem)

        setItem(self.get_config(f"{self.strTestInformation}/TestEquipment"), 0, 2)
        setItem(self.get_config(f"{self.strTestInformation}/SoftwareVersions.BTSServerVersion"), 1, 2)
        setItem(self.get_config(f"{self.strTestInformation}/SoftwareVersions.BTSClientVersion"), 2, 2)
        setItem(self.get_config(f"{self.strTestInformation}/SoftwareVersions.BTSDAVersion"), 3, 2)
        setItem(self.get_config(f"{self.strTestInformation}/MiddleMachines.Model"), 4, 2)
        setItem(self.get_config(f"{self.strTestInformation}/MiddleMachines.HardwareVersion"), 5, 2)
        setItem(self.get_config(f"{self.strTestInformation}/MiddleMachines.SerialNumber"), 6, 2)
        setItem(self.get_config(f"{self.strTestInformation}/MiddleMachines.FirmwareVersion"), 7, 2)
        setItem(self.get_config(f"{self.strTestInformation}/MiddleMachines.DeviceType"), 8, 2)
        setItem(self.get_config(f"{self.strTestInformation}/TestUnits.Model"), 9, 2)
        setItem(self.get_config(f"{self.strTestInformation}/TestUnits.HardwareVersion"), 10, 2)
        setItem(self.get_config(f"{self.strTestInformation}/TestUnits.FirmwareVersion"), 11, 2)

    def get_xlsxinfo(self) -> None:
        self.checkerInputXlsx.clear()
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
                self.strConstructionMethod = ""
                for c in range(self.comboBox_ConstructionMethod.count()):
                    if self.comboBox_ConstructionMethod.itemText(c) in strSampleInputXlsxTitle:
                        self.strConstructionMethod = self.comboBox_ConstructionMethod.itemText(c)
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

                self.strCCCurrent = ""
                listCCCurrentToSplit = re.findall(r"mA,(.*?)\)", strSampleInputXlsxTitle)
                if len(listCCCurrentToSplit) == 1:
                    strCCCurrentToSplit = listCCCurrentToSplit[0].replace("mAh", "")
                    listCCCurrentToSplit = re.findall(r"([\d.]+)mA", strCCCurrentToSplit)
                    if len(listCCCurrentToSplit) >= 1:
                        self.strCCCurrent = listCCCurrentToSplit[-1]
                self.lineEdit_SamplesQty.setText(str(len(listAllInXlsx)))
            else:
                self.checkerInputXlsx.setError("Input path has no data")
                self.statusBar_BatteryAnalysis.showMessage("[Error]: Input path has no data")

    def get_version(self) -> None:
        strInPutDir = self.lineEdit_InputPath.text()
        strOutoutDir = self.lineEdit_OutputPath.text()
        if os.path.exists(strInPutDir) and os.path.exists(strOutoutDir):
            listAllInXlsx = [strInPutDir + f"/{f}" for f in os.listdir(strInPutDir) if f[:2] != "~$" and f[-5:] == ".xlsx"]
            if len(listAllInXlsx) == 0:
                self.lineEdit_Version.setText("")
                return
            strCsvMd5Path = strOutoutDir + "/MD5.csv"
            self.strMd5Checksum = calc_md5checksum(listAllInXlsx)
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
                    csvMD5Writer.writerow([self.strMd5Checksum])
                    csvMD5Writer.writerow(["Times:"])
                    csvMD5Writer.writerow(["0"])
                    self.lineEdit_Version.setText("1.0")
                else:
                    intVersionMajor = 1
                    intVersionMinor = 0
                    for c in range(len(listChecksum)):
                        if self.strMd5Checksum == listChecksum[c]:
                            intVersionMajor = c + 1
                            intVersionMinor = int(listTimes[c])
                            # increase it after executing the whole program
                            break
                        if c == len(listChecksum) - 1:
                            intVersionMajor = c + 2
                            listChecksum.append(self.strMd5Checksum)
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
                csvMD5Writer.writerow([self.strMd5Checksum])
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
        if self.checkerBatteryType.bCheckPass and self.checkerTable.bCheckPass and self.checkerInputXlsx.bCheckPass:
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
                    if self.checkerUpdateConfig.bCheckPass:
                        self.strMd5ChecksumRun = self.strMd5Checksum
                        self.statusBar_BatteryAnalysis.showMessage("status:ok")
                        self.thread.start()     
        else:
            self.statusBar_BatteryAnalysis.showMessage(f"[Error]: {self.checkerBatteryType.strErrorMsg} {self.checkerTable.strErrorMsg} {self.checkerInputXlsx.strErrorMsg}")
            self.pushButton_Run.setText("Rerun")
            self.pushButton_Run.setFocus()

    def save_table(self) -> None:
        # set focus on pushButton_Run for saving the input text
        self.pushButton_Run.setFocus()

        def setItem(_strConfig: str, _intRow: int, _intCol: int):
            listItemText = self.tableWidget_TestInformation.item(_intRow, _intCol).text().split(",")
            for i in range(len(listItemText)):
                listItemText[i] = listItemText[i].strip()
            if len(listItemText) == 1:
                self.config.setValue(f"{_strConfig}", listItemText[0])
            else:
                self.config.setValue(f"{_strConfig}", listItemText)

        if self.strTestInformation != "":
            setItem(f"{self.strTestInformation}/TestEquipment", 0, 2)
            setItem(f"{self.strTestInformation}/SoftwareVersions.BTSServerVersion", 1, 2)
            setItem(f"{self.strTestInformation}/SoftwareVersions.BTSClientVersion", 2, 2)
            setItem(f"{self.strTestInformation}/SoftwareVersions.BTSDAVersion", 3, 2)
            setItem(f"{self.strTestInformation}/MiddleMachines.Model", 4, 2)
            setItem(f"{self.strTestInformation}/MiddleMachines.HardwareVersion", 5, 2)
            setItem(f"{self.strTestInformation}/MiddleMachines.SerialNumber", 6, 2)
            setItem(f"{self.strTestInformation}/MiddleMachines.FirmwareVersion", 7, 2)
            setItem(f"{self.strTestInformation}/MiddleMachines.DeviceType", 8, 2)
            setItem(f"{self.strTestInformation}/TestUnits.Model", 9, 2)
            setItem(f"{self.strTestInformation}/TestUnits.HardwareVersion", 10, 2)
            setItem(f"{self.strTestInformation}/TestUnits.FirmwareVersion", 11, 2)

        setItem("TestInformation/TestEquipment", 0, 2)
        setItem("TestInformation/SoftwareVersions.BTSServerVersion", 1, 2)
        setItem("TestInformation/SoftwareVersions.BTSClientVersion", 2, 2)
        setItem("TestInformation/SoftwareVersions.BTSDAVersion", 3, 2)
        setItem("TestInformation/MiddleMachines.Model", 4, 2)
        setItem("TestInformation/MiddleMachines.HardwareVersion", 5, 2)
        setItem("TestInformation/MiddleMachines.SerialNumber", 6, 2)
        setItem("TestInformation/MiddleMachines.FirmwareVersion", 7, 2)
        setItem("TestInformation/MiddleMachines.DeviceType", 8, 2)
        setItem("TestInformation/TestUnits.Model", 9, 2)
        setItem("TestInformation/TestUnits.HardwareVersion", 10, 2)
        setItem("TestInformation/TestUnits.FirmwareVersion", 11, 2)
        setItem("TestInformation/ReportedBy", 13, 2)

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
        listMD5Reader = []
        f = open(self.lineEdit_OutputPath.text() + "/MD5.csv", mode='r', encoding='utf-8')
        csvMD5Reader = csv.reader(f)
        for row in csvMD5Reader:
            listMD5Reader.append(row)
        f.close()
        [_, listChecksum, _, listTimes] = listMD5Reader

        os.remove(self.lineEdit_OutputPath.text() + "/MD5.csv")
        f = open(self.lineEdit_OutputPath.text() + "/MD5.csv", mode='w', newline='', encoding='utf-8')
        csvMD5Writer = csv.writer(f)
        for c in range(len(listChecksum)):
            if self.strMd5ChecksumRun == listChecksum[c]:
                intVersionMajor = c + 1
                intVersionMinor = int(listTimes[c]) + 1
                listTimes[c] = str(intVersionMinor)
                if self.strMd5ChecksumRun == self.strMd5Checksum:
                    self.lineEdit_Version.setText(f"{intVersionMajor}.{intVersionMinor}")
                break
        csvMD5Writer.writerow(["Checksums:"])
        csvMD5Writer.writerow(listChecksum)
        csvMD5Writer.writerow(["Times:"])
        csvMD5Writer.writerow(listTimes)
        f.close()
        win32api.SetFileAttributes(self.lineEdit_OutputPath.text() + "/MD5.csv", win32con.FILE_ATTRIBUTE_HIDDEN)

    def rename_pltPath(self, strTestDate):
        self.config.setValue("PltConfig/Path", f"{self.lineEdit_OutputPath.text()}/{strTestDate}_V{self.lineEdit_Version.text()}")

    def update_config(self, test_info) -> None:
        self.checkerUpdateConfig.clear()
        self.config.setValue("PltConfig/Path", f"{self.lineEdit_OutputPath.text()}/V{test_info[16]}")

        bSetTitle = False
        setRule = self.get_config("BatteryConfig/Rules")
        specification_type = self.comboBox_Specification_Type.currentText()
        strPulseCurrent = ""
        for c in range(len(self.listCurrentLevel)):
            strPulseCurrent += f"{self.listCurrentLevel[c]}mA/"
        for r in range(len(setRule)):
            listRule = list(setRule[r].split("/"))
            if self.strCCCurrent == "":
                self.strCCCurrent = listRule[5]
            if listRule[0] == specification_type:
                self.config.setValue("PltConfig/Title", f"{test_info[4]} {test_info[2]} {test_info[3]}({test_info[5]}), -{test_info[8]}mAh@{self.strCCCurrent}mA, {strPulseCurrent[:-1]}, {test_info[7]}")
                bSetTitle = True
                break
            elif listRule[0] in specification_type:
                self.config.setValue("PltConfig/Title", f"{test_info[4]} {test_info[2]} {test_info[3]}({test_info[5]}), -{test_info[8]}mAh@{self.strCCCurrent}mA, {strPulseCurrent[:-1]}, {test_info[7]}")
                bSetTitle = True
            else:
                pass
        if not bSetTitle:
            self.checkerUpdateConfig.setError("PltTitle")
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
                print(self.strErrorXlsx)
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
                        print(f"启动ImageMaker: {exe_path}")
                        try:
                            # 使用CREATE_NEW_CONSOLE标志启动，以便新窗口中运行
                            subprocess.run(exe_path, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                            exe_executed = True
                            break
                        except Exception as e:
                            print(f"启动失败 {exe_path}: {e}")
                            continue
                
                if not exe_executed:
                    print("警告: 未找到battery-analysis-visualizer可执行文件")
                    print("候选路径:")
                    for path in exe_candidates:
                        print(f"  - {path}: {'存在' if os.path.exists(path) else '不存在'}")
        else:
            print(self.strErrorBattery)
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
    matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    
    app = QW.QApplication(sys.argv)
    main = Main()
    # 移除固定窗口大小，允许自由调整
    main.setMinimumSize(970, 885)  # 设置最小尺寸以确保UI元素正常显示
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
