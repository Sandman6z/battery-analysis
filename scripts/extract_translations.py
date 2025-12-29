#!/usr/bin/env python3
"""
Translation Extraction Script

This script extracts translatable strings from Python source files
using xgettext tool following international standards.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def find_python_files(source_dir: Path) -> List[Path]:
    """
    Find all Python files in the source directory.
    
    Args:
        source_dir: Source directory path
        
    Returns:
        List of Python file paths
    """
    python_files = []
    
    # Walk through source directory
    for file_path in source_dir.rglob("*.py"):
        # Skip test files, __pycache__, and other non-source files
        if any(part in str(file_path) for part in ['__pycache__', '.git', 'tests']):
            continue
        python_files.append(file_path)
    
    return python_files


def extract_translatable_strings(python_file: Path) -> Set[str]:
    """
    Extract translatable strings from a Python file using regex.
    
    Args:
        python_file: Path to Python file
        
    Returns:
        Set of translatable strings
    """
    translatable_strings = set()
    
    try:
        with open(python_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to find _(...) function calls
        # Matches: _('string'), _("string"), _('string' % vars), etc.
        pattern = r'_\([\'"](.+?)[\'"]'
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            # Clean up the string
            string = match.strip()
            if string and len(string) > 0:
                translatable_strings.add(string)
        
        # Also look for pgettext(context, "string")
        pgettext_pattern = r'pgettext\([\'"](.+?)[\'"],\s*[\'"](.+?)[\'"]'
        pgettext_matches = re.findall(pgettext_pattern, content)
        
        for context, string in pgettext_matches:
            translatable_strings.add(string)
        
        # Look for ngettext("singular", "plural", n)
        ngettext_pattern = r'ngettext\([\'"](.+?)[\'"],\s*[\'"](.+?)[\'"]'
        ngettext_matches = re.findall(ngettext_pattern, content)
        
        for singular, plural in ngettext_matches:
            translatable_strings.add(singular)
            translatable_strings.add(plural)
        
    except Exception as e:
        logger.warning(f"Error processing {python_file}: {e}")
    
    return translatable_strings


def extract_with_xgettext(python_files: List[Path], output_file: Path) -> bool:
    """
    Extract translatable strings using xgettext tool.
    
    Args:
        python_files: List of Python files
        output_file: Path to output .pot file
        
    Returns:
        True if extraction successful
    """
    try:
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Build xgettext command
        cmd = [
            'xgettext',
            '--language=Python',
            '--keyword=_',
            '--keyword=pgettext:1,2',
            '--keyword=ngettext:1,2',
            '--from-code=UTF-8',
            '--output=' + str(output_file),
            '--sort-output',
            '--add-comments=TRANSLATORS'
        ]
        
        # Add all Python files
        cmd.extend(str(f) for f in python_files)
        
        # Run xgettext
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Successfully extracted translations to: {output_file}")
            return True
        else:
            logger.error(f"xgettext failed: {result.stderr}")
            return False
    
    except FileNotFoundError:
        logger.warning("xgettext not found. Please install gettext package.")
        logger.info("On Windows, install gettext from: https://mlocati.github.io/gettext-iconv-windows/")
        return False
    except Exception as e:
        logger.error(f"Error running xgettext: {e}")
        return False


def create_pot_template(strings: Set[str], output_file: Path) -> bool:
    """
    Create a .pot template file from extracted strings.
    
    Args:
        strings: Set of translatable strings
        output_file: Path to output .pot file
        
    Returns:
        True if creation successful
    """
    try:
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create .pot content
        pot_content = """# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: Battery Analysis\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-12-26 12:00+0000\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

"""
        
        # Add each string as a message
        for string in sorted(strings):
            # Escape special characters
            escaped_string = string.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            pot_content += f'msgid "{escaped_string}"\n'
            pot_content += 'msgstr ""\n\n'
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pot_content)
        
        logger.info(f"Created .pot template: {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating .pot file: {e}")
        return False


def analyze_ui_files(source_dir: Path) -> Dict[str, List[str]]:
    """
    Analyze UI files for translatable strings.
    
    Args:
        source_dir: Source directory path
        
    Returns:
        Dictionary mapping UI file types to found strings
    """
    ui_strings = {}
    
    # Find .ui files
    ui_files = list(source_dir.rglob("*.ui"))
    
    for ui_file in ui_files:
        try:
            with open(ui_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract text from UI elements
            # This is a simplified approach - real UI extraction would be more complex
            strings = []
            
            # Look for text attributes in UI files
            text_pattern = r'text="([^"]*)"'
            matches = re.findall(text_pattern, content)
            
            for match in matches:
                if match and len(match.strip()) > 0:
                    strings.append(match.strip())
            
            ui_strings[str(ui_file)] = strings
        
        except Exception as e:
            logger.warning(f"Error processing UI file {ui_file}: {e}")
    
    return ui_strings


def main():
    """Main extraction function"""
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    source_dir = project_root / "src"
    locale_dir = project_root / "locale"
    pot_file = locale_dir / "messages.pot"
    
    if not source_dir.exists():
        logger.error(f"Source directory not found: {source_dir}")
        sys.exit(1)
    
    if not locale_dir.exists():
        logger.error(f"Locale directory not found: {locale_dir}")
        sys.exit(1)
    
    logger.info(f"Extracting translations from: {source_dir}")
    
    # Find Python files
    python_files = find_python_files(source_dir)
    
    if not python_files:
        logger.warning("No Python files found")
        return
    
    logger.info(f"Found {len(python_files)} Python files")
    
    # Extract strings using xgettext
    logger.info("Attempting extraction with xgettext...")
    xgettext_success = extract_with_xgettext(python_files, pot_file)
    
    if not xgettext_success:
        # Fallback to manual extraction
        logger.info("Falling back to manual string extraction...")
        
        all_strings = set()
        
        # Extract from Python files
        for python_file in python_files:
            strings = extract_translatable_strings(python_file)
            all_strings.update(strings)
            if strings:
                logger.debug(f"Found {len(strings)} strings in {python_file}")
        
        # Analyze UI files
        logger.info("Analyzing UI files...")
        ui_strings = analyze_ui_files(source_dir)
        
        for ui_file, strings in ui_strings.items():
            all_strings.update(strings)
            if strings:
                logger.info(f"Found {len(strings)} strings in UI file: {ui_file}")
        
        # Create .pot file manually
        if all_strings:
            create_pot_template(all_strings, pot_file)
        else:
            logger.warning("No translatable strings found")
            return
    
    # Update existing .po files with new strings
    po_files = list(locale_dir.rglob("*.po"))
    
    if po_files:
        logger.info(f"Found {len(po_files)} .po files to update")
        
        for po_file in po_files:
            update_po_file(po_file, pot_file)
    
    logger.info("Translation extraction completed")


def update_po_file(po_file: Path, pot_file: Path) -> bool:
    """
    Update an existing .po file with new strings from .pot file.
    
    Args:
        po_file: Path to existing .po file
        pot_file: Path to .pot template file
        
    Returns:
        True if update successful
    """
    try:
        # Use msgmerge to update the .po file
        result = subprocess.run([
            'msgmerge', '--update', '--backup=off', str(po_file), str(pot_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Updated: {po_file}")
            return True
        else:
            logger.error(f"Failed to update {po_file}: {result.stderr}")
            return False
    
    except FileNotFoundError:
        logger.warning("msgmerge not found. Please install gettext package.")
        return False
    except Exception as e:
        logger.error(f"Error updating {po_file}: {e}")
        return False


if __name__ == "__main__":
    main()