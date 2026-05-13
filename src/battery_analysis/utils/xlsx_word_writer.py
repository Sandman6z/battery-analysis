from battery_analysis.utils import csv_utils
from battery_analysis.utils.data_utils import build_plot_title
from battery_analysis.utils import word_utils
from battery_analysis.utils import excel_utils
from battery_analysis.utils import numeric_utils
from battery_analysis.utils import plot_writer
from battery_analysis.utils.exception_type import BatteryAnalysisException
from docx.shared import Pt, Cm
from docx.enum.text import WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx import Document
import matplotlib.pyplot as plt
import re
import importlib.resources
from pathlib import Path

# 配置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans', 'Arial', 'Times New Roman']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

import xlsxwriter as xwt
import os
import csv
import math
import datetime
import logging

# 导入软件版本信息
from battery_analysis import __version__

# 设置Matplotlib使用非交互式后端，避免线程安全问题
import matplotlib
matplotlib.use('Agg')  # 使用Agg后端，不会启动GUI


class XlsxWordWriter:
    def __init__(self, strResultPath: str, listTestInfo: list, listBatteryInfo: list) -> None:
        # 从 ConfigService 加载设备信息用于报告
        self._equipment_info = self._load_equipment_info()

        # 使用测试信息生成动态标题（使用listTestInfo[4]作为实际制造商）
        try:
            strImageTitle = build_plot_title(
                manufacturer=listTestInfo[4],
                spec_type=listTestInfo[2],
                spec_method=listTestInfo[3],
                batch_code=listTestInfo[5],
                capacity=listTestInfo[8] if len(listTestInfo) > 8 else "",
                temperature=listTestInfo[7] if len(listTestInfo) > 7 else "",
            )
        except (IndexError, TypeError, ValueError) as e:
            logging.error("获取标题时发生错误: %s", e)
            strImageTitle = "默认电池分析图标题"

        # init variables for all files
        self.listTestInfo = listTestInfo
        self.listBatteryInfo = listBatteryInfo
        try:
            # 优先使用从Excel提取的Test Date（listBatteryInfo[3]）
            if (len(self.listBatteryInfo) > 3 and \
                self.listBatteryInfo[3] and \
                self.listBatteryInfo[3] != "00000000"):
                test_date = self.listBatteryInfo[3]
                logging.info("使用从Excel提取的Test Date: %s", test_date)
                # 处理YYYYMMDD格式（8位数字）
                if len(test_date) == 8 and test_date.isdigit():
                    sy = test_date[:4]
                    sm = test_date[4:6]
                    sd = test_date[6:8]
                    td = f"{sy}{sm}{sd}"
                # 处理YYYY-MM-DD格式
                elif "-" in test_date:
                    [sy, sm, sd] = test_date.split(" ")[0].split("-")
                    td = f"{sy}{sm}{sd}"
                # 处理YYYY/MM/DD格式
                elif "/" in test_date:
                    [sy, sm, sd] = test_date.split(" ")[0].split("/")
                    td = f"{sy}{sm}{sd}"
                else:
                    raise ValueError(f"不支持的日期格式: {test_date}")
            else:
                # 使用从BatteryAnalysis类获取的test_date（在索引3位置）
                if (len(self.listBatteryInfo) > 3 and \
                    self.listBatteryInfo[3] and \
                    self.listBatteryInfo[3] != "00000000"):
                    # test_date已经是YYYYMMDD格式的字符串
                    td = self.listBatteryInfo[3]
                    logging.info("使用从Excel提取的Test Date: %s", td)
                else:
                    raise ValueError("无法从BatteryInfo列表中提取有效日期信息")
            # 验证日期有效性
            if not (len(td) == 8 and td.isdigit() and td != "00000000"):
                raise ValueError(f"无效的日期格式: {td}")
            logging.info("成功解析日期: %s", td)
        except (ValueError, IndexError) as e:
            logging.error("日期解析失败: %s", e)
            # 尝试从文件名中提取日期
            # 注意：listTestInfo[0] 是电池类型，不是文件名
            # 从第一个Excel文件路径提取日期
            if len(listBatteryInfo) > 1 and listBatteryInfo[1]:
                # listBatteryInfo[1] 是电池名称列表，使用第一个电池名称
                first_battery_name = listBatteryInfo[1][0] if listBatteryInfo[1] else ""
                if first_battery_name:
                    # 匹配文件名中所有连续的数字组
                    digit_groups = re.findall(r'(\d+)', first_battery_name)
                    if digit_groups:
                        # 取最后一组连续数字
                        last_digit_group = digit_groups[-1]
                        # 提取前8位作为日期（如果长度足够）
                        if len(last_digit_group) >= 8:
                            td = last_digit_group[:8]
                            logging.info("从电池名称最后一组连续数字提取前8位作为日期: %s", td)
                        else:
                            # 如果最后一组数字不足8位，尝试匹配任意8位数字
                            match = re.search(r'(\d{8})', first_battery_name)
                            if match:
                                td = match.group(1)
                                logging.info("从电池名称提取任意8位日期: %s", td)
                            else:
                                td = "00000000"
                                logging.warning("无法从电池名称提取日期，使用默认值: %s", td)
                    else:
                        td = "00000000"
                        logging.warning("电池名称中没有数字，无法提取日期，使用默认值: %s", td)
                else:
                    td = "00000000"
                    logging.warning("无法从电池名称提取日期，使用默认值: %s", td)
            else:
                td = "00000000"
                logging.warning("无法从电池信息提取日期，使用默认值: %s", td)
        # 使用os.path.join确保路径分隔符一致性
        self.strResultPath = os.path.join(
            strResultPath, f"{td}_v{listTestInfo[16]}")

        # 确保输出目录存在，如果不存在则自动创建
        os.makedirs(self.strResultPath, exist_ok=True)

        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.intCurrentLevelNum = len(self.listCurrentLevel)
        self.intVoltageLevelNum = len(self.listVoltageLevel)
        self.strFileCurrentType = ""
        for c in range(self.intCurrentLevelNum):
            self.strFileCurrentType = self.strFileCurrentType + \
                f"{self.listCurrentLevel[c]}-"
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
            strBoxplotTitle = (
                strImageTitle.split(strSplit)[0] + strSplit + "\n" +
                strImageTitle.split(strSplit)[1] + strSplit +
                strImageTitle.split(strSplit)[2]
            )
        for b in range(self.intCurrentLevelNum):
            self.listBoxplotTitle.append(
                (f"Useable Capacity over Cutoff Voltage, {self.listCurrentLevel[b]}mA Load\n" \
                 f"{strBoxplotTitle}"))
            self.listPngPath.append(
                (f"{self.strResultPath}/Image_UseableCapacityOver"
                 f"CutoffVoltage{self.listCurrentLevel[b]}mALoad.png"))
            self.listSvgPath.append(
                (f"{self.strResultPath}/Image_UseableCapacityOver"
                 f"CutoffVoltage{self.listCurrentLevel[b]}mALoad.svg"))
        self.strUnfilteredPngPath = (
            f"{self.strResultPath}/Image_UnfilteredLoadVoltageOverCharge.png"
        )
        self.strUnfilteredSvgPath = (
            f"{self.strResultPath}/Image_UnfilteredLoadVoltageOverCharge.svg"
        )
        self.strFilteredPngPath = (
            f"{self.strResultPath}/Image_FilteredLoadVoltageOverCharge.png"
        )
        self.strFilteredSvgPath = (
            f"{self.strResultPath}/Image_FilteredLoadVoltageOverCharge.svg"
        )
        self.strPltName = f"Load Voltage over Charge\n{strImageTitle}"
        self.strInfoImageCsvPath = f"{self.strResultPath}/Info_Image.csv"
        self.listPltColorType = ['#DF7040', '#0675BE', '#EDB120',
                                 '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']
        self.listColorName = ["red = ", "blue = ", "yellow = ",
                              "violet = ", "green = ", "orange = ", "black1 = ", "black2 = "]
        strStrF = ""
        for c in range(self.intCurrentLevelNum):
            strStrF += f"{self.listColorName[c]}{self.listCurrentLevel[c]}mA, "
        strStrF = strStrF[:-2]

        # init variables for excel
        # 替换文件名中的无效字符，特别是冒号
        safe_temperature = self.listTestInfo[7].replace(':', '_')
        self.strResultXlsxPath = (
            f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.xlsx"
        )
        self.strSampleXlsxPath = (
            f"{self.strResultPath}/Sample_{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.xlsx"
        )

        # init variables for word
        # 确定使用哪个模板文件（根据电流等级数量）
        if self.intCurrentLevelNum <= 4:
            template_filename = "Battery Measurement Report of TypeC TypeA_TypeD.docx"
        else:
            template_filename = "Battery Measurement Report of TypeC TypeA_TypeD_MP.docx"

        # 优先从包内 templates/ 目录加载，找不到则回退到外部 0_doc 目录
        try:
            pkg_template = (
                importlib.resources.files('battery_analysis')
                / 'templates'
                / template_filename
            )
            if pkg_template.is_file():
                self.strSampleReportWordPath = str(pkg_template)
                logging.info("从包内模板目录加载Word模板: %s", self.strSampleReportWordPath)
            else:
                raise FileNotFoundError
        except (TypeError, ModuleNotFoundError, FileNotFoundError):
            self.strSampleReportWordPath = str(
                Path(self.strResultPath) / f"../../0_doc/{template_filename}"
            )
            logging.info("从外部0_doc目录加载Word模板: %s", self.strSampleReportWordPath)

        # strTimeStamp = datetime.datetime.now().strftime("%Y%m%d")

        # 使用pathlib.Path来规范化路径，避免出现../符号
        report_name = (
            f"{self.listTestInfo[4]}_{self.listTestInfo[2]}_DC{self.listTestInfo[5]}"
            f"_TD{td}_v{self.listTestInfo[16]}.docx"
        )
        result_dir = Path(self.strResultPath).parent
        self.strReportWordPath = str(result_dir / report_name)
        self.listTextToReplace = [
            "TypeA", "TypeB", "TypeC", "TypeD",
            "TypeE", "TypeF", "TypeG", "StrA",
            "StrB", "StrC", "StrD", "StrF"
        ]
        self.listImageToReplace = ["<<Image_FilteredLoadVoltageOverCharge>>"]
        for i in range(10):     # max 10 images to replace
            self.listImageToReplace.append(
                f"<<Image_UseableCapacityOverCutoffVoltage{i}>>")
            self.listImageToReplace.append(
                f"<<Title_UseableCapacityOverCutoffVoltage{i}>>")
        # 电池类型基础规格（固定值）
        listBatteryTypeBase = [
            "CoinCell", "ButtonCell", "Cylindrical", "Prismatic", "PouchCell"]

        # 简化电池类型匹配逻辑
        try:
            test_info_type = self.listTestInfo[2]
            # 移除空格以便更好地匹配
            stripped_types = [battery_type.strip() for battery_type in listBatteryTypeBase]
            # 查找匹配的电池类型
            strBatteryType = next((battery_type for battery_type in stripped_types
                                  if battery_type in test_info_type), None)

            # 如果没有匹配到，使用列表中的第一个or直接使用测试信息
            if not strBatteryType:
                if stripped_types:
                    strBatteryType = stripped_types[0]
                    logging.warning("未找到精确匹配的电池类型，使用默认值: %s", strBatteryType)
                else:
                    strBatteryType = test_info_type  # 直接使用测试信息中的类型
                    logging.warning("电池类型列表empty，直接使用测试信息: %s", strBatteryType)
        except (IndexError, TypeError, ValueError) as e:
            logging.error("获取电池类型时发生错误: %s", e)
            strBatteryType = self.listTestInfo[2]  # 发生错误时使用测试信息中的类型
        self.listTestInfoForReplace = [
            self.listTestInfo[2], self.listTestInfo[3], self.listTestInfo[4],
            self.listTestInfo[5], self.listTestInfo[7], self.listTestInfo[11],
            strBatteryType, None, None, None, None, strStrF
        ]

        # init variables for csv
        # 使用已经处理过的安全温度变量
        self.strResultCsvPath = (
            f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.csv"
        )

        # execute
        self.UXWW_XlsxWordCsvWrite()

    @staticmethod
    def _load_equipment_info() -> dict:
        """从 ConfigService 获取设备信息，用于 Word 报告"""
        try:
            from battery_analysis.main.services.service_container import get_service_container
            container = get_service_container()
            svc = container.get("config")
            if svc:
                equipment = svc.get_config_value("test.equipment", {})
                if equipment:
                    first_key = next(iter(equipment))
                    info = equipment[first_key]
                    logging.info("从 ConfigService 加载设备信息 (key=%s)", first_key)
                    return info
        except Exception as e:
            logging.warning("从 ConfigService 加载设备信息失败: %s", e)
        return {}

    def _get_equip_value(self, dotted_key: str, fallback: str = "") -> str:
        """从 _equipment_info 字典读取带点号的键（如 softwareVersions.btsServer）"""
        parts = dotted_key.split(".")
        value = self._equipment_info
        try:
            for p in parts:
                value = value[p]
            if isinstance(value, str):
                return value
            if isinstance(value, (list, tuple)):
                return ", ".join(str(v) for v in value)
        except (KeyError, TypeError, IndexError):
            pass
        return fallback

    def UXWW_XlsxWordCsvWrite(self) -> None:
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
        plot_writer.draw_boxplot_and_curves(
            self.intCurrentLevelNum,
            self.intVoltageLevelNum,
            self.listVoltageLevel,
            self.listBoxplotTitle,
            self.listPngPath,
            self.listSvgPath,
            self.strInfoImageCsvPath,
            self.strPltName,
            self.strUnfilteredPngPath,
            self.strUnfilteredSvgPath,
            self.strFilteredPngPath,
            self.strFilteredSvgPath,
            self.listTestInfo,
            self.listPltColorType,
            self.intBatteryNum,
            listCpt,
            int(self.listTestInfo[8]),
        )

        # Delegate to specialized writers
        from battery_analysis.utils.writers.excel_report_writer import ExcelReportWriter
        from battery_analysis.utils.writers.word_report_writer import WordReportWriter
        from battery_analysis.utils.writers.csv_writer import CsvWriter

        ExcelReportWriter(self.strResultPath, self.listTestInfo, self.listBatteryInfo).write()
        WordReportWriter(self.strResultPath, self.listTestInfo, self.listBatteryInfo).write()
        CsvWriter(self.strResultPath, self.listTestInfo, self.listBatteryInfo).write()

    def handle_data_error(self, error_msg):
        """处理数据错误"""
        return "retry"

    def create_directories(self):
        """创建目录"""
        os.makedirs(self.strResultPath, exist_ok=True)
