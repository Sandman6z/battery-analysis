#!/usr/bin/env python3
"""
测试exe文件的启动是否正常
"""

import os
import subprocess
import sys

def test_exe_launch(exe_path, test_name):
    """测试exe文件启动"""
    print(f"\n=== 测试 {test_name} ===")
    print(f"可执行文件路径: {exe_path}")
    
    if not os.path.exists(exe_path):
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False
    
    try:
        # 尝试启动exe（使用短暂的超时来检查启动是否有错误）
        print("正在启动...")
        result = subprocess.run(
            [exe_path], 
            capture_output=True, 
            text=True, 
            timeout=10  # 10秒超时
        )
        
        # 检查退出代码
        if result.returncode == 0:
            print(f"✅ {test_name} 启动成功")
            return True
        else:
            print(f"❌ {test_name} 启动失败，退出代码: {result.returncode}")
            if result.stderr:
                print("错误输出:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✅ {test_name} 启动成功（正常超时）")
        return True
    except Exception as e:
        print(f"❌ {test_name} 启动异常: {e}")
        return False

def main():
    # 测试两个exe文件
    exe_dir = r"c:\Users\zbnsa\Desktop\battery-analysis\build\Debug"
    
    # 测试battery-analyzer
    analyzer_exe = os.path.join(exe_dir, "battery-analyzer_1_0_1.exe")
    analyzer_result = test_exe_launch(analyzer_exe, "Battery Analyzer")
    
    # 测试battery-analysis-visualizer  
    visualizer_exe = os.path.join(exe_dir, "battery-analysis-visualizer_1_0_1.exe")
    visualizer_result = test_exe_launch(visualizer_exe, "Battery Analysis Visualizer")
    
    # 总结
    print("\n=== 测试总结 ===")
    print(f"Battery Analyzer: {'✅ 通过' if analyzer_result else '❌ 失败'}")
    print(f"Battery Analysis Visualizer: {'✅ 通过' if visualizer_result else '❌ 失败'}")
    
    if analyzer_result and visualizer_result:
        print("\n🎉 所有测试通过！exe文件可以正常启动。")
    else:
        print("\n⚠️  存在失败的测试，请检查错误信息。")

if __name__ == "__main__":
    main()