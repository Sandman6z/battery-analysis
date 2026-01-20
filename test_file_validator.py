#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileValidator测试脚本
"""

import os
import tempfile
from src.battery_analysis.utils.file_validator import FileValidator


def test_file_validator():
    """
    测试FileValidator类的所有方法
    """
    validator = FileValidator()
    
    print("=== 测试FileValidator类 ===")
    
    # 测试1: 验证文件名
    print("\n1. 测试文件名验证:")
    test_cases = [
        ("valid_file.xlsx", True),
        ("invalid file/name.xlsx", False),  # 包含无效字符
        ("文件中文名.xlsx", False),  # 包含中文
        ("CON.xlsx", False),  # 保留文件名
        ("a" * 256 + ".xlsx", False),  # 过长文件名
    ]
    
    for filename, expected in test_cases:
        is_valid, error_msg = validator.validate_filename(filename)
        status = "通过" if is_valid == expected else "失败"
        print(f"  {filename}: {status} - {error_msg}")
    
    # 测试2: 验证Excel文件名
    print("\n2. 测试Excel文件名验证:")
    excel_test_cases = [
        ("DC20230101,Test,100-200mA,25C.xlsx", True),
        ("invalid.xlsx", False),  # 缺少DC前缀
        ("DC20230101,Test,25C.xlsx", False),  # 缺少mA
        ("DC20230101Test100-200mA25C.xlsx", False),  # 缺少逗号
        ("DC20230101,Test,100-200mA.xlsx", False),  # 缺少温度信息
    ]
    
    for filename, expected in excel_test_cases:
        is_valid, error_msg = validator.validate_excel_filename(filename)
        status = "通过" if is_valid == expected else "失败"
        print(f"  {filename}: {status} - {error_msg}")
    
    # 测试3: 验证XML文件名
    print("\n3. 测试XML文件名验证:")
    xml_test_cases = [
        ("test_profile.xml", True),
        ("invalid.xml", True),  # 基本验证
        ("文件中文名.xml", False),  # 包含中文
        ("CON.xml", False),  # 保留文件名
    ]
    
    for filename, expected in xml_test_cases:
        is_valid, error_msg = validator.validate_xml_filename(filename)
        status = "通过" if is_valid == expected else "失败"
        print(f"  {filename}: {status} - {error_msg}")
    
    # 测试4: 验证完整路径
    print("\n4. 测试完整路径验证:")
    path_test_cases = [
        ("C:\\valid\\path", True),
        ("C:\\invalid\\path\\with?char", False),  # 包含无效字符
        ("C:" + "\\a" * 200, False),  # 过长路径
    ]
    
    for path, expected in path_test_cases:
        is_valid, error_msg = validator.validate_full_path(path)
        status = "通过" if is_valid == expected else "失败"
        print(f"  {path}: {status} - {error_msg}")
    
    # 测试5: 验证目录结构
    print("\n5. 测试目录结构验证:")
    with tempfile.TemporaryDirectory() as temp_dir:
        # 有效目录
        is_valid, error_msg = validator.validate_directory_structure(temp_dir)
        print(f"  有效目录: {'通过' if is_valid else '失败'} - {error_msg}")
        
        # 无效目录（不存在）
        non_existent_dir = os.path.join(temp_dir, "non_existent")
        is_valid, error_msg = validator.validate_directory_structure(non_existent_dir)
        print(f"  不存在目录: {'通过' if not is_valid else '失败'} - {error_msg}")
    
    # 测试6: 验证输入目录
    print("\n6. 测试输入目录验证:")
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建2_xlsx目录
        xlsx_dir = os.path.join(temp_dir, "2_xlsx")
        os.makedirs(xlsx_dir)
        
        # 有效输入目录
        is_valid, error_msg = validator.validate_input_directory(xlsx_dir)
        print(f"  有效输入目录: {'通过' if is_valid else '失败'} - {error_msg}")
        
        # 无效输入目录（不是2_xlsx）
        wrong_dir = os.path.join(temp_dir, "wrong_dir")
        os.makedirs(wrong_dir)
        is_valid, error_msg = validator.validate_input_directory(wrong_dir)
        print(f"  非2_xlsx目录: {'通过' if not is_valid else '失败'} - {error_msg}")
    
    # 测试7: 验证输出目录
    print("\n7. 测试输出目录验证:")
    with tempfile.TemporaryDirectory() as temp_dir:
        # 有效输出目录（存在）
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir)
        is_valid, error_msg = validator.validate_output_directory(output_dir)
        print(f"  有效输出目录: {'通过' if is_valid else '失败'} - {error_msg}")
        
        # 有效输出目录（不存在）
        new_output_dir = os.path.join(temp_dir, "new_output")
        is_valid, error_msg = validator.validate_output_directory(new_output_dir)
        print(f"  不存在输出目录: {'通过' if is_valid else '失败'} - {error_msg}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_file_validator()
