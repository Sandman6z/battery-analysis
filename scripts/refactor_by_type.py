#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将Pylint报告中的问题按类型分类的脚本

此脚本用于将按文件分类的Pylint报告转换为按问题类型分类的报告，
更便于后续有针对性地解决问题。
"""

import re
from collections import defaultdict
from datetime import datetime


def parse_refactoring_plan(file_path):
    """解析refactoring_plan.md文件，提取问题信息"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取概述信息
    overview_pattern = r'## 概述\n- 分析日期: (.+)\n- 总文件数: (\d+)\n- 存在问题的文件数: (\d+)'
    overview_match = re.search(overview_pattern, content)
    overview = {
        'analysis_date': overview_match.group(1) if overview_match else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_files': int(overview_match.group(2)) if overview_match else 0,
        'files_with_issues': int(overview_match.group(3)) if overview_match else 0
    }
    
    # 提取所有文件部分
    file_sections = re.split(r'## 文件:', content)[1:]
    
    # 按类型分类问题
    issues_by_type = defaultdict(list)
    
    for section in file_sections:
        # 提取文件名
        file_name_match = re.match(r'\s*([^\n]+)\n', section)
        if not file_name_match:
            continue
        file_name = file_name_match.group(1).strip()
        
        # 提取详细问题
        issue_pattern = r'#### 行 (\d+), 列 (\d+)\n- 类型: (\w+)\n- 代码: ([^\n]+)\n- 描述: ([^\n]+)\n- 符号: ([^\n]+)'
        issues = re.findall(issue_pattern, section)
        
        for issue in issues:
            line = issue[0]
            col = issue[1]
            issue_type = issue[2]
            code = issue[3].strip()
            description = issue[4].strip()
            symbol = issue[5].strip()
            
            # 将问题添加到对应类型的列表中
            issues_by_type[symbol].append({
                'file_name': file_name,
                'line': line,
                'col': col,
                'type': issue_type,
                'code': code,
                'description': description,
                'symbol': symbol
            })
    
    return overview, issues_by_type


def generate_refactoring_md(overview, issues_by_type, output_path):
    """生成按类型分类的refactoring.md文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入标题
        f.write("# 代码重构计划\n\n")
        
        # 写入概述
        f.write("## 概述\n")
        f.write(f"- 分析日期: {overview['analysis_date']}\n")
        f.write(f"- 总文件数: {overview['total_files']}\n")
        f.write(f"- 存在问题的文件数: {overview['files_with_issues']}\n")
        f.write(f"- 问题类型总数: {len(issues_by_type)}\n")
        total_issues = sum(len(issues) for issues in issues_by_type.values())
        f.write(f"- 问题总数: {total_issues}\n\n")
        
        # 按问题类型排序（按问题数量降序）
        sorted_types = sorted(issues_by_type.items(), key=lambda x: len(x[1]), reverse=True)
        
        # 写入各类问题
        for symbol, issues in sorted_types:
            issue_count = len(issues)
            # 获取该类型问题的第一个实例的类型和描述
            first_issue = issues[0]
            issue_type = first_issue['type']
            description = first_issue['description']
            code = first_issue['code']
            
            f.write(f"## 问题类型: {symbol}\n")
            f.write(f"### 问题信息\n")
            f.write(f"- 类型: {issue_type}\n")
            f.write(f"- 代码: {code}\n")
            f.write(f"- 描述: {description}\n")
            f.write(f"- 出现次数: {issue_count}\n")
            
            # 统计涉及的文件数
            affected_files = len(set(issue['file_name'] for issue in issues))
            f.write(f"- 涉及文件数: {affected_files}\n\n")
            
            f.write(f"### 详细问题列表\n")
            for issue in issues:
                f.write(f"#### 文件: {issue['file_name']}\n")
                f.write(f"- 位置: 行 {issue['line']}, 列 {issue['col']}\n")
                f.write(f"- 类型: {issue['type']}\n")
                f.write(f"- 代码: {issue['code']}\n")
                f.write(f"- 描述: {issue['description']}\n")
                f.write(f"- 符号: {issue['symbol']}\n\n")


if __name__ == "__main__":
    input_file = "refactoring_plan.md"
    output_file = "refactoring.md"
    
    print(f"正在解析 {input_file}...")
    overview, issues_by_type = parse_refactoring_plan(input_file)
    
    print(f"正在生成 {output_file}...")
    generate_refactoring_md(overview, issues_by_type, output_file)
    
    print(f"完成！生成了按类型分类的重构计划文件: {output_file}")
    print(f"共发现 {len(issues_by_type)} 种问题类型，总计 {sum(len(issues) for issues in issues_by_type.values())} 个问题")
