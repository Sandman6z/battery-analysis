#!/usr/bin/env python3
"""
Use Python's built-in gettext module to properly compile .po files to .mo files.
"""

import os
import sys
from pathlib import Path
import gettext
import struct
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GettextCompiler:
    """Use gettext to compile .po files properly"""
    
    def __init__(self):
        self.magic = 0x950412de
        self.version = 0
    
    def parse_po_file(self, po_file_path):
        """Parse .po file and extract messages"""
        messages = {}
        
        try:
            with open(po_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple parsing - look for msgid/msgstr pairs
            lines = content.split('\n')
            current_msgid = ""
            current_msgstr = ""
            in_msgid = False
            in_msgstr = False
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('msgid '):
                    # Save previous entry if exists
                    if current_msgid and current_msgstr and current_msgid.strip():
                        messages[current_msgid] = current_msgstr
                    
                    # Start new entry
                    msgid_content = line[6:].strip('"')
                    current_msgid = msgid_content
                    current_msgstr = ""
                    in_msgid = True
                    in_msgstr = False
                    
                elif line.startswith('msgstr '):
                    msgstr_content = line[7:].strip('"')
                    current_msgstr = msgstr_content
                    in_msgid = False
                    in_msgstr = True
                    
                elif line.startswith('"') and (in_msgid or in_msgstr):
                    # Continuation line
                    content_part = line.strip('"')
                    if in_msgid:
                        current_msgid += content_part
                    elif in_msgstr:
                        current_msgstr += content_part
                        
                elif line.startswith('#') or not line:
                    # Comment or empty line - skip
                    pass
                    
            # Don't forget the last entry
            if current_msgid and current_msgstr and current_msgid.strip():
                messages[current_msgid] = current_msgstr
                
            # Remove empty msgid (header entry)
            if "" in messages:
                del messages[""]
                
            logger.info(f"Parsed {len(messages)} messages from {po_file_path}")
            return messages
            
        except Exception as e:
            logger.error(f"Error parsing {po_file_path}: {e}")
            return {}
    
    def write_mo_file(self, messages, mo_file_path):
        """Write messages to .mo file using gettext format"""
        try:
            # Ensure output directory exists
            mo_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Sort messages by msgid
            sorted_items = sorted(messages.items())
            msgids = [msgid.encode('utf-8') for msgid, _ in sorted_items]
            msgstrs = [msgstr.encode('utf-8') for _, msgstr in sorted_items]
            
            n = len(msgids)
            
            # Calculate offsets
            koffsets = []
            voffsets = []
            
            # Header is 7 * 4 bytes
            # Key table is n * 8 bytes  
            # Value table is n * 8 bytes
            # String data starts after tables
            string_start = 7 * 4 + n * 8 + n * 8
            
            # Calculate key offsets
            offset = string_start
            for msgid in msgids:
                koffsets.append((len(msgid), offset))
                offset += len(msgid)
            
            # Calculate value offsets  
            for msgstr in msgstrs:
                voffsets.append((len(msgstr), offset))
                offset += len(msgstr)
            
            # Write .mo file
            with open(mo_file_path, 'wb') as f:
                # Header
                f.write(struct.pack('<I', self.magic))    # Magic
                f.write(struct.pack('<I', self.version))  # Version
                f.write(struct.pack('<I', n))             # Number of messages
                f.write(struct.pack('<I', 7 * 4))         # Offset of key table
                f.write(struct.pack('<I', 7 * 4 + n * 8)) # Offset of value table
                f.write(struct.pack('<I', 0))             # Hash table size
                f.write(struct.pack('<I', 0))             # Hash table offset
                
                # Key table
                for length, offset in koffsets:
                    f.write(struct.pack('<I', length))
                    f.write(struct.pack('<I', offset))
                
                # Value table
                for length, offset in voffsets:
                    f.write(struct.pack('<I', length))
                    f.write(struct.pack('<I', offset))
                
                # Key strings
                for msgid in msgids:
                    f.write(msgid)
                
                # Value strings
                for msgstr in msgstrs:
                    f.write(msgstr)
            
            logger.info(f"Successfully wrote {n} messages to {mo_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing {mo_file_path}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def compile_file(self, po_file_path, mo_file_path):
        """Compile a single .po file to .mo"""
        messages = self.parse_po_file(po_file_path)
        
        if not messages:
            logger.warning(f"No messages found in {po_file_path}")
            return False
        
        return self.write_mo_file(messages, mo_file_path)


def main():
    """Main compilation function"""
    project_root = Path(__file__).parent.parent
    locale_dir = project_root / "locale"
    
    logger.info(f"Compiling translations from: {locale_dir}")
    
    if not locale_dir.exists():
        logger.error(f"Locale directory not found: {locale_dir}")
        return
    
    compiler = GettextCompiler()
    
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
        
        if compiler.compile_file(po_file, mo_file):
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