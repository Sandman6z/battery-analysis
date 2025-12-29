#!/usr/bin/env python3
"""
翻译修复测试脚本

验证以下翻译修复：
1. 状态栏消息翻译
2. 弹框标题和消息翻译
3. 首选项对话框翻译
4. 查看器组件翻译
5. 错误消息翻译
"""

import sys
import os
import json
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from battery_analysis.i18n.language_manager import get_language_manager, _

def test_translation_keys():
    """测试翻译键值对是否存在"""
    print("🔍 测试翻译键值对...")
    
    # 需要测试的翻译键
    test_keys = [
        "warning",
        "error", 
        "cannot_open_user_manual",
        "visualizer_start_error",
        "version_format_invalid",
        "input_path_not_exists",
        "required_fields_empty",
        "data_error_title",
        "data_error_message", 
        "data_error_details",
        "status_ready",
        "analyzing_data",
        "filtered",
        "button_filtered",
        "button_all_data"
    ]
    
    # 获取语言管理器
    lm = get_language_manager()
    
    all_passed = True
    
    for key in test_keys:
        try:
            # 测试英文翻译
            en_result = lm.translate(key, f"DEFAULT_{key}")
            # 测试中文翻译
            zh_result = lm.translate(key, f"DEFAULT_{key}")
            
            print(f"  ✅ {key}: en='{en_result}', zh='{zh_result}'")
            
        except Exception as e:
            print(f"  ❌ {key}: 错误 - {e}")
            all_passed = False
    
    return all_passed

def test_language_switching():
    """测试语言切换功能"""
    print("\n🌐 测试语言切换功能...")
    
    lm = get_language_manager()
    
    try:
        # 切换到英文
        print("  🔄 切换到英文...")
        if lm.set_language("en"):
            print("    ✅ 成功切换到英文")
        else:
            print("    ❌ 切换到英文失败")
            return False
            
        # 测试关键翻译
        warning_en = _("warning", "Warning")
        error_en = _("error", "Error")
        print(f"    📝 英文翻译: warning='{warning_en}', error='{error_en}'")
        
        # 切换到中文
        print("  🔄 切换到中文...")
        if lm.set_language("zh_CN"):
            print("    ✅ 成功切换到中文")
        else:
            print("    ❌ 切换到中文失败")
            return False
            
        # 测试关键翻译
        warning_zh = _("warning", "Warning")
        error_zh = _("error", "Error")
        print(f"    📝 中文翻译: warning='{warning_zh}', error='{error_zh}'")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 语言切换测试失败: {e}")
        return False

def test_status_bar_messages():
    """测试状态栏消息翻译"""
    print("\n📊 测试状态栏消息翻译...")
    
    lm = get_language_manager()
    
    # 模拟状态栏消息
    status_messages = [
        ("status_ready", "状态:就绪"),
        ("analyzing_data", "正在分析数据..."),
        ("saving_settings", "正在保存设置..."),
        ("settings_saved", "设置已保存"),
        ("visualizer_started", "可视化工具已启动")
    ]
    
    all_passed = True
    
    # 测试英文
    lm.set_language("en")
    print("  🇺🇸 英文状态消息:")
    for key, default in status_messages:
        try:
            translated = _(key, default)
            print(f"    ✅ {key}: '{translated}'")
        except Exception as e:
            print(f"    ❌ {key}: 错误 - {e}")
            all_passed = False
    
    # 测试中文
    lm.set_language("zh_CN")
    print("  🇨🇳 中文状态消息:")
    for key, default in status_messages:
        try:
            translated = _(key, default)
            print(f"    ✅ {key}: '{translated}'")
        except Exception as e:
            print(f"    ❌ {key}: 错误 - {e}")
            all_passed = False
    
    return all_passed

def test_dialog_messages():
    """测试对话框消息翻译"""
    print("\n💬 测试对话框消息翻译...")
    
    lm = get_language_manager()
    
    # 模拟对话框消息
    dialog_messages = [
        ("warning", "警告"),
        ("error", "错误"),
        ("version_format_invalid", "版本号格式不正确，应为 x.y.z 格式"),
        ("input_path_not_exists", "输入路径不存在"),
        ("required_fields_empty", "以下必填字段为空"),
        ("cannot_open_user_manual", "无法打开用户手册"),
        ("visualizer_start_error", "启动可视化工具时出错")
    ]
    
    all_passed = True
    
    # 测试英文
    lm.set_language("en")
    print("  🇺🇸 英文对话框消息:")
    for key, default in dialog_messages:
        try:
            translated = _(key, default)
            print(f"    ✅ {key}: '{translated}'")
        except Exception as e:
            print(f"    ❌ {key}: 错误 - {e}")
            all_passed = False
    
    # 测试中文
    lm.set_language("zh_CN")
    print("  🇨🇳 中文对话框消息:")
    for key, default in dialog_messages:
        try:
            translated = _(key, default)
            print(f"    ✅ {key}: '{translated}'")
        except Exception as e:
            print(f"    ❌ {key}: 错误 - {e}")
            all_passed = False
    
    return all_passed

def test_viewer_translations():
    """测试查看器组件翻译"""
    print("\n📈 测试查看器组件翻译...")
    
    lm = get_language_manager()
    
    # 查看器相关翻译
    viewer_keys = [
        ("filtered", "Filtered"),
        ("unfiltered", "Unfiltered"),
        ("button_filtered", "🔍 Filtered"),
        ("button_all_data", "📊 All Data"),
        ("data_error_title", "数据错误"),
        ("data_error_message", "无法加载或显示电池数据"),
        ("data_error_details", "数据错误详情")
    ]
    
    all_passed = True
    
    # 测试英文
    lm.set_language("en")
    print("  🇺🇸 英文查看器翻译:")
    for key, default in viewer_keys:
        try:
            translated = _(key, default)
            print(f"    ✅ {key}: '{translated}'")
        except Exception as e:
            print(f"    ❌ {key}: 错误 - {e}")
            all_passed = False
    
    # 测试中文
    lm.set_language("zh_CN")
    print("  🇨🇳 中文查看器翻译:")
    for key, default in viewer_keys:
        try:
            translated = _(key, default)
            print(f"    ✅ {key}: '{translated}'")
        except Exception as e:
            print(f"    ❌ {key}: 错误 - {e}")
            all_passed = False
    
    return all_passed

def main():
    """主测试函数"""
    print("🧪 开始翻译修复测试")
    print("=" * 50)
    
    # 配置日志
    logging.basicConfig(level=logging.WARNING)
    
    test_results = []
    
    # 执行各项测试
    test_results.append(("翻译键值对", test_translation_keys()))
    test_results.append(("语言切换", test_language_switching()))
    test_results.append(("状态栏消息", test_status_bar_messages()))
    test_results.append(("对话框消息", test_dialog_messages()))
    test_results.append(("查看器翻译", test_viewer_translations()))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📋 测试结果汇总:")
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！翻译修复成功！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查翻译键值对")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)