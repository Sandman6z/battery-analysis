import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """项目根目录路径"""
    return Path(__file__).parent.parent


@pytest.fixture
def tests_root() -> Path:
    """测试目录路径"""
    return Path(__file__).parent


@pytest.fixture
def test_data_dir() -> Path:
    """测试数据目录路径"""
    return Path(__file__).parent / "data"


def pytest_collection_modifyitems(config, items):
    """自动跳过 tests/manual/ 下的测试（除非用 --run-manual 标记运行）"""
    if config.getoption("--run-manual", default=False):
        return  # 运行所有测试

    skip_manual = pytest.mark.skip(reason="manual test, use --run-manual to run")
    for item in items:
        if "manual" in str(item.fspath):
            item.add_marker(skip_manual)


def pytest_addoption(parser):
    """添加 --run-manual 命令行选项"""
    parser.addoption(
        "--run-manual",
        action="store_true",
        default=False,
        help="run tests in tests/manual/ directory"
    )
