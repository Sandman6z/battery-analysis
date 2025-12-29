#!/usr/bin/env python3
"""
最小化翻译编译脚本
正确生成.mo文件
"""

import os
import sys
from pathlib import Path
import struct
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_po_file(po_path: Path):
    """解析.po文件，提取消息对"""
    messages = []
    
    try:
        with open(po_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过注释和空行
            if line.startswith('#') or not line:
                i += 1
                continue
            
            # 查找msgid
            if line.startswith('msgid'):
                msgid_line = line
                if msgid_line == 'msgid ""':
                    # 处理多行msgid
                    i += 1
                    msgid = ""
                    while i < len(lines):
                        line = lines[i].strip()
                        if line.startswith('msgstr'):
                            if line == 'msgstr ""':
                                # 处理多行msgstr
                                i += 1
                                msgstr = ""
                                while i < len(lines):
                                    line = lines[i].strip()
                                    if line.startswith('msgid') or line.startswith('#'):
                                        break
                                    if line:
                                        # 去掉引号
                                        msgstr += line.strip('"')
                                    i += 1
                                break
                            else:
                                # 单行msgstr
                                msgstr = line[7:].strip('"')
                                i += 1
                                break
                        elif line:
                            msgid += line.strip('"')
                        i += 1
                else:
                    # 单行msgid
                    msgid = line[6:].strip('"')
                    i += 1
                
                # 跳过空的消息
                if msgid:
                    messages.append((msgid, msgstr))
            else:
                i += 1
    
    except Exception as e:
        logger.error(f"Error parsing {po_path}: {e}")
        return []
    
    return messages

def compile_to_mo(messages, mo_path: Path):
    """将消息编译为.mo格式"""
    try:
        # 确保输出目录存在
        mo_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 按msgid排序
        messages.sort(key=lambda x: x[0])
        
        # 构建目录
        koffsets = []
        voffsets = []
        kencoded = []
        vencoded = []
        
        for msgid, msgstr in messages:
            kencoded.append(msgid.encode('utf-8'))
            vencoded.append(msgstr.encode('utf-8'))
        
        # 计算偏移量
        koffset = 7 * 4 + len(messages) * 8  # 头信息 + 键表
        voffset = koffset + sum(len(k) for k in kencoded)  # 键字符串之后
        
        for i, (k, v) in enumerate(zip(kencoded, vencoded)):
            koffsets.append((len(k), koffset))
            voffsets.append((len(v), voffset))
            koffset += len(k)
            voffset += len(v)
        
        # 写入.mo文件
        with open(mo_path, 'wb') as f:
            # 头部
            f.write(struct.pack('<I', 0x950412de))  # magic
            f.write(struct.pack('<I', 0))           # version
            f.write(struct.pack('<I', len(messages)))  # count
            f.write(struct.pack('<I', 7 * 4))       # offset of table
            f.write(struct.pack('<I', 7 * 4 + len(messages) * 8))  # offset of strings
            f.write(struct.pack('<I', 0))           # hash table size
            f.write(struct.pack('<I', 0))           # hash table offset
            
            # 键表
            for length, offset in koffsets:
                f.write(struct.pack('<I', length))
                f.write(struct.pack('<I', offset))
            
            # 值表
            for length, offset in voffsets:
                f.write(struct.pack('<I', length))
                f.write(struct.pack('<I', offset))
            
            # 键字符串
            for k in kencoded:
                f.write(k)
            
            # 值字符串
            for v in vencoded:
                f.write(v)
        
        logger.info(f"Successfully compiled to: {mo_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error compiling to {mo_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    project_root = Path(__file__).parent.parent
    locale_dir = project_root / "locale"
    
    logger.info(f"Compiling translations from: {locale_dir}")
    
    if not locale_dir.exists():
        logger.error(f"Locale directory not found: {locale_dir}")
        return
    
    # 查找所有.po文件
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
        logger.info(f"Processing {po_file}...")
        
        # 解析.po文件
        messages = parse_po_file(po_file)
        if not messages:
            logger.error(f"Failed to parse {po_file}")
            failed += 1
            continue
        
        logger.info(f"Parsed {len(messages)} messages")
        
        # 编译为.mo文件
        if compile_to_mo(messages, mo_file):
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
        logger.warning("Some translations failed to compile!")

if __name__ == "__main__":
    main()