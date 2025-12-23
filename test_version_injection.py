#!/usr/bin/env python3
"""
测试版本管理功能的脚本
"""
import sys
import os
from pathlib import Path
import tomllib

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入Version类
from src.battery_analysis.utils.version import Version

def test_default_version():
    """测试默认从pyproject.toml读取版本号"""
    print("=== 测试默认版本获取 ===")
    # 重置单例
    Version._instance = None
    
    version = Version()
    print(f"从pyproject.toml读取的版本号: {version.version}")
    assert version.version != "0.0.0", "版本号不应该是默认值"
    print("✓ 默认版本获取测试通过")

def test_debug_suffix():
    """测试debug后缀功能"""
    print("\n=== 测试Debug后缀功能 ===")
    # 重置单例
    Version._instance = None
    
    # 读取原始版本号用于比较
    with open(Path(__file__).parent / "pyproject.toml", "rb") as f:
        pyproject_data = tomllib.load(f)
    original_version = pyproject_data["project"]["version"]
    
    # 设置debug环境变量
    os.environ["DEBUG"] = "true"
    
    version = Version()
    expected_version = f"{original_version}.debug"
    print(f"原始版本号: {original_version}")
    print(f"Debug环境下的版本号: {version.version}")
    assert version.version == expected_version, f"版本号应该是{expected_version}，但实际是{version.version}"
    print("✓ Debug后缀测试通过")
    
    # 清除环境变量
    del os.environ["DEBUG"]

def test_development_version():
    """测试开发环境版本获取"""
    print("\n=== 测试开发环境版本获取 ===")
    # 重置单例
    Version._instance = None
    
    # 模拟开发环境（非frozen状态）
    original_frozen = getattr(sys, 'frozen', False)
    try:
        # 确保sys.frozen为False
        if hasattr(sys, 'frozen'):
            del sys.frozen
        
        version = Version()
        print(f"开发环境版本号: {version.version}")
        assert version.version != "0.0.0", "版本号不应该是默认值"
        print("✓ 开发环境版本获取测试通过")
    finally:
        # 恢复原来的frozen状态
        if original_frozen:
            sys.frozen = original_frozen

def test_version_consistency():
    """测试版本一致性：多次调用应该返回相同的版本号"""
    print("\n=== 测试版本一致性 ===")
    # 重置单例
    Version._instance = None
    
    # 第一次获取版本
    version1 = Version()
    print(f"第一次获取的版本号: {version1.version}")
    
    # 第二次获取版本（应该使用缓存）
    version2 = Version()
    print(f"第二次获取的版本号: {version2.version}")
    
    # 检查是否是同一个实例
    print(f"是否是同一个实例: {version1 is version2}")
    assert version1.version == version2.version, "多次获取的版本号应该一致"
    assert version1 is version2, "Version类应该是单例模式"
    print("✓ 版本一致性测试通过")

if __name__ == "__main__":
    try:
        test_default_version()
        test_debug_suffix()
        test_development_version()
        test_version_consistency()
        print("\n🎉 所有测试都通过了！版本管理功能正常工作。")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
