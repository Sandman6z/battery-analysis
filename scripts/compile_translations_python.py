#!/usr/bin/env python3
"""
Python-based Translation Compilation Script

This script compiles .po files to .mo files using Python's built-in capabilities,
suitable for environments where gettext tools are not available (e.g., Windows).
"""

import os
import struct
import logging
import locale
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PythonPoCompiler:
    """Python-based .po to .mo compiler"""
    
    def __init__(self):
        self.msgids = []
        self.msgstrs = []
        self.contexts = []
    
    def parse_po_file(self, po_file: Path) -> bool:
        """
        Parse a .po file and extract messages.
        
        Args:
            po_file: Path to .po file
            
        Returns:
            True if parsing successful
        """
        try:
            with open(po_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process the content
            # We'll split on msgid to get blocks
            blocks = content.split('\n\n')
            
            for block in blocks:
                if not block.strip():
                    continue
                
                lines = block.split('\n')
                
                # Extract msgid and msgstr
                msgid = ""
                msgstr = ""
                
                for line in lines:
                    line = line.strip()
                    
                    if line.startswith('msgid '):
                        msgid = line[6:].strip('"')
                    elif line.startswith('msgstr '):
                        msgstr = line[7:].strip('"')
                    elif line.startswith('"') and line.endswith('"') and len(line) > 2:
                        # This is a continuation line
                        content = line[1:-1]
                        
                        if msgid and not msgstr:
                            # Still building msgid
                            msgid += content
                        elif msgstr:
                            # Building msgstr
                            msgstr += content
                
                # Skip header (empty msgid)
                if msgid != "":
                    self._add_message(msgid, msgstr)
            
            logger.info(f"Parsed {len(self.msgids)} messages from {po_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error parsing {po_file}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _add_message(self, msgid: str, msgstr: str):
        """Add a message to the internal storage"""
        # Accept all msgid, even empty ones
        self.msgids.append(msgid)
        self.msgstrs.append(msgstr)
        self.contexts.append("")
    
    def compile_to_mo(self, mo_file: Path) -> bool:
        """
        Compile the parsed messages to .mo format.
        
        Args:
            mo_file: Path to output .mo file
            
        Returns:
            True if compilation successful
        """
        try:
            # Ensure output directory exists
            mo_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create the .mo file structure
            keys = []
            
            # Build the key-value pairs
            for i, (msgid, msgstr) in enumerate(zip(self.msgids, self.msgstrs)):
                keys.append((msgid.encode('utf-8'), msgstr.encode('utf-8')))
            
            # Sort by key
            keys.sort(key=lambda x: x[0])
            
            # Calculate string lengths and offsets
            # The format of a .mo file is:
            # - Magic number (4 bytes)
            # - Version (4 bytes)
            # - Number of entries (4 bytes)
            # - Offset of key table (4 bytes)
            # - Offset of value table (4 bytes)
            # - Hash table size (4 bytes) - unused
            # - Hash table offset (4 bytes) - unused
            # - Key table (8 bytes per entry: length + offset)
            # - Value table (8 bytes per entry: length + offset)
            # - Key strings
            # - Value strings
            
            num_entries = len(keys)
            
            # Calculate the size of the fixed header
            header_size = 7 * 4  # 7 * 4-byte integers
            
            # Calculate offsets
            key_table_size = num_entries * 8  # 8 bytes per entry
            value_table_size = num_entries * 8  # 8 bytes per entry
            
            # Calculate string offsets
            key_strings_offset = header_size + key_table_size + value_table_size
            value_strings_offset = key_strings_offset
            
            # Calculate the total size of all key strings
            key_strings_total_size = sum(len(key) for key, _ in keys)
            
            # Calculate the offset of value strings (after key strings)
            value_strings_offset += key_strings_total_size
            
            # Write the .mo file
            with open(mo_file, 'wb') as f:
                # Magic number (0x950412de in little-endian format)
                f.write(struct.pack('<I', 0x950412de))
                
                # Version (0)
                f.write(struct.pack('<I', 0))
                
                # Number of entries
                f.write(struct.pack('<I', num_entries))
                
                # Offset of key table
                f.write(struct.pack('<I', header_size))
                
                # Offset of value table
                f.write(struct.pack('<I', header_size + key_table_size))
                
                # Hash table size (unused)
                f.write(struct.pack('<I', 0))
                
                # Hash table offset (unused)
                f.write(struct.pack('<I', 0))
                
                # Key table
                for key, _ in keys:
                    length = len(key)
                    f.write(struct.pack('<I', length))
                    # We'll update the offset later
                    f.write(struct.pack('<I', 0))
                
                # Value table
                for _, value in keys:
                    length = len(value)
                    f.write(struct.pack('<I', length))
                    # We'll update the offset later
                    f.write(struct.pack('<I', 0))
                
                # Key strings
                for key, _ in keys:
                    f.write(key)
                
                # Value strings
                current_value_offset = 0
                for _, value in keys:
                    f.write(value)
                    current_value_offset += len(value)
            
            # Now we need to go back and update the offsets in the file
            with open(mo_file, 'r+b') as f:
                # Skip header
                f.seek(header_size)
                
                # Update key table offsets
                for key, _ in keys:
                    # Write the offset (skip length and write offset)
                    f.seek(4, 1)  # Skip length
                    offset = struct.pack('<I', 0)
                    f.write(offset)
                
                # Update value table offsets
                current_value_offset = 0
                for _, value in keys:
                    # Write the offset (skip length and write offset)
                    f.seek(4, 1)  # Skip length
                    offset = struct.pack('<I', current_value_offset)
                    f.write(offset)
                    current_value_offset += len(value)
                
                # Update key table offsets with correct values
                current_key_offset = 0
                for key, _ in keys:
                    # Skip the length field
                    f.seek(4, 1)
                    # Write the offset
                    offset = struct.pack('<I', current_key_offset)
                    f.write(offset)
                    current_key_offset += len(key)
            
            logger.info(f"Successfully compiled to: {mo_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error compiling to {mo_file}: {e}")
            import traceback
            traceback.print_exc()
            return False


def find_po_files(locale_dir: Path) -> List[Path]:
    """Find all .po files in locale directory"""
    po_files = []
    
    if not locale_dir.exists():
        logger.error(f"Locale directory not found: {locale_dir}")
        return po_files
    
    # Search for .po files
    for locale_subdir in locale_dir.iterdir():
        if locale_subdir.is_dir():
            po_file = locale_subdir / "LC_MESSAGES" / "messages.po"
            if po_file.exists():
                po_files.append(po_file)
    
    return po_files


def main():
    """Main function"""
    # Get locale directory
    locale_dir = Path(__file__).parent.parent / "locale"
    
    logger.info(f"Compiling translations from: {locale_dir}")
    
    # Find all .po files
    po_files = find_po_files(locale_dir)
    
    if not po_files:
        logger.warning("No .po files found")
        return
    
    logger.info(f"Found {len(po_files)} .po files")
    
    # Process each file
    success_count = 0
    for po_file in po_files:
        logger.info(f"Processing: {po_file}")
        
        # Create compiler
        compiler = PythonPoCompiler()
        
        # Parse .po file
        if compiler.parse_po_file(po_file):
            # Compile to .mo file
            mo_file = po_file.with_suffix('.mo')
            if compiler.compile_to_mo(mo_file):
                success_count += 1
    
    # Print summary
    logger.info("\nCompilation Summary:")
    logger.info(f"  Total files: {len(po_files)}")
    logger.info(f"  Successful: {success_count}")
    logger.info(f"  Failed: {len(po_files) - success_count}")
    
    if success_count == len(po_files):
        logger.info("All translations compiled successfully!")
    else:
        logger.error("Some translations failed to compile")


if __name__ == "__main__":
    main()