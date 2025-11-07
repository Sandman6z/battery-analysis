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

import PyQt5.QtGui as QG
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

import win32api, win32con

from src.battery_analysis.ui import ui_main_window

from src.battery_analysis.utils import version
from src.battery_analysis.utils import file_writer
from src.battery_analysis.utils import battery_analysis


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

    def __init__(self, bBuild: bool) -> None:
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

        # 将传入的bBuild赋值给实例变量
        self.bBuild = bBuild
        if self.bBuild:
            self.path = os.path.dirname(sys.executable)
            if not os.path.exists(self.path + "/setting.ini"):
                self.bHasConfig = False
            else:
                self.bHasConfig = True
            self.config = QC.QSettings(self.path + "/setting.ini", QC.QSettings.IniFormat)
            self.current_directory = self.path
        else:
            self.path = os.path.dirname(os.path.abspath(__file__))
            # 向上三级目录到项目根目录，再访问config目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            grandparent_dir = os.path.dirname(parent_dir)
            great_grandparent_dir = os.path.dirname(grandparent_dir)
            project_root = great_grandparent_dir
            config_path = os.path.join(project_root, "config", "Config_BatteryAnalysis.ini")
            if not os.path.exists(config_path):
                self.bHasConfig = False
            else:
                self.bHasConfig = True
            # 使用UTF-8编码明确初始化QSettings，确保正确读取INI文件
            self.config = QC.QSettings(config_path, QC.QSettings.IniFormat)
            self.config.setIniCodec('UTF-8')
            self.current_directory = f"C:/Users/{os.getlogin()}/Desktop/"

        self.setupUi(self)

        self.init_window()
        self.init_widget()

        listPulseCurrent = self.get_config("BatteryConfig/PulseCurrent")
        listCutoffVoltage = self.get_config("BatteryConfig/CutoffVoltage")
        self.listCurrentLevel = [int(listPulseCurrent[c].strip()) for c in range(len(listPulseCurrent))]
        self.listVoltageLevel = [float(listCutoffVoltage[c].strip()) for c in range(len(listCutoffVoltage))]

    def get_config(self, strValue):
        # DEBUG: 打印尝试读取的配置路径
        print(f"DEBUG: 尝试读取配置路径: {strValue}")
        
        listValue = []
        value = self.config.value(strValue)
        
        # DEBUG: 打印原始值及类型
        print(f"DEBUG: 读取到的原始值: {value}, 类型: {type(value)}")
        
        # 特别处理TestInformation相关的配置路径
        if "TestInformation" in strValue:
            print(f"DEBUG: 正在读取TestInformation相关配置: {strValue}")
            # 检查配置文件中是否存在该section
            parts = strValue.split('/')
            if len(parts) >= 1:
                section = parts[0]
                # 列出所有可用的sections
                all_sections = self.config.childGroups()
                print(f"DEBUG: 可用的sections: {all_sections}")
                if section in all_sections:
                    print(f"DEBUG: Section {section} 存在于配置文件中")
                    # 列出该section下的所有keys
                    self.config.beginGroup(section)
                    all_keys = self.config.allKeys()
                    self.config.endGroup()
                    print(f"DEBUG: {section} 下的可用keys: {all_keys}")
                else:
                    print(f"DEBUG: Section {section} 不存在于配置文件中")
        
        if type(value) == list:
            for v in range(len(value)):
                if value[v] != "":
                    listValue.append(value[v])
        elif type(value) == str:
            listValue = [value]
        else:
            pass
        
        # DEBUG: 打印处理后的返回值
        print(f"DEBUG: 处理后的返回值: {listValue}")
        return listValue                    

    def init_window(self) -> None:
        self.setWindowTitle("BatteryAnalysis-DataConverter")
        Icon_BatteryAnalysis = "AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAADs7Oz/7ezs/+zs7P/s7Oz/7ezs/+zs7P/t7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/t7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+3s7P/s7Oz/7Ozs/+3s7P/s7Oz/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7ezs/+3s7P/s7Oz/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7ezs/+zs7P/s7Oz/7Ozs/+3s7P/s7Oz/7Ozs/+zs7P/s7Oz/7ezs/+3s7P/s7Oz/7Ozs/+zs7P/t7Oz/7Ozs/+zs7P/t7Oz/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/6+vr/+rq6v/q6ur/6urq/+vr6//s7Oz/7Ozs/+zs7P/t7Oz/7Ozs/+zs7P/s7Oz/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+3s7P/s7Oz/7Ozs/+3s7P/s6+v/6urp/+7u7v/19fb/+fn6//r6+//39/j/8/Pz/+3t7f/q6en/7Ovr/+3s7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/t7e3/6urq//Dw8P/6+vv/5eTk/8TDwP+urKj/pqOf/7e1sv/Qz87/6+vr//j4+f/u7u7/6+rq/+3s7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7ezt/+rq6v/19fb/4eDg/5CMh/92cmr/hIF6/5WSjP+dmpX/U01E/0Q+NP9kX1b/nJmU/+fn5v/z8/P/6urq/+vq6v/q6ur/6urq/+rq6v/q6ur/6urq/+vr6//s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/q6ur/9fX2/8rJxv9rZ17/qKWh/+bm5f/8/P3///////////+FgXr/Qjwx/zs1Kf84MSb/YVxT/9bV0//19fX/9PT0//X19f/19fX/9fX1//X19f/19fb/8PDw/+vr6//t7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ovr//Dw8P/e3dz/bGhf/9fW1f//////9PT1/9fW1P/Bv7z/ube0/7WzsP+wrqr/mpeS/2VgV/83MSX/Yl1V/93c2//Dwb//xMK//8TCwP/EwsD/xMPA/8LAvf/d3Nv/8fDx/+vr6//s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/q6ur/+vv8/52alf+tq6f//////6CdmP9qZV3/ZmJZ/3JtZv91cWn/dHBo/21oYP9ybmb/k5CK/3x4cf8/OS7/nJmU/1dRSP9AOi7/RD80/0Q+M/9FPzX/Pjgt/1tWTf/i4uH/7+/v/+zr6//s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+rq6v/4+Pn/mpeR/66sqP9uaWH/aWVc/7++u//n5ub/9fX1///////09PX/5ubl/727uP9va2P/ZmJZ/01HPf+Wk43/bWlh/0Q+M/9NRz3/TEY8/0pEOv+JhX//S0Y8/83Lyf/z8/T/6+vr/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/6unp//j4+f+hn5r/PTYr/46Lhf/7+/z/9fX2/+7u7v/j4+L/rqyo/+Xk5P/t7e3/9fX2//n5+v+Pi4X/NzAl/5uYk/9rZl7/Qz0y/0tGPP9LRTv/R0I3/5yZlP9TTUT/zs3L//Pz8//r6+v/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/q6un/+vr7/5aTjv9XUkj/9PT1/+zs7P/r6ur/+fn6/9ra2f9KRDn/397e//j5+f/r6ur/7e3t//Ly8v9XUkn/k5CK/2xoX/9DPTL/S0Y7/0tFO/9HQjf/mJWP/1FMQv/Ozcv/8/P0/+vr6//s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+rp6f/7+/z/k5CK/3Vxaf/4+Pn/7u7u/8/Ny/9vamL/bGhg/1FLQf9taGD/cGxk/9PR0P/u7u7/9vb3/29qYv+Rjoj/bGhg/0M9Mv9LRjv/S0U7/0dCN/+ZlpD/UUxC/87Ny//z8/T/6+vr/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/6+rq//X29v/Avrv/UEpA/+np6f/19fX/397d/8jHxf+ysK3/SUQ5/7WzsP/HxsT/4N/f//b29//i4eD/Uk1D/6+tqf9UTkX/SEM4/0tFO/9LRTv/R0I3/5mWkP9RTEL/zs3L//Pz8//r6+v/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/6+vr//b29v+Cf3j/aGNb/+jn5//9/f7//////+no6P95dW7/7Ozs///////8/f7/4N/f/2FdVP+Vko3/jYmD/z03LP9LRTv/SUQ5/0tFO/9HQjf/mZaQ/1FMQv/Ozcv/8/Pz/+vr6//s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7e3t//Pz8/+TkIr/YFtS/5eVj//EwsD/29rZ/+Tj4//Z2Nf/wb+8/5aSjf9nY1r/npuW/52alf9FPzX/Tkk//01IPv9LRjz/SkU6/0dCN/+ZlpD/UUxC/87Ny//z8/T/6+vr/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s6+z/7Ozs//n6+//W1dT/mJWP/3p2bv9zb2f/cm1l/3Vxav+Cfnf/k4+K/6ekoP92cmr/tLKu/+Pi4v/Z2Nf/4uHh/7+9uv9JQzj/R0I3/5mWkf9RTEL/zs3L//Pz9P/r6+v/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/6urq//Ly8v/7+/z/9fb2/+rq6v/s7Oz/19bV/3t3cP9nYln/RkA2/z85Lv9pZFz/cm1l/29rYv9ybWX/Z2Ja/0pEOv9HQjf/mZaQ/1FMQv/Ozcv/8/P0/+vr6//s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/6+vr/+rp6f/r6ur/6+vr//X19v/Lycf/PTcr/0U/NP9LRjv/TEc8/0Q+M/9BPDH/Qjwx/0I8Mf9EPjP/S0U7/0dBN/+ZlpD/UUxC/87Ny//z8/T/6+vr/+zs7P/t7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/r6ur/8/Pz/83Lyf9JQzn/S0Y7/0pFOv9KRTr/S0Y7/0xGPP9MRjz/TEY8/0tGO/9LRTv/R0I3/5mWkf9RTEL/zs3L//Pz9P/r6+v/7Ozs/+3s7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+vr6v/z8/T/zMvJ/0dCN/9MRz3/TUc9/01HPf9NRz3/TEc9/01HPf9NRz3/TUc9/01IPv9KRDr/mZeR/1FMQv/Ozcv/8/P0/+vr6//s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/6+vq//Pz9P/Ny8r/SEI4/0E7MP8+OC3/Pjgt/z44Lf8+OC3/Pjgt/z44Lf8+OC3/Pzku/zo0Kf+Vko3/U01E/87Ny//z8/T/6+vr/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/r6+v/9PT0/8vKyP9IQjf/h4N9/5aTjf+QjYf/ko+K/5SRi/+UkIv/lJGL/5KPif+QjYf/lZKN/7a0sP9NRz3/zs3L//Pz9P/r6+v/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+vr6//y8vP/09LQ/0E7MP9eWVD/dHBp/3h0bf9ybmb/a2de/2xoYP9rZ17/cm5m/3h0bf91cWn/V1JI/0I9Mv/X1tX/8fHy/+vr6//s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/v7+//qqik/4SBev9jXlX/OjQo/19aUf+Ggnz/gHx1/4aCfP9eWU//OjQp/2RfVv+Ggnv/rqyo//Dw8P/s7Ov/7Ozs/+zs7P/s7Oz/7Ozs/+3s7P/s7Oz/7ezs/+3s7P/s7Oz/7ezs/+3s7P/t7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+3s7P/z8/P//////52alf8nIBP/lZGM///////z8/T//////4+Mhv8nIBT/oJ2Y///////z8/P/7Ozs/+3s7P/s7Oz/7ezs/+3s7P/s7Oz/7Ozs/+zs7P/t7Oz/7Ozs/+zs7P/t7Oz/7ezs/+3s7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+no6P/x8fL/u7m2/3RwaP+3tbH/8fHy/+fm5v/x8fL/tLKu/3RwaP+9u7j/8fHx/+no6P/s7Oz/7Ozs/+zs7P/s7Oz/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+3s7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7ezs/+zr6//y8vL/+Pj5//Ly8//s6+v/7e3t/+zs6//z8/P/+Pj5//Ly8v/s6+v/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+3s7P/s7Oz/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7ezs/+vr6//q6un/6+vr/+3s7P/s7Oz/7ezt/+vr6//q6ur/6+vr/+3s7P/s7Oz/7Ozs/+3s7P/t7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7ezs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+3s7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+3s7P/s7Oz/7Ozs/+zs7P/t7Oz/7Ozs/+zs7P/s7Oz/7Ozs/+zs7P/t7Oz/7Ozs/+zs7P/s7Oz/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        Logo = QG.QPixmap()
        Logo.loadFromData(base64.b64decode(Icon_BatteryAnalysis))
        icon = QG.QIcon()
        icon.addPixmap(Logo, QG.QIcon.Normal, QG.QIcon.Off)
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
        reg = QC.QRegExp("^\d*$")
        validator = QG.QRegExpValidator(self)
        validator.setRegExp(reg)
        # self.lineEdit_BatchDateCode.setValidator(validator)
        self.lineEdit_SamplesQty.setValidator(validator)
        # self.lineEdit_Temperature.setValidator(validator)
        self.lineEdit_DatasheetNominalCapacity.setValidator(validator)
        self.lineEdit_CalculationNominalCapacity.setValidator(validator)
        self.lineEdit_RequiredUseableCapacity.setValidator(validator)
        self.lineEdit_AcceleratedAging.setValidator(validator)

        reg = QC.QRegExp("^\d+(\.\d+)?$")
        validator = QG.QRegExpValidator(self)
        validator.setRegExp(reg)
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
            self.tableWidget_TestInformation.setSpan(_intRow, _intCol, _intRowLengthDown, _intColLengthRight)
            _item = QW.QTableWidgetItem(_strItem)
            if not _bEditable:
                _item.setFlags(QC.Qt.ItemIsEnabled)
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
                    listRequiredUseableCapacityPercentage = re.findall("(\d+)%", listRule[4])
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
                    listRequiredUseableCapacityPercentage = re.findall("(\d+)%", listRule[4])
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
                listPulseCurrentToSplit = re.findall("\(([\d.]+[-\d.]+)mA", strSampleInputXlsxTitle)
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
                listCCCurrentToSplit = re.findall("mA,(.*?)\)", strSampleInputXlsxTitle)
                if len(listCCCurrentToSplit) == 1:
                    strCCCurrentToSplit = listCCCurrentToSplit[0].replace("mAh", "")
                    listCCCurrentToSplit = re.findall("([\d.]+)mA", strCCCurrentToSplit)
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
            self.current_directory = self.current_directory + "/../"

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
                        self.lineEdit_AcceleratedAging.text(),
                        self.comboBox_TesterLocation.currentText(),
                        self.comboBox_TestedBy.currentText(),
                        self.lineEdit_TestProfile.text(),
                        self.listCurrentLevel,
                        self.listVoltageLevel,
                        self.lineEdit_Version.text(),
                        self.lineEdit_RequiredUseableCapacity.text()
                    ]
                    self.thread.get_info(self.path, self.lineEdit_InputPath.text(), self.lineEdit_OutputPath.text(), test_info, self.bBuild)
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
        if self.lineEdit_AcceleratedAging.text() == "":
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

    def get_info(self, strPath, strInputPath, strOutputPath, listTestInfo, bBuild) -> None:
        self.strPath = strPath
        self.strInputPath = strInputPath
        self.strOutputPath = strOutputPath
        self.listTestInfo = listTestInfo
        self.bBuild = bBuild

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
                    if self.bBuild:
                        # 获取构建类型和版本信息
                        # 优先使用可执行文件所在目录，而不是输出目录
                        import sys
                        exe_dir = os.path.dirname(sys.executable)
                        build_type = "Debug" if "Debug" in exe_dir else "Release"
                        version = "1.0.0"
                        
                        # 尝试在可执行文件所在目录查找ImageMaker
                        exe_path = os.path.join(exe_dir, f"BatteryTest-ImageMaker_{build_type}_{version.replace('.', '_')}.exe")
                        
                        if os.path.exists(exe_path):
                            subprocess.run(exe_path, shell=True)
                        else:
                            print(f"可执行文件不存在: {exe_path}")
                            # 如果找不到带版本的文件，尝试不带版本的名称
                            fallback_path = os.path.join(exe_dir, "BatteryTest-ImageMaker.exe")
                            if os.path.exists(fallback_path):
                                subprocess.run(fallback_path, shell=True)
                            else:
                                print(f"可执行文件不存在: {fallback_path}")
                                # 最后尝试在当前strPath中查找（保持原有逻辑作为备份）
                                exe_path_backup = os.path.join(self.strPath, f"BatteryTest-ImageMaker_{build_type}_{version.replace('.', '_')}.exe")
                                if os.path.exists(exe_path_backup):
                                    subprocess.run(exe_path_backup, shell=True)
                                else:
                                    fallback_path_backup = os.path.join(self.strPath, "BatteryTest-ImageMaker.exe")
                                    if os.path.exists(fallback_path_backup):
                                        subprocess.run(fallback_path_backup, shell=True)
                    else:
                        # 使用python -m方式调用，确保模块路径正确
                        os.system("python -m src.battery_analysis.main.image_show")
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
    if os.path.exists(f"{os.path.dirname(os.path.abspath(__file__))}/main_window.py"):
        bBuild = False
    else:
        bBuild = True
    app = QW.QApplication(sys.argv)
    main = Main(bBuild)
    # 移除固定窗口大小，允许自由调整
    main.setMinimumSize(970, 885)  # 设置最小尺寸以确保UI元素正常显示
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
