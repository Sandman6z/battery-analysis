#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Battery Chart Viewer - Fixed Version
修复了所有语法错误的核心功能版本
已优化为支持多种环境（开发、IDE、容器、PyInstaller打包）
"""

import os
import sys
import configparser
import logging
import traceback
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 导入环境检测工具
try:
    from battery_analysis.utils.environment_utils import get_environment_detector, EnvironmentType
except ImportError:
    # 如果环境检测模块不可用，使用备用方案
    get_environment_detector = None
    EnvironmentType = None

class PlotConfig:
    """
    Chart configuration class for storing configurable chart parameters
    
    Attributes:
    axis_default: Default axis range [xmin, xmax, ymin, ymax]
    axis_special: Axis range under special rules [xmin, xmax, ymin, ymax]
    """
    
    def __init__(self):
        self.axis_default = [0, 1000, 0, 5]  # [xmin, xmax, ymin, ymax]
        self.axis_special = [0, 1000, 0, 5]  # [xmin, xmax, ymin, ymax]

class BatteryChartViewer:
    """
    Chart generation and data visualization class

    This class is responsible for battery data visualization processing, including configuration file reading, data loading, filtering and chart generation.
    Supports reading actual data from CSV files or generating simulated data, and provides interactive chart interface for data analysis.

    Attributes:
    strPltName: Chart title name
    listColor: Chart color list
    maxXaxis: X-axis maximum value
    listPlt: Chart data list
    listBatteryNameSplit: Battery name list
    intBatteryNum: Number of batteries
    listAxis: Axis ranges
    listXTicks: X-axis tick values
    plot_config: Chart configuration object
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize BatteryChartViewer class, set default configuration and load user configuration
        
        Initialize chart parameters, read configuration file, and set default values. If configuration file does not exist,
        use hardcoded default values.

        Args:
        data_path: Optional, specify the directory path to load data
        """
        # 初始化环境检测器
        self.env_detector = None
        self.env_info = None
        self._init_environment_detection()
        
        self.config = configparser.ConfigParser()
        
        # Initialize default configuration
        if not self.config.has_section("PltConfig"):
            self.config.add_section("PltConfig")

        # Get project root config folder path
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.project_root = current_dir.parent.parent
        self.path = self.project_root

        # Load configuration file
        self._load_config_file()

        # Initialize chart configuration object
        self.plot_config = PlotConfig()

        # Set other initialization parameters
        self.listColor = ['#DF7040', '#0675BE', '#EDB120',
                         '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']
        self.maxXaxis = self.plot_config.axis_default[1]  # Default maximum value
        self.intBatteryNum = 0  # Default no battery data
        self.loaded_data = False  # Data loading status flag
        self.current_fig = None  # Current chart instance reference

        # Initialize axis ranges and ticks
        # [xmin, xmax, ymin, ymax]
        self.listAxis = [self.plot_config.axis_default[0], self.maxXaxis, 
                        self.plot_config.axis_default[2], self.plot_config.axis_default[3]]
        self.listXTicks = list(range(0, self.maxXaxis + 1, 100))  # X-axis tick values

        # Initialize default data structure first
        self.listPlt = []
        self.listBatteryName = []
        self.listBatteryNameSplit = []
        self.strPltPath = None
        self.strInfoImageCsvPath = None

        # Read configuration items
        self._read_configurations()

        # 如果提供了data_path，则加载数据
        if data_path:
            self.set_data_path(data_path)

        # 根据环境调整行为
        self._adapt_for_environment()

    def _init_environment_detection(self):
        """
        初始化环境检测器
        """
        try:
            if get_environment_detector:
                self.env_detector = get_environment_detector()
                self.env_info = self.env_detector.get_environment_info()
                logging.debug(f"环境检测成功: {self.env_info['environment_type']}")
        except Exception as e:
            logging.warning(f"环境检测失败: {e}")
            self.env_detector = None
            self.env_info = {}

    def _adapt_for_environment(self):
        """
        根据环境调整图表查看器的行为
        """
        if not self.env_info:
            return
            
        env_type = self.env_info.get('environment_type')
        
        if env_type == EnvironmentType.IDE:
            logging.debug("IDE环境：调整图表配置以适应开发环境")
            self._adapt_for_ide()
        elif env_type == EnvironmentType.CONTAINER:
            logging.debug("容器环境：调整图表配置以适应容器环境")
            self._adapt_for_container()
        elif env_type == EnvironmentType.PRODUCTION:
            logging.debug("生产环境：优化图表性能")
            self._adapt_for_production()

    def _adapt_for_ide(self):
        """
        IDE环境适配
        """
        # 在IDE中可能没有显示，添加调试信息
        if not self.env_info.get('gui_available', True):
            logging.warning("IDE环境且无GUI显示，图表可能无法正常显示")

    def _adapt_for_container(self):
        """
        容器环境适配
        """
        logging.debug("容器环境中运行，配置图表为无头模式")

    def _adapt_for_production(self):
        """
        生产环境适配
        """
        logging.debug("生产环境中运行，优化图表性能")

    def _load_config_file(self):
        """Load configuration file"""
        # 使用环境检测器来找到配置文件
        config_file = None
        
        if self.env_detector:
            try:
                # 尝试多个可能的配置路径
                possible_paths = [
                    self.env_detector.get_resource_path("src/Config_BatteryAnalysis.ini"),
                    self.env_detector.get_resource_path("config/Config_BatteryAnalysis.ini"),
                    self.project_root / "src" / "Config_BatteryAnalysis.ini",
                ]
                
                for path in possible_paths:
                    if path.exists():
                        config_file = path
                        break
                        
            except Exception as e:
                logging.warning(f"环境检测器加载配置文件失败: {e}")
        
        # 如果环境检测器不可用或没有找到文件，使用默认路径
        if not config_file:
            config_file = self.project_root / "src" / "Config_BatteryAnalysis.ini"
        
        if config_file and config_file.exists():
            try:
                self.config.read(config_file, encoding='utf-8')
                logging.info(f"Configuration loaded from: {config_file}")
            except Exception as e:
                logging.error(f"加载配置文件失败: {e}")
        else:
            logging.info("No configuration file found, using defaults")

    def _read_configurations(self):
        """Read and set configuration values"""
        try:
            # Set default configuration values
            if self.config.has_option("PltConfig", "axis_default"):
                axis_default_str = self.config.get("PltConfig", "axis_default")
                self.plot_config.axis_default = [float(x.strip()) for x in axis_default_str.split(',')]
                
            if self.config.has_option("PltConfig", "axis_special"):
                axis_special_str = self.config.get("PltConfig", "axis_special")
                self.plot_config.axis_special = [float(x.strip()) for x in axis_special_str.split(',')]
                
            # Update derived values
            self.maxXaxis = self.plot_config.axis_default[1]
            self.listAxis = [self.plot_config.axis_default[0], self.maxXaxis, 
                            self.plot_config.axis_default[2], self.plot_config.axis_default[3]]
            self.listXTicks = list(range(0, self.maxXaxis + 1, 100))
            
        except Exception as e:
            logging.error(f"Error reading configurations: {e}")

    def _search_for_data_files(self):
        """Search for data files in the data directory"""
        if not self.strPltPath or not os.path.exists(self.strPltPath):
            return []

        try:
            import glob
            csv_files = glob.glob(os.path.join(self.strPltPath, "*.csv"))
            logging.info(f"Found {len(csv_files)} CSV files in {self.strPltPath}")
            return csv_files
        except Exception as e:
            logging.error(f"Error searching for data files: {e}")
            return []

    def set_data_path(self, data_path: str):
        """Set the data path and search for files"""
        self.strPltPath = data_path
        self.loaded_data = False
        
        # Search for Info_Image.csv
        info_csv_path = os.path.join(data_path, "Info_Image.csv")
        if os.path.exists(info_csv_path):
            self.strInfoImageCsvPath = info_csv_path
            logging.info(f"Found Info_Image.csv: {info_csv_path}")
            
            # Load the CSV data
            if self.csv_read():
                self.loaded_data = True
        else:
            logging.info("No Info_Image.csv found")

    def load_data(self) -> bool:
        """Load data from CSV files"""
        try:
            if not self.strPltPath:
                logging.error("No data path set")
                return False
                
            # Search for data files
            data_files = self._search_for_data_files()
            
            if not data_files:
                logging.info("No data files found")
                return False
            
            # 读取Info_Image.csv文件（如果存在）
            if self.strInfoImageCsvPath and self.csv_read():
                self.loaded_data = True
                logging.info(f"Successfully loaded data from {self.strInfoImageCsvPath}")
            else:
                logging.info("No Info_Image.csv found or failed to read CSV")
                # 如果没有Info_Image.csv，我们仍然认为数据已加载（空数据）
                self.loaded_data = True
                self.intBatteryNum = 0
            
            logging.info(f"Data loading completed. Battery count: {self.intBatteryNum}")
            return True
            
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            traceback.print_exc()
            return False

    def csv_read(self):
        """Read CSV data"""
        try:
            if not self.strInfoImageCsvPath:
                return False
                
            # 读取实际的CSV数据
            import pandas as pd
            
            if not os.path.exists(self.strInfoImageCsvPath):
                logging.error(f"CSV文件不存在: {self.strInfoImageCsvPath}")
                return False
                
            # 读取CSV文件
            df = pd.read_csv(self.strInfoImageCsvPath)
            logging.info(f"成功读取CSV文件，数据行数: {len(df)}")
            
            # 存储数据到实例变量
            self.csv_data = df
            
            # 如果有Battery_ID列，统计电池数量
            if 'Battery_ID' in df.columns:
                self.intBatteryNum = df['Battery_ID'].nunique()
                self.listBatteryName = df['Battery_ID'].unique().tolist()
                logging.info(f"检测到 {self.intBatteryNum} 个电池")
            else:
                self.intBatteryNum = 1
                self.listBatteryName = ['Battery_01']
                
            return True
            
        except Exception as e:
            logging.error(f"Error reading CSV: {e}")
            traceback.print_exc()
            return False

    def _read_rules_configuration(self):
        """Read rules configuration if needed"""
        # This method can be expanded to read additional configuration rules
        pass

    def create_visualization(self):
        """Create the visualization chart"""
        try:
            if not self.loaded_data:
                logging.warning("No data loaded, cannot create visualization")
                return False
                
            # 创建真正的图表
            import matplotlib.pyplot as plt
            import numpy as np
            
            self.current_fig, ax = plt.subplots(figsize=(12, 8))
            ax.set_title("Battery Analysis Chart", fontsize=16, fontweight='bold')
            ax.set_xlabel("Time (s)", fontsize=12)
            ax.set_ylabel("Voltage (V)", fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # 如果有CSV数据，绘制实际数据
            if hasattr(self, 'csv_data') and self.csv_data is not None:
                df = self.csv_data
                
                # 检查是否有必要的列
                if ('Time(s)' in df.columns or 'Time' in df.columns) and ('Voltage(V)' in df.columns or 'Voltage' in df.columns):
                    # 标准化列名
                    time_col = 'Time(s)' if 'Time(s)' in df.columns else 'Time'
                    voltage_col = 'Voltage(V)' if 'Voltage(V)' in df.columns else 'Voltage'
                    
                    # 按电池ID分组绘制
                    if 'Battery_ID' in df.columns:
                        for i, battery_id in enumerate(df['Battery_ID'].unique()):
                            battery_data = df[df['Battery_ID'] == battery_id]
                            color = self.listColor[i % len(self.listColor)]
                            ax.plot(battery_data[time_col], battery_data[voltage_col], 
                                   label=battery_id, color=color, linewidth=2, marker='o', markersize=4)
                    else:
                        # 没有Battery_ID列，绘制所有数据
                        color = self.listColor[0]
                        ax.plot(df[time_col], df[voltage_col], 
                               label='Battery Data', color=color, linewidth=2, marker='o', markersize=4)
                    
                    ax.legend()
                    
                    # 设置坐标轴范围
                    if len(df) > 0:
                        x_max = df[time_col].max()
                        y_min = df[voltage_col].min()
                        y_max = df[voltage_col].max()
                        
                        # 添加一些边距
                        ax.set_xlim(0, x_max * 1.1)
                        ax.set_ylim(y_min - 0.1, y_max + 0.1)
                    
                    logging.info(f"成功绘制 {len(df)} 行数据")
                else:
                    logging.warning("CSV文件中缺少必要的列（Time(s), Voltage(V)）")
                    # 显示可用的列名
                    logging.warning(f"可用列名: {list(df.columns)}")
                    # 创建示例图表
                    self._create_sample_chart(ax)
            else:
                # 没有数据，创建示例图表
                logging.info("没有CSV数据，创建示例图表")
                self._create_sample_chart(ax)
            
            logging.info("Chart created successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error creating visualization: {e}")
            traceback.print_exc()
            return False
    
    def _create_sample_chart(self, ax):
        """创建示例图表"""
        import numpy as np
        
        # 生成示例数据
        x = np.linspace(0, 10, 100)
        y1 = 3.7 - 0.1 * x + 0.02 * np.sin(2 * x)  # 电池1的电压衰减
        y2 = 3.8 - 0.08 * x + 0.015 * np.cos(1.5 * x)  # 电池2的电压衰减
        
        ax.plot(x, y1, label='Battery_01 (Sample)', color=self.listColor[0], linewidth=2)
        ax.plot(x, y2, label='Battery_02 (Sample)', color=self.listColor[1], linewidth=2)
        ax.legend()
        ax.set_title("Sample Battery Analysis Chart (No Data Available)", fontsize=14, style='italic')
        
        logging.info("Created sample chart with synthetic data")

    def show_chart(self):
        """Display the chart"""
        try:
            if self.current_fig is None:
                if not self.create_visualization():
                    return False
                    
            import matplotlib.pyplot as plt
            plt.show()
            return True
            
        except Exception as e:
            logging.error(f"Error showing chart: {e}")
            traceback.print_exc()
            return False

    def plt_figure(self):
        """Display the chart - alias for show_chart()"""
        return self.show_chart()

    def save_chart(self, filename: str = "battery_chart.png"):
        """Save chart to file"""
        try:
            if self.current_fig is None:
                if not self.create_visualization():
                    return False
                    
            import matplotlib.pyplot as plt
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            logging.info(f"Chart saved to: {filename}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving chart: {e}")
            traceback.print_exc()
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current status information"""
        return {
            'loaded_data': self.loaded_data,
            'battery_count': self.intBatteryNum,
            'data_path': self.strPltPath,
            'config_loaded': len(self.config.sections()) > 0
        }

# 简单的导入测试
if __name__ == "__main__":
    print("🧪 测试BatteryChartViewer...")
    try:
        viewer = BatteryChartViewer()
        status = viewer.get_status()
        print(f"✅ BatteryChartViewer 初始化成功: {status}")
    except Exception as e:
        print(f"❌ BatteryChartViewer 初始化失败: {e}")