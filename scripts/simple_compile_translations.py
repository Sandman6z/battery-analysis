#!/usr/bin/env python3
"""
简化版翻译编译脚本
使用Python标准库直接生成.mo文件
"""

import os
import sys
from pathlib import Path
import gettext
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def compile_po_to_mo(po_path: Path, mo_path: Path) -> bool:
    """
    编译.po文件到.mo文件
    
    Args:
        po_path: .po文件路径
        mo_path: 目标.mo文件路径
        
    Returns:
        True if successful
    """
    try:
        # 确保输出目录存在
        mo_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用gettext模块读取.po文件
        translation = gettext.GNUTranslations(open(po_path, 'rb'))
        
        # 生成.mo文件
        with open(mo_path, 'wb') as f:
            f.write(translation._catalog[1])  # 写入目录表
        
        logger.info(f"Successfully compiled {po_path} to {mo_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error compiling {po_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_and_compile_translations(locale_dir: Path):
    """查找并编译所有翻译文件"""
    if not locale_dir.exists():
        logger.error(f"Locale directory not found: {locale_dir}")
        return
    
    po_files = []
    for locale_subdir in locale_dir.iterdir():
        if locale_subdir.is_dir():
            po_file = locale_subdir / "LC_MESSAGES" / "messages.po"
            if po_file.exists():
                po_files.append((locale_subdir.name, po_file))
    
    if not po_files:
        logger.warning("No .po files found")
        return
    
    logger.info(f"Found {len(po_files)} .po files")
    
    successful = 0
    failed = 0
    
    for locale_name, po_file in po_files:
        mo_file = po_file.parent / "messages.mo"
        logger.info(f"Compiling {po_file}...")
        
        if compile_po_to_mo(po_file, mo_file):
            successful += 1
        else:
            failed += 1
    
    logger.info("\nCompilation Summary:")
    logger.info(f"  Total files: {len(po_files)}")
    logger.info(f"  Successful: {successful}")
    logger.info(f"  Failed: {failed}")
    
    if failed == 0:
        logger.info("All translations compiled successfully!")
    else:
        logger.warning("Some translations failed to compile!")

if __name__ == "__main__":
    # 设置路径
    project_root = Path(__file__).parent.parent
    locale_dir = project_root / "locale"
    
    logger.info(f"Compiling translations from: {locale_dir}")
    find_and_compile_translations(locale_dir)