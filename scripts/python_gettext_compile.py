#!/usr/bin/env python3
"""
Use Python's built-in gettext module to compile .po files to .mo files
This should generate properly compatible .mo files.
"""

import os
import sys
import polib
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compile_with_polib(po_file: Path, mo_file: Path):
    """Use polib to compile .po to .mo"""
    try:
        # Import polib
        import polib
        
        # Parse the .po file
        po = polib.pofile(str(po_file))
        
        # Compile to .mo
        po.save_as_mofile(str(mo_file))
        
        logger.info(f"Successfully compiled {po_file} -> {mo_file}")
        logger.info(f"  {len(po)} entries compiled")
        return True
        
    except ImportError:
        logger.warning("polib not available, trying alternative method...")
        return None  # Signal to try alternative method
    except Exception as e:
        logger.error(f"Error compiling {po_file} with polib: {e}")
        return False

def compile_with_gettext(po_file: Path, mo_file: Path):
    """Use gettext module to compile .po to .mo"""
    try:
        import gettext
        
        # Parse .po file using gettext
        po_content = gettext._catalog_po(str(po_file))
        
        # Write .mo file
        with open(mo_file, 'wb') as f:
            f.write(po_content)
        
        logger.info(f"Successfully compiled {po_file} -> {mo_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error compiling {po_file} with gettext: {e}")
        return False

def main():
    """Main compilation function"""
    project_root = Path(__file__).parent.parent
    locale_dir = project_root / "locale"
    
    logger.info(f"Compiling translations from: {locale_dir}")
    
    if not locale_dir.exists():
        logger.error(f"Locale directory not found: {locale_dir}")
        return
    
    # Install polib if available
    try:
        import polib
        logger.info("Using polib for compilation")
    except ImportError:
        logger.info("polib not available, will try gettext module")
    
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
        
        # Try polib first
        result = compile_with_polib(po_file, mo_file)
        if result is None:
            # Try gettext as fallback
            result = compile_with_gettext(po_file, mo_file)
        
        if result:
            successful += 1
        else:
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
    main()