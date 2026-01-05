#!/usr/bin/env python3
"""
环境检测功能验证脚本

此脚本用于验证环境检测模块在不同平台和环境下的工作状态，
包括路径处理、GUI检测、环境类型识别等功能。

使用方法:
    python test_environment_detection.py
    python test_environment_detection.py --verbose
    python test_environment_detection.py --test-gui
"""

import sys
import os
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from environment_utils import (
    EnvironmentDetector, 
    get_environment_detector,
    EnvironmentType,
    PlatformType
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnvironmentDetectionTester:
    """环境检测功能测试器"""
    
    def __init__(self, verbose: bool = False):
        """初始化测试器"""
        self.verbose = verbose
        self.test_results = []
        self.detector = get_environment_detector()
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'status': status
        }
        self.test_results.append(result)
        
        if self.verbose or not success:
            logger.info("%s - %s: %s", status, test_name, message)
        else:
            logger.info("%s - %s", status, test_name)
    
    def test_basic_environment_detection(self) -> bool:
        """测试基础环境检测功能"""
        logger.info("=" * 50)
        logger.info("测试基础环境检测功能")
        logger.info("=" * 50)
        
        try:
            # 测试环境信息获取
            env_info = self.detector.get_environment_info()
            self.log_result("环境信息获取", True, f"检测到环境类型: {env_info['environment_type']}")
            
            # 验证必要字段
            required_fields = [
                'platform', 'environment_type', 'gui_available', 
                'python_executable', 'python_version', 'working_directory'
            ]
            
            for field in required_fields:
                if field in env_info:
                    self.log_result(f"字段 {field} 存在", True, f"值为: {env_info[field]}")
                else:
                    self.log_result(f"字段 {field} 存在", False, "字段缺失")
            
            # 测试平台检测
            if isinstance(env_info['platform'], PlatformType):
                self.log_result("平台类型检测", True, f"检测到平台: {env_info['platform'].value}")
            else:
                self.log_result("平台类型检测", False, "平台类型不是枚举值")
            
            # 测试环境类型检测
            if isinstance(env_info['environment_type'], EnvironmentType):
                self.log_result("环境类型检测", True, f"检测到环境: {env_info['environment_type'].value}")
            else:
                self.log_result("环境类型检测", False, "环境类型不是枚举值")
            
            return True
            
        except (AttributeError, TypeError, ValueError, OSError) as e:
            self.log_result("基础环境检测", False, f"异常: {str(e)}")
            return False
    
    def test_gui_detection(self) -> bool:
        """测试GUI检测功能"""
        logger.info("=" * 50)
        logger.info("测试GUI检测功能")
        logger.info("=" * 50)
        
        try:
            # 测试GUI可用性检测
            gui_available = self.detector._detect_gui_availability()
            self.log_result("GUI可用性检测", True, f"GUI可用: {gui_available}")
            
            # 测试显示环境检测
            display = self.detector._detect_display()
            if display:
                self.log_result("显示环境检测", True, f"检测到显示: {display}")
            else:
                self.log_result("显示环境检测", True, "无显示环境（可能为服务器环境）")
            
            # 测试GUI模式判断
            gui_mode = self.detector.is_gui_mode()
            self.log_result("GUI模式判断", True, f"GUI模式: {gui_mode}")
            
            # 测试CLI模式判断
            cli_mode = self.detector.is_cli_mode()
            self.log_result("CLI模式判断", True, f"CLI模式: {cli_mode}")
            
            # 验证GUI和CLI模式互斥
            if gui_mode != (not cli_mode):
                self.log_result("模式互斥性", False, "GUI模式和CLI模式应该互斥")
            else:
                self.log_result("模式互斥性", True, "GUI模式和CLI模式正确互斥")
            
            return True
            
        except (AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
            self.log_result("GUI检测功能", False, f"异常: {str(e)}")
            return False
    
    def test_path_handling(self) -> bool:
        """测试路径处理功能"""
        logger.info("=" * 50)
        logger.info("测试路径处理功能")
        logger.info("=" * 50)
        
        try:
            # 测试资源路径获取
            test_resource_path = self.detector.get_resource_path("test.txt")
            self.log_result("资源路径获取", True, f"资源路径: {test_resource_path}")
            
            # 验证路径有效性
            if isinstance(test_resource_path, Path):
                self.log_result("路径类型验证", True, "返回有效Path对象")
            else:
                self.log_result("路径类型验证", False, "返回的不是Path对象")
            
            # 测试项目根目录查找
            project_root = self.detector.get_environment_info()['project_root']
            if isinstance(project_root, Path) and project_root.exists():
                self.log_result("项目根目录查找", True, f"项目根目录: {project_root}")
            else:
                self.log_result("项目根目录查找", False, "项目根目录无效或不存在")
            
            # 测试当前文件目录
            current_file_dir = self.detector.get_environment_info()['current_file_dir']
            if isinstance(current_file_dir, Path) and current_file_dir.exists():
                self.log_result("当前文件目录", True, f"文件目录: {current_file_dir}")
            else:
                self.log_result("当前文件目录", False, "当前文件目录无效")
            
            return True
            
        except (AttributeError, TypeError, ValueError, OSError) as e:
            self.log_result("路径处理功能", False, f"异常: {str(e)}")
            return False
    
    def test_configuration_paths(self) -> bool:
        """测试配置路径查找"""
        logger.info("=" * 50)
        logger.info("测试配置路径查找")
        logger.info("=" * 50)
        
        try:
            # 测试配置文件路径查找
            config_path = self.detector.get_config_path("Config_BatteryAnalysis.ini")
            if config_path:
                self.log_result("配置文件查找", True, f"找到配置: {config_path}")
            else:
                self.log_result("配置文件查找", True, "未找到配置文件（正常现象）")
            
            # 测试不存在的配置文件
            non_existent_config = self.detector.get_config_path("non_existent.ini")
            if non_existent_config is None:
                self.log_result("不存在配置查找", True, "正确返回None")
            else:
                self.log_result("不存在配置查找", False, f"错误返回: {non_existent_config}")
            
            return True
            
        except (AttributeError, TypeError, ValueError, OSError) as e:
            self.log_result("配置路径查找", False, f"异常: {str(e)}")
            return False
    
    def test_environment_specific_features(self) -> bool:
        """测试环境特定功能"""
        logger.info("=" * 50)
        logger.info("测试环境特定功能")
        logger.info("=" * 50)
        
        try:
            env_info = self.detector.get_environment_info()
            env_type = env_info['environment_type']
            
            # 测试冻结环境检测
            is_frozen = env_info['is_frozen']
            self.log_result("冻结环境检测", True, f"冻结环境: {is_frozen}")
            
            # 测试MEIPASS环境（PyInstaller）
            meipass = env_info['meipass']
            if meipass:
                self.log_result("MEIPASS检测", True, f"MEIPASS: {meipass}")
            else:
                self.log_result("MEIPASS检测", True, "无MEIPASS环境（正常）")
            
            # 测试Python可执行文件路径
            python_executable = env_info['python_executable']
            if os.path.exists(python_executable):
                self.log_result("Python可执行文件", True, f"路径存在: {python_executable}")
            else:
                self.log_result("Python可执行文件", True, f"路径: {python_executable}（可能为虚拟路径）")
            
            # 测试工作目录
            working_directory = env_info['working_directory']
            if os.path.isdir(working_directory):
                self.log_result("工作目录", True, f"目录存在: {working_directory}")
            else:
                self.log_result("工作目录", False, f"目录不存在: {working_directory}")
            
            return True
            
        except (AttributeError, TypeError, ValueError, OSError) as e:
            self.log_result("环境特定功能", False, f"异常: {str(e)}")
            return False
    
    def test_cross_platform_compatibility(self) -> bool:
        """测试跨平台兼容性"""
        logger.info("=" * 50)
        logger.info("测试跨平台兼容性")
        logger.info("=" * 50)
        
        try:
            platform_type = self.detector.get_environment_info()['platform']
            
            # 验证平台类型
            valid_platforms = [PlatformType.WINDOWS, PlatformType.LINUX, PlatformType.MACOS, PlatformType.UNKNOWN]
            if platform_type in valid_platforms:
                self.log_result("平台类型有效性", True, f"平台类型: {platform_type.value}")
            else:
                self.log_result("平台类型有效性", False, f"无效平台类型: {platform_type}")
            
            # 测试路径分隔符处理
            test_path = "config/test_file.ini"
            resource_path = self.detector.get_resource_path(test_path)
            
            # 在不同平台上路径应该能正确处理
            if '\\' in str(resource_path) or '/' in str(resource_path):
                self.log_result("路径分隔符处理", True, "路径分隔符正确处理")
            else:
                self.log_result("路径分隔符处理", False, "路径分隔符处理异常")
            
            return True
            
        except (AttributeError, TypeError, ValueError, OSError) as e:
            self.log_result("跨平台兼容性", False, f"异常: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        logger.info("=" * 50)
        logger.info("测试错误处理")
        logger.info("=" * 50)
        
        try:
            # 测试多次调用相同方法
            env_info_1 = self.detector.get_environment_info()
            env_info_2 = self.detector.get_environment_info()
            
            if env_info_1 == env_info_2:
                self.log_result("缓存一致性", True, "多次调用返回一致结果")
            else:
                self.log_result("缓存一致性", False, "多次调用返回不一致结果")
            
            # 测试无效路径处理
            invalid_path = self.detector.get_resource_path("../../../invalid_path")
            if isinstance(invalid_path, Path):
                self.log_result("无效路径处理", True, "无效路径正确处理")
            else:
                self.log_result("无效路径处理", False, "无效路径处理异常")
            
            return True
            
        except (AttributeError, TypeError, ValueError, OSError) as e:
            self.log_result("错误处理", False, f"异常: {str(e)}")
            return False
    
    def generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        logger.info("=" * 50)
        logger.info("生成测试报告")
        logger.info("=" * 50)
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        # 按测试组分类
        test_groups = {}
        for result in self.test_results:
            test_name = result['test_name']
            if '基础' in test_name or '环境检测' in test_name:
                group = '基础环境检测'
            elif 'GUI' in test_name or '显示' in test_name:
                group = 'GUI检测'
            elif '路径' in test_name:
                group = '路径处理'
            elif '配置' in test_name:
                group = '配置路径'
            elif '环境' in test_name or '冻结' in test_name or 'MEIPASS' in test_name or 'Python' in test_name or '工作' in test_name:
                group = '环境特定功能'
            elif '平台' in test_name or '兼容' in test_name:
                group = '跨平台兼容性'
            elif '错误' in test_name or '缓存' in test_name:
                group = '错误处理'
            else:
                group = '其他'
            
            if group not in test_groups:
                test_groups[group] = {'passed': 0, 'failed': 0, 'total': 0}
            
            test_groups[group]['total'] += 1
            if result['success']:
                test_groups[group]['passed'] += 1
            else:
                test_groups[group]['failed'] += 1
        
        # 生成报告
        report = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'environment_info': self.detector.get_environment_info(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            'test_groups': test_groups,
            'detailed_results': self.test_results,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于环境类型生成建议
        env_info = self.detector.get_environment_info()
        env_type = env_info['environment_type']
        
        if env_type == EnvironmentType.IDE:
            recommendations.append("当前在IDE环境中，建议测试GUI显示功能是否正常")
            recommendations.append("确保IDE支持GUI应用运行（如PyCharm, VS Code等）")
        
        elif env_type == EnvironmentType.CONTAINER:
            recommendations.append("当前在容器环境中，建议使用无头模式")
            recommendations.append("确保容器配置了适当的显示环境变量（如DISPLAY）")
        
        elif env_type == EnvironmentType.PRODUCTION:
            recommendations.append("当前在生产环境中，确保所有资源文件正确打包")
            recommendations.append("验证PyInstaller打包后的资源路径访问")
        
        # 基于GUI可用性生成建议
        if not env_info['gui_available']:
            recommendations.append("当前环境不支持GUI，建议使用命令行模式")
            recommendations.append("考虑使用静态图表生成功能")
        
        # 基于平台生成建议
        platform = env_info['platform']
        if platform == PlatformType.LINUX:
            recommendations.append("Linux环境下确保DISPLAY环境变量正确设置")
            recommendations.append("考虑在服务器环境中使用Agg后端")
        
        return recommendations
    
    def print_summary(self, report: Dict[str, Any]):
        """打印测试摘要"""
        logger.info("=" * 60)
        logger.info("环境检测功能测试摘要")
        logger.info("=" * 60)
        
        summary = report['summary']
        logger.info("总测试数: %s", summary['total_tests'])
        logger.info("通过测试: %s", summary['passed_tests'])
        logger.info("失败测试: %s", summary['failed_tests'])
        logger.info("成功率: %s", summary['success_rate'])
        
        logger.info("\n各测试组结果:")
        for group_name, group_result in report['test_groups'].items():
            success_rate = (group_result['passed'] / group_result['total'] * 100) if group_result['total'] > 0 else 0
            logger.info("  %s: %s/%s (%s%)", group_name, group_result['passed'], group_result['total'], success_rate:.1f)
        
        logger.info("\n环境信息:")
        env_info = report['environment_info']
        logger.info("  平台: %s", env_info['platform'].value)
        logger.info("  环境类型: %s", env_info['environment_type'].value)
        logger.info("  GUI可用: %s", env_info['gui_available'])
        logger.info("  冻结环境: %s", env_info['is_frozen'])
        logger.info("  Python路径: %s", env_info['python_executable'])
        logger.info("  工作目录: %s", env_info['working_directory'])
        
        if report['recommendations']:
            logger.info("\n改进建议:")
            for i, rec in enumerate(report['recommendations'], 1):
                logger.info("  %s. %s", i, rec)
    
    def save_report(self, report: Dict[str, Any], output_file: str = None):
        """保存测试报告到文件"""
        if output_file is None:
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"environment_detection_test_report_{timestamp}.json"
        
        report_path = Path.cwd() / output_file
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info("测试报告已保存到: %s", report_path)
            return str(report_path)
        except (IOError, OSError, ValueError, TypeError, UnicodeError) as e:
            logger.error("保存测试报告失败: %s", e)
            return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="环境检测功能验证脚本")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--test-gui", action="store_true", help="测试GUI相关功能")
    parser.add_argument("--save-report", "-s", help="保存测试报告到指定文件")
    
    args = parser.parse_args()
    
    logger.info("开始环境检测功能验证")
    logger.info("命令行参数: %s", args)
    
    # 创建测试器
    tester = EnvironmentDetectionTester(verbose=args.verbose)
    
    # 运行所有测试
    test_methods = [
        tester.test_basic_environment_detection,
        tester.test_gui_detection,
        tester.test_path_handling,
        tester.test_configuration_paths,
        tester.test_environment_specific_features,
        tester.test_cross_platform_compatibility,
        tester.test_error_handling,
    ]
    
    for test_method in test_methods:
        try:
            test_method()
        except (AttributeError, TypeError, ValueError, OSError, RuntimeError) as e:
            logger.error("测试方法 %s 执行失败: %s", test_method.__name__, e)
    
    # 生成和显示报告
    report = tester.generate_test_report()
    tester.print_summary(report)
    
    # 保存报告
    if args.save_report:
        report_file = tester.save_report(report, args.save_report)
        if report_file:
            print(f"\n详细报告已保存到: {report_file}")
    
    # 返回适当的退出码
    failed_tests = sum(1 for result in tester.test_results if not result['success'])
    if failed_tests > 0:
        logger.warning("检测到 %s 个失败的测试", failed_tests)
        sys.exit(1)
    else:
        logger.info("所有测试通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()
