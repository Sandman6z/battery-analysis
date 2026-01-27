#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试版本号管理修复效果

此脚本用于测试版本号是否每次只增加1，而不是每次增加2
"""

import os
import sys
import csv
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from battery_analysis.main.utils.file_utils import FileUtils


def test_version_increment():
    """
    测试版本号递增逻辑
    """
    print("=== 测试版本号递增逻辑 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"创建临时目录: {temp_dir}")
        
        # 创建测试XLSX文件
        test_xlsx = os.path.join(temp_dir, "test.xlsx")
        with open(test_xlsx, 'w') as f:
            f.write("测试文件内容")
        print(f"创建测试文件: {test_xlsx}")
        
        # 测试1: 第一次运行
        print("\n测试1: 第一次运行")
        sha256_file = os.path.join(temp_dir, "SHA256.csv")
        
        # 计算校验和
        checksum1 = FileUtils.calc_checksum([test_xlsx])
        print(f"第一次校验和: {checksum1}")
        
        # 写入SHA256.csv文件
        with open(sha256_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Checksums:"])
            writer.writerow([checksum1])
            writer.writerow(["Times:"])
            writer.writerow(["0"])
        print(f"写入SHA256.csv文件")
        
        # 测试2: 第二次运行（相同文件内容）
        print("\n测试2: 第二次运行（相同文件内容）")
        checksum2 = FileUtils.calc_checksum([test_xlsx])
        print(f"第二次校验和: {checksum2}")
        
        # 读取并检查校验和
        with open(sha256_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if len(rows) >= 4:
            existing_checksums = rows[1]
            print(f"现有校验和列表: {existing_checksums}")
            
            # 检查校验和是否已存在
            existing_index = -1
            for i, checksum in enumerate(existing_checksums):
                if checksum == checksum2:
                    existing_index = i
                    break
            
            if existing_index >= 0:
                print(f"校验和已存在，使用现有版本号: {existing_index + 1}.0")
            else:
                print(f"校验和不存在，增加版本号: {len(existing_checksums) + 1}.0")
        
        # 测试3: 第三次运行（修改文件内容）
        print("\n测试3: 第三次运行（修改文件内容）")
        # 修改测试文件内容
        with open(test_xlsx, 'w') as f:
            f.write("修改后的测试文件内容")
        
        checksum3 = FileUtils.calc_checksum([test_xlsx])
        print(f"第三次校验和: {checksum3}")
        
        # 读取并检查校验和
        with open(sha256_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if len(rows) >= 4:
            existing_checksums = rows[1]
            print(f"现有校验和列表: {existing_checksums}")
            
            # 检查校验和是否已存在
            existing_index = -1
            for i, checksum in enumerate(existing_checksums):
                if checksum == checksum3:
                    existing_index = i
                    break
            
            if existing_index >= 0:
                print(f"校验和已存在，使用现有版本号: {existing_index + 1}.0")
            else:
                print(f"校验和不存在，增加版本号: {len(existing_checksums) + 1}.0")
        
        print("\n=== 测试完成 ===")
        print("修复后的版本号管理逻辑应该会：")
        print("1. 第一次运行: 版本号 = 1.0")
        print("2. 第二次运行（相同文件）: 版本号 = 1.0（不变）")
        print("3. 第三次运行（修改文件）: 版本号 = 2.0（增加1）")


if __name__ == "__main__":
    test_version_increment()
