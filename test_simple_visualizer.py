import os
import sys
import logging
import tempfile
import shutil
from datetime import datetime
import time

# 设置日志配置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('test_simple')

# 添加项目路径到sys.path
sys.path.insert(0, 'c:\\Users\\boe\\Desktop\\battery-analysis\\src')

logger.info('开始简单测试visualizer...')
logger.info(f'当前工作目录: {os.getcwd()}')

# 1. 模拟分析结果目录结构
analysis_results_dir = '3_analysis results'
test_subdir = os.path.join(analysis_results_dir, f'test_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

os.makedirs(test_subdir, exist_ok=True)
logger.info(f'创建测试分析结果目录: {test_subdir}')

# 2. 创建模拟的Info_Image.csv文件 - 使用更简单的数据格式
info_image_content = """Index,时间,OBD总压(VP),电池单体电压最小值(Vmin),电池单体电压最大值(Vmax),电池单体温度最小值(Tmin),电池单体温度最大值(Tmax),SOH(%),SOC(%),电池总电流(A),累计充放电量(Ah),电池健康状态
0,0,380.5,3.25,3.35,25.5,30.2,95,80,50.2,10.5,正常
1,300,381.2,3.26,3.34,26.1,30.5,95,81,49.8,10.6,正常
2,600,381.8,3.27,3.33,26.8,30.8,95,82,49.5,10.7,正常
3,900,382.5,3.28,3.32,27.5,31.0,95,83,49.2,10.8,正常
4,1200,383.1,3.29,3.31,28.2,31.2,95,84,48.9,10.9,正常
"""

info_image_path = os.path.join(test_subdir, 'Info_Image.csv')
with open(info_image_path, 'w', encoding='utf-8') as f:
    f.write(info_image_content)

logger.info(f'创建模拟的Info_Image.csv文件: {info_image_path}')

# 3. 等待一小段时间
time.sleep(1)

# 4. 测试直接调用run_visualizer_function
logger.info('\n=== 测试: 直接调用run_visualizer_function ===')
try:
    from battery_analysis.main.main_window import run_visualizer_function
    
    logger.info('调用run_visualizer_function...')
    success = run_visualizer_function()
    
    if success:
        logger.info('测试完成：run_visualizer_function调用成功')
    else:
        logger.error('测试完成：run_visualizer_function调用失败')
    
except Exception as e:
    logger.error(f'测试失败：调用run_visualizer_function时出错 - {str(e)}', exc_info=True)

# 5. 清理测试文件
logger.info('\n清理测试文件...')
try:
    shutil.rmtree(analysis_results_dir)
    logger.info(f'删除测试分析结果目录: {analysis_results_dir}')
except Exception as e:
    logger.error(f'清理测试文件时出错 - {str(e)}')

logger.info('简单测试完成！')
