#!/usr/bin/env python3
"""
Internationalization Setup Script

This script sets up the internationalization framework for the Battery Analysis
application and updates existing files to use standard i18n patterns.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def backup_old_i18n_files():
    """Backup the old i18n directory"""
    old_i18n_dir = Path(__file__).parent.parent / "src" / "battery_analysis" / "i18n"
    
    if old_i18n_dir.exists():
        backup_dir = old_i18n_dir.parent / "i18n_backup"
        
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        
        shutil.copytree(old_i18n_dir, backup_dir)
        logger.info(f"Backed up old i18n files to: {backup_dir}")


def create_new_i18n_structure():
    """Create the new i18n structure"""
    # Remove old files
    old_i18n_dir = Path(__file__).parent.parent / "src" / "battery_analysis" / "i18n"
    
    if old_i18n_dir.exists():
        # Keep only the new files we created
        files_to_keep = ['language_manager.py']
        
        for file_path in old_i18n_dir.iterdir():
            if file_path.name not in files_to_keep:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
        
        logger.info("Cleaned up old i18n files")
    
    # Create __init__.py if it doesn't exist
    init_file = old_i18n_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        logger.info("Created __init__.py in i18n directory")


def update_main_window_i18n():
    """Update main_window.py to use standard i18n"""
    main_window_file = Path(__file__).parent.parent / "src" / "battery_analysis" / "main" / "main_window.py"
    
    if not main_window_file.exists():
        logger.warning(f"main_window.py not found: {main_window_file}")
        return
    
    try:
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it already uses the new i18n framework
        if 'from battery_analysis.i18n import _' in content:
            logger.info("main_window.py already uses new i18n framework")
            return
        
        # Update imports
        if 'from battery_analysis.i18n.language_manager import get_language_manager, _' in content:
            content = content.replace(
                'from battery_analysis.i18n.language_manager import get_language_manager, _',
                'from battery_analysis.i18n import _'
            )
        
        # Replace hardcoded Chinese strings with _() calls
        replacements = [
            ('"电池分析器"', '_("battery-analyzer")'),
            ('"电池分析进度"', '_("Progress")'),
            ('"错误"', '_("Error")'),
            ('"成功"', '_("Success")'),
            ('"失败"', '_("Failed")'),
            ('"警告"', '_("Warning")'),
            ('"信息"', '_("Information")'),
            ('"确认"', '_("Confirm")'),
            ('"取消"', '_("Cancel")'),
            ('"保存"', '_("Save")'),
            ('"加载"', '_("Load")'),
            ('"文件"', '_("File")'),
            ('"编辑"', '_("Edit")'),
            ('"帮助"', '_("Help")'),
            ('"关于"', '_("About")'),
            ('"退出"', _('Exit"')),
            ('"设置"', '_("Settings")'),
            ('"配置"', '_("Configuration")'),
        ]
        
        changes_made = 0
        for old_str, new_str in replacements:
            if old_str in content:
                content = content.replace(old_str, new_str)
                changes_made += 1
        
        if changes_made > 0:
            # Backup original
            backup_file = main_window_file.with_suffix('.py.backup')
            shutil.copy2(main_window_file, backup_file)
            
            # Write updated content
            with open(main_window_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Updated main_window.py with {changes_made} i18n replacements")
            logger.info(f"Original backed up to: {backup_file}")
        else:
            logger.info("No i18n updates needed for main_window.py")
    
    except Exception as e:
        logger.error(f"Error updating main_window.py: {e}")


def update_battery_chart_viewer_i18n():
    """Update battery_chart_viewer.py to use standard i18n"""
    chart_viewer_file = Path(__file__).parent.parent / "src" / "battery_analysis" / "main" / "battery_chart_viewer.py"
    
    if not chart_viewer_file.exists():
        logger.warning(f"battery_chart_viewer.py not found: {chart_viewer_file}")
        return
    
    try:
        with open(chart_viewer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it already uses the new i18n framework
        if 'from battery_analysis.i18n import _' in content:
            logger.info("battery_chart_viewer.py already uses new i18n framework")
            return
        
        # Update imports
        import_pattern = r'from battery_analysis\.i18n\.language_manager import get_language_manager, _'
        if 'from battery_analysis.i18n.language_manager import get_language_manager, _' in content:
            content = content.replace(
                'from battery_analysis.i18n.language_manager import get_language_manager, _',
                'from battery_analysis.i18n import _'
            )
        
        # Replace hardcoded strings with _() calls
        chinese_strings = [
            '图表', '显示', '隐藏', '刷新', '更新', '分析', '数据',
            '状态', '进度', '完成', '处理', '测试', '调试', '日志',
            '记录', '监控', '跟踪', '统计', '报告', '生成', '创建'
        ]
        
        changes_made = 0
        for chinese_str in chinese_strings:
            if f'"{chinese_str}"' in content:
                # Create translation key
                key = chinese_str.lower().replace(' ', '_')
                content = content.replace(f'"{chinese_str}"', f'_("{key}")')
                changes_made += 1
        
        if changes_made > 0:
            # Backup original
            backup_file = chart_viewer_file.with_suffix('.py.backup')
            shutil.copy2(chart_viewer_file, backup_file)
            
            # Write updated content
            with open(chart_viewer_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Updated battery_chart_viewer.py with {changes_made} i18n replacements")
            logger.info(f"Original backed up to: {backup_file}")
        else:
            logger.info("No i18n updates needed for battery_chart_viewer.py")
    
    except Exception as e:
        logger.error(f"Error updating battery_chart_viewer.py: {e}")


def create_i18n_test():
    """Create a test script to verify i18n functionality"""
    test_script = Path(__file__).parent / "test_i18n.py"
    
    test_content = '''#!/usr/bin/env python3
"""
Internationalization Test Script

