#!/usr/bin/env python3
"""测试exe文件启动"""

import os
import sys
import subprocess
import time

def test_exe_start():
    """测试exe文件启动"""
    exe_path = "battery-analyzer_1_0_1.exe"
    
    # 检查exe文件是否存在
    if not os.path.exists(exe_path):
        print(f"错误: 找不到 {exe_path}")
        return False
    
    print(f"正在测试exe启动: {exe_path}")
    print(f"当前目录: {os.getcwd()}")
    print(f"exe文件大小: {os.path.getsize(exe_path)} bytes")
    
    try:
        # 启动exe进程
        print("正在启动exe...")
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 cwd=os.getcwd())
        
        # 等待2秒观察进程状态
        print("等待2秒观察进程状态...")
        time.sleep(2)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✓ exe进程正在运行中...")
            # 等待5秒再检查
            time.sleep(5)
            if process.poll() is None:
                print("✓ exe进程持续运行，UI应该已经显示")
                return True
            else:
                stdout, stderr = process.communicate()
                print("✗ exe进程过早退出")
                print(f"STDOUT: {stdout.decode('gbk', errors='ignore')}")
                print(f"STDERR: {stderr.decode('gbk', errors='ignore')}")
                return False
        else:
            stdout, stderr = process.communicate()
            print("✗ exe进程启动后立即退出")
            print(f"STDOUT: {stdout.decode('gbk', errors='ignore')}")
            print(f"STDERR: {stderr.decode('gbk', errors='ignore')}")
            return False
            
    except Exception as e:
        print(f"✗ 启动exe时发生异常: {e}")
        return False

if __name__ == "__main__":
    success = test_exe_start()
    if success:
        print("\n✓ 测试成功: exe正常启动并运行")
        sys.exit(0)
    else:
        print("\n✗ 测试失败: exe启动异常")
        sys.exit(1)