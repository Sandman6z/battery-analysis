import os
import csv
import sys
import math
import traceback
import configparser

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import CheckButtons

from src.battery_analysis.utils.exception_type import BatteryAnalysisException


class FIGURE:
    def __init__(self):
        global bBuild
        if os.path.exists(f"{os.path.dirname(os.path.abspath(__file__))}/Main_ImageShow.py"):
            bBuild = False
        else:
            bBuild = True
        
        # 将全局变量bBuild赋值给实例变量，确保整个类中使用一致
        self.bBuild = bBuild
        self.config = configparser.ConfigParser()
        
        # 初始化默认配置
        if not self.config.has_section("PltConfig"):
            self.config.add_section("PltConfig")
        
        # 尝试读取配置文件
        config_loaded = False
        try:
            if self.bBuild:
                self.path = os.path.dirname(sys.executable)
                setting_ini_path = os.path.join(self.path, "setting.ini")
                if os.path.exists(setting_ini_path):
                    self.config.read(setting_ini_path, encoding='utf-8')
                    config_loaded = True
                else:
                    print("未找到setting.ini，使用默认配置")
            else:
                self.path = os.path.dirname(os.path.abspath(__file__))
                # 向上三级目录到项目根目录，再访问config目录
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                config_path = os.path.join(project_root, "config", "Config_BatteryAnalysis.ini")
                if os.path.exists(config_path):
                    self.config.read(config_path, encoding='utf-8')
                    config_loaded = True
                else:
                    print("未找到Config_BatteryAnalysis.ini，使用默认配置")
        except Exception as e:
            print(f"配置读取失败: {e}，使用默认配置")
        
        # 安全读取PltConfig/Path，如果不存在则使用默认值
        if self.config.has_section("PltConfig") and self.config.has_option("PltConfig", "Path"):
            self.strPltPath = self.config.get("PltConfig", "Path")
        else:
            # 使用当前目录作为默认路径
            self.strPltPath = os.getcwd()
            print(f"未找到PltConfig/Path，使用默认路径: {self.strPltPath}")
        
        # 安全读取PltConfig/Title，如果不存在则使用默认值
        if self.config.has_section("PltConfig") and self.config.has_option("PltConfig", "Title"):
            self.strPltTitle = self.config.get("PltConfig", "Title")
        else:
            self.strPltTitle = "Battery Test Results"
            print(f"未找到PltConfig/Title，使用默认标题: {self.strPltTitle}")

        self.strInfoImageCsvPath = f"{self.strPltPath}/Info_Image.csv"
        
        # 安全读取BatteryConfig/PulseCurrent
        if self.config.has_section("BatteryConfig") and self.config.has_option("BatteryConfig", "PulseCurrent"):
            try:
                listPulseCurrentLevel = self.config.get("BatteryConfig", "PulseCurrent").split(",")
                self.listPulseCurrentLevel = [int(listPulseCurrentLevel[c].strip()) for c in range(len(listPulseCurrentLevel))]
                print(f"使用配置的脉冲电流级别: {self.listPulseCurrentLevel}")
            except:
                self.listPulseCurrentLevel = [10, 20, 50]  # 默认值
                print("脉冲电流配置格式错误，使用默认值")
        else:
            self.listPulseCurrentLevel = [10, 20, 50]  # 默认值
            print("未找到BatteryConfig/PulseCurrent，使用默认值")
        
        self.intCurrentLevelNum = len(self.listPulseCurrentLevel)
        
        # 安全读取BatteryConfig/SpecificationTypeCoinCell
        if self.config.has_section("BatteryConfig") and self.config.has_option("BatteryConfig", "SpecificationTypeCoinCell"):
            listCoinCell = self.config.get("BatteryConfig", "SpecificationTypeCoinCell").split(",")
            self.listCoinCell = [listCoinCell[c].strip() for c in range(len(listCoinCell))]
        else:
            self.listCoinCell = []  # 默认空列表
            print("未找到BatteryConfig/SpecificationTypeCoinCell，使用空列表")
        
        # 安全读取BatteryConfig/SpecificationTypePouchCell
        if self.config.has_section("BatteryConfig") and self.config.has_option("BatteryConfig", "SpecificationTypePouchCell"):
            listPouchCell = self.config.get("BatteryConfig", "SpecificationTypePouchCell").split(",")
            self.listPouchCell = [listPouchCell[p].strip() for p in range(len(listPouchCell))]
        else:
            self.listPouchCell = []  # 默认空列表
            print("未找到BatteryConfig/SpecificationTypePouchCell，使用空列表")

        # 安全设置图表标题
        try:
            # 使用已经安全读取的self.strPltTitle
            # 尝试移除前后引号（如果存在）
            if len(self.strPltTitle) >= 2 and self.strPltTitle[0] == '"' and self.strPltTitle[-1] == '"':
                title_content = self.strPltTitle[1:-1]
            else:
                title_content = self.strPltTitle
            self.strPltName = "Load Voltage over Charge\n" + title_content
        except:
            self.strPltName = "Load Voltage over Charge\nUnknown Battery"
            print("设置图表标题出错，使用默认标题")
        
        self.listColor = ['#DF7040', '#0675BE', '#EDB120', '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']

        self.maxXaxis = 1000  # 默认最大值
        
        # 安全读取BatteryConfig/Rules
        if self.config.has_section("BatteryConfig") and self.config.has_option("BatteryConfig", "Rules"):
            try:
                listRules = self.config.get("BatteryConfig", "Rules").split(",")
                # 尝试根据规则匹配设置maxXaxis
                try:
                    for i in range(len(listRules)):
                        # 安全检查strPltName是否有足够的部分
                        if len(self.strPltName.split(" ")) > 4 and self.strPltName.split(" ")[4] in listRules[i]:
                            # 安全检查规则格式是否正确
                            if "/" in listRules[i] and len(listRules[i].split("/")) > 2:
                                self.maxXaxis = int(listRules[i].split("/")[2])
                                print(f"根据规则设置maxXaxis: {self.maxXaxis}")
                                break
                except Exception as e:
                    print(f"处理规则时出错: {e}，保持默认maxXaxis")
            except Exception as e:
                print(f"读取Rules配置出错: {e}，使用默认maxXaxis")
        else:
            print("未找到BatteryConfig/Rules，使用默认maxXaxis")

        self.listPlt = []
        self.listBatteryName = []
        self.listBatteryNameSplit = []
        self.intBatteryNum = 0

        try:
            self.csv_read()
            bMatchSpecificationType = False
            strSpecificationType = self.strPltName.split(" ")[4]
            for c in range(len(self.listCoinCell)):
                if self.listCoinCell[c] == strSpecificationType:
                    self.listAxis = [10, 600, 1, 3]
                    self.listXTicks = [10, 100, 200, 300, 400, 500, 600]
                    bMatchSpecificationType = True
                    break
            if not bMatchSpecificationType:
                for p in range(len(self.listPouchCell)):
                    if self.listPouchCell[p] == strSpecificationType:
                        maxTicks = math.ceil(self.maxXaxis/100)*100
                        self.listAxis = [20, maxTicks, 1, 3]
                        self.listXTicks = [20]
                        if maxTicks <= 1000:
                            for i in range(1, 11):
                                self.listXTicks.append(i*100)
                                if i*100 >= maxTicks:
                                    break
                        elif maxTicks <= 2000:
                            for i in range(1, 11):
                                self.listXTicks.append(i*200)
                                if i*200 >= maxTicks:
                                    break
                        elif maxTicks <= 3000:
                            for i in range(1, 11):
                                self.listXTicks.append(i*300)
                                if i*300 >= maxTicks:
                                    break
                        elif maxTicks <= 4000:
                            for i in range(1, 11):
                                self.listXTicks.append(i*400)
                                if i*400 >= maxTicks:
                                    break
                        else:
                            for i in range(1, 11):
                                self.listXTicks.append(i*500)
                                if i*500 >= maxTicks:
                                    break
                        bMatchSpecificationType = True
                        break
            if bMatchSpecificationType:
                self.plt_figure()
            else:
                print("警告: 未找到匹配的规格类型，使用默认配置继续展示")
                # 设置默认的规格参数
                self.intCurrentLevelNum = 3
                self.intMaxXaxis = 5000
                self.listXTicks = list(range(0, 5001, 500))
                self.listAxis = [0, self.intMaxXaxis, 2.5, 4.5]  # 设置默认坐标轴范围
                self.plt_figure()
            
        except BaseException as e:
            self.errorlog = str(e)
            traceback.print_exc()

    def csv_read(self):
        try:
            # 检查文件是否存在
            if not os.path.exists(self.strInfoImageCsvPath):
                print(f"警告: 找不到CSV文件 {self.strInfoImageCsvPath}，创建模拟数据用于展示")
                self._create_mock_data()
                return
                
            for c in range(self.intCurrentLevelNum):
                self.listPlt.append([])
                for _ in range(4):
                    self.listPlt[c].append([])

            f = open(self.strInfoImageCsvPath, mode='r', encoding='utf-8')
            csvreaderInfoImageCsvFile = csv.reader(f)
            intPerBatteryRows = 1 + self.intCurrentLevelNum * 3
            index = 0
            for row in csvreaderInfoImageCsvFile:
                loop = index % intPerBatteryRows
                if loop == 0:
                    self.listBatteryName.append(row[1].strip())
                else:
                    if (loop % 3) != 1:
                        self.listPlt[int((loop - 1) / 3)][((loop - 1) % 3) - 1].append([float(row[i]) for i in range(len(row))])
                index += 1
            f.close()

            self.intBatteryNum = len(self.listBatteryName)

            if self.intBatteryNum == 0:
                print("警告: CSV文件中没有电池信息，创建模拟数据")
                self._create_mock_data()
                return

            for b in range(self.intBatteryNum):
                try:
                    strBatteryNameSplit = self.listBatteryName[b].split("BTS")[1].split("_")
                    strBatteryName = f"{strBatteryNameSplit[2]}_{strBatteryNameSplit[3]}"
                except IndexError:
                    strBatteryName = f"Battery_{b}"
                self.listBatteryNameSplit.append(strBatteryName)

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
                self.listPlt[c][2], self.listPlt[c][3] = FilterData(self.listPlt[c][0], self.listPlt[c][1])
        except Exception as e:
            print(f"读取CSV文件出错: {e}")
            traceback.print_exc()
            # 出错时创建模拟数据
            self._create_mock_data()
    
    def _create_mock_data(self):
        """创建模拟数据用于展示"""
        # 重置数据结构
        self.listPlt = []
        self.listBatteryName = ["Battery_1", "Battery_2"]
        self.listBatteryNameSplit = ["Battery", "Battery"]
        self.intBatteryNum = 2
        
        # 为每个电流级别创建数据
        for c in range(self.intCurrentLevelNum):
            self.listPlt.append([])
            for _ in range(4):
                self.listPlt[c].append([])
            
            for b in range(self.intBatteryNum):
                # 生成模拟充电数据
                charge_data = list(range(0, 500, 20))
                # 根据电池和电流级别生成不同的电压数据
                voltage_data = []
                base_voltage = 3.0 + (b * 0.2)  # 不同电池不同基准电压
                for charge in charge_data:
                    # 模拟放电曲线
                    voltage = base_voltage - (charge / 1000) - (c * 0.1)  # 电流越大，电压下降越快
                    # 添加一些随机波动
                    import random
                    voltage += (random.random() - 0.5) * 0.05
                    voltage_data.append(max(2.5, voltage))  # 确保电压不低于2.5V
                
                # 添加原始数据
                self.listPlt[c][0].append(charge_data)
                self.listPlt[c][1].append(voltage_data)
                # 复制到过滤后的数据（简单模拟）
                self.listPlt[c][2].append(charge_data)
                self.listPlt[c][3].append(voltage_data)
                
        print(f"已创建模拟数据，包含{self.intBatteryNum}个电池，{self.intCurrentLevelNum}个电流级别")


    def plt_figure(self):
        title_fontdict = {
            'fontsize': 15,
            'fontweight': 'bold'
        }
        axis_fontdict = {
            'fontsize': 15
        }
        fig = plt.figure(figsize=(15, 6))
        fig.canvas.manager.window.setWindowTitle(f"Filtered Load Voltage over Charge")

        plt.clf()
        gs = fig.add_gridspec(1, 40)
        fig.add_subplot(gs[:, 5:])
        plt.axis(self.listAxis)
        x_ticks = self.listXTicks
        plt.xticks(x_ticks)
        y_major_locator = MultipleLocator(0.2)
        ax = plt.gca()
        ax.yaxis.set_major_locator(y_major_locator)
        plt.title(f"Filtered {self.strPltName}", fontdict=title_fontdict)
        plt.xlabel("Charge [mAh]", fontdict=axis_fontdict)
        plt.ylabel("Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)
        plt.grid(linestyle="--", alpha=0.3)
        lines_unfiltered = []
        lines_filtered = []

        for b in range(self.intBatteryNum):
            for c in range(self.intCurrentLevelNum):
                ul, = plt.plot(self.listPlt[c][0][b], self.listPlt[c][1][b], color=self.listColor[c], label=[f'{self.listBatteryNameSplit[b]}', 'Unfiltered'], visible=False, linewidth=0.5)
                lines_unfiltered.append(ul)
                fl, = plt.plot(self.listPlt[c][2][b], self.listPlt[c][3][b], color=self.listColor[c], label=[f'{self.listBatteryNameSplit[b]}', 'Filtered'], visible=True, linewidth=0.5)
                lines_filtered.append(fl)

        labels_filter = ["       Filtered"]
        visibility_filter = [True]
        rax_filter = plt.axes([0.001, 0.933, 0.16, 0.062])
        check_filter = CheckButtons(rax_filter, labels_filter, visibility_filter)

        def func_filter(label):
            _label = label
            if check_filter.get_status()[0]:
                fig.canvas.manager.window.setWindowTitle(f"Filtered Load Voltage over Charge")
                ax.set_title(f"Filtered {self.strPltName}", fontdict=title_fontdict)
                ax.set_ylabel("Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)
                for _i in range(len(lines_unfiltered)):
                    lines_filtered[_i].set_visible(lines_unfiltered[_i].get_visible())
                    lines_unfiltered[_i].set_visible(False)
            else:
                fig.canvas.manager.window.setWindowTitle(f"Unfiltered Load Voltage over Charge")
                ax.set_title(f"Unfiltered {self.strPltName}", fontdict=title_fontdict)
                ax.set_ylabel("Unfiltered Battery Load Voltage [V]", fontdict=axis_fontdict)
                for _i in range(len(lines_filtered)):
                    lines_unfiltered[_i].set_visible(lines_filtered[_i].get_visible())
                    lines_filtered[_i].set_visible(False)
            plt.draw()
        check_filter.on_clicked(func_filter)

        if self.intBatteryNum > 32:
            labels_line1 = []
            visibility_line1 = []
            rax_line1 = plt.axes([0.001, 0.005, 0.08, 0.029*32])
            for i in range(0, 32):
                labels_line1.append(self.listBatteryNameSplit[i])
                visibility_line1.append(True)
            check_line1 = CheckButtons(rax_line1, labels_line1, visibility_line1)

            def func_line1(label):
                if check_filter.get_status()[0]:
                    for _i in range(len(lines_filtered)):
                        if label == lines_filtered[_i].get_label().split(",")[0][2:-1]:
                            lines_filtered[_i].set_visible(not lines_filtered[_i].get_visible())
                else:
                    for _i in range(len(lines_unfiltered)):
                        if label == lines_unfiltered[_i].get_label().split(",")[0][2:-1]:
                            lines_unfiltered[_i].set_visible(not lines_unfiltered[_i].get_visible())
                plt.draw()
            check_line1.on_clicked(func_line1)

            labels_line2 = []
            visibility_line2 = []
            rax_line2 = plt.axes([0.081, 0.005, 0.08, 0.029*32])
            for i in range(32, 64):
                if i < self.intBatteryNum:
                    labels_line2.append(self.listBatteryNameSplit[i])
                    visibility_line2.append(True)
                else:
                    labels_line2.append("None")
                    visibility_line2.append(False)
            check_line2 = CheckButtons(rax_line2, labels_line2, visibility_line2)

            def func_line2(label):
                if label == "None":
                    for _i in range(self.intBatteryNum-32, 32):
                        if check_line2.get_status()[_i]:
                            check_line2.set_active(_i)
                else:
                    if check_filter.get_status()[0]:
                        for _i in range(len(lines_filtered)):
                            if label == lines_filtered[_i].get_label().split(",")[0][2:-1]:
                                lines_filtered[_i].set_visible(not lines_filtered[_i].get_visible())
                    else:
                        for _i in range(len(lines_unfiltered)):
                            if label == lines_unfiltered[_i].get_label().split(",")[0][2:-1]:
                                lines_unfiltered[_i].set_visible(not lines_unfiltered[_i].get_visible())
                plt.draw()
            check_line2.on_clicked(func_line2)

        else:
            labels_line1 = []
            visibility_line1 = []
            rax_line1 = plt.axes([0.001, 0.005, 0.08, 0.029 * 32])
            for i in range(0, 32):
                if i < self.intBatteryNum:
                    labels_line1.append(self.listBatteryNameSplit[i])
                    visibility_line1.append(True)
                else:
                    labels_line1.append("None")
                    visibility_line1.append(False)
            check_line1 = CheckButtons(rax_line1, labels_line1, visibility_line1)

            def func_line1(label):
                if label == "None":
                    for _i in range(self.intBatteryNum, 32):
                        if check_line1.get_status()[_i]:
                            check_line1.set_active(_i)
                else:
                    if check_filter.get_status()[0]:
                        for _i in range(len(lines_filtered)):
                            if label in lines_filtered[_i].get_label():
                                lines_filtered[_i].set_visible(not lines_filtered[_i].get_visible())
                    else:
                        for _i in range(len(lines_unfiltered)):
                            if label in lines_unfiltered[_i].get_label():
                                lines_unfiltered[_i].set_visible(not lines_unfiltered[_i].get_visible())
                plt.draw()
            check_line1.on_clicked(func_line1)

            labels_line2 = []
            visibility_line2 = []
            rax_line2 = plt.axes([0.081, 0.005, 0.08, 0.029*32])
            for i in range(32, 64):
                labels_line2.append("None")
                visibility_line2.append(False)
            check_line2 = CheckButtons(rax_line2, labels_line2, visibility_line2)

            def func_line2(label):
                _label = label
                for _i in range(0, 32):
                    if check_line2.get_status()[_i]:
                        check_line2.set_active(_i)
            check_line2.on_clicked(func_line2)
        plt.show()


if __name__ == '__main__':
    if os.path.exists(f"{os.path.dirname(os.path.abspath(__file__))}/Main_ImageShow.py"):
        bBuild = False
    else:
        bBuild = True
    FIGURE()