This script tests the i18n functionality of the Battery Analysis application.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from battery_analysis.i18n import _, set_locale, get_available_locales


def test_translations():
    """Test translation functionality"""
    print("Testing Internationalization Framework")
    print("=" * 40)
    
    # Test available locales
    locales = get_available_locales()
    print(f"Available locales: {locales}")
    
    # Test translations
    test_strings = [
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
    
    print("\\nTesting English translations:")
    set_locale("en")
    for string in test_strings:
        translated = _(string)
        print(f"  {string} -> {translated}")
    
    print("\\nTesting Chinese translations:")
    set_locale("zh_CN")
    for string in test_strings:
        translated = _(string)
        print(f"  {string} -> {translated}")
    
    print("\\ni18n test completed successfully!")


if __name__ == "__main__":
    test_translations()
'''
    
    with open(test_script, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    logger.info(f"Created i18n test script: {test_script}")


def create_documentation():
    """Create documentation for the i18n framework"""
    doc_file = Path(__file__).parent.parent / "docs" / "INTERNATIONALIZATION.md"
    
    doc_content = '''# Internationalization (i18n) Guide

This document describes the internationalization framework for the Battery Analysis application.

## Overview

The application uses standard GNU gettext-based internationalization following Python best practices.

## Directory Structure

```
locale/
├── en/
│   └── LC_MESSAGES/
│       ├── messages.po    # English translations (source)
│       └── messages.mo    # English translations (compiled)
├── zh_CN/
│   └── LC_MESSAGES/
│       ├── messages.po    # Chinese translations (source)
│       └── messages.mo    # Chinese translations (compiled)
└── messages.pot           # Translation template
```

## Usage

### In Python Code

```python
from battery_analysis.i18n import _

# Simple translation
label.setText(_("File"))

# Context-aware translation
status = pgettext("file_status", "Open")

# Plural forms
message = ngettext("One file processed", "%d files processed", count)
```

### Translation Files

#### Adding New Translations

1. Edit `.po` files in `locale/{locale}/LC_MESSAGES/`
2. Compile using: `python scripts/compile_translations_python.py`
3. Test with: `python scripts/test_i18n.py`

#### Extracting New Strings

1. Add `_("string")` calls in Python code
2. Extract using: `python scripts/extract_translations.py`
3. Update `.po` files with new strings
4. Recompile translations

## Scripts

- `compile_translations_python.py`: Compile .po to .mo files
- `extract_translations.py`: Extract translatable strings from code
- `setup_i18n.py`: Setup i18n framework
- `test_i18n.py`: Test i18n functionality

## Standards Compliance

This implementation follows:
- GNU gettext standards
- Python i18n best practices
- Qt translation conventions
- POSIX locale standards

## Adding New Languages

1. Create directory: `locale/{locale_code}/LC_MESSAGES/`
2. Copy `messages.po` from existing language
3. Update translations
4. Compile with `compile_translations_python.py`
5. Add to `SUPPORTED_LOCALES` in `language_manager.py`
'''
    
    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    logger.info(f"Created i18n documentation: {doc_file}")


def main():
    """Main setup function"""
    print("Setting up Internationalization Framework")
    print("=" * 45)
    
    # Backup old files
    backup_old_i18n_files()
    
    # Create new structure
    create_new_i18n_structure()
    
    # Update existing files
    update_main_window_i18n()
    update_battery_chart_viewer_i18n()
    
    # Create supporting files
    create_i18n_test()
    create_documentation()
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Test i18n: python scripts/test_i18n.py")
    print("2. Compile translations: python scripts/compile_translations_python.py")
    print("3. Read documentation: docs/INTERNATIONALIZATION.md")


if __name__ == "__main__":
    main()