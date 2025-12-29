#!/usr/bin/env python3
"""
最终环境检测验证脚本

此脚本用于最终验证环境检测功能的完整性和稳定性，
测试所有主要功能点并生成详细的验证报告。

使用方法:
    python test_environment_final.py
    python test_environment_final.py --detailed
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


class FinalEnvironmentValidator:
    """最终环境验证器"""
    
    def __init__(self, detailed: bool = False):
        """初始化验证器"""
        self.detailed = detailed
        self.test_results = []
        self.critical_tests_passed = 0
        self.total_tests = 0
        self.detector = get_environment_detector()
        
    def log_result(self, test_category: str, test_name: str, success: bool, details: str = "", is_critical: bool = False):
        """记录测试结果"""
        self.total_tests += 1
        if success and is_critical:
            self.critical_tests_passed += 1
            
        status = "✅ PASS" if success else "❌ FAIL"
        marker = "🔴" if is_critical else "⚪"
        
        result = {
            'category': test_category,
            'test_name': test_name,
            'success': success,
            'details': details,
            'is_critical': is_critical,
            'status': status,
            'marker': marker
        }
        self.test_results.append(result)
        
        if self.detailed or not success or is_critical:
            logger.info(f"{status} {marker} [{test_category}] {test_name}: {details}")
        else:
            logger.info(f"{status} {marker} [{test_category}] {test_name}")
    
    def validate_core_functionality(self) -> bool:
        """验证核心功能"""
        logger.info("=" * 60)
        logger.info("验证核心功能")
        logger.info("=" * 60)
        
        success = True
        
        try:
            # 核心测试1: 环境信息获取
            env_info = self.detector.get_environment_info()
            self.log_result(
                "核心功能", "环境信息获取", 
                env_info is not None and len(env_info) > 0,
                f"获取到 {len(env_info)} 个环境属性", 
                is_critical=True
            )
            
            # 核心测试2: 平台检测
            platform = self.detector.get_environment_info()['platform']
            platform_valid = isinstance(platform, PlatformType)
            self.log_result(
                "核心功能", "平台检测有效性", 
                platform_valid,
                f"检测到平台: {platform.value if platform_valid else '无效'}",
                is_critical=True
            )
            
            # 核心测试3: 环境类型检测
            env_type = self.detector.get_environment_info()['environment_type']
            env_type_valid = isinstance(env_type, EnvironmentType)
            self.log_result(
                "核心功能", "环境类型检测有效性", 
                env_type_valid,
                f"检测到环境: {env_type.value if env_type_valid else '无效'}",
                is_critical=True
            )
            
            # 核心测试4: GUI可用性检测
            gui_available = self.detector.get_environment_info()['gui_available']
            self.log_result(
                "核心功能", "GUI可用性检测", 
                isinstance(gui_available, bool),
                f"GUI可用: {gui_available}",
                is_critical=True
            )
            
            # 核心测试5: 路径处理
            resource_path = self.detector.get_resource_path("test.txt")
            path_valid = isinstance(resource_path, Path)
            self.log_result(
                "核心功能", "路径处理功能", 
                path_valid,
                f"资源路径: {resource_path}",
                is_critical=True
            )
            
        except Exception as e:
            self.log_result("核心功能", "核心功能验证", False, f"异常: {str(e)}", is_critical=True)
            success = False
        
        return success
    
    def validate_environment_detection(self) -> bool:
        """验证环境检测准确性"""
        logger.info("=" * 60)
        logger.info("验证环境检测准确性")
        logger.info("=" * 60)
        
        success = True
        
        try:
            env_info = self.detector.get_environment_info()
            
            # 测试1: 验证当前环境检测
            current_env = env_info['environment_type']
            expected_env = EnvironmentType.IDE  # 在IDE中运行
            
            if current_env == expected_env:
                self.log_result("环境检测", "当前环境类型", True, f"正确检测为: {current_env.value}")
            else:
                self.log_result("环境检测", "当前环境类型", False, f"期望: {expected_env.value}, 实际: {current_env.value}")
                success = False
            
            # 测试2: 验证平台检测
            current_platform = env_info['platform']
            expected_platform = PlatformType.WINDOWS  # Windows系统
            
            if current_platform == expected_platform:
                self.log_result("环境检测", "当前平台类型", True, f"正确检测为: {current_platform.value}")
            else:
                self.log_result("环境检测", "当前平台类型", False, f"期望: {expected_platform.value}, 实际: {current_platform.value}")
            
            # 测试3: 验证GUI检测逻辑
            gui_should_be_available = current_platform == PlatformType.WINDOWS
            gui_actually_available = env_info['gui_available']
            
            if gui_should_be_available == gui_actually_available:
                self.log_result("环境检测", "GUI检测逻辑", True, f"GUI检测逻辑正确: {gui_actually_available}")
            else:
                self.log_result("环境检测", "GUI检测逻辑", False, f"期望: {gui_should_be_available}, 实际: {gui_actually_available}")
            
            # 测试4: 验证路径一致性
            project_root = env_info['project_root']
            current_file_dir = env_info['current_file_dir']
            
            if isinstance(project_root, Path) and isinstance(current_file_dir, Path):
                self.log_result("环境检测", "路径类型一致性", True, "所有路径都是Path对象")
            else:
                self.log_result("环境检测", "路径类型一致性", False, "路径类型不一致")
                success = False
            
        except Exception as e:
            self.log_result("环境检测", "环境检测验证", False, f"异常: {str(e)}")
            success = False
        
        return success
    
    def validate_gui_functionality(self) -> bool:
        """验证GUI功能"""
        logger.info("=" * 60)
        logger.info("验证GUI功能")
        logger.info("=" * 60)
        
        success = True
        
        try:
            # 测试1: GUI模式判断
            gui_mode = self.detector.is_gui_mode()
            self.log_result("GUI功能", "GUI模式判断", isinstance(gui_mode, bool), f"GUI模式: {gui_mode}")
            
            # 测试2: CLI模式判断
            cli_mode = self.detector.is_cli_mode()
            self.log_result("GUI功能", "CLI模式判断", isinstance(cli_mode, bool), f"CLI模式: {cli_mode}")
            
            # 测试3: 模式互斥性
            if gui_mode != (not cli_mode):
                self.log_result("GUI功能", "模式互斥性", False, "GUI模式和CLI模式应该互斥")
                success = False
            else:
                self.log_result("GUI功能", "模式互斥性", True, "模式互斥性正确")
            
            # 测试4: 显示环境检测
            display = self.detector._detect_display()
            display_valid = display is None or isinstance(display, str)
            self.log_result("GUI功能", "显示环境检测", display_valid, f"显示环境: {display}")
            
        except Exception as e:
            self.log_result("GUI功能", "GUI功能验证", False, f"异常: {str(e)}")
            success = False
        
        return success
    
    def validate_resource_management(self) -> bool:
        """验证资源管理"""
        logger.info("=" * 60)
        logger.info("验证资源管理")
        logger.info("=" * 60)
        
        success = True
        
        try:
            # 测试1: 资源路径处理
            test_resources = [
                "config/test.ini",
                "data/test.csv",
                "locale/zh_CN/messages.po",
                "src/main.py"
            ]
            
            for resource in test_resources:
                resource_path = self.detector.get_resource_path(resource)
                if isinstance(resource_path, Path):
                    self.log_result("资源管理", f"资源路径-{resource}", True, f"路径: {resource_path}")
                else:
                    self.log_result("资源管理", f"资源路径-{resource}", False, f"无效路径: {resource_path}")
                    success = False
            
            # 测试2: 配置文件查找
            config_path = self.detector.get_config_path("test.ini")
            config_valid = config_path is None or isinstance(config_path, Path)
            self.log_result("资源管理", "配置文件查找", config_valid, f"配置路径: {config_path}")
            
            # 测试3: 国际化文件查找
            locale_path = self.detector.get_locale_path("test.po")
            locale_valid = locale_path is None or isinstance(locale_path, Path)
            self.log_result("资源管理", "国际化文件查找", locale_valid, f"国际化路径: {locale_path}")
            
        except Exception as e:
            self.log_result("资源管理", "资源管理验证", False, f"异常: {str(e)}")
            success = False
        
        return success
    
    def validate_stability(self) -> bool:
        """验证稳定性"""
        logger.info("=" * 60)
        logger.info("验证稳定性")
        logger.info("=" * 60)
        
        success = True
        
        try:
            # 测试1: 多次调用一致性
            env_info_1 = self.detector.get_environment_info()
            env_info_2 = self.detector.get_environment_info()
            
            if env_info_1 == env_info_2:
                self.log_result("稳定性", "多次调用一致性", True, "多次调用结果一致")
            else:
                self.log_result("稳定性", "多次调用一致性", False, "多次调用结果不一致")
                success = False
            
            # 测试2: 缓存机制
            env_info_3 = self.detector.get_environment_info()
            if id(env_info_1) == id(env_info_3):
                self.log_result("稳定性", "缓存机制", True, "正确使用缓存")
            else:
                self.log_result("稳定性", "缓存机制", False, "缓存机制可能有问题")
            
            # 测试3: 异常恢复
            try:
                original_platform = platform.system
                # 模拟异常
                import platform
                platform.system = lambda: exec('raise Exception("Test exception")')
                
                detector_backup = EnvironmentDetector()
                backup_platform = detector_backup._detect_platform()
                
                if backup_platform == PlatformType.UNKNOWN:
                    self.log_result("稳定性", "异常恢复", True, "异常时正确返回UNKNOWN")
                else:
                    self.log_result("稳定性", "异常恢复", False, f"异常时返回: {backup_platform}")
                    success = False
                
                # 恢复
                platform.system = original_platform
                
            except Exception as e:
                self.log_result("稳定性", "异常恢复", False, f"异常处理失败: {str(e)}")
                success = False
            
        except Exception as e:
            self.log_result("稳定性", "稳定性验证", False, f"异常: {str(e)}")
            success = False
        
        return success
    
    def validate_integration(self) -> bool:
        """验证集成功能"""
        logger.info("=" * 60)
        logger.info("验证集成功能")
        logger.info("=" * 60)
        
        success = True
        
        try:
            # 测试1: 全局检测器
            global_detector = get_environment_detector()
            if global_detector is not None:
                self.log_result("集成功能", "全局检测器", True, "全局检测器正常工作")
            else:
                self.log_result("集成功能", "全局检测器", False, "全局检测器为空")
                success = False
            
            # 测试2: 便捷函数
            try:
                resource_path = get_resource_path("test.txt")
                self.log_result("集成功能", "便捷函数-get_resource_path", 
                              isinstance(resource_path, Path), f"路径: {resource_path}")
            except Exception as e:
                self.log_result("集成功能", "便捷函数-get_resource_path", False, f"异常: {str(e)}")
                success = False
            
            try:
                config_path = get_config_path("test.ini")
                self.log_result("集成功能", "便捷函数-get_config_path", 
                              config_path is None or isinstance(config_path, Path), f"路径: {config_path}")
            except Exception as e:
                self.log_result("集成功能", "便捷函数-get_config_path", False, f"异常: {str(e)}")
                success = False
            
            try:
                gui_available = is_gui_available()
                self.log_result("集成功能", "便捷函数-is_gui_available", 
                              isinstance(gui_available, bool), f"GUI可用: {gui_available}")
            except Exception as e:
                self.log_result("集成功能", "便捷函数-is_gui_available", False, f"异常: {str(e)}")
                success = False
            
        except Exception as e:
            self.log_result("集成功能", "集成功能验证", False, f"异常: {str(e)}")
            success = False
        
        return success
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        logger.info("=" * 60)
        logger.info("生成验证报告")
        logger.info("=" * 60)
        
        # 统计测试结果
        total_tests = self.total_tests
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        critical_passed = self.critical_tests_passed
        
        # 按类别分类
        categories = {}
        for result in self.test_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0, 'total': 0, 'critical_passed': 0}
            
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
            
            if result['is_critical'] and result['success']:
                categories[category]['critical_passed'] += 1
        
        # 生成结论
        conclusions = self._generate_final_conclusions(passed_tests, total_tests, critical_passed)
        
        # 生成报告
        report = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'validation_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                'critical_tests_passed': critical_passed,
                'critical_tests_total': len([r for r in self.test_results if r['is_critical']]),
                'overall_status': 'PASS' if passed_tests == total_tests else 'PARTIAL' if passed_tests > total_tests * 0.8 else 'FAIL'
            },
            'categories': categories,
            'detailed_results': self.test_results,
            'environment_info': self.detector.get_environment_info(),
            'conclusions': conclusions,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_final_conclusions(self, passed: int, total: int, critical_passed: int) -> List[str]:
        """生成最终结论"""
        conclusions = []
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        if passed == total:
            conclusions.append("🎉 所有验证测试通过！环境检测功能完全正常")
            conclusions.append("✅ 环境检测模块已准备就绪，可以在生产环境中使用")
        elif passed > total * 0.9:
            conclusions.append("✅ 绝大部分验证测试通过，环境检测功能基本正常")
            conclusions.append("⚠️ 建议检查少量失败的测试项目")
        elif passed > total * 0.8:
            conclusions.append("⚠️ 大部分验证测试通过，环境检测功能基本可用")
            conclusions.append("🔧 建议优化失败的测试项目以提高稳定性")
        else:
            conclusions.append("❌ 多个验证测试失败，环境检测功能存在问题")
            conclusions.append("🚨 需要重新检查和修复环境检测逻辑")
        
        # 关键测试分析
        critical_total = len([r for r in self.test_results if r['is_critical']])
        if critical_passed == critical_total:
            conclusions.append(f"✅ 所有 {critical_total} 个关键测试通过")
        else:
            conclusions.append(f"⚠️ {critical_total} 个关键测试中 {critical_passed} 个通过")
        
        return conclusions
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        env_info = self.detector.get_environment_info()
        
        # 基于环境类型的建议
        env_type = env_info['environment_type']
        if env_type == EnvironmentType.IDE:
            recommendations.append("当前在IDE环境中，确保IDE支持GUI应用程序运行")
            recommendations.append("考虑在生产环境中测试打包后的应用程序")
        elif env_type == EnvironmentType.CONTAINER:
            recommendations.append("容器环境中建议使用无头模式运行")
            recommendations.append("确保容器配置了必要的显示环境变量")
        
        # 基于GUI可用性的建议
        if not env_info['gui_available']:
            recommendations.append("当前环境不支持GUI，建议使用命令行模式")
            recommendations.append("图表生成将使用静态模式")
        
        # 基于平台类型的建议
        platform = env_info['platform']
        if platform == PlatformType.LINUX:
            recommendations.append("Linux环境下确保DISPLAY环境变量正确设置")
            recommendations.append("服务器环境中建议使用Agg后端生成图表")
        
        # 通用建议
        recommendations.append("建议在多种环境中测试环境检测功能")
        recommendations.append("定期更新环境检测逻辑以支持新的运行环境")
        
        return recommendations
    
    def print_final_summary(self, report: Dict[str, Any]):
        """打印最终摘要"""
        logger.info("=" * 80)
        logger.info("🔍 环境检测功能最终验证报告")
        logger.info("=" * 80)
        
        summary = report['validation_summary']
        logger.info(f"📊 总体结果:")
        logger.info(f"   总测试数: {summary['total_tests']}")
        logger.info(f"   通过测试: {summary['passed_tests']}")
        logger.info(f"   失败测试: {summary['failed_tests']}")
        logger.info(f"   成功率: {summary['success_rate']}")
        logger.info(f"   关键测试: {summary['critical_tests_passed']}/{summary['critical_tests_total']}")
        logger.info(f"   整体状态: {summary['overall_status']}")
        
        logger.info(f"\n📂 各功能模块结果:")
        for category_name, category_result in report['categories'].items():
            success_rate = (category_result['passed'] / category_result['total'] * 100) if category_result['total'] > 0 else 0
            critical_rate = (category_result['critical_passed'] / category_result['total'] * 100) if category_result['total'] > 0 else 0
            logger.info(f"   {category_name}: {category_result['passed']}/{category_result['total']} ({success_rate:.1f}%) - 关键测试: {category_result['critical_passed']}/{category_result['total']} ({critical_rate:.1f}%)")
        
        logger.info(f"\n🌍 当前环境信息:")
        env_info = report['environment_info']
        logger.info(f"   平台: {env_info['platform'].value}")
        logger.info(f"   环境类型: {env_info['environment_type'].value}")
        logger.info(f"   GUI可用: {env_info['gui_available']}")
        logger.info(f"   冻结环境: {env_info['is_frozen']}")
        logger.info(f"   Python路径: {env_info['python_executable']}")
        
        logger.info(f"\n🎯 验证结论:")
        for i, conclusion in enumerate(report['conclusions'], 1):
            logger.info(f"   {i}. {conclusion}")
        
        if report['recommendations']:
            logger.info(f"\n💡 改进建议:")
            for i, recommendation in enumerate(report['recommendations'], 1):
                logger.info(f"   {i}. {recommendation}")
        
        logger.info("=" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="环境检测功能最终验证脚本")
    parser.add_argument("--detailed", "-d", action="store_true", help="显示详细输出")
    parser.add_argument("--save-report", "-s", help="保存验证报告到指定文件")
    
    args = parser.parse_args()
    
    logger.info("🚀 开始环境检测功能最终验证")
    
    # 创建验证器
    validator = FinalEnvironmentValidator(detailed=args.detailed)
    
    # 运行所有验证
    validation_methods = [
        validator.validate_core_functionality,
        validator.validate_environment_detection,
        validator.validate_gui_functionality,
        validator.validate_resource_management,
        validator.validate_stability,
        validator.validate_integration,
    ]
    
    all_passed = True
    for validation_method in validation_methods:
        try:
            if not validation_method():
                all_passed = False
        except Exception as e:
            logger.error(f"验证方法 {validation_method.__name__} 执行失败: {e}")
            all_passed = False
    
    # 生成和显示报告
    report = validator.generate_validation_report()
    validator.print_final_summary(report)
    
    # 保存报告
    if args.save_report:
        try:
            with open(args.save_report, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"📄 验证报告已保存到: {args.save_report}")
        except Exception as e:
            logger.error(f"保存验证报告失败: {e}")
    
    # 返回适当的退出码
    if report['validation_summary']['overall_status'] == 'PASS':
        logger.info("🎉 所有验证测试通过！环境检测功能完全正常")
        sys.exit(0)
    elif report['validation_summary']['overall_status'] == 'PARTIAL':
        logger.warning("⚠️ 大部分验证测试通过，环境检测功能基本可用")
        sys.exit(1)
    else:
        logger.error("❌ 多个验证测试失败，环境检测功能存在问题")
        sys.exit(2)


if __name__ == "__main__":
    main()