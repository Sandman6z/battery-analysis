#!/usr/bin/env python3
"""
最小化国际化测试脚本

这个脚本测试核心的国际化功能，而不依赖于整个应用程序的导入
"""

import sys
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 1. 测试直接 .po 文件解析功能
def test_po_parsing():
    """测试 .po 文件解析功能"""
    logger.info("\n测试 .po 文件解析功能...")
    
    try:
        from battery_analysis.i18n import SimplePOTranslator
        
        # 测试解析英文翻译文件
        po_file_en = Path(__file__).parent.parent / "locale" / "en" / "LC_MESSAGES" / "messages.po"
        if po_file_en.exists():
            translator = SimplePOTranslator()
            translations_en = translator.parse_po_file(po_file_en)
            logger.info(f"✓ 解析英文翻译文件: {len(translations_en)} 个翻译")
            
            # 测试一些基础翻译
            test_keys = ["battery-analyzer", "Preferences", "Language", "OK", "Cancel"]
            for key in test_keys:
                if key in translations_en:
                    logger.info(f"  ✓ {key} -> {translations_en[key]}")
                else:
                    logger.warning(f"  ⚠ {key} 未找到翻译")
        else:
            logger.error(f"✗ 英文翻译文件不存在: {po_file_en}")
            return False
        
        # 测试解析中文翻译文件
        po_file_zh = Path(__file__).parent.parent / "locale" / "zh_CN" / "LC_MESSAGES" / "messages.po"
        if po_file_zh.exists():
            translator = SimplePOTranslator()
            translations_zh = translator.parse_po_file(po_file_zh)
            logger.info(f"✓ 解析中文翻译文件: {len(translations_zh)} 个翻译")
            
            # 测试一些基础翻译
            test_keys = ["battery-analyzer", "Preferences", "Language", "OK", "Cancel"]
            for key in test_keys:
                if key in translations_zh:
                    logger.info(f"  ✓ {key} -> {translations_zh[key]}")
                else:
                    logger.warning(f"  ⚠ {key} 未找到翻译")
        else:
            logger.error(f"✗ 中文翻译文件不存在: {po_file_zh}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ .po 文件解析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 2. 测试翻译加载功能
def test_translation_loading():
    """测试翻译加载功能"""
    logger.info("\n测试翻译加载功能...")
    
    try:
        from battery_analysis.i18n import SimplePOTranslator
        
        # 测试加载英文翻译
        translator_en = SimplePOTranslator()
        success_en = translator_en.load_locale('en')
        if success_en:
            logger.info("✓ 成功加载英文翻译")
            
            # 测试翻译
            result = translator_en._("battery-analyzer")
            logger.info(f"  ✓ 测试翻译: battery-analyzer -> {result}")
            
            # 测试多个翻译
            test_keys = ["Preferences", "Language", "OK", "Cancel"]
            for key in test_keys:
                result = translator_en._(key)
                logger.info(f"  ✓ {key} -> {result}")
        else:
            logger.error("✗ 无法加载英文翻译")
            return False
        
        # 测试加载中文翻译
        translator_zh = SimplePOTranslator()
        success_zh = translator_zh.load_locale('zh_CN')
        if success_zh:
            logger.info("✓ 成功加载中文翻译")
            
            # 测试翻译
            result = translator_zh._("battery-analyzer")
            logger.info(f"  ✓ 测试翻译: battery-analyzer -> {result}")
            
            # 测试多个翻译
            test_keys = ["Preferences", "Language", "OK", "Cancel"]
            for key in test_keys:
                result = translator_zh._(key)
                logger.info(f"  ✓ {key} -> {result}")
        else:
            logger.error("✗ 无法加载中文翻译")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 翻译加载测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 3. 测试翻译功能
def test_translation_functionality():
    """测试翻译功能"""
    logger.info("\n测试翻译功能...")
    
    try:
        from battery_analysis.i18n import SimplePOTranslator
        
        # 测试英文翻译
        translator_en = SimplePOTranslator()
        translator_en.load_locale('en')
        
        # 测试基础翻译
        test_keys = [
            "battery-analyzer",
            "Preferences",
            "Language",
            "OK",
            "Cancel",
            "File",
            "Edit",
            "Help",
            "About"
        ]
        
        logger.info("测试英文翻译:")
        for key in test_keys:
            result = translator_en._(key)
            # 对于英文，翻译应该与原文本相同
            if result == key:
                logger.info(f"  ✓ {key} -> {result}")
            else:
                logger.error(f"  ✗ {key} -> {result} (期望: {key})")
        
        # 测试中文翻译
        translator_zh = SimplePOTranslator()
        translator_zh.load_locale('zh_CN')
        
        # 映射预期中文翻译
        expected_zh = {
            "battery-analyzer": "电池分析器",
            "Preferences": "首选项",
            "Language": "语言",
            "OK": "确定",
            "Cancel": "取消",
            "File": "文件",
            "Edit": "编辑",
            "Help": "帮助",
            "About": "关于"
        }
        
        logger.info("测试中文翻译:")
        for key, expected in expected_zh.items():
            result = translator_zh._(key)
            if result == expected:
                logger.info(f"  ✓ {key} -> {result}")
            else:
                logger.error(f"  ✗ {key} -> {result} (期望: {expected})")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 翻译功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 4. 测试语言管理器功能
def test_language_manager():
    """测试语言管理器功能"""
    logger.info("\n测试语言管理器...")
    
    try:
        # 尝试导入语言管理器
        from battery_analysis.i18n.language_manager import LanguageManager
        
        # 由于我们需要PyQt6，但可能在没有GUI环境的情况下运行，
        # 我们会检查类定义是否存在而不实例化它
        logger.info("✓ 语言管理器类存在")
        
        # 尝试检查其方法
        methods = dir(LanguageManager)
        required_methods = ["get_available_locales", "set_locale", "get_current_locale"]
        
        for method in required_methods:
            if method in methods:
                logger.info(f"  ✓ 语言管理器包含方法: {method}")
            else:
                logger.warning(f"  ⚠ 语言管理器缺少方法: {method}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 语言管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 5. 测试 .po 文件存在性
def test_po_files_existence():
    """测试 .po 文件存在性"""
    logger.info("\n测试 .po 文件存在性...")
    
    locales = ["en", "zh_CN"]
    all_exist = True
    
    for locale in locales:
        po_file = Path(__file__).parent.parent / "locale" / locale / "LC_MESSAGES" / "messages.po"
        if po_file.exists():
            logger.info(f"✓ 找到 {locale} 翻译文件: {po_file}")
        else:
            logger.error(f"✗ 找不到 {locale} 翻译文件: {po_file}")
            all_exist = False
    
    return all_exist

# 运行所有测试
def run_all_tests():
    """运行所有测试"""
    logger.info("=" * 50)
    logger.info("开始最小化国际化功能测试")
    logger.info("=" * 50)
    
    # 执行测试
    tests = [
        ("检查 .po 文件存在性", test_po_files_existence),
        (".po 文件解析", test_po_parsing),
        ("翻译加载", test_translation_loading),
        ("翻译功能", test_translation_functionality),
        ("语言管理器", test_language_manager)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n\n测试: {test_name}")
        logger.info("-" * 50)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 '{test_name}' 出现异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 输出总结
    logger.info("\n\n" + "=" * 50)
    logger.info("测试总结")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n通过: {passed}/{total} 项测试")
    
    if passed == total:
        logger.info("\n✓ 所有测试通过！核心国际化功能正常工作。")
    else:
        logger.error(f"\n✗ {total - passed} 项测试失败，请检查以上错误并修复问题。")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()