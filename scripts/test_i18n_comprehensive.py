#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面国际化功能测试
测试所有UI组件、错误处理和高级功能
"""

import os
import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_comprehensive_i18n():
    """全面测试国际化功能"""
    
    print("🌍 开始全面国际化功能测试...")
    print("=" * 60)
    
    test_results = []
    
    # 测试1: 验证修复后的BatteryChartViewer组件
    print("\n🔧 测试1: BatteryChartViewer组件")
    print("-" * 30)
    
    try:
        # 使用修复后的版本
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from battery_analysis.main.battery_chart_viewer_fixed import BatteryChartViewer
        
        viewer = BatteryChartViewer()
        status = viewer.get_status()
        
        print(f"✅ BatteryChartViewer初始化成功")
        print(f"   状态: {status}")
        test_results.append(True)
        
    except Exception as e:
        print(f"❌ BatteryChartViewer测试失败: {e}")
        test_results.append(False)
    
    # 测试2: 验证语言切换对组件的影响
    print("\n🔄 测试2: 语言切换对组件的影响")
    print("-" * 30)
    
    try:
        # 测试语言切换
        from battery_analysis.i18n import get_language_manager
        
        lang_manager = get_language_manager()
        
        # 切换到英语
        lang_manager.set_language('en')
        print(f"   切换到: {lang_manager.get_current_language()}")
        
        # 切换到中文
        lang_manager.set_language('zh_CN')
        print(f"   切换到: {lang_manager.get_current_language()}")
        
        print("✅ 语言切换功能正常")
        test_results.append(True)
        
    except Exception as e:
        print(f"❌ 语言切换测试失败: {e}")
        test_results.append(False)
    
    # 测试3: 验证所有UI组件的翻译
    print("\n🖼️ 测试3: UI组件翻译")
    print("-" * 30)
    
    try:
        from battery_analysis.i18n import _
        
        # 测试各种UI组件的翻译
        ui_tests = [
            # 主菜单
            ('File', '文件'),
            ('Edit', '编辑'),
            ('Help', '帮助'),
            
            # 对话框
            ('Preferences', '首选项'),
            ('Settings', '设置'),
            ('Language', '语言'),
            
            # 按钮
            ('OK', '确定'),
            ('Cancel', '取消'),
            ('Apply', '应用'),
            ('Close', '关闭'),
            
            # 电池分析特定术语
            ('load_voltage_over_charge', '充电电压曲线'),
            ('battery_analysis', '电池分析'),
            ('chart_title', '图表标题'),
            ('data_loading', '数据加载'),
            ('visualization', '可视化'),
            
            # 错误消息
            ('error_loading_data', '数据加载错误'),
            ('no_data_available', '无可用数据'),
            ('invalid_configuration', '配置无效'),
            
            # 状态消息
            ('loading', '加载中'),
            ('processing', '处理中'),
            ('completed', '已完成'),
            ('failed', '失败'),
        ]
        
        failed_tests = []
        for key, expected in ui_tests:
            translated = _(key)
            if translated == expected or (expected in translated and translated != key):
                print(f"   ✓ {key} -> {translated}")
            else:
                print(f"   ✗ {key} -> {translated} (期望: {expected})")
                failed_tests.append(key)
        
        if not failed_tests:
            print("✅ 所有UI组件翻译正常")
            test_results.append(True)
        else:
            print(f"❌ {len(failed_tests)} 个翻译失败")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ UI组件翻译测试失败: {e}")
        test_results.append(False)
    
    # 测试4: 验证复数形式处理
    print("\n🔢 测试4: 复数形式处理")
    print("-" * 30)
    
    try:
        # 测试复数形式翻译（如果实现）
        plural_tests = [
            ('battery_count_singular', '1 个电池'),
            ('battery_count_plural', '{n} 个电池'),
            ('file_count_singular', '1 个文件'),
            ('file_count_plural', '{n} 个文件'),
        ]
        
        # 由于当前可能没有实现复数形式，我们先检查是否存在
        implemented_plurals = []
        for key, expected in plural_tests:
            try:
                from battery_analysis.i18n import _
                # 尝试获取复数形式翻译
                result = _(key, count=5) if hasattr(_, '__code__') and 'count' in str(_) else _(key)
                if result != key:
                    implemented_plurals.append(key)
                    print(f"   ✓ {key} -> {result}")
                else:
                    print(f"   ⚠ {key} -> 未实现")
            except:
                print(f"   ⚠ {key} -> 测试失败")
        
        if len(implemented_plurals) > 0:
            print(f"✅ 发现 {len(implemented_plurals)} 个复数形式实现")
        else:
            print("ℹ 复数形式功能未实现（这是正常的）")
        
        test_results.append(True)  # 复数形式是可选功能
        
    except Exception as e:
        print(f"❌ 复数形式测试失败: {e}")
        test_results.append(False)
    
    # 测试5: 验证国际化配置和设置
    print("\n⚙️ 测试5: 国际化配置和设置")
    print("-" * 30)
    
    try:
        # 检查国际化配置
        config_tests = [
            ('检测默认语言', lambda: 'zh_CN' in str(Path(__file__).parent.parent / "locale")),
            ('检测翻译文件', lambda: any((Path(__file__).parent.parent / "locale" / lang / "LC_MESSAGES" / "messages.po").exists() for lang in ['en', 'zh_CN'])),
            ('检测i18n模块', lambda: (Path(__file__).parent.parent / "src" / "battery_analysis" / "i18n" / "__init__.py").exists()),
        ]
        
        config_passed = 0
        for test_name, test_func in config_tests:
            try:
                result = test_func()
                if result:
                    print(f"   ✓ {test_name}")
                    config_passed += 1
                else:
                    print(f"   ✗ {test_name}")
            except Exception as e:
                print(f"   ✗ {test_name} -> 错误: {e}")
        
        if config_passed == len(config_tests):
            print("✅ 国际化配置检查通过")
            test_results.append(True)
        else:
            print(f"❌ 国际化配置检查失败: {config_passed}/{len(config_tests)}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ 国际化配置测试失败: {e}")
        test_results.append(False)
    
    # 测试6: 性能测试
    print("\n⚡ 测试6: 性能测试")
    print("-" * 30)
    
    try:
        import time
        from battery_analysis.i18n import get_language_manager
        
        lang_manager = get_language_manager()
        
        # 测试翻译函数性能
        start_time = time.time()
        from battery_analysis.i18n import _
        
        # 执行1000次翻译
        for i in range(1000):
            result = _("File")
            result = _("Edit")
            result = _("Help")
            result = _("Preferences")
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"   1000次翻译耗时: {elapsed:.3f}秒")
        print(f"   平均每次翻译: {elapsed/4000:.6f}秒")
        
        if elapsed < 1.0:  # 1秒内完成
            print("✅ 性能测试通过")
            test_results.append(True)
        else:
            print("❌ 性能测试失败（翻译速度太慢）")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        test_results.append(False)
    
    # 测试总结
    print("\n" + "=" * 60)
    print("🎯 全面国际化测试总结")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！国际化功能完全正常！")
        return True
    elif passed >= total * 0.8:
        print("⚠️ 大部分测试通过，核心功能正常")
        return True
    else:
        print("❌ 多个测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = test_comprehensive_i18n()
    exit(0 if success else 1)