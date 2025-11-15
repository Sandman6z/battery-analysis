#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试exe启动和运行状态
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

def test_exe_detailed():
    exe_path = "battery-analyzer_1_0_1.exe"
    current_dir = Path.cwd()
    
    print(f"=== 详细测试exe启动 ===")
    print(f"当前目录: {current_dir}")
    print(f"exe路径: {exe_path}")
    print(f"exe存在: {os.path.exists(exe_path)}")
    
    if not os.path.exists(exe_path):
        print("❌ exe文件不存在!")
        return False
    
    exe_size = os.path.getsize(exe_path)
    print(f"exe文件大小: {exe_size:,} bytes")
    
    try:
        print("正在启动exe...")
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=current_dir
        )
        
        print(f"进程启动，PID: {process.pid}")
        
        # 等待一段时间观察进程状态
        print("等待3秒观察进程状态...")
        time.sleep(3)
        
        # 检查进程状态
        poll_result = process.poll()
        print(f"进程状态: {'正在运行' if poll_result is None else f'已退出，退出码: {poll_result}'}")
        
        if poll_result is None:
            print("✓ 进程仍在运行")
            # 终止进程
            print("正在终止进程...")
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✓ 进程已正常终止")
            except subprocess.TimeoutExpired:
                print("⚠ 进程未响应终止，强制终止...")
                process.kill()
                process.wait()
        else:
            print("❌ 进程已退出")
            # 获取输出
            try:
                stdout, stderr = process.communicate(timeout=5)
                if stdout:
                    print(f"标准输出:\n{stdout}")
                if stderr:
                    print(f"标准错误:\n{stderr}")
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                stdout, stderr = process.communicate()
                if stdout:
                    print(f"标准输出:\n{stdout}")
                if stderr:
                    print(f"标准错误:\n{stderr}")
        
        return poll_result is None
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

if __name__ == "__main__":
    success = test_exe_detailed()
    print(f"\n=== 测试结果: {'成功' if success else '失败'} ===")