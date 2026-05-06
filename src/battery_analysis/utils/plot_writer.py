"""
图形绘制模块

提供箱线图和电压曲线绘制功能，用于电池数据可视化
"""

import logging
import csv

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from battery_analysis.utils import data_utils
from battery_analysis.utils import plot_utils

logger = logging.getLogger(__name__)


def draw_boxplot_and_curves(xlsx_word_writer, list_cpt, max_xaxis):
    """
    绘制箱线图和电压曲线

    从XlsxWordWriter实例读取配置，绘制箱线图和过滤/未过滤电压曲线并保存为PNG和SVG。

    Args:
        xlsx_word_writer: XlsxWordWriter实例，提供配置和数据
        list_cpt: 容量数据列表
        max_xaxis: X轴最大值
    """
    fontdict_label = {
        'fontsize': 9,
        'fontweight': 'bold'
    }
    medianprofile = dict(linewidth=1, color='red')

    plt.figure()

    for c in range(xlsx_word_writer.intCurrentLevelNum):
        list_box_plot = []
        list_label = []
        for v in range(xlsx_word_writer.intVoltageLevelNum):
            list_box_plot.append(list_cpt[c][v])
            list_label.append(f"{xlsx_word_writer.listVoltageLevel[v]}V")
        plt.cla()
        plt.boxplot(list_box_plot, labels=list_label,
                    medianprops=medianprofile)
        plt.title(xlsx_word_writer.listBoxplotTitle[c], fontdict=fontdict_label)
        plt.xlabel("Cutoff Voltage [V]")
        plt.ylabel("Useable Capacity [mAh]")
        plt.grid(linestyle="--", alpha=0.3)
        plt.savefig(xlsx_word_writer.listPngPath[c])
        plt.savefig(xlsx_word_writer.listSvgPath[c], dpi=1200)

    # analysis Info_Image.csv
    list_plt = []
    for c in range(xlsx_word_writer.intCurrentLevelNum):
        list_plt.append([])
        for _ in range(4):
            list_plt[c].append([])

    with open(xlsx_word_writer.strInfoImageCsvPath, mode='r', encoding='utf-8') as f:
        csvreader_info_image = csv.reader(f)
        int_per_battery_rows = 1 + xlsx_word_writer.intCurrentLevelNum * 3
        index = 0
        for row in csvreader_info_image:
            loop = index % int_per_battery_rows
            if loop != 0 and (loop % 3) != 1:
                list_plt[int((loop - 1) / 3)][((loop - 1) % 3) -
                                               1].append([float(row[i]) for i in range(len(row))])
            index += 1

    for c in range(xlsx_word_writer.intCurrentLevelNum):
        list_plt[c][2], list_plt[c][3] = data_utils.filter_data(
            list_plt[c][0], list_plt[c][1])

    title_fontdict = {
        'fontsize': 15,
        'fontweight': 'bold'
    }
    axis_fontdict = {
        'fontsize': 15
    }

    plt.figure(figsize=(15, 6))

    plt.clf()
    plot_utils.set_plt_axis(xlsx_word_writer.listTestInfo[0], max_xaxis)
    y_major_locator = MultipleLocator(0.2)
    ax = plt.gca()
    ax.yaxis.set_major_locator(y_major_locator)
    plt.title(f"Unfiltered {xlsx_word_writer.strPltName}", fontdict=title_fontdict)
    plt.xlabel("Charge [mAh]", fontdict=axis_fontdict)
    plt.ylabel("Unfiltered Battery Load Voltage [V]", fontdict=axis_fontdict)
    for b in range(xlsx_word_writer.intBatteryNum):
        for c in range(xlsx_word_writer.intCurrentLevelNum):
            plt.plot(list_plt[c][0][b], list_plt[c][1][b],
                     color=f"{xlsx_word_writer.listPltColorType[c]}", linewidth=0.5)
    plt.grid(linestyle="--", alpha=0.3)
    plt.savefig(xlsx_word_writer.strUnfilteredPngPath)
    plt.savefig(xlsx_word_writer.strUnfilteredSvgPath, dpi=1200)

    plt.clf()
    plot_utils.set_plt_axis(xlsx_word_writer.listTestInfo[0], max_xaxis)
    y_major_locator = MultipleLocator(0.2)
    ax = plt.gca()
    ax.yaxis.set_major_locator(y_major_locator)
    plt.title(f"Filtered {xlsx_word_writer.strPltName}", fontdict=title_fontdict)
    plt.xlabel("Charge [mAh]", fontdict=axis_fontdict)
    plt.ylabel("Filtered Battery Load Voltage [V]", fontdict=axis_fontdict)
    for b in range(xlsx_word_writer.intBatteryNum):
        for c in range(xlsx_word_writer.intCurrentLevelNum):
            plt.plot(list_plt[c][0][b], list_plt[c][1][b],
                     color=f"{xlsx_word_writer.listPltColorType[c]}", linewidth=0.5)
    plt.grid(linestyle="--", alpha=0.3)
    plt.savefig(xlsx_word_writer.strFilteredPngPath)
    plt.savefig(xlsx_word_writer.strFilteredSvgPath, dpi=1200)
