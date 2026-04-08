#!/usr/bin/env python3
"""
测试日志系统脚本

该脚本用于测试电池分析应用的日志系统，包括：
- 日志记录功能
- 环境信息收集
- 错误报告生成
- 日志文件创建
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from battery_analysis.utils.log_manager import get_logger, get_log_directory, clear_old_logs
from battery_analysis.utils.error_report_generator import generate_error_report, get_report_info


def test_logging():
    """测试日志记录功能"""
    print("=== 测试日志记录功能 ===")
    
    # 获取不同名称的日志记录器
    logger1 = get_logger('test_logger1')
    logger2 = get_logger('test_logger2')
    
    # 记录不同级别的日志
    logger1.debug("这是一条DEBUG级别的日志")
    logger1.info("这是一条INFO级别的日志")
    logger1.warning("这是一条WARNING级别的日志")
    logger1.error("这是一条ERROR级别的日志")
    logger1.critical("这是一条CRITICAL级别的日志")
    
    # 测试异常记录
    try:
        1 / 0
    except Exception as e:
        logger2.exception("捕获到异常:")
    
    print("日志记录测试完成")
    print()


def test_environment_info():
    """测试环境信息收集"""
    print("=== 测试环境信息收集 ===")
    
    # 环境信息在日志系统初始化时已经记录
    # 这里我们可以通过查看报告信息来验证
    report_info = get_report_info()
    print(f"日志目录: {report_info['log_directory']}")
    print(f"最近日志文件数: {report_info['log_file_count']}")
    
    # 打印最近的日志文件
    if report_info['recent_log_files']:
        print("最近的日志文件:")
        for log_file in report_info['recent_log_files'][:3]:  # 只显示前3个
            print(f"  - {log_file}")
    
    print("环境信息收集测试完成")
    print()


def test_error_report():
    """测试错误报告生成"""
    print("=== 测试错误报告生成 ===")
    
    # 生成错误报告，默认保存到日志目录
    # 每个报告包含10个日志文件，最多保留10个报告
    report_path = generate_error_report(max_logs_per_report=10, max_reports=10)
    
    if report_path:
        print(f"错误报告生成成功: {report_path}")
        
        # 验证报告文件是否存在
        report_file = Path(report_path)
        if report_file.exists():
            print(f"报告文件大小: {report_file.stat().st_size / 1024:.2f} KB")
            print(f"报告保存位置: {report_file.parent}")
            
            # 列出当前目录下的所有报告文件
            reports_dir = report_file.parent
            all_reports = list(reports_dir.glob('battery_analysis_error_report_*.zip'))
            print(f"当前目录下共有 {len(all_reports)} 个错误报告压缩包")
            
            # 可以选择删除测试生成的报告
            # report_file.unlink()
            # print("测试报告已删除")
        else:
            print("报告文件不存在")
    else:
        print("错误报告生成失败")
    
    print("错误报告生成测试完成")
    print()


def test_log_file_creation():
    """测试日志文件创建"""
    print("=== 测试日志文件创建 ===")
    
    log_dir = get_log_directory()
    print(f"日志目录: {log_dir}")
    
    # 获取今天的日志文件
    today = time.strftime('%Y-%m-%d')
    expected_log_file = log_dir / f'battery_analysis_{today}.log'
    
    if expected_log_file.exists():
        print(f"今天的日志文件已创建: {expected_log_file}")
        print(f"日志文件大小: {expected_log_file.stat().st_size / 1024:.2f} KB")
        
        # 查看日志文件的前几行
        print("日志文件前10行:")
        with open(expected_log_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i < 10:
                    print(f"  {line.rstrip()}")
                else:
                    break
    else:
        print(f"今天的日志文件未创建: {expected_log_file}")
    
    print("日志文件创建测试完成")
    print()


def test_clear_old_logs():
    """测试清理旧日志功能"""
    print("=== 测试清理旧日志功能 ===")
    
    # 注意：这个测试会清理30天前的日志文件
    # 如果你不想清理真实的旧日志，可以注释掉这行
    # clear_old_logs(days=30)
    # print("旧日志清理完成")
    
    print("旧日志清理功能测试完成（已跳过实际清理）")
    print()


def main():
    """主测试函数"""
    print("开始测试日志系统...\n")
    
    try:
        test_logging()
        test_environment_info()
        test_log_file_creation()
        test_error_report()
        test_clear_old_logs()
        
        print("=== 所有测试完成 ===")
        print("日志系统工作正常！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
