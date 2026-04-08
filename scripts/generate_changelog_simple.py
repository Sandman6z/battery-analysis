#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的CHANGELOG生成工具

由于Windows环境下git命令的编码问题，这个脚本提供基本的changelog框架生成。
建议手动编辑生成的内容以确保准确性。

使用方法:
    python scripts/generate_changelog.py --version v2.9.0
"""

import argparse
import sys
from datetime import datetime


def generate_changelog_template(version: str = "Unreleased") -> str:
    """生成changelog模板"""

    template = f"""### {version}

#### 功能增强
- feat:

#### 修复和改进
- fix:

#### 性能优化
- perf:

#### 重构优化
- refactor:

#### 文档
- docs:

#### 测试
- test:

#### 构建和CI/CD
- build:
- ci:

#### 其他变更
- chore:

"""
    return template


def main():
    parser = argparse.ArgumentParser(
        description='Generate CHANGELOG.md template',
        epilog="""
注意: 由于编码问题，此工具只生成模板。
请手动填写具体的更改内容。

建议工作流:
1. 运行此脚本生成模板
2. 使用 git log 查看提交历史
3. 手动填写 CHANGELOG.md

查看提交历史的命令:
  git log --oneline --no-merges v2.8.1..HEAD
  git log --format="%s" --no-merges v2.8.1..HEAD
        """
    )

    parser.add_argument(
        '--version',
        default='Unreleased',
        help='Version string for the changelog entry'
    )

    parser.add_argument(
        '--show-commits',
        action='store_true',
        help='Show recent commits (may have encoding issues on Windows)'
    )

    args = parser.parse_args()

    # 生成模板
    template = generate_changelog_template(args.version)

    print("="*60)
    print("CHANGELOG Template")
    print("="*60)
    print(template)

    if args.show_commits:
        print("\n" + "="*60)
        print("Recent commits (for reference):")
        print("="*60)
        print("\nRun this command to see commits:")
        print("  git log --oneline --no-merges HEAD~10..HEAD")
        print("\nOr in your Git GUI tool for better encoding support.")

    print("\n" + "="*60)
    print("Next steps:")
    print("="*60)
    print("1. Copy the template above")
    print("2. Paste it at the top of CHANGELOG.md")
    print("3. Fill in the actual changes from git log")
    print("4. Remove empty sections")
    print("5. Commit the updated CHANGELOG.md")

    return 0


if __name__ == '__main__':
    sys.exit(main())
