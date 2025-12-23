#!/usr/bin/env python3
"""
测试版本号处理是否符合要求
1. 验证Version类是否正确从pyproject.toml读取3位版本号
2. 验证版本号格式是否严格按照3位语义化格式
3. 验证没有不必要的4位版本号
"""
import os
import sys
import tomlkit

# 添加src目录到Python路径，以便导入Version类
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from battery_analysis.utils.version import Version

def test_version_format():
    """测试版本号格式是否符合要求"""
    print("开始测试版本号处理...")
    
    # 1. 从Version类获取版本号
    version_instance = Version()
    version_from_class = version_instance.version
    print(f"1. 从Version类获取的版本号: {version_from_class}")
    
    # 2. 直接从pyproject.toml读取版本号进行对比
    with open('pyproject.toml', 'r', encoding='utf-8') as f:
        pyproject_data = tomlkit.parse(f.read())
    version_from_toml = pyproject_data['project']['version']
    print(f"2. 直接从pyproject.toml读取的版本号: {version_from_toml}")
    
    # 3. 验证版本格式
    # 移除可能的.debug后缀
    clean_version = version_from_class.replace('.debug', '')
    version_parts = clean_version.split('.')
    
    print(f"3. 清理后的版本号: {clean_version}")
    print(f"4. 版本号部分: {version_parts}")
    
    # 检查是否严格为3位
    if len(version_parts) == 3:
        print("✅ 版本号格式正确: 严格按照3位语义化格式 (MAJOR.MINOR.PATCH)")
    else:
        print(f"❌ 版本号格式错误: 不是3位格式，而是{len(version_parts)}位")
        return False
    
    # 检查是否所有部分都是数字
    for part in version_parts:
        if not part.isdigit():
            print(f"❌ 版本号部分错误: {part} 不是数字")
            return False
    
    # 4. 验证Version类读取的版本号与pyproject.toml一致
    if version_from_class.replace('.debug', '') == version_from_toml:
        print("✅ Version类读取的版本号与pyproject.toml一致")
    else:
        print(f"❌ Version类读取的版本号与pyproject.toml不一致")
        return False
    
    print("\n🎉 所有版本号处理测试通过！")
    return True

if __name__ == "__main__":
    success = test_version_format()
    sys.exit(0 if success else 1)