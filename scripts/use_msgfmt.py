#!/usr/bin/env python3
"""
Use Python's built-in msgfmt module to compile .po files
"""

import sys
import os
from pathlib import Path
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compile_with_msgfmt():
    """Use Python's msgfmt to compile .po files"""
    project_root = Path(__file__).parent.parent
    locale_dir = project_root / "locale"
    
    logger.info(f"Compiling translations from: {locale_dir}")
    
    if not locale_dir.exists():
        logger.error(f"Locale directory not found: {locale_dir}")
        return
    
    # Find all .po files
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
        logger.info(f"Processing {locale_name}: {po_file}")
        
        try:
            # Use Python's msgfmt module
            import msgfmt
            result = msgfmt.compile(str(po_file), str(mo_file))
            
            if result:
                logger.info(f"✓ Successfully compiled {po_file} -> {mo_file}")
                successful += 1
            else:
                logger.error(f"✗ Failed to compile {po_file}")
                failed += 1
                
        except ImportError:
            logger.info("msgfmt module not available, trying direct usage...")
            
            # Try to use msgfmt as a script
            try:
                # Find Python's msgfmt.py script
                python_lib = sys.executable.rsplit(os.sep, 1)[0]
                msgfmt_script = Path(python_lib) / "Lib" / "msgfmt.py"
                
                if msgfmt_script.exists():
                    result = subprocess.run([
                        sys.executable, str(msgfmt_script), str(po_file), str(mo_file)
                    ], capture_output=True, text=True, cwd=project_root)
                    
                    if result.returncode == 0:
                        logger.info(f"✓ Successfully compiled {po_file} -> {mo_file}")
                        successful += 1
                    else:
                        logger.error(f"✗ Failed to compile {po_file}: {result.stderr}")
                        failed += 1
                else:
                    # Try python -m msgfmt
                    result = subprocess.run([
                        sys.executable, "-m", "msgfmt", str(po_file), "-o", str(mo_file)
                    ], capture_output=True, text=True, cwd=project_root)
                    
                    if result.returncode == 0:
                        logger.info(f"✓ Successfully compiled {po_file} -> {mo_file}")
                        successful += 1
                    else:
                        logger.error(f"✗ Failed to compile {po_file}: {result.stderr}")
                        failed += 1
                        
            except Exception as e:
                logger.error(f"✗ Error using msgfmt for {po_file}: {e}")
                failed += 1
    
    logger.info(f"\nCompilation Summary:")
    logger.info(f"  Total files: {len(po_files)}")
    logger.info(f"  Successful: {successful}")
    logger.info(f"  Failed: {failed}")
    
    if failed == 0:
        logger.info("All translations compiled successfully!")
    else:
        logger.error(f"Failed to compile {failed} translation files")

if __name__ == "__main__":
    compile_with_msgfmt()