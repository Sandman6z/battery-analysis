#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成CHANGELOG.md的工具脚本

使用方法:
    python scripts/generate_changelog.py [--from-tag TAG] [--to-tag TAG]

示例:
    # 生成从上一个tag到HEAD的changelog
    python scripts/generate_changelog.py

    # 生成指定范围的changelog
    python scripts/generate_changelog.py --from-tag v2.8.0 --to-tag v2.8.1
"""

import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

# 设置环境变量强制UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8'


class ChangelogGenerator:
    """Changelog生成器，遵循Conventional Commits规范"""

    # Conventional Commits类型映射
    TYPE_MAPPING = {
        'feat': '功能增强',
        'fix': '修复和改进',
        'refactor': '重构优化',
        'perf': '性能优化',
        'docs': '文档',
        'style': '代码风格',
        'test': '测试',
        'build': '构建和CI/CD',
        'ci': '构建和CI/CD',
        'chore': '其他变更',
    }

    def __init__(self):
        self.commits: Dict[str, List[str]] = defaultdict(list)

    def get_git_tags(self) -> List[str]:
        """获取所有git标签，按时间倒序"""
        try:
            result = subprocess.run(
                ['git', 'tag', '--sort=-creatordate'],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='ignore'
            )
            return [tag.strip() for tag in result.stdout.split('\n') if tag.strip()]
        except subprocess.CalledProcessError:
            return []

    def get_commits(self, from_ref: str = None, to_ref: str = 'HEAD') -> List[Tuple[str, str]]:
        """获取指定范围的提交记录

        Returns:
            List of (commit_hash, commit_message) tuples
        """
        if from_ref:
            git_range = f"{from_ref}..{to_ref}"
        else:
            # 如果没有指定起始tag，获取最近的tag
            tags = self.get_git_tags()
            if tags:
                git_range = f"{tags[0]}..{to_ref}"
            else:
                # 如果没有任何tag，获取所有提交
                git_range = to_ref

        try:
            result = subprocess.run(
                ['git', 'log', '--format=%H|%s', '--no-merges', git_range],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='ignore'
            )

            commits = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 1)
                        if len(parts) == 2:
                            commits.append((parts[0], parts[1]))
            return commits
        except subprocess.CalledProcessError as e:
            print(f"Error getting commits: {e}", file=sys.stderr)
            return []

    def parse_commit_message(self, message: str) -> Tuple[str, str]:
        """解析commit message，提取类型和描述

        支持格式:
        - feat: 添加新功能
        - feat(scope): 添加新功能
        - fix: 修复bug
        """
        # 确保message是字符串
        if not isinstance(message, str):
            message = str(message)

        # Conventional Commits格式: type(scope): description
        pattern = r'^(\w+)(?:\(([^)]+)\))?: (.+)$'
        match = re.match(pattern, message)

        if match:
            commit_type = match.group(1).lower()
            scope = match.group(2) or ''
            description = match.group(3)

            # 如果有scope，添加到描述前面
            if scope:
                description = f"({scope}): {description}"

            return commit_type, description

        # 如果不符合规范，归类为chore
        return 'chore', message

    def categorize_commits(self, commits: List[Tuple[str, str]]):
        """将提交按类型分类"""
        self.commits.clear()

        for commit_hash, message in commits:
            commit_type, description = self.parse_commit_message(message)

            # 映射到中文分类
            category = self.TYPE_MAPPING.get(commit_type, '其他变更')

            # 格式化为markdown列表项
            formatted = f"- {description}"
            self.commits[category].append(formatted)

    def generate_markdown(self, version: str = None) -> str:
        """生成markdown格式的changelog"""
        if not version:
            version = "Unreleased"

        lines = [f"### {version}\n"]

        # 按预定义顺序输出各个分类
        order = [
            '功能增强',
            '修复和改进',
            '性能优化',
            '重构优化',
            '文档',
            '测试',
            '构建和CI/CD',
            '代码风格',
            '其他变更',
        ]

        for category in order:
            if category in self.commits and self.commits[category]:
                lines.append(f"#### {category}")
                lines.extend(self.commits[category])
                lines.append("")  # 空行

        return '\n'.join(lines)

    def update_changelog_file(self, new_content: str, changelog_path: str = 'CHANGELOG.md'):
        """更新CHANGELOG.md文件，在文件开头插入新内容"""
        try:
            # 读取现有内容
            try:
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            except FileNotFoundError:
                existing_content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"

            # 在第一个版本标题之前插入新内容
            # 查找第一个 "### v" 的位置
            match = re.search(r'\n### v', existing_content)
            if match:
                insert_pos = match.start() + 1  # +1 保留换行符
                updated_content = (
                    existing_content[:insert_pos] +
                    new_content + '\n' +
                    existing_content[insert_pos:]
                )
            else:
                # 如果没有找到版本标题，直接追加
                updated_content = existing_content + '\n' + new_content

            # 写回文件
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            print(f"✓ Updated {changelog_path}")
            return True
        except Exception as e:
            print(f"✗ Error updating changelog: {e}", file=sys.stderr)
            return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate CHANGELOG.md from git commits',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate changelog from last tag to HEAD
  python scripts/generate_changelog.py

  # Generate changelog for specific range
  python scripts/generate_changelog.py --from-tag v2.8.0 --to-tag v2.8.1

  # Generate changelog with custom version
  python scripts/generate_changelog.py --version v2.9.0
        """
    )

    parser.add_argument(
        '--from-tag',
        help='Starting git tag/commit (default: last tag)'
    )
    parser.add_argument(
        '--to-tag',
        default='HEAD',
        help='Ending git tag/commit (default: HEAD)'
    )
    parser.add_argument(
        '--version',
        help='Version string for the changelog entry (default: Unreleased)'
    )
    parser.add_argument(
        '--output',
        action='store_true',
        help='Only output to stdout, do not update CHANGELOG.md'
    )

    args = parser.parse_args()

    generator = ChangelogGenerator()

    # 获取提交记录
    print(f"Fetching commits from {args.from_tag or 'last tag'} to {args.to_tag}...")
    commits = generator.get_commits(args.from_tag, args.to_tag)

    if not commits:
        print("No commits found in the specified range.")
        return 0

    print(f"Found {len(commits)} commits")

    # 分类提交
    generator.categorize_commits(commits)

    # 生成markdown
    markdown = generator.generate_markdown(args.version)

    if args.output:
        # 只输出到stdout
        print("\n" + "="*60)
        print(markdown)
    else:
        # 更新CHANGELOG.md
        if generator.update_changelog_file(markdown):
            print("\nPreview:")
            print("="*60)
            print(markdown)
            return 0
        else:
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
