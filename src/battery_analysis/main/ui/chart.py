"""
电池数据分析图表显示模块

本模块提供了用于电池数据可视化的图表绘制功能。它能够根据处理后的电池数据，
生成交互式图表，并提供各种交互控件以增强用户体验。

主要功能：
- 初始化图表和坐标轴
- 绘制电池数据曲线
- 添加交互控件（过滤按钮、电池选择按钮等）
- 实现数据点悬停功能
- 显示错误信息图表
"""

import os
import logging
import traceback
import math

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.widgets import CheckButtons

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Chart:
    """
    图表生成和数据可视化类
    
    这个类负责电池数据的可视化处理，包括图表初始化、曲线绘制和交互控件添加。
    """
    
    def __init__(self, data_processor, config_manager):
        """
        初始化图表类
        
        Args:
            data_processor: 数据处理器实例，包含处理后的电池数据
            config_manager: 配置管理器实例，包含图表配置
        """
        self.data_processor = data_processor
        self.config_manager = config_manager
        self.listColor = ['#DF7040', '#0675BE', '#EDB120', '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']
        
        # 从数据处理器获取数据
        self.listPlt = data_processor.listPlt
        self.listBatteryName = data_processor.listBatteryName
        self.listBatteryNameSplit = data_processor.listBatteryNameSplit
        self.intBatteryNum = data_processor.intBatteryNum
        
        # 从配置管理器获取配置
        self.strPltName = config_manager.strPltName
        self.intCurrentLevelNum = config_manager.intCurrentLevelNum
        self.maxXaxis = config_manager.maxXaxis
        self.listCoinCell = config_manager.listCoinCell
        self.listPouchCell = config_manager.listPouchCell
        
        # 坐标轴设置
        self.listAxis = None
        self.listXTicks = None
        
        # 设置坐标轴范围和刻度
        self._set_axis_config()
    
    def _set_axis_config(self):
        """
        设置坐标轴范围和刻度
        """
        bMatchSpecificationType = False
        if len(self.strPltName.split(" ")) > 4:
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
        
        if not bMatchSpecificationType:
            logging.warning("未找到匹配的规格类型，使用默认配置继续展示")
            # 设置默认的规格参数
            self.intCurrentLevelNum = 3
            self.intMaxXaxis = 5000
            self.listXTicks = list(range(0, 5001, 500))
            self.listAxis = [0, self.intMaxXaxis, 2.5, 4.5]  # 设置默认坐标轴范围
    
    def plt_figure(self):
        """
        创建并显示电池数据图表，包含交互控件以切换数据显示
        """
        try:
            logging.info("开始绘制图表，仅使用CSV文件中的真实数据")
            
            # 执行多层次的数据有效性检查
            if self.intBatteryNum <= 0:
                logging.error("严重错误: 没有有效的电池数据可供显示")
                self._show_error_plot()
                return
            
            # 检查必要的数据结构是否有效
            if not hasattr(self, 'listPlt') or not self.listPlt:
                logging.error("严重错误: 电池数据结构未初始化或为空")
                self._show_error_plot()
                return
            
            # 初始化图表和轴
            try:
                fig, ax, title_fontdict, axis_fontdict = self._initialize_figure()
                if fig is None or ax is None:
                    raise ValueError("无法初始化图表或坐标轴")
            except Exception as init_error:
                logging.error(f"图表初始化失败: {str(init_error)}")
                self._show_error_plot()
                return
            
            # 绘制电池数据曲线
            try:
                lines_unfiltered, lines_filtered = self._plot_battery_curves(ax)
                valid_data_found = bool(lines_filtered) or bool(lines_unfiltered)
                
                if valid_data_found:
                    logging.info(f"成功绘制了 {len(lines_filtered)} 条过滤曲线和 {len(lines_unfiltered)} 条原始曲线")
            except Exception as plot_error:
                logging.error(f"绘制电池曲线时出错: {str(plot_error)}")
                lines_unfiltered, lines_filtered = [], []
                valid_data_found = False
            
            # 检查是否成功绘制了曲线
            if not valid_data_found:
                logging.error("严重错误: 无法绘制任何电池数据曲线")
                self._show_error_plot()
                return
            
            # 添加交互控件
            try:
                check_filter = self._add_filter_button(fig, ax, lines_unfiltered, lines_filtered, title_fontdict, axis_fontdict)
                check_line1, check_line2 = self._add_battery_selection_buttons(
                    fig, check_filter, lines_unfiltered, lines_filtered
                )
                self._add_hover_functionality(fig, ax, lines_filtered, lines_unfiltered, check_filter)
                logging.info("成功添加图表交互控件")
            except Exception as ui_error:
                logging.warning(f"添加交互控件时出错: {str(ui_error)}")
                # 即使交互控件添加失败，仍然尝试显示图表
            
            # 添加快捷键提示
            fig.text(0.01, 0.98, "快捷键: 滚轮缩放, 鼠标拖拽平移, 右键重置视图", fontsize=8)
            
            logging.info("图表创建完成，显示CSV文件中的真实电池测试数据")
            plt.show()
        
        except Exception as e:
            logging.error(f"严重错误: 绘制图表时发生未预期的异常: {str(e)}")
            logging.error(f"错误类型: {type(e).__name__}")
            traceback.print_exc()
            self._show_error_plot()
    
    def _initialize_figure(self):
        """
        初始化图表和坐标轴
        
        Returns:
            tuple: 图表对象、坐标轴对象、标题字体设置、坐标轴字体设置
        """
        try:
            fig = plt.figure(figsize=(14, 9), dpi=100)
            ax = fig.add_subplot(111)
            
            # 设置字体和颜色
            title_fontdict = {'fontsize': 16, 'fontweight': 'bold', 'color': '#333333'}
            axis_fontdict = {'fontsize': 12, 'fontweight': 'bold', 'color': '#333333'}
            
            # 设置标题
            ax.set_title(self.strPltName, fontdict=title_fontdict, pad=20)
            
            # 设置坐标轴标签
            ax.set_xlabel('Charge (mAh)', fontdict=axis_fontdict, labelpad=15)
            ax.set_ylabel('Voltage (V)', fontdict=axis_fontdict, labelpad=15)
            
            # 设置坐标轴范围
            ax.set_xlim(self.listAxis[0], self.listAxis[1])
            ax.set_ylim(self.listAxis[2], self.listAxis[3])
            
            # 设置刻度标签大小
            plt.tick_params(axis='both', which='major', labelsize=10)
            
            # 设置网格线
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # 设置X轴主刻度
            if self.listXTicks:
                ax.set_xticks(self.listXTicks)
            
            return fig, ax, title_fontdict, axis_fontdict
            
        except Exception as e:
            logging.error(f"初始化图表时出错: {str(e)}")
            return None, None, None, None
    
    def _plot_battery_curves(self, ax):
        """
        绘制电池数据曲线
        
        Args:
            ax: 坐标轴对象
            
        Returns:
            tuple: 未过滤曲线列表、过滤曲线列表
        """
        lines_unfiltered = []
        lines_filtered = []
        
        try:
            # 遍历每个电池和电流级别绘制曲线
            for b in range(self.intBatteryNum):
                if b >= len(self.listBatteryNameSplit):
                    continue
                    
                battery_name = self.listBatteryNameSplit[b]
                
                for c in range(self.intCurrentLevelNum):
                    if c >= len(self.listPlt) or not self.listPlt[c]:
                        continue
                        
                    # 绘制过滤后的数据
                    if len(self.listPlt[c]) > 2 and self.listPlt[c][2] and b < len(self.listPlt[c][2]):
                        try:
                            # 仅绘制有有效长度的数据
                            if len(self.listPlt[c][2][b]) > 0 and len(self.listPlt[c][3][b]) > 0:
                                line, = ax.plot(
                                    self.listPlt[c][2][b],
                                    self.listPlt[c][3][b],
                                    color=self.listColor[b % len(self.listColor)],
                                    linewidth=2,
                                    label=f"{battery_name} ({self.config_manager.listPulseCurrentLevel[c]}mA)"
                                )
                                lines_filtered.append(line)
                        except Exception as e:
                            logging.warning(f"绘制电池 {b} 电流级别 {c} 的过滤数据时出错: {str(e)}")
                            
                    # 绘制原始数据（默认隐藏）
                    if len(self.listPlt[c]) > 1 and self.listPlt[c][0] and b < len(self.listPlt[c][0]):
                        try:
                            # 仅绘制有有效长度的数据
                            if len(self.listPlt[c][0][b]) > 0 and len(self.listPlt[c][1][b]) > 0:
                                line, = ax.plot(
                                    self.listPlt[c][0][b],
                                    self.listPlt[c][1][b],
                                    color=self.listColor[b % len(self.listColor)],
                                    linestyle='--',
                                    alpha=0.3,
                                    linewidth=1,
                                    label=f"{battery_name} ({self.config_manager.listPulseCurrentLevel[c]}mA) [原始]"
                                )
                                line.set_visible(False)  # 默认隐藏原始数据
                                lines_unfiltered.append(line)
                        except Exception as e:
                            logging.warning(f"绘制电池 {b} 电流级别 {c} 的原始数据时出错: {str(e)}")
            
            # 添加图例
            if lines_filtered:
                ax.legend(loc='upper right', fontsize=9, frameon=True, shadow=False)
            
            return lines_unfiltered, lines_filtered
            
        except Exception as e:
            logging.error(f"绘制电池曲线时发生错误: {str(e)}")
            return [], []
    
    def _add_filter_button(self, fig, ax, lines_unfiltered, lines_filtered, title_fontdict, axis_fontdict):
        """
        添加过滤数据切换按钮
        
        Args:
            fig: 图表对象
            ax: 坐标轴对象
            lines_unfiltered: 未过滤曲线列表
            lines_filtered: 过滤曲线列表
            title_fontdict: 标题字体设置
            axis_fontdict: 坐标轴字体设置
            
        Returns:
            CheckButtons: 过滤按钮对象
        """
        try:
            # 创建过滤按钮
            ax_filter = fig.add_axes([0.81, 0.94, 0.15, 0.05])
            check_filter = CheckButtons(ax_filter, ['显示原始数据'], [False])
            
            # 设置按钮标签字体
            for label in check_filter.labels:
                label.set_fontsize(9)
            
            # 定义按钮点击事件
            def filter_button_clicked(label):
                b_visible = check_filter.get_status()[0]
                # 切换原始数据可见性
                for line in lines_unfiltered:
                    line.set_visible(b_visible)
                # 如果显示原始数据，隐藏过滤数据
                for line in lines_filtered:
                    line.set_visible(not b_visible)
                plt.draw()
            
            # 连接按钮点击事件
            check_filter.on_clicked(filter_button_clicked)
            
            return check_filter
            
        except Exception as e:
            logging.error(f"添加过滤按钮时出错: {str(e)}")
            return None
    
    def _add_battery_selection_buttons(self, fig, check_filter, lines_unfiltered, lines_filtered):
        """
        添加电池选择按钮
        
        Args:
            fig: 图表对象
            check_filter: 过滤按钮对象
            lines_unfiltered: 未过滤曲线列表
            lines_filtered: 过滤曲线列表
            
        Returns:
            tuple: 电池选择按钮1, 电池选择按钮2
        """
        try:
            # 这里可以根据需要添加电池选择按钮
            # 由于原始代码中没有完整实现这部分功能，这里保留框架
            return None, None
            
        except Exception as e:
            logging.error(f"添加电池选择按钮时出错: {str(e)}")
            return None, None
    
    def _add_hover_functionality(self, fig, ax, lines_filtered, lines_unfiltered, check_filter):
        """
        添加数据点悬停功能
        
        Args:
            fig: 图表对象
            ax: 坐标轴对象
            lines_filtered: 过滤曲线列表
            lines_unfiltered: 未过滤曲线列表
            check_filter: 过滤按钮对象
        """
        try:
            # 这里可以根据需要添加悬停功能
            # 由于原始代码中没有完整实现这部分功能，这里保留框架
            pass
            
        except Exception as e:
            logging.error(f"添加悬停功能时出错: {str(e)}")
    
    def _show_error_plot(self, title=None, main_message=None, details=None):
        """
        显示详细的错误信息图表，提供清晰的错误反馈和故障排除建议
        
        Args:
            title (str, optional): 错误标题，默认为"数据错误"
            main_message (str, optional): 主要错误信息，默认为"无法加载或显示电池数据"
            details (str, optional): 详细错误信息和故障排除建议
        """
        try:
            # 设置默认错误信息
            if title is None:
                title = "数据错误"
            if main_message is None:
                main_message = "无法加载或显示电池数据"
            if details is None:
                details = "1. CSV文件是否存在且格式正确\n"
                details += "2. 配置文件是否正确配置\n"
                details += "3. 文件路径是否包含中文字符或特殊字符\n"
                details += "4. CSV文件是否包含有效的电池测试数据"
            
            # 创建错误图表
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 隐藏坐标轴
            ax.axis('off')
            
            # 设置标题和文本
            ax.text(0.5, 0.7, title, fontsize=18, fontweight='bold', color='red', ha='center')
            ax.text(0.5, 0.5, main_message, fontsize=14, color='black', ha='center')
            ax.text(0.5, 0.3, details, fontsize=12, color='gray', ha='center', va='top')
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            logging.error(f"显示错误图表时出错: {str(e)}")
            print(f"严重错误: {main_message}\n{details}")