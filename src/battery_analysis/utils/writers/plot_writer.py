"""
图形绘制模块

提供箱线图和电压曲线绘制功能，用于电池数据可视化
"""

import csv
import logging

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator

from battery_analysis.utils.processors import data_utils
from battery_analysis.utils.writers import plot_utils

logger = logging.getLogger(__name__)


def draw_boxplot_and_curves(
    int_current_level_num,
    int_voltage_level_num,
    list_voltage_level,
    list_boxplot_title,
    list_png_path,
    list_svg_path,
    str_info_image_csv_path,
    str_plt_name,
    str_unfiltered_png_path,
    str_unfiltered_svg_path,
    str_filtered_png_path,
    str_filtered_svg_path,
    list_test_info,
    list_plt_color_type,
    int_battery_num,
    list_cpt,
    max_xaxis,
):
    """
    绘制箱线图和电压曲线

    从参数读取配置，绘制箱线图和过滤/未过滤电压曲线并保存为PNG和SVG。

    Args:
        int_current_level_num: 电流等级数量
        int_voltage_level_num: 电压等级数量
        list_voltage_level: 电压等级列表
        list_boxplot_title: 箱线图标题列表
        list_png_path: PNG输出路径列表
        list_svg_path: SVG输出路径列表
        str_info_image_csv_path: 图像信息CSV路径
        str_plt_name: 图表名称
        str_unfiltered_png_path: 未过滤PNG路径
        str_unfiltered_svg_path: 未过滤SVG路径
        str_filtered_png_path: 过滤后PNG路径
        str_filtered_svg_path: 过滤后SVG路径
        list_test_info: 测试信息列表
        list_plt_color_type: 绘图颜色类型列表
        int_battery_num: 电池数量
        list_cpt: 容量数据列表
        max_xaxis: X轴最大值
    """
    fontdict_label = {"fontsize": 9, "fontweight": "bold"}
    medianprofile = dict(linewidth=1, color="red")

    # 创建独立的 Figure（不使用全局 plt 状态）
    fig_boxplot = Figure()
    canvas_boxplot = FigureCanvasAgg(fig_boxplot)
    ax_boxplot = fig_boxplot.add_subplot(111)

    for c in range(int_current_level_num):
        list_box_plot = []
        list_label = []
        for v in range(int_voltage_level_num):
            list_box_plot.append(list_cpt[c][v])
            list_label.append(f"{list_voltage_level[v]}V")
        ax_boxplot.clear()
        ax_boxplot.boxplot(list_box_plot, labels=list_label, medianprops=medianprofile)
        ax_boxplot.set_title(list_boxplot_title[c], fontdict=fontdict_label)
        ax_boxplot.set_xlabel("Cutoff Voltage [V]")
        ax_boxplot.set_ylabel("Useable Capacity [mAh]")
        ax_boxplot.grid(linestyle="--", alpha=0.3)
        fig_boxplot.savefig(list_png_path[c])
        fig_boxplot.savefig(list_svg_path[c], dpi=1200)

    # analysis Info_Image.csv
    list_plt = []
    for c in range(int_current_level_num):
        list_plt.append([])
        for _ in range(4):
            list_plt[c].append([])

    with open(str_info_image_csv_path, encoding="utf-8") as f:
        csvreader_info_image = csv.reader(f)
        int_per_battery_rows = 1 + int_current_level_num * 3
        index = 0
        for row in csvreader_info_image:
            loop = index % int_per_battery_rows
            if loop != 0 and (loop % 3) != 1:
                list_plt[int((loop - 1) / 3)][((loop - 1) % 3) - 1].append(
                    [float(row[i]) for i in range(len(row))]
                )
            index += 1

    # list_plt[c] 布局：[0]=原始 charge, [1]=原始 voltage, [2]=过滤 charge, [3]=过滤 voltage
    for c in range(int_current_level_num):
        list_plt[c][2], list_plt[c][3] = data_utils.filter_data(list_plt[c][0], list_plt[c][1])

    title_fontdict = {"fontsize": 15, "fontweight": "bold"}
    axis_fontdict = {"fontsize": 15}

    # 创建独立的 Figure（不使用全局 plt 状态）
    fig_curve = Figure(figsize=(15, 6))
    canvas_curve = FigureCanvasAgg(fig_curve)
    ax_curve = fig_curve.add_subplot(111)

    # 绘制未过滤曲线
    plot_utils.set_plt_axis(list_test_info[0], max_xaxis)
    y_major_locator = MultipleLocator(0.2)
    ax_curve.yaxis.set_major_locator(y_major_locator)
    ax_curve.set_title(f"Unfiltered {str_plt_name}", fontdict=title_fontdict)
    ax_curve.set_xlabel("Charge [mAh]", fontdict=axis_fontdict)
    ax_curve.set_ylabel("Unfiltered Battery Load Voltage [V]", fontdict=axis_fontdict)
    for b in range(int_battery_num):
        for c in range(int_current_level_num):
            ax_curve.plot(
                list_plt[c][0][b],
                list_plt[c][1][b],
                color=f"{list_plt_color_type[c]}",
                linewidth=0.5,
            )
    ax_curve.grid(linestyle="--", alpha=0.3)
    fig_curve.savefig(str_unfiltered_png_path)
    fig_curve.savefig(str_unfiltered_svg_path, dpi=1200)

    # 清除并绘制过滤后曲线
    ax_curve.clear()
    plot_utils.set_plt_axis(list_test_info[0], max_xaxis)
    y_major_locator = MultipleLocator(0.2)
    ax_curve.yaxis.set_major_locator(y_major_locator)
    ax_curve.set_title(f"Filtered {str_plt_name}", fontdict=title_fontdict)
    ax_curve.set_xlabel("Charge [mAh]", fontdict=axis_fontdict)
    ax_curve.set_ylabel("Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)
    for b in range(int_battery_num):
        for c in range(int_current_level_num):
            ax_curve.plot(
                list_plt[c][2][b],
                list_plt[c][3][b],
                color=f"{list_plt_color_type[c]}",
                linewidth=0.5,
            )
    ax_curve.grid(linestyle="--", alpha=0.3)
    fig_curve.savefig(str_filtered_png_path)
    fig_curve.savefig(str_filtered_svg_path, dpi=1200)
