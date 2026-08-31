#!/usr/bin/env python3
"""测试图表嵌入功能的脚本"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from battery_analysis.main.battery_chart_viewer import BatteryChartViewer


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Chart Embedding")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建图表容器
        self.chart_container = QWidget()
        self.chart_container.setMinimumSize(800, 600)
        layout.addWidget(self.chart_container)

        # 创建控制面板
        self.chart_control_panel = QWidget()
        self.chart_control_panel.setMinimumWidth(150)
        self.chart_control_panel.setMaximumWidth(200)
        layout.addWidget(self.chart_control_panel)

        # 创建测试按钮
        test_btn = QPushButton("Test Embed Chart")
        test_btn.clicked.connect(self.test_embed)
        layout.addWidget(test_btn)

        # 创建viewer实例
        self.viewer = BatteryChartViewer(auto_search=False)

    def test_embed(self):
        """测试嵌入图表"""
        print("Testing chart embedding...")

        # 尝试嵌入图表（没有数据）
        result = self.viewer.embed_to_widget(self.chart_container)

        if result is not None:
            fig, canvas, filter_checkbox, scroll_area, battery_checkboxes = result
            print("Chart embedded successfully!")
            print(f"  fig: {fig}")
            print(f"  canvas: {canvas}")
            print(f"  filter_checkbox: {filter_checkbox}")
            print(f"  scroll_area: {scroll_area}")
            print(f"  battery_checkboxes: {battery_checkboxes}")
        else:
            print("Chart embedding returned None (no data available)")


def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
