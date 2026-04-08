# Changelog 维护指南

本文档说明如何维护项目的 CHANGELOG.md 文件。

## 自动生成工具

项目提供了自动化工具 `scripts/generate_changelog.py` 来从 git 提交历史生成 changelog。

### 使用方法

#### 1. 生成从上一个 tag 到 HEAD 的 changelog

```bash
python scripts/generate_changelog.py
```

这会自动：
- 查找最近的 git tag
- 提取从该 tag 到 HEAD 的所有提交
- 按类型分类并生成 markdown
- 更新 CHANGELOG.md 文件

#### 2. 生成指定范围的 changelog

```bash
# 从 v2.8.0 到 v2.8.1
python scripts/generate_changelog.py --from-tag v2.8.0 --to-tag v2.8.1

# 从 v2.8.1 到 HEAD
python scripts/generate_changelog.py --from-tag v2.8.1
```

#### 3. 指定版本号

```bash
python scripts/generate_changelog.py --version v2.9.0
```

#### 4. 只预览不更新文件

```bash
python scripts/generate_changelog.py --output
```

## Commit Message 规范

为了让自动化工具正确分类提交，请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### 格式

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### 类型 (type)

- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 代码重构
- `perf`: 性能优化
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `test`: 测试相关
- `build`: 构建系统或依赖更新
- `ci`: CI/CD 配置更改
- `chore`: 其他杂项更改

### 示例

```bash
# 新功能
git commit -m "feat: 添加电池温度监控功能"
git commit -m "feat(ui): 添加深色主题支持"

# Bug 修复
git commit -m "fix: 修复文件路径解析错误"
git commit -m "fix(config): 修复配置文件加载失败的问题"

# 重构
git commit -m "refactor: 优化数据处理性能"
git commit -m "refactor(core): 重构服务容器架构"

# 文档
git commit -m "docs: 更新安装指南"

# 构建
git commit -m "build: 升级 PyQt6 到 6.7.0"
```

## 发布流程

### 1. 准备发布

```bash
# 1. 确保所有更改已提交
git status

# 2. 生成 changelog
python scripts/generate_changelog.py --version v2.9.0

# 3. 检查生成的 changelog
git diff CHANGELOG.md

# 4. 更新版本号（pyproject.toml）
# 手动编辑或使用工具

# 5. 提交 changelog 和版本号更新
git add CHANGELOG.md pyproject.toml
git commit -m "chore: 准备发布 v2.9.0"
```

### 2. 创建 tag

```bash
# 创建带注释的 tag
git tag -a v2.9.0 -m "Release v2.9.0"

# 推送 tag
git push origin v2.9.0
```

### 3. 创建 GitHub Release

在 GitHub 上创建 Release 时，可以直接复制 CHANGELOG.md 中对应版本的内容作为 Release Notes。

## 手动维护

如果某些更改需要手动添加到 changelog（例如合并了不符合规范的提交），可以直接编辑 CHANGELOG.md：

1. 在文件顶部找到对应版本
2. 在相应的分类下添加条目
3. 使用 `- ` 开头的列表格式

## 最佳实践

1. **每次发布前生成 changelog** - 确保所有更改都被记录
2. **遵循 commit 规范** - 让自动化工具能正确分类
3. **定期更新** - 不要等到发布时才生成，可以在开发过程中定期更新
4. **人工审查** - 自动生成后检查内容，必要时手动调整
5. **保持简洁** - changelog 应该面向用户，不需要包含所有技术细节

## 工具集成

### Pre-commit Hook

可以添加 pre-commit hook 来检查 commit message 格式：

```bash
# .git/hooks/commit-msg
#!/bin/bash
commit_msg=$(cat "$1")
pattern="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\(.+\))?: .+"

if ! echo "$commit_msg" | grep -qE "$pattern"; then
    echo "Error: Commit message does not follow Conventional Commits format"
    echo "Format: <type>(<scope>): <description>"
    echo "Example: feat(ui): add dark mode support"
    exit 1
fi
```

### CI/CD 集成

可以在 CI/CD 流程中自动检查和生成 changelog：

```yaml
# .github/workflows/release.yml
- name: Generate Changelog
  run: |
    python scripts/generate_changelog.py --version ${{ github.ref_name }}
    git diff --exit-code CHANGELOG.md || echo "Changelog needs update"
```
