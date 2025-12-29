#!/usr/bin/env python3
"""
核心国际化功能测试 - 跳过有问题的组件
"""
import os
import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_core_i18n():
    """测试核心国际化功能"""
    logger.info("开始核心国际化功能测试...")
    logger.info("=" * 50)
    
    passed_tests = 0
    total_tests = 0
    
    # 测试1: 检查翻译文件
    total_tests += 1
    logger.info("\n测试1: 检查翻译文件")
    logger.info("-" * 30)
    
    try:
        locale_dir = Path("locale")
        if locale_dir.exists():
            lang_dirs = [d for d in locale_dir.iterdir() if d.is_dir() and (d / "LC_MESSAGES" / "messages.po").exists()]
            logger.info(f"找到 {len(lang_dirs)} 种语言翻译:")
            for lang_dir in lang_dirs:
                po_file = lang_dir / "LC_MESSAGES" / "messages.po"
                if po_file.exists():
                    with open(po_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        msgid_count = content.count('msgid ')
                        logger.info(f"  ✓ {lang_dir.name}: {msgid_count} 个翻译条目")
            passed_tests += 1
            logger.info("  ✓ 翻译文件检查通过")
        else:
            logger.error("  ✗ locale目录不存在")
    except Exception as e:
        logger.error(f"  ✗ 翻译文件检查失败: {e}")
    
    # 测试2: 测试语言管理器基础功能
    total_tests += 1
    logger.info("\n测试2: 语言管理器基础功能")
    logger.info("-" * 30)
    
    try:
        sys.path.insert(0, 'src')
        from battery_analysis.i18n.language_manager import get_language_manager
        
        lang_manager = get_language_manager()
        logger.info(f"语言管理器初始化成功")
        logger.info(f"可用语言: {lang_manager.get_available_languages()}")
        logger.info(f"已安装语言: {lang_manager.get_installed_languages()}")
        
        # 测试语言切换
        current_lang = lang_manager.get_current_language()
        logger.info(f"当前语言: {current_lang}")
        
        # 尝试切换到中文
        lang_manager.set_language('zh_CN')
        new_lang = lang_manager.get_current_language()
        logger.info(f"切换后语言: {new_lang}")
        
        if new_lang == 'zh_CN':
            passed_tests += 1
            logger.info("  ✓ 语言切换功能正常")
        else:
            logger.error("  ✗ 语言切换失败")
            
    except Exception as e:
        logger.error(f"  ✗ 语言管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试3: 测试翻译函数
    total_tests += 1
    logger.info("\n测试3: 翻译函数")
    logger.info("-" * 30)
    
    try:
        from battery_analysis.i18n.language_manager import _
        
        # 设置为中文
        lang_manager.set_language('zh_CN')
        
        # 测试基础翻译
        tests = [
            ("File", "文件"),
            ("Edit", "编辑"),
            ("Help", "帮助"),
            ("Preferences", "首选项"),
            ("Language", "语言"),
            ("Settings", "设置"),
            ("OK", "确定"),
            ("Cancel", "取消"),
        ]
        
        failed_translations = 0
        for key, expected in tests:
            translated = _(key)
            if translated == expected:
                logger.info(f"  ✓ {key} -> {translated}")
            else:
                logger.error(f"  ✗ {key} -> {translated} (期望: {expected})")
                failed_translations += 1
        
        if failed_translations == 0:
            passed_tests += 1
            logger.info("  ✓ 基础翻译功能正常")
        else:
            logger.error(f"  ✗ {failed_translations} 个翻译失败")
            
    except Exception as e:
        logger.error(f"  ✗ 翻译函数测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试4: 测试首选项对话框翻译
    total_tests += 1
    logger.info("\n测试4: 首选项对话框翻译")
    logger.info("-" * 30)
    
    try:
        # 测试首选项对话框的翻译功能
        from battery_analysis.i18n.preferences_dialog import PreferencesDialog
        
        # 设置为中文
        lang_manager.set_language('zh_CN')
        
        logger.info("  ✓ 首选项对话框模块导入成功")
        
        # 测试一些关键翻译
        key_translations = {
            "preferences_title": "首选项",
            "general_settings": "常规设置",
            "language_settings": "语言设置",
            "theme": "主题",
            "select_language": "选择语言"
        }
        
        failed_count = 0
        for key, expected in key_translations.items():
            translated = _(key)
            if translated == expected:
                logger.info(f"  ✓ {key} -> {translated}")
            else:
                logger.info(f"  ✗ {key} -> {translated} (期望: {expected})")
                failed_count += 1
        
        if failed_count == 0:
            passed_tests += 1
            logger.info("  ✓ 首选项对话框翻译正常")
        else:
            logger.error(f"  ✗ {failed_count} 个翻译失败")
            
    except Exception as e:
        logger.error(f"  ✗ 首选项对话框测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试5: 测试多语言切换
    total_tests += 1
    logger.info("\n测试5: 多语言切换测试")
    logger.info("-" * 30)
    
    try:
        # 测试在英文和中文之间切换
        test_keys = ["File", "Edit", "Help", "Preferences"]
        
        # 切换到英文
        lang_manager.set_language('en')
        en_translations = {}
        for key in test_keys:
            en_translations[key] = _(key)
        
        # 切换到中文
        lang_manager.set_language('zh_CN')
        zh_translations = {}
        for key in test_keys:
            zh_translations[key] = _(key)
        
        # 检查翻译是否不同
        differences = 0
        for key in test_keys:
            if en_translations[key] != zh_translations[key]:
                logger.info(f"  ✓ {key}: EN='{en_translations[key]}' -> ZH='{zh_translations[key]}'")
            else:
                logger.error(f"  ✗ {key}: 两种语言翻译相同 '{en_translations[key]}'")
                differences += 1
        
        if differences == 0:
            passed_tests += 1
            logger.info("  ✓ 多语言切换正常")
        else:
            logger.error(f"  ✗ {differences} 个翻译在语言切换时未发生变化")
            
    except Exception as e:
        logger.error(f"  ✗ 多语言切换测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 总结
    logger.info("\n" + "=" * 50)
    logger.info("核心国际化功能测试总结")
    logger.info("=" * 50)
    logger.info(f"通过: {passed_tests}/{total_tests} 项测试")
    
    if passed_tests == total_tests:
        logger.info("✓ 所有核心国际化功能测试通过！")
        return True
    else:
        logger.error(f"✗ {total_tests - passed_tests} 项测试失败")
        return False

if __name__ == "__main__":
    success = test_core_i18n()
    sys.exit(0 if success else 1)