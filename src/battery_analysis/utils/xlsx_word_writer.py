"""Xlsx/Word/Csv 写入器（旧版适配器）

主要功能是协调绘图和委托给专用的 ExcelReportWriter / WordReportWriter / CsvWriter。
与新版 writer 的差异：生成插件标题、管理图片/ SVG 路径、处理旧式日期回退逻辑。
"""

import os
import re
import logging
import importlib.resources
from pathlib import Path

from battery_analysis.utils.processors.data_utils import build_plot_title
from battery_analysis.utils.writers import plot_writer
from battery_analysis.utils.readers.date_parser import parse_test_date
from battery_analysis import __version__

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Segoe UI Emoji',
                                    'Apple Color Emoji', 'Noto Color Emoji',
                                    'DejaVu Sans', 'Arial', 'Times New Roman']
plt.rcParams['axes.unicode_minus'] = False


logger = logging.getLogger(__name__)


class XlsxWordWriter:
    """Xlsx/Word/Csv 写入器（旧版适配器）"""

    def __init__(self, strResultPath: str, listTestInfo: list, listBatteryInfo: list,
                 equipment_info: dict | None = None) -> None:
        self.listTestInfo = listTestInfo
        self.listBatteryInfo = listBatteryInfo
        self._equipment_info = equipment_info or {}

        # 提取测试日期（YYYYMMDD）
        td = self._extract_test_date()

        # 构建输出路径
        self.strResultPath = os.path.join(strResultPath, f"{td}_v{listTestInfo[16]}")
        os.makedirs(self.strResultPath, exist_ok=True)

        # 电流/电压等级信息
        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.intCurrentLevelNum = len(self.listCurrentLevel)
        self.intVoltageLevelNum = len(self.listVoltageLevel)
        self.strFileCurrentType = ""
        for c in range(self.intCurrentLevelNum):
            self.strFileCurrentType += f"{self.listCurrentLevel[c]}-"
        self.strFileCurrentType = self.strFileCurrentType[:-1]

        # 电池信息
        self.listBatteryCharge = self.listBatteryInfo[0]
        self.listBatteryName = self.listBatteryInfo[1]
        self.intBatteryNum = len(self.listBatteryName)

        # 图像标题与路径
        self._build_image_paths_and_titles(td)
        # 文档路径（excel / word / csv）
        self._build_document_paths(td)
        # 文本替换列表
        self._build_replacements()

    def _extract_test_date(self) -> str:
        """从 BatteryInfo 提取测试日期，返回 YYYYMMDD 字符串"""
        # 优先使用 listBatteryInfo[3] (标准路径)
        test_date = self.listBatteryInfo[3] if len(self.listBatteryInfo) > 3 else ""
        original_cycle = self.listBatteryInfo[4] if len(self.listBatteryInfo) > 4 else ""
        td = parse_test_date(str(test_date) if test_date else "",
                             str(original_cycle) if original_cycle else "")

        if td and td != "00000000":
            logger.info("成功解析日期: %s", td)
            return td

        # 回退：从电池名称中提取
        return self._extract_date_from_battery_name()

    def _extract_date_from_battery_name(self) -> str:
        """从电池名称的最后一组连续数字提取日期"""
        logger.warning("标准日期解析失败，尝试从电池名称提取")
        if len(self.listBatteryInfo) > 1 and self.listBatteryInfo[1]:
            first_name = self.listBatteryInfo[1][0] if self.listBatteryInfo[1] else ""
            if first_name:
                digit_groups = re.findall(r'(\d+)', first_name)
                if digit_groups:
                    last_group = digit_groups[-1]
                    if len(last_group) >= 8:
                        td = last_group[:8]
                        logger.info("从电池名称提取前8位日期: %s", td)
                        return td
                    match = re.search(r'(\d{8})', first_name)
                    if match:
                        td = match.group(1)
                        logger.info("从电池名称提取8位日期: %s", td)
                        return td
        logger.warning("无法从电池名称提取日期，使用默认值")
        return "00000000"

    def _build_image_paths_and_titles(self, td: str) -> None:
        """构建图像路径与框线图标题"""
        # 生成动态标题
        try:
            strImageTitle = build_plot_title(
                manufacturer=self.listTestInfo[4],
                spec_type=self.listTestInfo[2],
                spec_method=self.listTestInfo[3],
                batch_code=self.listTestInfo[5],
                capacity=self.listTestInfo[8] if len(self.listTestInfo) > 8 else "",
                temperature=self.listTestInfo[7] if len(self.listTestInfo) > 7 else "",
            )
        except (IndexError, TypeError, ValueError) as e:
            logging.error("获取标题时发生错误: %s", e)
            strImageTitle = "默认电池分析图标题"

        # 框线图标题
        self.listBoxplotTitle = []
        if len(strImageTitle) <= 70:
            strBoxplotTitle = strImageTitle
        else:
            strSplit = "A, "
            strBoxplotTitle = (
                strImageTitle.split(strSplit)[0] + strSplit + "\n" +
                strImageTitle.split(strSplit)[1] + strSplit +
                strImageTitle.split(strSplit)[2]
            )

        # 图像路径
        self.listPngPath = []
        self.listSvgPath = []
        for b in range(self.intCurrentLevelNum):
            self.listBoxplotTitle.append(
                f"Useable Capacity over Cutoff Voltage, {self.listCurrentLevel[b]}mA Load\n{strBoxplotTitle}")
            self.listPngPath.append(
                f"{self.strResultPath}/Image_UseableCapacityOverCutoffVoltage{self.listCurrentLevel[b]}mALoad.png")
            self.listSvgPath.append(
                f"{self.strResultPath}/Image_UseableCapacityOverCutoffVoltage{self.listCurrentLevel[b]}mALoad.svg")

        self.strUnfilteredPngPath = f"{self.strResultPath}/Image_UnfilteredLoadVoltageOverCharge.png"
        self.strUnfilteredSvgPath = f"{self.strResultPath}/Image_UnfilteredLoadVoltageOverCharge.svg"
        self.strFilteredPngPath = f"{self.strResultPath}/Image_FilteredLoadVoltageOverCharge.png"
        self.strFilteredSvgPath = f"{self.strResultPath}/Image_FilteredLoadVoltageOverCharge.svg"
        self.strPltName = f"Load Voltage over Charge\n{strImageTitle}"
        self.strInfoImageCsvPath = f"{self.strResultPath}/Info_Image.csv"

        # 颜色
        self.listPltColorType = ['#DF7040', '#0675BE', '#EDB120',
                                 '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']
        self.listColorName = ["red = ", "blue = ", "yellow = ",
                              "violet = ", "green = ", "orange = ", "black1 = ", "black2 = "]

    def _build_document_paths(self, td: str) -> None:
        """构建 Excel / Word / CSV 输出路径"""
        safe_temperature = self.listTestInfo[7].replace(':', '_')

        self.strResultXlsxPath = (
            f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.xlsx"
        )
        self.strSampleXlsxPath = (
            f"{self.strResultPath}/Sample_{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.xlsx"
        )

        # Word 模板
        if self.intCurrentLevelNum <= 4:
            template_filename = "Battery Measurement Report of TypeC TypeA_TypeD.docx"
        else:
            template_filename = "Battery Measurement Report of TypeC TypeA_TypeD_MP.docx"

        try:
            pkg_template = (
                importlib.resources.files('battery_analysis')
                / 'templates' / template_filename
            )
            if pkg_template.is_file():
                self.strSampleReportWordPath = str(pkg_template)
                logger.info("从包内模板目录加载Word模板: %s", self.strSampleReportWordPath)
            else:
                raise FileNotFoundError
        except (TypeError, ModuleNotFoundError, FileNotFoundError):
            self.strSampleReportWordPath = str(
                Path(self.strResultPath) / f"../../0_doc/{template_filename}")
            logger.info("从外部0_doc目录加载Word模板: %s", self.strSampleReportWordPath)

        report_name = (
            f"{self.listTestInfo[4]}_{self.listTestInfo[2]}_DC{self.listTestInfo[5]}"
            f"_TD{td}_v{self.listTestInfo[16]}.docx"
        )
        result_dir = Path(self.strResultPath).parent
        self.strReportWordPath = str(result_dir / report_name)

        self.strResultCsvPath = (
            f"{self.strResultPath}/{self.listTestInfo[4]}_{self.listTestInfo[2]}_{self.listTestInfo[3]}"
            f"_{self.strFileCurrentType}_{safe_temperature}.csv"
        )

    def _build_replacements(self) -> None:
        """构建 Word 模板文本替换列表"""
        self.listTextToReplace = [
            "TypeA", "TypeB", "TypeC", "TypeD",
            "TypeE", "TypeF", "TypeG", "StrA",
            "StrB", "StrC", "StrD", "StrF"
        ]
        self.listImageToReplace = ["<<Image_FilteredLoadVoltageOverCharge>>"]
        for i in range(10):
            self.listImageToReplace.append(f"<<Image_UseableCapacityOverCutoffVoltage{i}>>")
            self.listImageToReplace.append(f"<<Title_UseableCapacityOverCutoffVoltage{i}>>")

        # 电池类型匹配
        listBatteryTypeBase = ["CoinCell", "ButtonCell", "Cylindrical", "Prismatic", "PouchCell"]
        try:
            test_info_type = self.listTestInfo[2]
            stripped_types = [bt.strip() for bt in listBatteryTypeBase]
            strBatteryType = next((bt for bt in stripped_types if bt in test_info_type), None)
            if not strBatteryType:
                strBatteryType = stripped_types[0] if stripped_types else test_info_type
                logging.warning("未找到精确匹配的电池类型，使用默认值: %s", strBatteryType)
        except (IndexError, TypeError, ValueError) as e:
            logging.error("获取电池类型时发生错误: %s", e)
            strBatteryType = self.listTestInfo[2]

        # 颜色/电流等级字符串
        strStrF = ""
        for c in range(self.intCurrentLevelNum):
            strStrF += f"{self.listColorName[c]}{self.listCurrentLevel[c]}mA, "
        strStrF = strStrF[:-2]

        self.listTestInfoForReplace = [
            self.listTestInfo[2], self.listTestInfo[3], self.listTestInfo[4],
            self.listTestInfo[5], self.listTestInfo[7], self.listTestInfo[11],
            strBatteryType, None, None, None, None, strStrF
        ]

    # ── 公共方法 ──

    def write(self) -> None:
        """执行完整的写入流程：绘图 → Excel → Word → CSV"""
        from battery_analysis.utils.writers.statistics_utils import (
            compute_list_cpt, compute_statistics,
        )

        listCpt = compute_list_cpt(
            self.listBatteryCharge, self.intBatteryNum,
            self.intCurrentLevelNum, self.intVoltageLevelNum)
        stats = compute_statistics(
            listCpt, self.intCurrentLevelNum, self.intVoltageLevelNum)

        # 绘制箱线图
        plot_writer.draw_boxplot_and_curves(
            self.intCurrentLevelNum, self.intVoltageLevelNum,
            self.listVoltageLevel, self.listBoxplotTitle,
            self.listPngPath, self.listSvgPath,
            self.strInfoImageCsvPath, self.strPltName,
            self.strUnfilteredPngPath, self.strUnfilteredSvgPath,
            self.strFilteredPngPath, self.strFilteredSvgPath,
            self.listTestInfo, self.listPltColorType,
            self.intBatteryNum, listCpt,
            int(self.listTestInfo[8]),
        )

        # 委托给专用写入器
        from battery_analysis.utils.writers.excel_report_writer import ExcelReportWriter
        from battery_analysis.utils.writers.word_report_writer import WordReportWriter
        from battery_analysis.utils.writers.csv_writer import CsvWriter

        ExcelReportWriter(self.strResultPath, self.listTestInfo, self.listBatteryInfo).write(listCpt, stats)
        WordReportWriter(self.strResultPath, self.listTestInfo, self.listBatteryInfo,
                         equipment_info=self._equipment_info).write(listCpt, stats)
        CsvWriter(self.strResultPath, self.listTestInfo, self.listBatteryInfo).write(listCpt, stats)

    def handle_data_error(self, error_msg):
        return "retry"

    def create_directories(self):
        os.makedirs(self.strResultPath, exist_ok=True)

    # ── 静态工具 ──

    def _get_equip_value(self, dotted_key: str, fallback: str = "") -> str:
        """从 _equipment_info 读取带点号的键"""
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
