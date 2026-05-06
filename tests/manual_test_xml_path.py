import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 模拟BatteryChartViewerWrapper中的XML路径处理逻辑
def test_xml_path_processing(xml_path):
    """测试XML路径处理逻辑"""
    logging.info(f"测试XML路径: {xml_path}")
    
    # 获取XML所在目录
    test_profile_dir = os.path.dirname(xml_path)
    logging.info(f"XML所在目录: {test_profile_dir}")
    
    # 获取XML所在目录的上一级目录
    parent_dir = os.path.dirname(test_profile_dir)
    logging.info(f"XML上一级目录: {parent_dir}")
    
    # 定义可能的分析结果目录名称
    analysis_dir_names = ["3_analysis results", "analysis results", "Analysis Results", "3_Analysis Results"]
    
    # 尝试在XML上一级目录中寻找分析结果目录
    analysis_results_dir = None
    for dir_name in analysis_dir_names:
        analysis_dir = os.path.join(parent_dir, dir_name)
        logging.info(f"尝试分析结果目录: {analysis_dir}")
        if os.path.exists(analysis_dir):
            analysis_results_dir = analysis_dir
            logging.info(f"找到分析结果目录: {analysis_results_dir}")
            break
    
    # 如果找到分析结果目录，尝试获取最新的子目录
    if analysis_results_dir:
        subdirs = [d for d in os.listdir(analysis_results_dir) if os.path.isdir(os.path.join(analysis_results_dir, d))]
        if subdirs:
            # 按修改时间排序，获取最新的子目录
            latest_dir = max(subdirs, key=lambda d: os.path.getmtime(os.path.join(analysis_results_dir, d)))
            latest_dir_path = os.path.join(analysis_results_dir, latest_dir)
            logging.info(f"最新版本目录: {latest_dir_path}")
            
            # 检查最新目录中是否有Info_Image.csv文件
            info_image_csv = os.path.join(latest_dir_path, "Info_Image.csv")
            if os.path.exists(info_image_csv):
                logging.info(f"找到最新的Info_Image.csv文件: {info_image_csv}")
                return True, latest_dir_path
            else:
                logging.warning("最新版本目录中没有找到Info_Image.csv文件")
        else:
            logging.warning("分析结果目录中没有子目录")
    else:
        logging.warning("未找到分析结果目录")
    
    return False, None

# 测试
def main():
    # 假设用户选择的XML路径
    xml_path = "C:\\Users\\boe\\Desktop\\test\\test_profile.xml"
    logging.info("开始测试XML路径处理逻辑")
    success, data_path = test_xml_path_processing(xml_path)
    if success:
        logging.info(f"测试成功，找到数据路径: {data_path}")
    else:
        logging.info("测试失败，未找到数据路径")

if __name__ == "__main__":
    main()
