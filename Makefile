# Battery Analysis 开发任务入口
# 用法: make <target>
# 需要: uv (https://docs.astral.sh/uv/)

.PHONY: help install sync test test-cov lint format check build clean

help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## 安装项目及所有依赖
	uv sync --all-extras

sync: ## 同步依赖（等效 uv sync --frozen）
	uv sync --frozen

test: ## 运行测试
	uv run pytest

test-cov: ## 运行测试并生成覆盖率报告
	uv run python scripts/run_coverage_test.py

lint: ## 运行 ruff lint 检查
	uv run ruff check src/ tests/ scripts/

format: ## 格式化代码（ruff format + ruff fix）
	uv run ruff format src/ tests/ scripts/
	uv run ruff check --fix src/ tests/ scripts/

check: lint ## 运行全部静态检查（lint + mypy）
	uv run mypy src/

build: ## 构建 Release 版本
	uv run python scripts/build.py Release

build-debug: ## 构建 Debug 版本
	uv run python scripts/build.py Debug

clean: ## 清理构建产物
	@if exist build rmdir /s /q build
	@if exist __temp__ rmdir /s /q __temp__
	@if exist .ruff_cache rmdir /s /q .ruff_cache
	@if exist .mypy_cache rmdir /s /q .mypy_cache
	@if exist htmlcov rmdir /s /q htmlcov
	@if exist .pytest_cache rmdir /s /q .pytest_cache
