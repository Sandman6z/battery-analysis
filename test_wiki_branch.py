#!/usr/bin/env python3
"""
测试脚本：检查Wiki仓库的分支结构
"""
import subprocess
import sys
import os

def run_command(cmd):
    """运行shell命令并返回结果"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Exit code: {result.returncode}")
    if result.stdout:
        print(f"Stdout:\n{result.stdout}")
    if result.stderr:
        print(f"Stderr:\n{result.stderr}")
    return result

def main():
    """主函数"""
    # 检查当前目录
    print(f"Current directory: {os.getcwd()}")
    
    # 检查git状态
    run_command("git status")
    
    # 检查分支
    run_command("git branch -a")
    
    # 尝试克隆Wiki仓库（如果存在）
    wiki_url = "https://github.com/Sandman6z/battery-analysis.wiki.git"
    print(f"\nTrying to clone Wiki repository: {wiki_url}")
    result = run_command(f"git clone {wiki_url} temp_wiki")
    
    if result.returncode == 0:
        # 检查Wiki仓库的分支
        os.chdir("temp_wiki")
        print(f"\nIn Wiki directory: {os.getcwd()}")
        run_command("git branch -a")
        run_command("git log --oneline -n 5")
        os.chdir("..")
        # 清理临时目录
        run_command("rm -rf temp_wiki")
    else:
        print("\nFailed to clone Wiki repository. It may not be initialized yet.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())