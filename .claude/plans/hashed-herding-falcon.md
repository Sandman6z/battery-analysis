# 第二次项目审计 — 修复计划

## 上下文
经过第一轮清理（已删除 3 个冗余脚本、清理 locale/test/、config/test.ini、.pylintrc、分离 tkinter_ui_framework.py、创建 conftest.py），再次审计发现了更深层的问题：3 个运行时级别的 bug 和更多死代码。

## 问题分类

### A. 关键 Bug（必须修复）

**A1. `analyze_data_use_case.py:137` — 缺少 `datetime` 导入**
- 使用 `datetime.fromtimestamp()` 但未 `import datetime`
- **修复**: 在文件顶部添加 `from datetime import datetime`

**A2. `Battery` 实体字段名不匹配**
- `domain/entities/battery.py:19` 定义字段 `model_number: str`
- 但 `analyze_data_use_case.py:148` 访问 `battery.model`，:445 传入 `Battery(model=model, ...)`
- `infrastructure/services/battery_analysis_service_impl.py:417` 也访问 `battery.model`
- **修复**: 将 `Battery` 实体字段 `model_number` 重命名为 `model`，并同步更新所有测试文件（`test_battery.py` 等中所有 `model_number=` 改为 `model=`）

**A3. `BatteryAnalysisService` ABC 缺失调用者所需的方法**
- ABC 声明了 7 个方法，但 `analyze_data_use_case.py` 调用的 5 个方法(`validate_battery_data`, `calculate_battery_health`, `analyze_battery_performance`, `predict_battery_lifetime`, `compare_batteries`)均未在 ABC 中声明
- `BatteryAnalysisServiceImpl` 实现了这些方法，但静态检查会报错
- **修复**: 向 `BatteryAnalysisService` ABC 添加 5 个缺失的抽象方法声明

---

### B. 死代码文件（建议删除）
从未被任何其他模块导入的文件：

| 文件 | 理由 |
|------|------|
| `src/battery_analysis/utils/temperature_utils.py` | 无任何模块导入 |
| `src/battery_analysis/utils/parallel_utils.py` | 无任何模块导入 |
| `src/battery_analysis/main/business_logic/error_recovery.py` | 类 `DataErrorRecoveryHandler` 从未被直接引用 |
| `scripts/setup_i18n.py` | 一次性迁移脚本，已完成历史使命 |
| `scripts/archive/nuitka-build.py` | 路径计算已损坏，版本硬编码 2.8.2（当前 2.9.0），彻底删除 |

---

### C. 架构设计缺口（未完成的部分）

**C1. 3 个 Domain Repository 接口无实现 + 无消费者**
- `domain/repositories/configuration_repository.py` — 无 Infrastructure 实现
- `domain/repositories/test_profile_repository.py` — 同上
- `domain/repositories/test_result_repository.py` — 同上
- `domain/entities/configuration.py` — 唯一被上述未使用的 repo 引用，也成死代码

**C2. `domain/services/impl/test_service_impl.py`**
- 实现了 `test_service.py`，但从未被任何初始化或服务容器挂载

**C3. `ui_components/` 中 2 个仅存在于 `__init__.py` 导出的类**
- `Dialogs` (`dialogs.py`) — 只出现在 `__init__.py` 的 `__all__` 中，无实际代码使用
- `ThemeManager` (`theme_manager.py`) — 同上

**C4. 测试文件路径不对应**
- `tests/utils/test_environment_adapter.py` — 测试 `main/utils/environment_adapter.py`，但路径在 `utils/` 下
  → 应移到 `tests/main/utils/test_environment_adapter.py`
- `tests/main/ui/test_main_window.py` — 测试 `ui/ui_main_window.py`，但路径在 `main/ui/` 下
  → 应移到 `tests/ui/test_main_window.py`

---

## 执行步骤

### Step 1：修复 3 个关键 Bug
- `analyze_data_use_case.py` — 添加 `datetime` 导入
- `battery.py` — `model_number` → `model`
- 更新 `test_battery.py` 中所有 `model_number` 引用为 `model`
- `battery_analysis_service.py` — 添加 5 个缺失抽象方法

### Step 2：删除死代码文件
- 删除 `temperature_utils.py`、`parallel_utils.py`、`error_recovery.py`
- 删除 `scripts/setup_i18n.py`、`scripts/archive/nuitka-build.py`

### Step 3：移动路径不正确的测试文件
- 创建 `tests/main/utils/`，移动 `test_environment_adapter.py`
- 更新 `test_environment_adapter.py` 内部的导入路径
- 创建 `tests/ui/`，移动 `test_main_window.py`
- 更新 `test_main_window.py` 内部的导入路径

### Step 4：关于设计缺口（C1-C4）
- 不删除不处理，仅记录为已知的架构缺口
- 如果用户决定清理，可以在后续迭代中删除对应的接口文件（C1: `configuration_repository.py` 等）和 UI 组件（C3: `dialogs.py`、`theme_manager.py`）

---

## 验证方法
1. 运行 `pytest tests/ -x --no-header -q` 确保所有测试通过
2. 手动导入验证：启动 Python 并 `from battery_analysis.domain.entities.battery import Battery; b = Battery(model="test", ...)` 确认字段名正确
3. 确认死代码文件已被删除（git status）
4. 确认 `analyze_data_use_case.py` 中的 `datetime.fromtimestamp()` 不再报 NameError
