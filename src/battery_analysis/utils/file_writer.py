import os
import csv
import sys
import json
import math
import datetime
import traceback
import configparser
import logging

# 设置Matplotlib使用非交互式后端，避免线程安全问题
import matplotlib
matplotlib.use('Agg')  # 使用Agg后端，不会启动GUI

import numpy as np
import xlsxwriter as xwt
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from openpyxl.utils import get_column_letter

from docx import Document
from docx.enum.dml import MSO_THEME_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_LINE_SPACING
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm

from src.battery_analysis.utils.exception_type import BatteryAnalysisException


class XlsxWordWriter:
    def __init__(self, strResultPath: str, listTestInfo: list, listBatteryInfo: list) -> None:
        # get config
        self.config = configparser.ConfigParser()
        
        # 改进配置文件路径查找逻辑，支持开发环境和exe环境
        config_path = None
        
        # 确定基础目录（区分exe环境和开发环境）
        if getattr(sys, 'frozen', False):  # exe环境
            base_dir = os.path.dirname(sys.executable)
        else:  # 开发环境
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))
        
        # 定义可能的配置文件路径列表
        possible_config_paths = [
            # 1. 当前工作目录下的config目录
            os.path.join(os.getcwd(), "config", "setting.ini"),
            # 2. 基础目录下的config目录
            os.path.join(base_dir, "config", "setting.ini"),
            # 3. 当前工作目录下直接查找
            os.path.join(os.getcwd(), "setting.ini"),
            # 4. 基础目录下直接查找
            os.path.join(base_dir, "setting.ini")
        ]
        
        # 遍历查找第一个存在的配置文件
        for path in possible_config_paths:
            if os.path.exists(path):
                config_path = path
                print(f"找到配置文件: {config_path}")
                break
        
        # 尝试读取配置文件
        if config_path and os.path.exists(config_path):
            self.config.read(config_path, encoding='utf-8')
        else:
            print("警告: 找不到配置文件，尝试了以下路径:")
            for path in possible_config_paths:
                print(f"  - {path}")
            # 创建默认的PltConfig部分
            self.config.add_section("PltConfig")
            self.config.set("PltConfig", "Title", "\"默认标题\"")
            # 创建默认的TestInformation部分
            self.config.add_section("TestInformation")
        
        # 安全获取PltConfig/Title，添加默认值处理
        try:
            if self.config.has_section("PltConfig") and self.config.has_option("PltConfig", "Title"):
                strImageTitle = self.config.get("PltConfig", "Title")[1:-1]
            else:
                # 使用测试信息生成默认标题
                strImageTitle = f"{listTestInfo[4]} {listTestInfo[2]} {listTestInfo[3]}({listTestInfo[5]}), 默认标题"
        except Exception as e:
            print(f"获取标题时出错: {e}")
            strImageTitle = "默认电池分析图标题"

        # init variables for all files
        self.listTestInfo = listTestInfo
        self.listBatteryInfo = listBatteryInfo
        try:
            [sy, sm, sd] = self.listBatteryInfo[2][0].split(" ")[0].split("-")
            td = f"{sy}{sm}{sd}"
        except ValueError:
            td = "00000000"
        self.strResultPath = f"{strResultPath}/{td}_V{listTestInfo[16]}"

        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.intCurrentLevelNum = len(self.listCurrentLevel)
        self.intVoltageLevelNum = len(self.listVoltageLevel)
        self.strFileCurrentType = ""
        for c in range(self.intCurrentLevelNum):
            self.strFileCurrentType = self.strFileCurrentType + f"{self.listCurrentLevel[c]}-"
        self.strFileCurrentType = self.strFileCurrentType[:-1]

        self.listBatteryCharge = self.listBatteryInfo[0]
        self.listBatteryName = self.listBatteryInfo[1]
        self.intBatteryNum = len(self.listBatteryName)

        # init variables for plt
        self.listBoxplotTitle = []
        self.listPngPath = []
        self.listSvgPath = []
        if len(strImageTitle) <= 70:
            strBoxplotTitle = strImageTitle
        else:
            strSplit = "A, "
            strBoxplotTitle = strImageTitle.split(strSplit)[0] + strSplit + "\n" + strImageTitle.split(strSplit)[1] + strSplit + strImageTitle.split(strSplit)[2]
        for b in range(self.intCurrentLevelNum):
            self.listBoxplotTitle.append(f"Useable Capacity over Cutoff Voltage, {self.listCurrentLevel[b]}mA Load\n{strBoxplotTitle}")
            self.listPngPath.append(f"{self.strResultPath}/Image_UseableCapacityOverCutoffVoltage{self.listCurrentLevel[b]}mALoad.png")
            self.listSvgPath.append(f"{self.strResultPath}/Image_UseableCapacityOverCutoffVoltage{self.listCurrentLevel[b]}mALoad.svg")
        self.strUnfilteredPngPath = f"{self.strResultPath}/Image_UnfilteredLoadVoltageOverCharge.png"
        self.strUnfilteredSvgPath = f"{self.strResultPath}/Image_UnfilteredLoadVoltageOverCharge.svg"
        self.strFilteredPngPath = f"{self.strResultPath}/Image_FilteredLoadVoltageOverCharge.png"
        self.strFilteredSvgPath = f"{self.strResultPath}/Image_FilteredLoadVoltageOverCharge.svg"
        self.strPltName = f"Load Voltage over Charge\n{strImageTitle}"
        self.strInfoImageCsvPath = f"{self.strResultPath}/Info_Image.csv"
        self.listPltColorType = ['#DF7040', '#0675BE', '#EDB120', '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']
        self.listColorName = ["red = ", "blue = ", "yellow = ", "violet = ", "green = ", "orange = ", "black1 = ", "black2 = "]
        strStrF = ""
        for c in range(self.intCurrentLevelNum):
            strStrF += f"{self.listColorName[c]}{self.listCurrentLevel[c]}mA, "
        strStrF = strStrF[:-2]

        # init variables for excel
        self.strResultXlsxPath = f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}_{self.strFileCurrentType}_{self.listTestInfo[7]}.xlsx"
        self.strSampleXlsxPath = f"{self.strResultPath}/Sample_{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}_{self.strFileCurrentType}_{self.listTestInfo[7]}.xlsx"

        # init variables for word
        if self.intCurrentLevelNum <= 4:
            self.strSampleReportWordPath = f"{self.strResultPath}/../../0_doc/Battery Measurement Report of TypeC TypeA_TypeD.docx"
        else:
            self.strSampleReportWordPath = f"{self.strResultPath}/../../0_doc/Battery Measurement Report of TypeC TypeA_TypeD_MP.docx"
            
        # strTimeStamp = datetime.datetime.now().strftime("%Y%m%d")

        # 使用pathlib.Path来规范化路径，避免出现../符号
        from pathlib import Path
        report_name = f"{self.listTestInfo[4]}_{self.listTestInfo[2]}_DC{self.listTestInfo[5]}_TD{td}_V{self.listTestInfo[16]}.docx"
        result_dir = Path(self.strResultPath).parent
        self.strReportWordPath = str(result_dir / report_name)
        self.listTextToReplace = ["TypeA", "TypeB", "TypeC", "TypeD", "TypeE", "TypeF", "TypeG", "StrA", "StrB", "StrC", "StrD", "StrF"]
        self.listImageToReplace = ["<<Image_FilteredLoadVoltageOverCharge>>"]
        for i in range(10):     # max 10 images to replace
            self.listImageToReplace.append(f"<<Image_UseableCapacityOverCutoffVoltage{i}>>")
            self.listImageToReplace.append(f"<<Title_UseableCapacityOverCutoffVoltage{i}>>")
        # 安全获取电池类型基础规格，添加默认值
        try:
            if self.config.has_section("BatteryConfig") and self.config.has_option("BatteryConfig", "SpecificationTypeBase"):
                listBatteryTypeBase = self.config.get("BatteryConfig", "SpecificationTypeBase").split(",")
            else:
                # 设置默认值
                listBatteryTypeBase = ["CoinCell", "ButtonCell", "Cylindrical", "Prismatic", "PouchCell"]
                print("警告: 使用默认电池类型基础规格")
                
            strBatteryType = ""
            for b in range(len(listBatteryTypeBase)):
                if listBatteryTypeBase[b].strip() in self.listTestInfo[2]:
                    strBatteryType = listBatteryTypeBase[b]
                    break
            
            # 如果没有匹配到，使用列表中的第一个或直接使用测试信息
            if strBatteryType == "":
                if listBatteryTypeBase:
                    strBatteryType = listBatteryTypeBase[0]
                    print(f"警告: 未找到精确匹配的电池类型，使用默认值: {strBatteryType}")
                else:
                    strBatteryType = self.listTestInfo[2]  # 直接使用测试信息中的类型
                    print(f"警告: 电池类型列表为空，直接使用测试信息: {strBatteryType}")
        except Exception as e:
            print(f"获取电池类型时出错: {e}")
            strBatteryType = self.listTestInfo[2]  # 出错时使用测试信息中的类型
        self.listTestInfoForReplace = [self.listTestInfo[2], self.listTestInfo[3], self.listTestInfo[4],
                                       self.listTestInfo[5], self.listTestInfo[7], self.listTestInfo[11], strBatteryType,
                                       None, None, None, None, strStrF]

        # init variables for csv
        self.strResultCsvPath = f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}_{self.strFileCurrentType}_{self.listTestInfo[7]}.csv"

        # execute
        self.UXWW_XlsxWordCsvWrite()

    def UXWW_XlsxWordCsvWrite(self) -> None:
        # init excel writer
        wbResult = xwt.Workbook(self.strResultXlsxPath)
        wsOverview = wbResult.add_worksheet("overview")
        wsOverviewStatisticalStartLine = 13
        wsResult = wbResult.add_worksheet("result")
        wbSample = xwt.Workbook(self.strSampleXlsxPath)
        wsWord = wbSample.add_worksheet("word")
        wsExcel = wbSample.add_worksheet("excel")
        # init cxcel font format
        wsResultData = wbResult.add_format({
            'font_name': 'Microsoft YaHei',
            'font_size': 9,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter'
        })
        wsResultData_italic = wbResult.add_format({
            'font_name': 'Microsoft YaHei',
            'font_size': 9,
            'font_color': 'black',
            'italic': True,
            'bold': False,
            'align': 'center',
            'valign': 'vcenter'
        })
        wsOverviewStatistics = wbResult.add_format({
            'font_name': 'Arial Narrow',
            'font_size': 9,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': '#BFBFBF'
        })
        wsOverviewStatistics_bgdarkgray = wbResult.add_format({
            'font_name': 'Arial Narrow',
            'font_size': 12,
            'font_color': 'black',
            'bg_color': '#BFBFBF',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#BFBFBF'
        })
        wsOverviewStatistics_bglightgray = wbResult.add_format({
            'font_name': 'Arial Narrow',
            'font_size': 12,
            'font_color': 'black',
            'bg_color': '#F2F2F2',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#BFBFBF'
        })
        wsOverviewStatistics_bglightgray_blod = wbResult.add_format({
            'font_name': 'Arial Narrow',
            'font_size': 12,
            'font_color': 'black',
            'bg_color': '#F2F2F2',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#BFBFBF'
        })
        wsExcelLine = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': 'black'
        })
        wsExcelData = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })
        wsExcelData_bold = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })
        wsExcelData_percentage = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'num_format': '0%',
            'border': 1,
            'border_color': 'black'
        })
        wsExcelData_percentage_bold = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'num_format': '0%',
            'border': 1,
            'border_color': 'black',
        })
        wsExcelData_bgyellow = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black',
            'bg_color': '#FFFF00'
        })
        wsWordLine = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': 'black'
        })
        wsWordData = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })
        wsWordData_bold = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })
        wsWordData_percentage = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black',
            'num_format': '0%'
        })
        wsWordData_percentage_bold = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black',
            'num_format': '0%'
        })
        wsWordData_bgyellow = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': 'black',
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black',
            'bg_color': '#FFFF00'
        })
        wbSampleHyperlink = wbSample.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'font_color': '#0000FF',
            'underline': True,
            'bold': False,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'border_color': 'black'
        })

        # init excel function
        def WsSetCol(_WorkSheet, _intCol: int, _intLength: int, _intSize: int):
            _WorkSheet.set_column(_intCol, _intCol + _intLength - 1, _intSize)

        def WsResultWriteData(_intRow, _intCol, _strMessage, _format):
            if type(_strMessage) == int or type(_strMessage) == float:
                if not math.isnan(_strMessage) and _strMessage != 0:
                    wsResult.write(_intRow, _intCol, _strMessage, _format)
            else:
                wsResult.write(_intRow, _intCol, _strMessage, _format)

        def npMean(_listCpt):
            if len(_listCpt) > 0:
                return float(np.mean(_listCpt))
            else:
                return 0

        def npStd(_listCpt):
            if len(_listCpt) > 1:
                return float(np.std(_listCpt, ddof=1))
            else:
                return 0

        def npMax(_listCpt):
            if len(_listCpt) > 0:
                return float(np.max(_listCpt))
            else:
                return 0

        def npMin(_listCpt):
            if len(_listCpt) > 0:
                return float(np.min(_listCpt))
            else:
                return 0

        def npMed(_listCpt):
            if len(_listCpt) > 0:
                return float(np.median(_listCpt))
            else:
                return 0

        def Num2Letter(_intCol: int) -> str:
            return get_column_letter(_intCol + 1)

        # init word writer
        wdReport = Document(self.strSampleReportWordPath)

        # init word function
        def tableSetBgColor(_cell, _RGBColor: str) -> None:
            tc = _cell._tc
            tcPr = tc.get_or_add_tcPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:val'), 'pct100')
            shd.set(qn('w:fill'), f'{_RGBColor}')
            tcPr.append(shd)

        def GetItem(_strSection: str, _strItem: str, _intBlankspaceNum: int = 0) -> str:
            try:
                # 检查section是否存在
                if not self.config.has_section(_strSection):
                    print(f"警告: 配置中找不到section '{_strSection}'，返回空字符串")
                    return ""
                
                # 检查item是否存在
                if not self.config.has_option(_strSection, _strItem):
                    print(f"警告: 配置中找不到选项 '{_strItem}' in section '{_strSection}'，返回空字符串")
                    return ""
                
                # 获取值并处理
                _listItem = self.config.get(_strSection, _strItem).split(",")
                _strBlankSpace = " " * _intBlankspaceNum
                for _i in range(len(_listItem)):
                    _listItem[_i] = _listItem[_i].strip()
                _strValue = _listItem[0]
                for _i in range(1, len(_listItem)):
                    _strValue += f"\n{_strBlankSpace}{_listItem[_i]}"
                return _strValue
            except Exception as e:
                print(f"获取配置项 '{_strItem}' from section '{_strSection}'时出错: {e}")
                return ""

        def AddHyperlink(_pParagraph, _strUrl: str, _strText: str):
            # This gets access to the document.xml.rels file and gets a new relation id value
            _part = _pParagraph.part
            _rId = _part.relate_to(_strUrl, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

            # Create the w:hyperlink tag and add needed values
            _hyperlink = OxmlElement('w:hyperlink')
            _hyperlink.set(qn('r:id'), _rId, )

            # Create a w:r element
            _run = OxmlElement('w:r')

            # Create a new w:rPr element
            _rPr = OxmlElement('w:rPr')

            # Join all the xml elements together and add the required text to the w:r element
            _run.append(_rPr)
            _run.text = _strText
            _hyperlink.append(_run)

            # Create a new run
            _run = _pParagraph.add_run()

            # Set the new run format: hyperlink theme and underline
            _run._r.append(_hyperlink)
            _run.font.color.theme_color = MSO_THEME_COLOR_INDEX.HYPERLINK
            _run.font.underline = True

        # init csv writer
        f = open(self.strResultCsvPath, mode='w', newline='', encoding='utf-8')
        csvwriterResultCsvFile = csv.writer(f)

        def CsvWrite(_strMessage):
            if type(_strMessage) == str:
                _listTemp = [_strMessage]
                csvwriterResultCsvFile.writerow(_listTemp)
            elif type(_strMessage) == list:
                _listTemp = []
                for _i in range(len(_strMessage)):
                    if _strMessage[_i] != 0:
                        _listTemp.append(_strMessage[_i])
                    else:
                        _listTemp.append("")
                csvwriterResultCsvFile.writerow(_listTemp)
            else:
                raise BatteryAnalysisException("File: file_writer.py, Function:csv_write(_message), Error: Unknown _message type")

        # wbResult and csv write fixed part
        if wsOverview is None:
            raise BatteryAnalysisException(f"{self.strResultXlsxPath} sheet[overview] creation failed")
        wsOverview.write(0, 0, f"#BEGIN HEADER")
        wsOverview.write(1, 0, f"#PULSE DISCHARGE")
        wsOverview.write(2, 0, f"#BATTERY CHARACTERISTICS")
        wsOverview.write(3, 0, f"#Start Time: {self.listBatteryInfo[2][0]}")
        wsOverview.write(4, 0, f"#Start Time: {self.listBatteryInfo[2][1]}")
        wsOverview.write(5, 0, f"#Battery Type: {self.listTestInfo[2]} {self.listTestInfo[3]}")
        wsOverview.write(6, 0, f"#Battery Manufacturer: {self.listTestInfo[4]}")
        wsOverview.write(7, 0, f"#Battery Date Code: {self.listTestInfo[5]}")
        wsOverview.write(8, 0, f"#Temperature: {self.listTestInfo[6]}")
        wsOverview.write(9, 0, f"#Test Profile: {self.listTestInfo[13]}")
        wsOverview.write(10, 0, f"#Version: V1.0")
        wsOverview.write(11, 0, f"#END HEADER")
        CsvWrite(f"#BEGIN HEADER")
        CsvWrite(f"#PULSE DISCHARGE")
        CsvWrite(f"#BATTERY CHARACTERISTICS")
        CsvWrite(f"#Start Time: {self.listBatteryInfo[2][0]}")
        CsvWrite(f"#End Time: {self.listBatteryInfo[2][1]}")
        CsvWrite(f"#Battery Type: {self.listTestInfo[2]} {self.listTestInfo[3]}")
        CsvWrite(f"#Battery Manufacturer: {self.listTestInfo[4]}")
        CsvWrite(f"#Battery Date Code: {self.listTestInfo[5]}")
        CsvWrite(f"#Temperature: {self.listTestInfo[6]}")
        CsvWrite(f"#Test Profile: {self.listTestInfo[13]}")
        CsvWrite(f"#Version: V1.0")
        CsvWrite(f"#END HEADER")

        if wsResult is None:
            raise BatteryAnalysisException(f"{self.strResultXlsxPath} sheet[result] creation failed")
        WsSetCol(wsResult, 0, self.intCurrentLevelNum * (2 + self.intVoltageLevelNum) + 1, 10)
        WsSetCol(wsResult, 0, 1, 20)
        wsResult.write(2, 0, "Battery", wsResultData)
        wsResult.write(4 + self.intBatteryNum, 0, "Mean(\u03BC)", wsResultData_italic)
        wsResult.write(5 + self.intBatteryNum, 0, "Median", wsResultData_italic)
        wsResult.write(6 + self.intBatteryNum, 0, "Std. Var.(\u03C3)", wsResultData_italic)
        wsResult.write(7 + self.intBatteryNum, 0, "\u03BC-3\u03C3", wsResultData_italic)
        wsResult.write(8 + self.intBatteryNum, 0, "\u03BC-2\u03C3", wsResultData_italic)
        wsResult.write(9 + self.intBatteryNum, 0, "\u03BC+2\u03C3", wsResultData_italic)
        wsResult.write(10 + self.intBatteryNum, 0, "\u03BC+3\u03C3", wsResultData_italic)
        wsResult.write(11 + self.intBatteryNum, 0, "Minimum", wsResultData_italic)
        wsResult.write(12 + self.intBatteryNum, 0, "Maximum", wsResultData_italic)
        for c in range(self.intCurrentLevelNum):
            wsResult.write(1, 1 + c * (2 + self.intVoltageLevelNum), f"{self.listCurrentLevel[c]}mA", wsResultData)
            wsResult.merge_range(1, 2 + c * (2 + self.intVoltageLevelNum), 1, (c + 1) * (2 + self.intVoltageLevelNum) - 1, "Voltage", wsResultData)
            for v in range(self.intVoltageLevelNum):
                wsResult.write(2, 2 + c * (2 + self.intVoltageLevelNum) + v, f"{self.listVoltageLevel[v]}V", wsResultData)

        CsvWrite("")
        listCsvLine = [""]
        for c in range(self.intCurrentLevelNum):
            listCsvLine.append(f"{self.listCurrentLevel[c]}mA")
            listCsvLine.append("Voltage")
            for v in range(self.intVoltageLevelNum):
                listCsvLine.append("")
        CsvWrite(listCsvLine)
        listCsvLine = []
        for c in range(self.intCurrentLevelNum):
            listCsvLine.append("")
            listCsvLine.append("")
            for v in range(self.intVoltageLevelNum):
                listCsvLine.append(f"{self.listVoltageLevel[v]}V")
        listCsvLine[0] = "Battery"
        CsvWrite(listCsvLine)

        # wdReport write table Version History
        tableVersionHistory = wdReport.add_table(9, 4, style='Grid Table 4 Accent 3')
        for r in range(9):
            tableVersionHistory.rows[r].height = Cm(0.6)
            for c in range(4):
                if c < 4:
                    tableVersionHistory.cell(0, c).width = Cm(2.8)
                cell = tableVersionHistory.cell(r, c)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                cell.paragraphs[0].paragraph_format.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell.paragraphs[0].paragraph_format.line_spacing_rules = WD_LINE_SPACING.SINGLE
                cell.paragraphs[0].paragraph_format.space_after = Pt(0)
        tableVersionHistory.cell(0, 0).paragraphs[0].add_run("Date").font.size = Pt(10)
        tableVersionHistory.cell(0, 1).paragraphs[0].add_run("Version").font.size = Pt(10)
        tableVersionHistory.cell(0, 2).paragraphs[0].add_run("Editor").font.size = Pt(10)
        tableVersionHistory.cell(0, 3).paragraphs[0].add_run("Changes").font.size = Pt(10)
        tableVersionHistory.cell(1, 1).paragraphs[0].add_run("1.0").font.size = Pt(10)
        tableVersionHistory.cell(1, 3).paragraphs[0].add_run("Initial version").font.size = Pt(10)
        text = tableVersionHistory.cell(1, 0).paragraphs[0].add_run(datetime.datetime.now().strftime("%Y.%m.%d"))
        text.font.size = Pt(10)
        text.font.bold = False
        strReportedBy = GetItem("TestInformation", "ReportedBy")
        tableVersionHistory.cell(1, 2).paragraphs[0].add_run(f"{strReportedBy}").font.size = Pt(10)

        # wdReport write table Test Information
        tableTestInformation = wdReport.add_table(5, 2, style='Table Grid')
        tableTestInformation.cell(0, 1).width = Cm(10)
        for r in range(5):
            for c in range(2):
                cell = tableTestInformation.cell(r, c)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                cell.paragraphs[0].paragraph_format.alignment = WD_TABLE_ALIGNMENT.LEFT
                cell.paragraphs[0].paragraph_format.line_spacing_rules = WD_LINE_SPACING.SINGLE
                cell.paragraphs[0].paragraph_format.space_after = Pt(0)
        tableTestInformation.cell(0, 0).paragraphs[0].add_run("Test Equipment").font.size = Pt(10)
        tableTestInformation.cell(1, 0).paragraphs[0].add_run("Software Versions").font.size = Pt(10)
        tableTestInformation.cell(2, 0).paragraphs[0].add_run("Middle Machines").font.size = Pt(10)
        tableTestInformation.cell(3, 0).paragraphs[0].add_run("Test Units").font.size = Pt(10)
        tableTestInformation.cell(4, 0).paragraphs[0].add_run("Data Processing Platforms").font.size = Pt(10)

        strItemTestEquipment = GetItem("TestInformation", "TestEquipment")
        tableTestInformation.cell(0, 1).paragraphs[0].add_run(f"{strItemTestEquipment}").font.size = Pt(10)
        strItemSoftwareVersionsBTSServerVersion = GetItem("TestInformation", "SoftwareVersions.BTSServerVersion")
        strItemSoftwareVersionsBTSClientVersion = GetItem("TestInformation", "SoftwareVersions.BTSClientVersion")
        strItemSoftwareVersionsTSDAVersion = GetItem("TestInformation", "SoftwareVersions.BTSDAVersion")
        tableTestInformation.cell(1, 1).paragraphs[0].add_run(f"BTS Server Version: {strItemSoftwareVersionsBTSServerVersion}\n"
                                                              f"BTS Client Version: {strItemSoftwareVersionsBTSClientVersion}\n"
                                                              f"BTSDA (Data Analysis) Version: {strItemSoftwareVersionsTSDAVersion}").font.size = Pt(10)
        strItemMiddleMachinesModel = GetItem("TestInformation", "MiddleMachines.Model", 6)
        strItemMiddleMachinesHardwareVersion = GetItem("TestInformation", "MiddleMachines.HardwareVersion", 14)
        strItemMiddleMachinesSerialNumber = GetItem("TestInformation", "MiddleMachines.SerialNumber", 12)
        strItemMiddleMachinesFirmwareVersion = GetItem("TestInformation", "MiddleMachines.FirmwareVersion", 14)
        strItemMiddleMachinesDeviceType = GetItem("TestInformation", "MiddleMachines.DeviceType", 10)
        tableTestInformation.cell(2, 1).paragraphs[0].add_run(f"Model: {strItemMiddleMachinesModel}\n"
                                                              f"Hardware Version: {strItemMiddleMachinesHardwareVersion}\n"
                                                              f"Serial Number: {strItemMiddleMachinesSerialNumber}\n"
                                                              f"Firmware Version: {strItemMiddleMachinesFirmwareVersion}\n"
                                                              f"Device Type: {strItemMiddleMachinesDeviceType}").font.size = Pt(10)
        strItemTestUnitsModel = GetItem("TestInformation", "TestUnits.Model", 6)
        strItemTestUnitsHardwareVersion = GetItem("TestInformation", "TestUnits.HardwareVersion", 14)
        strItemTestUnitsFirmwareVersion = GetItem("TestInformation", "TestUnits.FirmwareVersion", 14)
        tableTestInformation.cell(3, 1).paragraphs[0].add_run(f"Model: {strItemTestUnitsModel}\n"
                                                              f"Hardware Version: {strItemTestUnitsHardwareVersion}\n"
                                                              f"Firmware Version: {strItemTestUnitsFirmwareVersion}").font.size = Pt(10)
        strItemDataProcessingPlatforms = GetItem("TestInformation", "DataProcessingPlatforms")
        tableTestInformation.cell(4, 1).paragraphs[0].add_run(f"{strItemDataProcessingPlatforms}").font.size = Pt(10)

        # wbResult and csv write analytical battery statistic
        for b in range(self.intBatteryNum):
            WsResultWriteData(3 + b, 0, self.listBatteryName[b], wsResultData)
            listCsvLine = []
            i = 0
            for c in range(self.intCurrentLevelNum):
                listCsvLine.append("")
                listCsvLine.append("")
                for v in range(self.intVoltageLevelNum):
                    listCsvLine.append(self.listBatteryCharge[b][i])
                    WsResultWriteData(3 + b, 2 + c * (2 + self.intVoltageLevelNum) + v, self.listBatteryCharge[b][i], wsResultData)
                    i += 1
            listCsvLine[0] = f"{self.listBatteryName[b]}"
            CsvWrite(listCsvLine)

        # init and fill listCpt for calculate
        listCpt = []
        for c in range(self.intCurrentLevelNum):
            listCpt.append([])
            for _ in range(self.intVoltageLevelNum):
                listCpt[c].append([])
        for b in range(self.intBatteryNum):
            i = 0
            for c in range(self.intCurrentLevelNum):
                for v in range(self.intVoltageLevelNum):
                    if self.listBatteryCharge[b][i] != 0:
                        listCpt[c][v].append(self.listBatteryCharge[b][i])
                    i += 1

        # draw boxplots
        self.UXWW_Draw(listCpt, int(self.listTestInfo[8]))

        # init list for calculate
        listMean = []
        listStd = []
        listMax = []
        listMin = []
        listMed = []
        listMM3S = []
        listMM2S = []
        listMP2S = []
        listMP3S = []
        for c in range(self.intCurrentLevelNum):
            listMean.append([])
            listMed.append([])
            listStd.append([])
            listMM3S.append([])
            listMM2S.append([])
            listMP2S.append([])
            listMP3S.append([])
            listMin.append([])
            listMax.append([])

        # calculate
        for c in range(self.intCurrentLevelNum):
            for v in range(self.intVoltageLevelNum):
                listMean[c].append(npMean(listCpt[c][v]))
                listMed[c].append(npMed(listCpt[c][v]))
                listStd[c].append(npStd(listCpt[c][v]))
                listMM3S[c].append(listMean[c][v] - 3 * listStd[c][v])
                listMM2S[c].append(listMean[c][v] - 2 * listStd[c][v])
                listMP2S[c].append(listMean[c][v] + 2 * listStd[c][v])
                listMP3S[c].append(listMean[c][v] + 3 * listStd[c][v])
                listMin[c].append(npMin(listCpt[c][v]))
                listMax[c].append(npMax(listCpt[c][v]))

        # wbResult and csv write calculated statistic
        listCsvName = ["Mean(\u03BC)", "Median", "Std. Var.(\u03C3)", "\u03BC-3\u03C3", "\u03BC-2\u03C3", "\u03BC+2\u03C3", "\u03BC+3\u03C3", "Minimum", "Maximum"]
        listCsvList = [listMean, listMed, listStd, listMM3S, listMM2S, listMP2S, listMP3S, listMin, listMax]
        CsvWrite("")
        for n in range(len(listCsvName)):
            listCsvLine = []
            for c in range(self.intCurrentLevelNum):
                listCsvLine.append("")
                listCsvLine.append("")
                for v in range(self.intVoltageLevelNum):
                    WsResultWriteData(4 + self.intBatteryNum, 2 + c * (2 + self.intVoltageLevelNum) + v, round(listMean[c][v], 5), wsResultData)
                    WsResultWriteData(5 + self.intBatteryNum, 2 + c * (2 + self.intVoltageLevelNum) + v, round(listMed[c][v], 5), wsResultData)
                    WsResultWriteData(6 + self.intBatteryNum, 2 + c * (2 + self.intVoltageLevelNum) + v, round(listStd[c][v], 5), wsResultData)
                    WsResultWriteData(7 + self.intBatteryNum, 2 + c * (2 + self.intVoltageLevelNum) + v, round(listMM3S[c][v], 5), wsResultData)
                    WsResultWriteData(8 + self.intBatteryNum, 2 + c * (2 + self.intVoltageLevelNum) + v, round(listMM2S[c][v], 5), wsResultData)
                    WsResultWriteData(9 + self.intBatteryNum, 2 + c * (2 + self.intVoltageLevelNum) + v, round(listMP2S[c][v], 5), wsResultData)
                    WsResultWriteData(10 + self.intBatteryNum, 2 + c * (2 + self.intVoltageLevelNum) + v, round(listMP3S[c][v], 5), wsResultData)
                    WsResultWriteData(11 + self.intBatteryNum, 2 + c * (2 + self.intVoltageLevelNum) + v, round(listMin[c][v], 5), wsResultData)
                    WsResultWriteData(12 + self.intBatteryNum, 2 + c * (2 + self.intVoltageLevelNum) + v, round(listMax[c][v], 5), wsResultData)
                    listCsvLine.append(round(listCsvList[n][c][v], 5))
            listCsvLine[0] = f"{listCsvName[n]}"
            CsvWrite(listCsvLine)

        for c in range(self.intCurrentLevelNum):
            wsResult.insert_image(14 + self.intBatteryNum, 1 + c * (2 + self.intVoltageLevelNum), self.listPngPath[c], {'x_scale': ((2 + self.intVoltageLevelNum) * 2 - 1) / 16, 'y_scale': ((2 + self.intVoltageLevelNum) * 2 - 1) / 16})

        tableStatisticalsResults = wdReport.add_table(self.intCurrentLevelNum + 1, self.intVoltageLevelNum + 1, style='Table Grid')
        for c in range(self.intCurrentLevelNum + 1):
            for v in range(self.intVoltageLevelNum + 1):
                cell = tableStatisticalsResults.cell(c, v)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                cell.paragraphs[0].paragraph_format.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell.paragraphs[0].paragraph_format.line_spacing_rules = WD_LINE_SPACING.SINGLE
                cell.paragraphs[0].paragraph_format.space_after = Pt(0)
                if c == 0 and v == 0:
                    tableStatisticalsResults.rows[c].height = Cm(0.7)
                    tableStatisticalsResults.cell(c, v).width = Cm(3.55)
                    text = cell.paragraphs[0].add_run("Statisticals\nResults")
                    text.font.size = Pt(12)
                    text.bold = True
                    tableSetBgColor(cell, '#BFBFBF')
                    wsOverview.set_row(wsOverviewStatisticalStartLine, 20)
                    wsOverview.set_column(v, v, 18)
                    wsOverview.write(wsOverviewStatisticalStartLine, v, "Statisticals Results", wsOverviewStatistics_bgdarkgray)
                elif c == 0 and v > 0:
                    tableStatisticalsResults.cell(c, v).width = Cm(3.55)
                    text1 = cell.paragraphs[0].add_run(f"Cut-off Voltage\n")
                    text1.font.size = Pt(12)
                    text2 = cell.paragraphs[0].add_run(f"{self.listVoltageLevel[v - 1]}V")
                    text2.font.bold = True
                    text2.font.size = Pt(12)
                    tableSetBgColor(cell, '#F2F2F2')
                    wsOverview.set_column(v, v, 18)
                    wsOverview.write_rich_string(wsOverviewStatisticalStartLine, v,
                                                 wsOverviewStatistics_bglightgray, "Cut-off Voltage ",
                                                 wsOverviewStatistics_bglightgray_blod, f"{self.listVoltageLevel[v - 1]}V",
                                                 wsOverviewStatistics_bglightgray)
                elif c > 0 and v == 0:
                    tableStatisticalsResults.rows[c].height = Cm(2.35)
                    text1 = cell.paragraphs[0].add_run(f"Pulse Current\n")
                    text1.font.size = Pt(12)
                    text2 = cell.paragraphs[0].add_run(f"{self.listCurrentLevel[c - 1]}mA")
                    text2.font.bold = True
                    text2.font.size = Pt(12)
                    tableSetBgColor(cell, '#F2F2F2')
                    wsOverview.set_row(wsOverviewStatisticalStartLine + c, 120)
                    wsOverview.write_rich_string(wsOverviewStatisticalStartLine + c, 0,
                                                 wsOverviewStatistics_bglightgray, "Pulse Current ",
                                                 wsOverviewStatistics_bglightgray_blod, f"{self.listCurrentLevel[c - 1]}mA",
                                                 wsOverviewStatistics_bglightgray)
                else:
                    text = cell.paragraphs[0].add_run(f"\u03BC: {round(listMean[c - 1][v - 1])}mAh\n"
                                                      f"Median: {round(listMed[c - 1][v - 1])}mAh\n"
                                                      f"\u03C3: {round(listStd[c - 1][v - 1])}mAh\n"
                                                      f"\u03BC - 3\u03C3: {round(listMM3S[c - 1][v - 1])}mAh\n"
                                                      f"\u03BC - 2\u03C3: {round(listMM2S[c - 1][v - 1])}mAh\n"
                                                      f"\u03BC + 2\u03C3: {round(listMP2S[c - 1][v - 1])}mAh\n"
                                                      f"\u03BC + 3\u03C3: {round(listMP3S[c - 1][v - 1])}mAh\n"
                                                      f"Minimum: {round(listMin[c - 1][v - 1])}mAh\n"
                                                      f"Maximum: {round(listMax[c - 1][v - 1])}mAh")
                    text.font.size = Pt(7)
                    cell.paragraphs[0].paragraph_format.line_spacing_rules = WD_LINE_SPACING.EXACTLY
                    cell.paragraphs[0].paragraph_format.line_spacing = Pt(10)
                    wsOverview.write(wsOverviewStatisticalStartLine + c, v, f"\u03BC: {round(listMean[c - 1][v - 1])}mAh\n"
                                                                            f"Median: {round(listMed[c - 1][v - 1])}mAh\n"
                                                                            f"\u03C3: {round(listStd[c - 1][v - 1])}mAh\n"
                                                                            f"\u03BC - 3\u03C3: {round(listMM3S[c - 1][v - 1])}mAh\n"
                                                                            f"\u03BC - 2\u03C3: {round(listMM2S[c - 1][v - 1])}mAh\n"
                                                                            f"\u03BC + 2\u03C3: {round(listMP2S[c - 1][v - 1])}mAh\n"
                                                                            f"\u03BC + 3\u03C3: {round(listMP3S[c - 1][v - 1])}mAh\n"
                                                                            f"Minimum: {round(listMin[c - 1][v - 1])}mAh\n"
                                                                            f"Maximum: {round(listMax[c - 1][v - 1])}mAh",
                                     wsOverviewStatistics)

        # wbSample write data
        if self.listTestInfo[0] == "Coin Cell":
            intTestProfileStartLine = 3
        elif self.listTestInfo[0] == "Pouch Cell":
            intTestProfileStartLine = 4
        else:
            raise BatteryAnalysisException("[Test Info Error]: listTestInfo[0] is a unknown battery type")
        WsSetCol(wsExcel, 0, 3, 12)
        WsSetCol(wsExcel, 3, 1, 20)
        WsSetCol(wsExcel, intTestProfileStartLine, 1, 12)
        WsSetCol(wsExcel, intTestProfileStartLine + 1, 1, 15)
        WsSetCol(wsExcel, intTestProfileStartLine + 2, 1, 10)
        WsSetCol(wsExcel, intTestProfileStartLine + 3, 1, 18)
        WsSetCol(wsExcel, intTestProfileStartLine + 4, 1, 25)
        WsSetCol(wsExcel, intTestProfileStartLine + 5, 2, 30)
        WsSetCol(wsExcel, intTestProfileStartLine + 7, 2, 15)
        intActualMeasuredCapacityLength = self.intVoltageLevelNum * 2
        WsSetCol(wsExcel, intTestProfileStartLine + 9, intActualMeasuredCapacityLength, 6)
        intTestDateStartCol = intTestProfileStartLine + 9 + intActualMeasuredCapacityLength
        WsSetCol(wsExcel, intTestDateStartCol, 1, 10)
        WsSetCol(wsExcel, intTestDateStartCol + 1, 1, 12)
        WsSetCol(wsExcel, intTestDateStartCol + 2, 1, 18)
        WsSetCol(wsExcel, intTestDateStartCol + 3, 1, 8)
        WsSetCol(wsExcel, intTestDateStartCol + 4, 2, 40)

        intPosiMaxmA = 0
        intPosi2V25 = 0
        intPresentmA = 0
        for c in range(self.intCurrentLevelNum):
            intPresentmA = self.listCurrentLevel[c]
            if self.listCurrentLevel[c] > intPresentmA:
                intPosiMaxmA = c
                break
        for v in range(self.intVoltageLevelNum):
            if self.listVoltageLevel[v] == 2.25:
                intPosi2V25 = v
                break

        listStrItems = [
            "Battery Type",  # 0
            "Specification",  # 1
            "Manufacturer",  # 2
            "Construction Method",  # 3
            "Test Profile",  # 4
            "Tester location",  # 5
            "Tested By",  # 6
            "Batch/Date Code",  # 7
            "Accelerated Aging[Years]",  # 8
            "Datasheet Nominal Capacity[mAh]",  # 9
            "Calculation Nominal Capacity[mAh]",  # 10
            "Required Useable Capacity[mAh]",  # 11
            None,  # 12
            f"Actual Measured Capacity[mAh]\n(at {self.listCurrentLevel[intPosiMaxmA]}mA/2.25V)",  # 13
            "Test Date",  # 14
            "Samples Qty",  # 15
            "Temperature[\u2103]",  # 16
            "Result",  # 17
            "Test Results File",  # 18
            "Remarks"  # 19
        ]

        try:
            strRelProfilePath = os.path.relpath(self.listTestInfo[13], os.path.dirname(self.strSampleXlsxPath))
        except ValueError:
            strRelProfilePath = self.listTestInfo[13]

        if self.listTestInfo[5] == "":
            strBatchDateCode = "n.a."
        else:
            strBatchDateCode = self.listTestInfo[5]

        intPassRate = float(int(self.listTestInfo[17])/int(self.listTestInfo[9]))
        strRequiredUseableCapacityPercentage = f"{int(100*int(self.listTestInfo[17])/int(self.listTestInfo[9]))}%"
        self.listTestInfoForReplace[9] = strRequiredUseableCapacityPercentage

        [sy, sm, sd] = self.listBatteryInfo[2][0].split(" ")[0].split("-")
        [ey, em, ed] = self.listBatteryInfo[2][1].split(" ")[0].split("-")

        strRelResultPath = os.path.relpath(self.strResultXlsxPath, os.path.dirname(self.strReportWordPath))
        if listMM2S[intPosiMaxmA][intPosi2V25] / int(self.listTestInfo[9]) >= intPassRate:
            strResult = "Pass"
            self.listTestInfoForReplace[8] = "meets"
            self.listTestInfoForReplace[10] = "Pass"
            strRemarks = "OK"
        else:
            strResult = "Fail"
            self.listTestInfoForReplace[8] = "doesn't meet"
            self.listTestInfoForReplace[10] = "Fail"
            strRemarks = f"The expected usable Q(stat) should be more than {strRequiredUseableCapacityPercentage}, " \
                         f"while the actual measured minimum capacity to 2.25V is " \
                         f"{math.floor(100 * listMM2S[intPosiMaxmA][intPosi2V25] / int(self.listTestInfo[9]))}%."
        self.listTestInfoForReplace[7] = f"{math.floor(100 * listMM2S[intPosiMaxmA][intPosi2V25] / int(self.listTestInfo[9]))}%"

        listStrContent = [
            self.listTestInfo[0],  # 0
            f"{self.listTestInfo[2]}-{self.listTestInfo[3]}",  # 1
            self.listTestInfo[4],  # 2
            self.listTestInfo[1],  # 3
            strRelProfilePath,  # 4
            self.listTestInfo[11],  # 5
            self.listTestInfo[12],  # 6
            strBatchDateCode,  # 7
            self.listTestInfo[10],  # 8
            self.listTestInfo[8],  # 9
            self.listTestInfo[9],  # 10
            self.listTestInfo[17],  # 11
            strRequiredUseableCapacityPercentage,  # 12
            None,  # 13
            f"{sd}.{sm}.{sy} - {ed}.{em}.{ey}",  # 14
            self.listTestInfo[6],  # 15
            self.listTestInfo[7],  # 16
            strResult,  # 17
            strRelResultPath,  # 18
            strRemarks  # 19
        ]

        wsExcel.merge_range(0, 0, 1, 0, listStrItems[0], wsExcelLine)
        wsExcel.merge_range(0, 1, 1, 1, listStrItems[1], wsExcelLine)
        wsExcel.merge_range(0, 2, 1, 2, listStrItems[2], wsExcelLine)
        wsExcel.merge_range(0, 3, 1, 3, listStrItems[3], wsExcelLine)
        if intTestProfileStartLine == 4:
            wsExcel.merge_range(0, intTestProfileStartLine, 1, intTestProfileStartLine, "", wsExcelLine)
        wsExcel.write(0, intTestProfileStartLine, listStrItems[4], wsExcelLine)
        wsExcel.merge_range(0, intTestProfileStartLine + 1, 1, intTestProfileStartLine + 1, listStrItems[5], wsExcelLine)
        wsExcel.merge_range(0, intTestProfileStartLine + 2, 1, intTestProfileStartLine + 2, listStrItems[6], wsExcelLine)
        wsExcel.merge_range(0, intTestProfileStartLine + 3, 1, intTestProfileStartLine + 3, listStrItems[7], wsExcelLine)
        wsExcel.merge_range(0, intTestProfileStartLine + 4, 1, intTestProfileStartLine + 4, listStrItems[8], wsExcelLine)
        wsExcel.merge_range(0, intTestProfileStartLine + 5, 1, intTestProfileStartLine + 5, listStrItems[9], wsExcelLine)
        wsExcel.merge_range(0, intTestProfileStartLine + 6, 1, intTestProfileStartLine + 6, listStrItems[10], wsExcelLine)
        wsExcel.merge_range(0, intTestProfileStartLine + 7, 1, intTestProfileStartLine + 8, listStrItems[11], wsExcelLine)
        wsExcel.merge_range(0, intTestProfileStartLine + 9, 0, intTestDateStartCol - 1, listStrItems[13], wsExcelLine)
        for v in range(self.intVoltageLevelNum):
            wsExcel.merge_range(1, intTestProfileStartLine + 9 + v * 2, 1, intTestProfileStartLine + 9 + v * 2 + 1, f"{self.listVoltageLevel[v]}V", wsExcelLine)
        wsExcel.merge_range(0, intTestDateStartCol, 1, intTestDateStartCol, listStrItems[14], wsExcelLine)
        wsExcel.merge_range(0, intTestDateStartCol + 1, 1, intTestDateStartCol + 1, listStrItems[15], wsExcelLine)
        wsExcel.merge_range(0, intTestDateStartCol + 2, 1, intTestDateStartCol + 2, listStrItems[16], wsExcelLine)
        wsExcel.merge_range(0, intTestDateStartCol + 3, 1, intTestDateStartCol + 3, listStrItems[17], wsExcelLine)
        wsExcel.merge_range(0, intTestDateStartCol + 4, 1, intTestDateStartCol + 4, listStrItems[18], wsExcelLine)
        wsExcel.merge_range(0, intTestDateStartCol + 5, 1, intTestDateStartCol + 5, listStrItems[19], wsExcelLine)

        wsExcel.write(2, 0, listStrContent[0], wsExcelData)
        wsExcel.write(2, 1, listStrContent[1], wsExcelData)
        wsExcel.write(2, 2, listStrContent[2], wsExcelData)
        wsExcel.write(2, 3, listStrContent[3], wsExcelData)
        if len(listStrContent[4].split("\\")) == 1:
            wsExcel.write(2, intTestProfileStartLine, listStrContent[4], wsExcelData)
        else:
            # 将相对路径转换为file:// URL格式
            url_path = listStrContent[4]
            # 确保路径使用正斜杠
            url_path = url_path.replace('\\', '/')
            # 添加file://前缀
            file_url = f'file:///{url_path}'
            wsExcel.write_url(2, intTestProfileStartLine, file_url, wbSampleHyperlink, string=listStrContent[4].split("\\")[-1])
        wsExcel.write(2, intTestProfileStartLine + 1, listStrContent[5], wsExcelData)
        wsExcel.write(2, intTestProfileStartLine + 2, listStrContent[6], wsExcelData)
        wsExcel.write(2, intTestProfileStartLine + 3, listStrContent[7], wsExcelData)
        wsExcel.write(2, intTestProfileStartLine + 4, listStrContent[8], wsExcelData)
        wsExcel.write(2, intTestProfileStartLine + 5, listStrContent[9], wsExcelData)
        wsExcel.write(2, intTestProfileStartLine + 6, listStrContent[10], wsExcelData)
        wsExcel.write(2, intTestProfileStartLine + 7, listStrContent[11], wsExcelData)
        wsExcel.write(2, intTestProfileStartLine + 8, listStrContent[12], wsExcelData)

        for v in range(self.intVoltageLevelNum):
            if v == intPosi2V25:
                wsExcel.write(2, intTestProfileStartLine + 9 + v * 2, f"{round(listMM2S[intPosiMaxmA][v], 2)}", wsExcelData_bold)
                wsExcel.write_formula(f"{Num2Letter(intTestProfileStartLine + 9 + v * 2 + 1)}3",
                                      f"=TRUNC({Num2Letter(intTestProfileStartLine + 9 + v * 2)}3/{Num2Letter(intTestProfileStartLine + 6)}3, 2)",
                                      wsExcelData_percentage_bold)
            else:
                wsExcel.write(2, intTestProfileStartLine + 9 + v * 2, f"{round(listMM2S[intPosiMaxmA][v], 2)}", wsExcelData)
                wsExcel.write_formula(f"{Num2Letter(intTestProfileStartLine + 9 + v * 2 + 1)}3",
                                      f"=TRUNC({Num2Letter(intTestProfileStartLine + 9 + v * 2)}3/{Num2Letter(intTestProfileStartLine + 6)}3, 2)",
                                      wsExcelData_percentage)

        wsExcel.write(2, intTestDateStartCol, listStrContent[14], wsExcelData)
        wsExcel.write(2, intTestDateStartCol + 1, listStrContent[15], wsExcelData)
        wsExcel.write(2, intTestDateStartCol + 2, listStrContent[16], wsExcelData)
        wsExcel.write(2, intTestDateStartCol + 3, listStrContent[17], wsExcelData_bgyellow)
        # 将相对路径转换为file:// URL格式
        url_path = listStrContent[18]
        # 确保路径使用正斜杠
        url_path = url_path.replace('\\', '/')
        # 添加file://前缀
        file_url = f'file:///{url_path}'
        wsExcel.write_url(2, intTestDateStartCol + 4, file_url, wbSampleHyperlink, string=listStrContent[18].split("\\")[-1])
        wsExcel.write(2, intTestDateStartCol + 5, listStrContent[19], wsExcelData)

        WsSetCol(wsWord, 0, 1, 30)
        WsSetCol(wsWord, 1, intActualMeasuredCapacityLength, 3)
        wsWord.write(0, 0, listStrItems[0], wsWordLine)
        wsWord.write(1, 0, listStrItems[1], wsWordLine)
        wsWord.write(2, 0, listStrItems[2], wsWordLine)
        wsWord.write(3, 0, listStrItems[3], wsWordLine)
        wsWord.write(intTestProfileStartLine, 0, listStrItems[4], wsWordLine)
        wsWord.write(intTestProfileStartLine + 1, 0, listStrItems[5], wsWordLine)
        wsWord.write(intTestProfileStartLine + 2, 0, listStrItems[6], wsWordLine)
        wsWord.write(intTestProfileStartLine + 3, 0, listStrItems[7], wsWordLine)
        wsWord.write(intTestProfileStartLine + 4, 0, listStrItems[8], wsWordLine)
        wsWord.write(intTestProfileStartLine + 5, 0, listStrItems[9], wsWordLine)
        wsWord.write(intTestProfileStartLine + 6, 0, listStrItems[10], wsWordLine)
        wsWord.write(intTestProfileStartLine + 7, 0, listStrItems[11], wsWordLine)
        wsWord.merge_range(intTestProfileStartLine + 8, 0, intTestProfileStartLine + 10, 0, listStrItems[13], wsWordLine)
        intTestDateStartRow = intTestProfileStartLine + 11
        wsWord.write(intTestDateStartRow, 0, listStrItems[14], wsWordLine)
        wsWord.write(intTestDateStartRow + 1, 0, listStrItems[15], wsWordLine)
        wsWord.write(intTestDateStartRow + 2, 0, listStrItems[16], wsWordLine)
        wsWord.write(intTestDateStartRow + 3, 0, listStrItems[17], wsWordLine)
        wsWord.write(intTestDateStartRow + 4, 0, listStrItems[18], wsWordLine)
        wsWord.write(intTestDateStartRow + 5, 0, listStrItems[19], wsWordLine)

        wsWord.merge_range(0, 1, 0, intActualMeasuredCapacityLength, listStrContent[0], wsWordData)
        wsWord.merge_range(1, 1, 1, intActualMeasuredCapacityLength, listStrContent[1], wsWordData)
        wsWord.merge_range(2, 1, 2, intActualMeasuredCapacityLength, listStrContent[2], wsWordData)
        wsWord.merge_range(3, 1, 3, intActualMeasuredCapacityLength, listStrContent[3], wsWordData)
        if intTestProfileStartLine == 4:
            wsWord.merge_range(intTestProfileStartLine, 1, intTestProfileStartLine, intActualMeasuredCapacityLength, "", wsWordData)
        if len(listStrContent[4].split("\\")) == 1:
            wsWord.write(intTestProfileStartLine, 1, listStrContent[4], wsWordData)
        else:
            # 将相对路径转换为file:// URL格式
            url_path = listStrContent[4]
            # 确保路径使用正斜杠
            url_path = url_path.replace('\\', '/')
            # 添加file://前缀
            file_url = f'file:///{url_path}'
            wsWord.write_url(intTestProfileStartLine, 1, file_url, wbSampleHyperlink, string=listStrContent[4].split("\\")[-1])
        wsWord.merge_range(intTestProfileStartLine + 1, 1, intTestProfileStartLine + 1, intActualMeasuredCapacityLength, listStrContent[5], wsWordData)
        wsWord.merge_range(intTestProfileStartLine + 2, 1, intTestProfileStartLine + 2, intActualMeasuredCapacityLength, listStrContent[6], wsWordData)
        wsWord.merge_range(intTestProfileStartLine + 3, 1, intTestProfileStartLine + 3, intActualMeasuredCapacityLength, listStrContent[7], wsWordData)
        wsWord.merge_range(intTestProfileStartLine + 4, 1, intTestProfileStartLine + 4, intActualMeasuredCapacityLength, listStrContent[8], wsWordData)
        wsWord.merge_range(intTestProfileStartLine + 5, 1, intTestProfileStartLine + 5, intActualMeasuredCapacityLength, listStrContent[9], wsWordData)
        wsWord.merge_range(intTestProfileStartLine + 6, 1, intTestProfileStartLine + 6, intActualMeasuredCapacityLength, listStrContent[10], wsWordData)
        wsWord.merge_range(intTestProfileStartLine + 7, 1, intTestProfileStartLine + 7, int(intActualMeasuredCapacityLength / 2), listStrContent[11], wsWordData)
        wsWord.merge_range(intTestProfileStartLine + 7, int(intActualMeasuredCapacityLength / 2) + 1, intTestProfileStartLine + 7, intActualMeasuredCapacityLength, listStrContent[12], wsWordData)
        for v in range(self.intVoltageLevelNum):
            if v == intPosi2V25:
                wsWord.merge_range(intTestProfileStartLine + 8, 1 + v * 2, intTestProfileStartLine + 8, 2 + v * 2, f"{self.listVoltageLevel[v]}V", wsWordData_bold)
                wsWord.merge_range(intTestProfileStartLine + 9, 1 + v * 2, intTestProfileStartLine + 9, 2 + v * 2, f"{round(listMM2S[intPosiMaxmA][v], 2)}", wsWordData_bold)
                wsWord.merge_range(intTestProfileStartLine + 10, 1 + v * 2, intTestProfileStartLine + 10, 2 + v * 2, "", wsWordData_bold)
                wsWord.write_formula(f"{Num2Letter(1 + v * 2)}{intTestProfileStartLine + 11}",
                                     f"=TRUNC({Num2Letter(1 + v * 2)}{intTestProfileStartLine + 10}/B{intTestProfileStartLine + 7}, 2)",
                                     wsWordData_percentage_bold)
            else:
                wsWord.merge_range(intTestProfileStartLine + 8, 1 + v * 2, intTestProfileStartLine + 8, 2 + v * 2, f"{self.listVoltageLevel[v]}V", wsWordData)
                wsWord.merge_range(intTestProfileStartLine + 9, 1 + v * 2, intTestProfileStartLine + 9, 2 + v * 2, f"{round(listMM2S[intPosiMaxmA][v], 2)}", wsWordData)
                wsWord.merge_range(intTestProfileStartLine + 10, 1 + v * 2, intTestProfileStartLine + 10, 2 + v * 2, "", wsWordData)
                wsWord.write_formula(f"{Num2Letter(1 + v * 2)}{intTestProfileStartLine + 11}",
                                     f"=TRUNC({Num2Letter(1 + v * 2)}{intTestProfileStartLine + 10}/B{intTestProfileStartLine + 7}, 2)",
                                     wsWordData_percentage)

        wsWord.merge_range(intTestDateStartRow, 1, intTestDateStartRow, intActualMeasuredCapacityLength, listStrContent[14], wsWordData)
        wsWord.merge_range(intTestDateStartRow + 1, 1, intTestDateStartRow + 1, intActualMeasuredCapacityLength, listStrContent[15], wsWordData)
        wsWord.merge_range(intTestDateStartRow + 2, 1, intTestDateStartRow + 2, intActualMeasuredCapacityLength, listStrContent[16], wsWordData)
        wsWord.merge_range(intTestDateStartRow + 3, 1, intTestDateStartRow + 3, intActualMeasuredCapacityLength, listStrContent[17], wsWordData_bgyellow)
        wsWord.merge_range(intTestDateStartRow + 4, 1, intTestDateStartRow + 4, intActualMeasuredCapacityLength, "", wsWordData)
        # 将相对路径转换为file:// URL格式
        url_path = strRelResultPath
        # 确保路径使用正斜杠
        url_path = url_path.replace('\\', '/')
        # 添加file://前缀
        file_url = f'file:///{url_path}'
        wsWord.write_url(intTestDateStartRow + 4, 1, file_url, wbSampleHyperlink, string=listStrContent[18].split("\\")[-1])
        wsWord.merge_range(intTestDateStartRow + 5, 1, intTestDateStartRow + 5, intActualMeasuredCapacityLength, listStrContent[19], wsWordData)

        # wdResult write table Overview
        tableOverview = wdReport.add_table(intTestDateStartRow + 6, 1 + self.intVoltageLevelNum * 2, style='Table Grid')
        for row in range(intTestDateStartRow + 6):
            tableOverview.rows[row].height = Cm(0.5)
            for col in range(1 + self.intVoltageLevelNum * 2):
                cell = tableOverview.cell(row, col)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                cell.paragraphs[0].paragraph_format.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell.paragraphs[0].paragraph_format.line_spacing_rules = WD_LINE_SPACING.SINGLE
                cell.paragraphs[0].paragraph_format.space_after = Pt(0)
                if row == intTestDateStartRow + 3:
                    tableSetBgColor(cell, '#FFFF00')

        # merge cell
        for row in range(intTestDateStartRow + 6):
            if row <= intTestProfileStartLine + 6 or row >= intTestDateStartRow:
                cell1 = tableOverview.cell(row, 1)
                for col in range(1, self.intVoltageLevelNum * 2):
                    cell2 = tableOverview.cell(row, col + 1)
                    cell1.merge(cell2)
            else:
                if row == intTestProfileStartLine + 7:
                    cell1 = tableOverview.cell(row, 1)
                    for col in range(1, self.intVoltageLevelNum):
                        cell2 = tableOverview.cell(row, col + 1)
                        cell1.merge(cell2)
                    cell1 = tableOverview.cell(row, 1 + self.intVoltageLevelNum)
                    for col in range(1 + self.intVoltageLevelNum, self.intVoltageLevelNum * 2):
                        cell2 = tableOverview.cell(row, col + 1)
                        cell1.merge(cell2)
                else:
                    for v in range(self.intVoltageLevelNum):
                        cell1 = tableOverview.cell(row, 1 + v * 2)
                        cell2 = tableOverview.cell(row, 2 + v * 2)
                        cell1.merge(cell2)

        cell1 = tableOverview.cell(intTestProfileStartLine + 8, 0)
        cell2 = tableOverview.cell(intTestProfileStartLine + 9, 0)
        cell1.merge(cell2)
        cell2 = tableOverview.cell(intTestProfileStartLine + 10, 0)
        cell1.merge(cell2)

        tableOverview.cell(0, 0).paragraphs[0].add_run(listStrItems[0])
        tableOverview.cell(1, 0).paragraphs[0].add_run(listStrItems[1])
        tableOverview.cell(2, 0).paragraphs[0].add_run(listStrItems[2])
        tableOverview.cell(3, 0).paragraphs[0].add_run(listStrItems[3])
        if intTestProfileStartLine == 3:
            tableOverview.cell(3, 0).paragraphs[0].text = tableOverview.cell(3, 0).paragraphs[0].text.replace(listStrItems[3], "")
        tableOverview.cell(intTestProfileStartLine, 0).paragraphs[0].add_run(listStrItems[4])
        tableOverview.cell(intTestProfileStartLine + 1, 0).paragraphs[0].add_run(listStrItems[5])
        tableOverview.cell(intTestProfileStartLine + 2, 0).paragraphs[0].add_run(listStrItems[6])
        tableOverview.cell(intTestProfileStartLine + 3, 0).paragraphs[0].add_run(listStrItems[7])
        tableOverview.cell(intTestProfileStartLine + 4, 0).paragraphs[0].add_run(listStrItems[8])
        tableOverview.cell(intTestProfileStartLine + 5, 0).paragraphs[0].add_run(listStrItems[9])
        tableOverview.cell(intTestProfileStartLine + 6, 0).paragraphs[0].add_run(listStrItems[10])
        tableOverview.cell(intTestProfileStartLine + 7, 0).paragraphs[0].add_run(listStrItems[11])
        tableOverview.cell(intTestProfileStartLine + 8, 0).paragraphs[0].add_run(listStrItems[13])
        tableOverview.cell(intTestDateStartRow, 0).paragraphs[0].add_run(listStrItems[14])
        tableOverview.cell(intTestDateStartRow + 1, 0).paragraphs[0].add_run(listStrItems[15])
        tableOverview.cell(intTestDateStartRow + 2, 0).paragraphs[0].add_run(listStrItems[16])
        tableOverview.cell(intTestDateStartRow + 3, 0).paragraphs[0].add_run(listStrItems[17])
        tableOverview.cell(intTestDateStartRow + 4, 0).paragraphs[0].add_run(listStrItems[18])
        tableOverview.cell(intTestDateStartRow + 5, 0).paragraphs[0].add_run(listStrItems[19])

        tableOverview.cell(0, 1).paragraphs[0].add_run(listStrContent[0])
        tableOverview.cell(1, 1).paragraphs[0].add_run(listStrContent[1])
        tableOverview.cell(2, 1).paragraphs[0].add_run(listStrContent[2])
        tableOverview.cell(3, 1).paragraphs[0].add_run(listStrContent[3])
        if intTestProfileStartLine == 3:
            tableOverview.cell(3, 1).paragraphs[0].text = tableOverview.cell(3, 1).paragraphs[0].text.replace(listStrContent[3], "")
        if len(listStrContent[4].split("\\")) == 1:
            tableOverview.cell(intTestProfileStartLine, 1).paragraphs[0].text = tableOverview.cell(intTestProfileStartLine, 1).paragraphs[0].text.replace("", listStrContent[4])
        else:
            AddHyperlink(tableOverview.cell(intTestProfileStartLine, 1).paragraphs[0], listStrContent[4], listStrContent[4].split("\\")[-1])
        tableOverview.cell(intTestProfileStartLine + 1, 1).paragraphs[0].add_run(listStrContent[5])
        tableOverview.cell(intTestProfileStartLine + 2, 1).paragraphs[0].add_run(listStrContent[6])
        tableOverview.cell(intTestProfileStartLine + 3, 1).paragraphs[0].add_run(listStrContent[7])
        tableOverview.cell(intTestProfileStartLine + 4, 1).paragraphs[0].add_run(listStrContent[8])
        tableOverview.cell(intTestProfileStartLine + 5, 1).paragraphs[0].add_run(listStrContent[9])
        tableOverview.cell(intTestProfileStartLine + 6, 1).paragraphs[0].add_run(listStrContent[10])
        tableOverview.cell(intTestProfileStartLine + 7, 1).paragraphs[0].add_run(listStrContent[11])
        tableOverview.cell(intTestProfileStartLine + 7, 1 + self.intVoltageLevelNum).paragraphs[0].add_run(listStrContent[12])
        for v in range(self.intVoltageLevelNum):
            text1 = tableOverview.cell(intTestProfileStartLine + 8, 1 + v * 2).paragraphs[0].add_run(f"{self.listVoltageLevel[v]}V")
            text2 = tableOverview.cell(intTestProfileStartLine + 9, 1 + v * 2).paragraphs[0].add_run(f"{round(listMM2S[intPosiMaxmA][v], 2)}")
            text3 = tableOverview.cell(intTestProfileStartLine + 10, 1 + v * 2).paragraphs[0].add_run(f"{math.floor(100 * listMM2S[intPosiMaxmA][v] / int(listStrContent[10]))}%")
            if v == intPosi2V25:
                text1.font.bold = True
                text2.font.bold = True
                text3.font.bold = True
        tableOverview.cell(intTestDateStartRow, 1).paragraphs[0].add_run(listStrContent[14])
        tableOverview.cell(intTestDateStartRow + 1, 1).paragraphs[0].add_run(listStrContent[15])
        tableOverview.cell(intTestDateStartRow + 2, 1).paragraphs[0].add_run(listStrContent[16])
        tableOverview.cell(intTestDateStartRow + 3, 1).paragraphs[0].add_run(listStrContent[17])
        AddHyperlink(tableOverview.cell(intTestDateStartRow + 4, 1).paragraphs[0], listStrContent[18], listStrContent[18].split("\\")[-1])
        tableOverview.cell(intTestDateStartRow + 5, 1).paragraphs[0].add_run(listStrContent[19])

        for row in range(intTestDateStartRow + 6):
            for col in range(1 + self.intVoltageLevelNum * 2):
                cell = tableOverview.cell(row, col)
                runs = cell.paragraphs[0].runs
                for run in runs:
                    run.font.size = Pt(9)
        tableOverview.cell(0, 0).width = Cm(27)

        # wdResult replace TypeA-TypeF, StrA-StrF and Image
        for paragraph in wdReport.paragraphs:
            for t in range(len(self.listTextToReplace)):
                if self.listTextToReplace[t] in paragraph.text:
                    if self.listTextToReplace[t] == "StrD":
                        paragraph.text = paragraph.text.replace(self.listTextToReplace[t], "")
                        text = paragraph.add_run(f"{self.listTestInfoForReplace[t]}")
                        text.font.bold = True
                        paragraph.add_run(".")
                    else:
                        paragraph.text = paragraph.text.replace(self.listTextToReplace[t], f"{self.listTestInfoForReplace[t]}")
            for i in range(len(self.listImageToReplace)):
                if self.listImageToReplace[i] in paragraph.text:
                    paragraph.text = paragraph.text.replace(self.listImageToReplace[i], "")
                    if i < 2 * len(self.listPngPath) + 1:
                        if i == 0:
                            paragraph.add_run("").add_picture(self.strFilteredPngPath, width=Cm(15))
                        elif i % 2 == 1:
                            paragraph.add_run("").add_picture(self.listPngPath[int((i - 1) / 2)], width=Cm(7.2))
                        else:
                            paragraph.add_run(f"Figure {int(i / 2 + 1)}  {self.listTestInfoForReplace[2]} {self.listTestInfoForReplace[0]}-{self.listTestInfoForReplace[1]} Boxplot, {self.listCurrentLevel[int(i / 2 - 1)]}mA")
                    else:
                        paragraph._element.getparent().remove(paragraph._element)   

        # add table Overview, Version History, Test Information and Statisticals Results
        bInsertOverview = False
        bInsertVersionHistory = False
        bInsertTestInformation = False
        bInsertStatisticalsResults = False
        intStepOut = 0
        for paragraph in wdReport.paragraphs:
            if "Battery Quality Test / Alternative Battery Test for ESL Batteries" in paragraph.text:
                bInsertOverview = True
                intStepOut = 4
            elif "Version history" in paragraph.text and "Heading 2" == paragraph.style.name:
                bInsertVersionHistory = True
                intStepOut = 0
            elif "Test Information" in paragraph.text and "Heading 1" == paragraph.style.name:
                bInsertTestInformation = True
                intStepOut = 0
            elif "Test results" in paragraph.text and "Heading 1" == paragraph.style.name:
                bInsertStatisticalsResults = True
                intStepOut = 2
            else:
                pass
            if intStepOut:
                intStepOut = intStepOut - 1
            else:
                if bInsertOverview:
                    bInsertOverview = False
                    paragraph._p.addnext(tableOverview._tbl)
                elif bInsertVersionHistory:
                    bInsertVersionHistory = False
                    paragraph._p.addnext(tableVersionHistory._tbl)
                elif bInsertTestInformation:
                    bInsertTestInformation = False
                    paragraph._p.addnext(tableTestInformation._tbl)
                elif bInsertStatisticalsResults:
                    bInsertStatisticalsResults = False
                    paragraph._p.addnext(tableStatisticalsResults._tbl)
                else:
                    pass

        # if "Room Temperature", delete "℃"
        for paragraph in wdReport.paragraphs:
            if listStrContent[16] == "Room Temperature" and "\u2103" in paragraph.text:
                paragraph.text = paragraph.text.replace(paragraph.text, paragraph.text.replace("\u2103", ""))

        # close xlsx writer
        wbResult.close()
        wbSample.close()
        # close word writer
        wdReport.save(self.strReportWordPath)
        # 输出docx文件的完整路径到日志
        logging.info(f"数据分析完成，生成的docx报告路径: {self.strReportWordPath}")
        # close csv writer
        f.close()

    def UXWW_Draw(self, _listCpt: list, maxXaxis: int) -> None:
        fontdictLabel = {
            'fontsize': 9,
            'fontweight': 'bold'
        }
        medianprofile = dict(linewidth=1, color='red')

        plt.figure()

        for c in range(self.intCurrentLevelNum):
            listBoxPlot = []
            listLabel = []
            for v in range(self.intVoltageLevelNum):
                listBoxPlot.append(_listCpt[c][v])
                listLabel.append(f"{self.listVoltageLevel[v]}V")
            plt.cla()
            plt.boxplot(listBoxPlot, labels=listLabel, medianprops=medianprofile)
            plt.title(self.listBoxplotTitle[c], fontdict=fontdictLabel)
            plt.xlabel("Cutoff Voltage [V]")
            plt.ylabel("Useable Capacity [mAh]")
            plt.grid(linestyle="--", alpha=0.3)
            plt.savefig(self.listPngPath[c])
            plt.savefig(self.listSvgPath[c], dpi=1200)

        # analysis Info_Image.csv
        listPlt = []
        for c in range(self.intCurrentLevelNum):
            listPlt.append([])
            for _ in range(4):
                listPlt[c].append([])

        f = open(self.strInfoImageCsvPath, mode='r', encoding='utf-8')
        csvreaderInfoImageCsvFile = csv.reader(f)
        intPerBatteryRows = 1 + self.intCurrentLevelNum * 3
        index = 0
        for row in csvreaderInfoImageCsvFile:
            loop = index % intPerBatteryRows
            if loop != 0 and (loop % 3) != 1:
                listPlt[int((loop - 1) / 3)][((loop - 1) % 3) - 1].append([float(row[i]) for i in range(len(row))])
            index += 1
        f.close()

        def FilterData(_listPltCharge: list, _listPltVoltage: list, _intTimes=5, _floatSlopeMax=0.2, _floatDifferenceMax=0.05):
            _listPltChargeFiltered = []
            _listPltVoltageFiltered = []
            for _p in range(len(_listPltCharge)):
                _lisPltChargeSingle = _listPltCharge[_p]
                _listPltVoltageSingle = _listPltVoltage[_p]
                _times = _intTimes
                while _times:
                    _listPltChargeSingleTemp = [_lisPltChargeSingle[0]]
                    _listPltVoltageSingleTemp = [_listPltVoltageSingle[0]]
                    for _c in range(1, len(_lisPltChargeSingle)):
                        if (_lisPltChargeSingle[_c] - _lisPltChargeSingle[_c - 1]) == 0:
                            slope = _floatSlopeMax
                        else:
                            slope = abs((_listPltVoltageSingle[_c] - _listPltVoltageSingle[_c - 1]) / (_lisPltChargeSingle[_c] - _lisPltChargeSingle[_c - 1]))
                        if slope >= _floatSlopeMax:
                            pass
                        else:
                            if abs(_listPltVoltageSingle[_c] - _listPltVoltageSingle[_c - 1]) >= _floatDifferenceMax:
                                pass
                            else:
                                _listPltChargeSingleTemp.append(_lisPltChargeSingle[_c])
                                _listPltVoltageSingleTemp.append(_listPltVoltageSingle[_c])
                    _lisPltChargeSingle = _listPltChargeSingleTemp
                    _listPltVoltageSingle = _listPltVoltageSingleTemp
                    _times -= 1
                _listPltChargeFiltered.append(_lisPltChargeSingle)
                _listPltVoltageFiltered.append(_listPltVoltageSingle)
            return _listPltChargeFiltered, _listPltVoltageFiltered

        for c in range(self.intCurrentLevelNum):
            listPlt[c][2], listPlt[c][3] = FilterData(listPlt[c][0], listPlt[c][1])

        title_fontdict = {
            'fontsize': 15,
            'fontweight': 'bold'
        }
        axis_fontdict = {
            'fontsize': 15
        }

        plt.figure(figsize=(15, 6))

        def SetPltAxis():
            if self.listTestInfo[0] == "Coin Cell":
                plt.axis([10, 600, 1, 3])
                x_ticks = [10, 100, 200, 300, 400, 500, 600]
            elif self.listTestInfo[0] == "Pouch Cell":
                maxTicks = math.ceil(maxXaxis/100)*100
                plt.axis([20, maxTicks, 1, 3])
                x_ticks = [20]
                if maxTicks <= 1000:
                    for i in range(1, 11):
                        x_ticks.append(i*100)
                        if i*100 >= maxTicks:
                            break
                elif maxTicks <= 2000:
                    for i in range(1, 11):
                        x_ticks.append(i*200)
                        if i*200 >= maxTicks:
                            break
                elif maxTicks <= 3000:
                    for i in range(1, 11):
                        x_ticks.append(i*300)
                        if i*300 >= maxTicks:
                            break
                elif maxTicks <= 4000:
                    for i in range(1, 11):
                        x_ticks.append(i*400)
                        if i*400 >= maxTicks:
                            break
                else:
                    for i in range(1, 11):
                        x_ticks.append(i*500)
                        if i*500 >= maxTicks:
                            break
            else:
                raise BatteryAnalysisException("[Plt LoadVoltageOverCharge Error]: Unknown battery type")
            plt.xticks(x_ticks)

        plt.clf()
        SetPltAxis()
        y_major_locator = MultipleLocator(0.2)
        ax = plt.gca()
        ax.yaxis.set_major_locator(y_major_locator)
        plt.title(f"Unfiltered {self.strPltName}", fontdict=title_fontdict)
        plt.xlabel("Charge [mAh]", fontdict=axis_fontdict)
        plt.ylabel("Unfiltered Battery Load Voltage [V]", fontdict=axis_fontdict)
        for b in range(self.intBatteryNum):
            for c in range(self.intCurrentLevelNum):
                plt.plot(listPlt[c][0][b], listPlt[c][1][b], color=f"{self.listPltColorType[c]}", linewidth=0.5)
        plt.grid(linestyle="--", alpha=0.3)
        plt.savefig(self.strUnfilteredPngPath)
        plt.savefig(self.strUnfilteredSvgPath, dpi=1200)

        plt.clf()
        SetPltAxis()
        y_major_locator = MultipleLocator(0.2)
        ax = plt.gca()
        ax.yaxis.set_major_locator(y_major_locator)
        plt.title(f"Filtered {self.strPltName}", fontdict=title_fontdict)
        plt.xlabel("Charge [mAh]", fontdict=axis_fontdict)
        plt.ylabel("Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)
        for b in range(self.intBatteryNum):
            for c in range(self.intCurrentLevelNum):
                plt.plot(listPlt[c][0][b], listPlt[c][1][b], color=f"{self.listPltColorType[c]}", linewidth=0.5)
        plt.grid(linestyle="--", alpha=0.3)
        plt.savefig(self.strFilteredPngPath)
        plt.savefig(self.strFilteredSvgPath, dpi=1200)


class JsonWriter:
    def __init__(self, strResultPath: str, listTestInfo: list, listBatteryInfo: list) -> None:
        self.config = configparser.ConfigParser()
        
        try:
            # 统一使用发布模式逻辑：从可执行文件目录读取
            self.path = os.path.dirname(sys.executable)
            self.config.read(self.path + "/setting.ini", encoding='utf-8')
        except Exception as e:
            # 发生错误时创建基本配置
            print(f"配置读取失败: {e}，使用默认配置")
            if not self.config.has_section("BatteryConfig"):
                self.config.add_section("BatteryConfig")
            if not self.config.has_section("PltConfig"):
                self.config.add_section("PltConfig")
        self.listTestInfo = listTestInfo
        self.listBatteryInfo = listBatteryInfo
        try:
            [sy, sm, sd] = self.listBatteryInfo[2][0].split(" ")[0].split("-")
            td = f"{sy}{sm}{sd}"
        except ValueError:
            td = "00000000"
        self.strResultPath = f"{strResultPath}/{td}_V{listTestInfo[16]}"
        self.dictJson = {}
        self.listTestRun = []
        self.dictMeasurements = {}
        self.runAt = datetime.datetime.strptime(self.listBatteryInfo[2][0], "%Y-%m-%d %H:%M:%S").astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.strFileCurrentType = ""
        for c in range(len(self.listCurrentLevel)):
            self.strFileCurrentType = self.strFileCurrentType + f"{self.listCurrentLevel[c]}-"
        self.strFileCurrentType = self.strFileCurrentType[:-1]
        self.strResultJsonPath = f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}_{self.strFileCurrentType}_{self.listTestInfo[7]}.json"
        self.listBatteryVoltage = []
        for v in range(len(self.listVoltageLevel)):
            self.listBatteryVoltage.append(len(str(self.listVoltageLevel[v])) < 4 and str(self.listVoltageLevel[v]) + '0' * (4 - len(str(self.listVoltageLevel[v]))) or str(self.listVoltageLevel[v]))

        self.UJS_FormatJson()

    def UJS_FormatJson(self) -> None:
        for i in range(len(self.listBatteryInfo[1])):
            index = -1
            dictMeasurements = []
            for c in range(len(self.listCurrentLevel)):
                dictMeasurements.append({})
            dictTestRun = {}
            for j in range(len(self.listBatteryInfo[0][i])):
                if j % (len(self.listVoltageLevel)) == 0:
                    index += 1
                if self.listBatteryInfo[0][i][j] != 0 and self.listBatteryVoltage[j % len(self.listBatteryVoltage)] != "":
                    dictMeasurements[index].update({self.listBatteryVoltage[j % len(self.listBatteryVoltage)]: self.listBatteryInfo[0][i][j]})
            try:
                battery_name_split = self.listBatteryInfo[1][i].split("BTS")[1].split("_")
                battery_name = f"{battery_name_split[2]}_{battery_name_split[3]}"
            except IndexError:
                battery_name = f"Battery_{i}"
            listResults = []
            for c in range(len(self.listCurrentLevel)):
                listResults.append({"scenario": f"{self.listCurrentLevel[c]}mA", "measurements": dictMeasurements[c]})
            dictTestRun.update({"slot": battery_name, "results": listResults})
            self.listTestRun.append(dictTestRun)

        strBatteryModel = self.listTestInfo[2]
        # 安全读取电池类型基础规格
        try:
            if self.config.has_section("BatteryConfig") and self.config.has_option("BatteryConfig", "SpecificationTypeBase"):
                listBatteryTypeBase = self.config.get("BatteryConfig", "SpecificationTypeBase").split(",")
                print(f"使用配置文件中的电池类型基础规格: {listBatteryTypeBase}")
            else:
                # 使用默认值
                listBatteryTypeBase = ["CoinCell", "ButtonCell", "Cylindrical", "Prismatic", "PouchCell"]
                print("使用默认电池类型基础规格")
            
            strBatteryType = ""
            for b in range(len(listBatteryTypeBase)):
                if listBatteryTypeBase[b].strip() in self.listTestInfo[2]:
                    strBatteryType = listBatteryTypeBase[b]
                    break
            
            # 如果没有找到匹配项，使用默认值
            if strBatteryType == "":
                strBatteryType = "CoinCell"
                print(f"未找到精确匹配的电池类型，使用默认值: {strBatteryType}")
        except Exception as e:
            print(f"处理电池类型时出错: {e}，使用默认值")
            strBatteryType = "CoinCell"

        self.dictJson.update({
            "batchId": self.listTestInfo[5],
            "runAt": self.runAt,
            "batteryType": strBatteryType,
            "batteryModel": strBatteryModel,
            "batteryManufacturer": self.listTestInfo[4],
            "testRuns": self.listTestRun})

        with open(self.strResultJsonPath, 'w') as file:
            json.dump(self.dictJson, file, indent=4)


class FileWriter:
    def __init__(self, strResultPath: str, listTestInfo: list, listBatteryInfo: list) -> None:
        self.strErrorLog = ""
        try:
            XlsxWordWriter(strResultPath, listTestInfo, listBatteryInfo)
            JsonWriter(strResultPath, listTestInfo, listBatteryInfo)
        except BaseException as e:
            self.strErrorLog = str(e)
            traceback.print_exc()

    def UFW_GetErrorLog(self) -> str:
        return self.strErrorLog
