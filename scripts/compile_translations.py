#!/usr/bin/env python3
"""
Translation Compilation Script

This script compiles .po files to .mo files using standard gettext tools.
It follows international standards for Python application internationalization.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def find_po_files(locale_dir: Path) -> List[Path]:
    """
    Find all .po files in the locale directory.
    
    Args:
        locale_dir: Root locale directory
        
    Returns:
        List of .po file paths
    """
    po_files = []
    for locale_path in locale_dir.iterdir():
        if locale_path.is_dir():
            messages_dir = locale_path / "LC_MESSAGES"
            if messages_dir.exists():
                po_file = messages_dir / "messages.po"
                if po_file.exists():
                    po_files.append(po_file)
    
    return po_files


def compile_po_to_mo(po_file: Path, mo_file: Path) -> bool:
    """
    Compile a .po file to .mo file using msgfmt.
    
    Args:
        po_file: Path to .po file
        mo_file: Path to output .mo file
        
    Returns:
        True if compilation successful
    """
    try:
        # Ensure output directory exists
        mo_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Try msgfmt first (part of gettext package)
        result = subprocess.run([
            'msgfmt', '--check', '--verbose', '--output-file', str(mo_file), str(po_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Successfully compiled: {po_file} -> {mo_file}")
            return True
        
        # Fallback to python msgfmt
        result = subprocess.run([
            sys.executable, '-m', 'msgfmt', '--check', '--verbose', 
            '--output-file', str(mo_file), str(po_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Successfully compiled (python): {po_file} -> {mo_file}")
            return True
        
        logger.error(f"Failed to compile {po_file}: {result.stderr}")
        return False
        
    except FileNotFoundError:
        logger.warning("msgfmt not found. Please install gettext package.")
        logger.info("On Windows, install gettext from: https://mlocati.github.io/gettext-iconv-windows/")
        return False
    except Exception as e:
        logger.error(f"Unexpected error compiling {po_file}: {e}")
        return False


def validate_po_file(po_file: Path) -> Dict[str, Any]:
    """
    Validate a .po file for common issues.
    
    Args:
        po_file: Path to .po file
        
    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'stats': {}
    }
    
    try:
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic validation
        lines = content.split('\n')
        msgid_count = 0
        msgstr_count = 0
        fuzzy_count = 0
        untranslated_count = 0
        
        for line in lines:
            if line.startswith('msgid '):
                msgid_count += 1
            elif line.startswith('msgstr '):
                msgstr_count += 1
            elif '#, fuzzy' in line:
                fuzzy_count += 1
            elif line.startswith('msgstr ""') and not line.startswith('msgstr ""'):
                untranslated_count += 1
        
        result['stats'] = {
            'msgid_count': msgid_count,
            'msgstr_count': msgstr_count,
            'fuzzy_count': fuzzy_count,
            'untranslated_count': untranslated_count
        }
        
        # Check for common issues
        if msgid_count != msgstr_count:
            result['errors'].append("Mismatch between msgid and msgstr counts")
            result['valid'] = False
        
        if fuzzy_count > 0:
            result['warnings'].append(f"{fuzzy_count} fuzzy translations found")
        
        if untranslated_count > 0:
            result['warnings'].append(f"{untranslated_count} untranslated messages found")
        
        # Check encoding
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            result['errors'].append("File contains non-UTF-8 characters")
            result['valid'] = False
    
    except Exception as e:
        result['errors'].append(f"Error reading file: {e}")
        result['valid'] = False
    
    return result


def update_pot_file(po_files: List[Path], pot_file: Path) -> bool:
    """
    Update .pot template file by merging all .po files.
    
    Args:
        po_files: List of .po files
        pot_file: Path to output .pot file
        
    Returns:
        True if update successful
    """
    try:
        if not po_files:
            logger.warning("No .po files found to update .pot file")
            return False
        
        # Use msgmerge to update the .pot file
        # For simplicity, we'll use the first .po file as template
        template_po = po_files[0]
        
        result = subprocess.run([
            'msginit', '--no-translator', '--output-file', str(pot_file),
            '--input', str(template_po)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Successfully created .pot file: {pot_file}")
            return True
        else:
            logger.error(f"Failed to create .pot file: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Error updating .pot file: {e}")
        return False


def main():
    """Main compilation function"""
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    locale_dir = project_root / "locale"
    
    if not locale_dir.exists():
        logger.error(f"Locale directory not found: {locale_dir}")
        sys.exit(1)
    
    logger.info(f"Compiling translations from: {locale_dir}")
    
    # Find all .po files
    po_files = find_po_files(locale_dir)
    
    if not po_files:
        logger.warning("No .po files found")
        return
    
    logger.info(f"Found {len(po_files)} .po files")
    
    # Validate and compile each file
    success_count = 0
    total_count = len(po_files)
    
    for po_file in po_files:
        logger.info(f"Processing: {po_file}")
        
        # Validate
        validation = validate_po_file(po_file)
        
        if not validation['valid']:
            logger.error(f"Validation failed for {po_file}")
            for error in validation['errors']:
                logger.error(f"  Error: {error}")
            for warning in validation['warnings']:
                logger.warning(f"  Warning: {warning}")
            continue
        
        if validation['warnings']:
            for warning in validation['warnings']:
                logger.warning(f"  {po_file.name}: {warning}")
        
        # Compile to .mo
        mo_file = po_file.with_suffix('.mo')
        
        if compile_po_to_mo(po_file, mo_file):
            success_count += 1
        else:
            logger.error(f"Failed to compile: {po_file}")
    
    # Summary
    logger.info(f"\nCompilation Summary:")
    logger.info(f"  Total files: {total_count}")
    logger.info(f"  Successful: {success_count}")
    logger.info(f"  Failed: {total_count - success_count}")
    
    if success_count == total_count:
        logger.info("All translations compiled successfully!")
        return 0
    else:
        logger.error("Some translations failed to compile")
        return 1


if __name__ == "__main__":
    sys.exit(main())