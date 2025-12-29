#!/usr/bin/env python3
"""
Proper .mo file compiler for gettext
This script creates properly formatted .mo files according to the gettext specification.
"""

import os
import sys
from pathlib import Path
import struct
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoParser:
    """Simple and robust PO file parser"""
    
    def __init__(self):
        self.messages = []
    
    def parse(self, po_path: Path):
        """Parse a .po file and extract messages"""
        try:
            with open(po_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex-based parsing
            # This handles most common PO file structures
            
            # Skip header entries (empty msgid)
            # Process each msgid/msgstr pair
            msgid_pattern = r'msgid\s+"([^"]*)"'
            msgstr_pattern = r'msgstr\s+"([^"]*)"'
            
            # Find all msgid entries
            msgid_matches = list(re.finditer(msgid_pattern, content))
            msgstr_matches = list(re.finditer(msgstr_pattern, content))
            
            if len(msgid_matches) != len(msgstr_matches):
                logger.warning(f"Mismatched msgid/msgstr count in {po_path}")
            
            # Process pairs
            for i in range(min(len(msgid_matches), len(msgstr_matches))):
                msgid_match = msgid_matches[i]
                msgstr_match = msgstr_matches[i]
                
                msgid = msgid_match.group(1)
                msgstr = msgstr_match.group(1)
                
                # Skip empty msgid (usually header)
                if not msgid.strip():
                    continue
                
                self.messages.append((msgid, msgstr))
            
            logger.info(f"Parsed {len(self.messages)} messages from {po_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error parsing {po_path}: {e}")
            return False
    
    def get_messages(self):
        """Get parsed messages"""
        return self.messages


class MoWriter:
    """Write .mo files in the correct gettext format"""
    
    @staticmethod
    def write(messages, mo_path: Path):
        """Write messages to a .mo file"""
        try:
            # Ensure output directory exists
            mo_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Sort messages by msgid for consistent output
            messages.sort(key=lambda x: x[0])
            
            # Prepare strings
            keys = [msgid.encode('utf-8') for msgid, _ in messages]
            values = [msgstr.encode('utf-8') for _, msgstr in messages]
            
            # Calculate offsets
            # Header: 7 * 4 bytes
            # Key table: len(messages) * 8 bytes
            # Value table: len(messages) * 8 bytes
            # String data starts after tables
            
            n = len(messages)
            header_size = 7 * 4
            table_size = n * 8
            
            # Calculate where string data starts
            string_data_start = header_size + table_size + table_size
            
            # Calculate offsets for keys and values
            key_offsets = []
            value_offsets = []
            
            current_offset = string_data_start
            
            # Key string offsets
            for key in keys:
                key_offsets.append((len(key), current_offset))
                current_offset += len(key)
            
            # Value string offsets
            for value in values:
                value_offsets.append((len(value), current_offset))
                current_offset += len(value)
            
            # Write .mo file
            with open(mo_path, 'wb') as f:
                # Header
                f.write(struct.pack('<I', 0x950412de))  # Magic number
                f.write(struct.pack('<I', 0))           # Version
                f.write(struct.pack('<I', n))           # Number of messages
                f.write(struct.pack('<I', header_size)) # Offset of key table
                f.write(struct.pack('<I', header_size + table_size))  # Offset of value table
                f.write(struct.pack('<I', 0))           # Hash table size (unused)
                f.write(struct.pack('<I', 0))           # Hash table offset (unused)
                
                # Key table (length, offset pairs)
                for length, offset in key_offsets:
                    f.write(struct.pack('<I', length))
                    f.write(struct.pack('<I', offset))
                
                # Value table (length, offset pairs)
                for length, offset in value_offsets:
                    f.write(struct.pack('<I', length))
                    f.write(struct.pack('<I', offset))
                
                # Key strings
                for key in keys:
                    f.write(key)
                
                # Value strings
                for value in values:
                    f.write(value)
            
            logger.info(f"Successfully wrote {n} messages to {mo_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing {mo_path}: {e}")
            import traceback
            traceback.print_exc()
            return False


def compile_locale(po_file: Path, mo_file: Path):
    """Compile a single .po file to .mo"""
    parser = PoParser()
    
    if not parser.parse(po_file):
        return False
    
    messages = parser.get_messages()
    
    if not messages:
        logger.warning(f"No messages found in {po_file}")
        return False
    
    return MoWriter.write(messages, mo_file)


def main():
    """Main compilation function"""
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
        
        if compile_locale(po_file, mo_file):
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