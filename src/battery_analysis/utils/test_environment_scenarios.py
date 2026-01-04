#!/usr/bin/env python3
"""
环境场景测试脚本

此脚本用于测试环境检测在不同场景下的行为，
包括模拟不同环境、验证路径处理、测试资源访问等。

使用方法:
    python test_environment_scenarios.py
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
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

import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnvironmentScenarioTester:
    """环境场景测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.original_env = dict(os.environ)
        self.test_results = []
        self.temp_dir = None
        
    def setup_temp_environment(self):
        """设置临时测试环境"""
        self.temp_dir = tempfile.mkdtemp(prefix="env_test_")
        logger.info("创建临时测试环境: %s", self.temp_dir)
        
    def cleanup_temp_environment(self):
        """清理临时测试环境"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info("清理临时测试环境: %s", self.temp_dir)
    
    def restore_original_environment(self):
        """恢复原始环境变量"""
        # 清理所有环境变量
        for key in list(os.environ.keys()):
            del os.environ[key]
        
        # 恢复原始环境变量
        os.environ.update(self.original_env)
        logger.info("恢复原始环境变量")
    
    def log_result(self, scenario: str, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'scenario': scenario,
            'test_name': test_name,
            'success': success,
            'details': details,
            'status': status
        }
        self.test_results.append(result)
        logger.info("%s [%s] %s: %s", status, scenario, test_name, details)
    
    def test_ide_environment_scenarios(self):
        """测试IDE环境场景"""
        logger.info("=" * 50)
        logger.info("测试IDE环境场景")
        logger.info("=" * 50)
        
        # 场景1: Trae IDE环境
        test_env = {'TRAE': '1', 'VSCODE_INJECTION': '1'}
        
        for env_var, env_value in test_env.items():
            with patch.dict(os.environ, {env_var: env_value}, clear=False):
                detector = EnvironmentDetector()
                env_info = detector.get_environment_info()
                
                if env_info['environment_type'] == EnvironmentType.IDE:
                    self.log_result("IDE环境", f"Trae IDE检测({env_var})", True, f"检测为: {env_info['environment_type'].value}")
                else:
                    self.log_result("IDE环境", f"Trae IDE检测({env_var})", False, f"检测为: {env_info['environment_type'].value}")
        
        # 场景2: PyCharm环境
        with patch.dict(os.environ, {'PYCHARM_HOSTED': '1'}, clear=False):
            detector = EnvironmentDetector()
            env_info = detector.get_environment_info()
            
            if env_info['environment_type'] == EnvironmentType.IDE:
                self.log_result("IDE环境", "PyCharm环境检测", True, f"检测为: {env_info['environment_type'].value}")
            else:
                self.log_result("IDE环境", "PyCharm环境检测", False, f"检测为: {env_info['environment_type'].value}")
        
        # 场景3: 虚拟环境检测
        with patch('sys.prefix', '/test/virtual/env'), \
             patch('sys.base_prefix', '/test/base/env'):
            detector = EnvironmentDetector()
            env_info = detector.get_environment_info()
            
            if env_info['environment_type'] == EnvironmentType.DEVELOPMENT:
                self.log_result("IDE环境", "虚拟环境检测", True, f"检测为: {env_info['environment_type'].value}")
            else:
                self.log_result("IDE环境", "虚拟环境检测", False, f"检测为: {env_info['environment_type'].value}")
    
    def test_container_environment_scenarios(self):
        """测试容器环境场景"""
        logger.info("=" * 50)
        logger.info("测试容器环境场景")
        logger.info("=" * 50)
        
        # 场景1: Docker环境
        test_files = ['/.dockerenv']
        
        for test_file in test_files:
            # 创建临时文件
            temp_file = os.path.join(self.temp_dir, test_file.lstrip('/'))
            os.makedirs(os.path.dirname(temp_file), exist_ok=True)
            Path(temp_file).touch()
            
            with patch('os.path.exists') as mock_exists:
                def exists_side_effect(path):
                    if path == test_file:
                        return True
                    return os.path.exists(path)
                
                mock_exists.side_effect = exists_side_effect
                
                detector = EnvironmentDetector()
                env_info = detector.get_environment_info()
                
                if env_info['environment_type'] == EnvironmentType.CONTAINER:
                    self.log_result("容器环境", f"Docker环境检测({test_file})", True, f"检测为: {env_info['environment_type'].value}")
                else:
                    self.log_result("容器环境", f"Docker环境检测({test_file})", False, f"检测为: {env_info['environment_type'].value}")
                
                # 清理
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        
        # 场景2: Kubernetes环境
        with patch.dict(os.environ, {'KUBERNETES_SERVICE_HOST': '10.0.0.1'}, clear=False):
            detector = EnvironmentDetector()
            env_info = detector.get_environment_info()
            
            if env_info['environment_type'] == EnvironmentType.CONTAINER:
                self.log_result("容器环境", "Kubernetes环境检测", True, f"检测为: {env_info['environment_type'].value}")
            else:
                self.log_result("容器环境", "Kubernetes环境检测", False, f"检测为: {env_info['environment_type'].value}")
        
        # 场景3: 容器环境变量
        with patch.dict(os.environ, {'CONTAINER': 'docker'}, clear=False):
            detector = EnvironmentDetector()
            env_info = detector.get_environment_info()
            
            if env_info['environment_type'] == EnvironmentType.CONTAINER:
                self.log_result("容器环境", "容器环境变量检测", True, f"检测为: {env_info['environment_type'].value}")
            else:
                self.log_result("容器环境", "容器环境变量检测", False, f"检测为: {env_info['environment_type'].value}")
    
    def test_production_environment_scenarios(self):
        """测试生产环境场景"""
        logger.info("=" * 50)
        logger.info("测试生产环境场景")
        logger.info("=" * 50)
        
        # 场景1: PyInstaller环境（模拟冻结状态）
        with patch('sys.frozen', True), \
             patch('sys._MEIPASS', '/test/meipass'):
            
            detector = EnvironmentDetector()
            env_info = detector.get_environment_info()
            
            if env_info['is_frozen'] and env_info['meipass']:
                self.log_result("生产环境", "PyInstaller环境检测", True, f"冻结: {env_info['is_frozen']}, MEIPASS: {env_info['meipass']}")
            else:
                self.log_result("生产环境", "PyInstaller环境检测", False, f"冻结: {env_info['is_frozen']}, MEIPASS: {env_info['meipass']}")
    
    def test_platform_scenarios(self):
        """测试平台检测场景"""
        logger.info("=" * 50)
        logger.info("测试平台检测场景")
        logger.info("=" * 50)
        
        # 场景1: Windows平台
        with patch('platform.system', return_value='Windows'):
            detector = EnvironmentDetector()
            platform = detector._detect_platform()
            
            if platform == PlatformType.WINDOWS:
                self.log_result("平台检测", "Windows平台检测", True, f"检测为: {platform.value}")
            else:
                self.log_result("平台检测", "Windows平台检测", False, f"检测为: {platform.value}")
        
        # 场景2: Linux平台
        with patch('platform.system', return_value='Linux'):
            detector = EnvironmentDetector()
            platform = detector._detect_platform()
            
            if platform == PlatformType.LINUX:
                self.log_result("平台检测", "Linux平台检测", True, f"检测为: {platform.value}")
            else:
                self.log_result("平台检测", "Linux平台检测", False, f"检测为: {platform.value}")
        
        # 场景3: macOS平台
        with patch('platform.system', return_value='Darwin'):
            detector = EnvironmentDetector()
            platform = detector._detect_platform()
            
            if platform == PlatformType.MACOS:
                self.log_result("平台检测", "macOS平台检测", True, f"检测为: {platform.value}")
            else:
                self.log_result("平台检测", "macOS平台检测", False, f"检测为: {platform.value}")
        
        # 场景4: 未知平台
        with patch('platform.system', return_value='Unknown'):
            detector = EnvironmentDetector()
            platform = detector._detect_platform()
            
            if platform == PlatformType.UNKNOWN:
                self.log_result("平台检测", "未知平台检测", True, f"检测为: {platform.value}")
            else:
                self.log_result("平台检测", "未知平台检测", False, f"检测为: {platform.value}")
    
    def test_gui_environment_scenarios(self):
        """测试GUI环境场景"""
        logger.info("=" * 50)
        logger.info("测试GUI环境场景")
        logger.info("=" * 50)
        
        # 场景1: 有DISPLAY环境变量（Linux）
        with patch.dict(os.environ, {'DISPLAY': ':0'}, clear=False):
            detector = EnvironmentDetector()
            display = detector._detect_display()
            
            if display == ':0':
                self.log_result("GUI环境", "DISPLAY环境变量检测", True, f"DISPLAY: {display}")
            else:
                self.log_result("GUI环境", "DISPLAY环境变量检测", False, f"DISPLAY: {display}")
        
        # 场景2: 无显示环境
        for env_var in ['DISPLAY', 'WAYLAND_DISPLAY']:
            if env_var in os.environ:
                del os.environ[env_var]
        
        with patch('platform.system', return_value='Linux'):
            detector = EnvironmentDetector()
            display = detector._detect_display()
            
            if display is None:
                self.log_result("GUI环境", "无显示环境检测", True, "无显示环境")
            else:
                self.log_result("GUI环境", "无显示环境检测", False, f"检测到显示: {display}")
        
        # 场景3: Windows平台GUI检测
        with patch('platform.system', return_value='Windows'):
            detector = EnvironmentDetector()
            display = detector._detect_display()
            
            if display and 'windows_monitor' in display:
                self.log_result("GUI环境", "Windows平台GUI检测", True, f"Windows显示器: {display}")
            else:
                self.log_result("GUI环境", "Windows平台GUI检测", False, f"显示状态: {display}")
    
    def test_path_handling_scenarios(self):
        """测试路径处理场景"""
        logger.info("=" * 50)
        logger.info("测试路径处理场景")
        logger.info("=" * 50)
        
        # 场景1: 开发环境路径
        detector = EnvironmentDetector()
        test_resource = detector.get_resource_path("test/config.ini")
        
        if isinstance(test_resource, Path) and "test" in str(test_resource):
            self.log_result("路径处理", "开发环境资源路径", True, f"路径: {test_resource}")
        else:
            self.log_result("路径处理", "开发环境资源路径", False, f"路径: {test_resource}")
        
        # 场景2: PyInstaller环境路径
        with patch('sys.frozen', True), \
             patch('sys._MEIPASS', '/test/meipass'):
            
            detector = EnvironmentDetector()
            test_resource = detector.get_resource_path("test/config.ini")
            
            expected_path = Path("/test/meipass/test/config.ini")
            if test_resource == expected_path:
                self.log_result("路径处理", "PyInstaller环境资源路径", True, f"路径: {test_resource}")
            else:
                self.log_result("路径处理", "PyInstaller环境资源路径", False, f"预期: {expected_path}, 实际: {test_resource}")
        
        # 场景3: 项目根目录查找
        detector = EnvironmentDetector()
        project_root = detector._find_project_root()
        
        if isinstance(project_root, Path) and project_root.exists():
            self.log_result("路径处理", "项目根目录查找", True, f"项目根目录: {project_root}")
        else:
            self.log_result("路径处理", "项目根目录查找", False, f"项目根目录: {project_root}")
    
    def test_resource_access_scenarios(self):
        """测试资源访问场景"""
        logger.info("=" * 50)
        logger.info("测试资源访问场景")
        logger.info("=" * 50)
        
        detector = EnvironmentDetector()
        
        # 场景1: 配置文件查找
        config_path = detector.get_config_path("test_config.ini")
        
        if config_path is None or isinstance(config_path, Path):
            self.log_result("资源访问", "配置文件查找", True, f"结果: {config_path}")
        else:
            self.log_result("资源访问", "配置文件查找", False, f"无效结果: {config_path}")
        
        # 场景2: 国际化文件查找
        locale_path = detector.get_locale_path("test_messages.po")
        
        if locale_path is None or isinstance(locale_path, Path):
            self.log_result("资源访问", "国际化文件查找", True, f"结果: {locale_path}")
        else:
            self.log_result("资源访问", "国际化文件查找", False, f"无效结果: {locale_path}")
    
    def test_error_recovery_scenarios(self):
        """测试错误恢复场景"""
        logger.info("=" * 50)
        logger.info("测试错误恢复场景")
        logger.info("=" * 50)
        
        # 场景1: 多次初始化
        detector1 = EnvironmentDetector()
        detector2 = EnvironmentDetector()
        
        env_info1 = detector1.get_environment_info()
        env_info2 = detector2.get_environment_info()
        
        if env_info1 == env_info2:
            self.log_result("错误恢复", "多次初始化一致性", True, "多次初始化结果一致")
        else:
            self.log_result("错误恢复", "多次初始化一致性", False, "多次初始化结果不一致")
        
        # 场景2: 异常处理
        try:
            with patch('platform.system', side_effect=Exception("Test exception")):
                detector = EnvironmentDetector()
                platform = detector._detect_platform()
                
                if platform == PlatformType.UNKNOWN:
                    self.log_result("错误恢复", "异常处理", True, "异常时正确返回UNKNOWN")
                else:
                    self.log_result("错误恢复", "异常处理", False, f"异常时返回: {platform}")
        except Exception as e:
            self.log_result("错误恢复", "异常处理", False, f"未处理的异常: {e}")
    
    def generate_scenario_report(self) -> Dict[str, Any]:
        """生成场景测试报告"""
        logger.info("=" * 50)
        logger.info("生成场景测试报告")
        logger.info("=" * 50)
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        # 按场景分类
        scenarios = {}
        for result in self.test_results:
            scenario = result['scenario']
            if scenario not in scenarios:
                scenarios[scenario] = {'passed': 0, 'failed': 0, 'total': 0}
            
            scenarios[scenario]['total'] += 1
            if result['success']:
                scenarios[scenario]['passed'] += 1
            else:
                scenarios[scenario]['failed'] += 1
        
        # 生成报告
        report = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            'scenarios': scenarios,
            'detailed_results': self.test_results,
            'conclusions': self._generate_conclusions()
        }
        
        return report
    
    def _generate_conclusions(self) -> List[str]:
        """生成结论和建议"""
        conclusions = []
        
        # 分析测试结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        
        if passed_tests == total_tests:
            conclusions.append("✅ 所有环境场景测试通过，环境检测功能稳定可靠")
        elif passed_tests > total_tests * 0.8:
            conclusions.append("⚠️ 大部分环境场景测试通过，建议检查失败的场景")
        else:
            conclusions.append("❌ 多个环境场景测试失败，需要重新检查环境检测逻辑")
        
        # 检查特定场景
        ide_tests = [r for r in self.test_results if r['scenario'] == 'IDE环境']
        container_tests = [r for r in self.test_results if r['scenario'] == '容器环境']
        production_tests = [r for r in self.test_results if r['scenario'] == '生产环境']
        
        if ide_tests:
            ide_passed = sum(1 for t in ide_tests if t['success'])
            if ide_passed == len(ide_tests):
                conclusions.append("✅ IDE环境检测功能正常")
            else:
                conclusions.append("⚠️ IDE环境检测存在问题，需要优化")
        
        if container_tests:
            container_passed = sum(1 for t in container_tests if t['success'])
            if container_passed == len(container_tests):
                conclusions.append("✅ 容器环境检测功能正常")
            else:
                conclusions.append("⚠️ 容器环境检测存在问题，需要优化")
        
        if production_tests:
            production_passed = sum(1 for t in production_tests if t['success'])
            if production_passed == len(production_tests):
                conclusions.append("✅ 生产环境检测功能正常")
            else:
                conclusions.append("⚠️ 生产环境检测存在问题，需要优化")
        
        return conclusions
    
    def print_summary(self, report: Dict[str, Any]):
        """打印场景测试摘要"""
        logger.info("=" * 60)
        logger.info("环境场景测试摘要")
        logger.info("=" * 60)
        
        summary = report['summary']
        logger.info("总场景测试数: %s", summary['total_tests'])
        logger.info("通过测试: %s", summary['passed_tests'])
        logger.info("失败测试: %s", summary['failed_tests'])
        logger.info("成功率: %s", summary['success_rate'])
        
        logger.info("\n各场景组结果:")
        for scenario_name, scenario_result in report['scenarios'].items():
            success_rate = (scenario_result['passed'] / scenario_result['total'] * 100) if scenario_result['total'] > 0 else 0
            logger.info("  %s: %s/%s (%s%)", scenario_name, scenario_result['passed'], scenario_result['total'], success_rate:.1f)
        
        logger.info("\n结论和建议:")
        for i, conclusion in enumerate(report['conclusions'], 1):
            logger.info("  %s. %s", i, conclusion)


def main():
    """主函数"""
    logger.info("开始环境场景测试")
    
    # 创建测试器
    tester = EnvironmentScenarioTester()
    
    try:
        # 设置临时环境
        tester.setup_temp_environment()
        
        # 运行所有场景测试
        test_methods = [
            tester.test_ide_environment_scenarios,
            tester.test_container_environment_scenarios,
            tester.test_production_environment_scenarios,
            tester.test_platform_scenarios,
            tester.test_gui_environment_scenarios,
            tester.test_path_handling_scenarios,
            tester.test_resource_access_scenarios,
            tester.test_error_recovery_scenarios,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error("场景测试方法 %s 执行失败: %s", test_method.__name__, e)
        
        # 生成和显示报告
        report = tester.generate_scenario_report()
        tester.print_summary(report)
        
        # 返回适当的退出码
        failed_tests = sum(1 for result in tester.test_results if not result['success'])
        if failed_tests > 0:
            logger.warning("检测到 %s 个失败的场景测试", failed_tests)
            sys.exit(1)
        else:
            logger.info("所有场景测试通过！")
            sys.exit(0)
            
    finally:
        # 清理环境
        tester.cleanup_temp_environment()
        tester.restore_original_environment()


if __name__ == "__main__":
    main()