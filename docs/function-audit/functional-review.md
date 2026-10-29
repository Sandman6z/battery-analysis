# 功能级梳理：输入校验与 NDAX 文件发现

> 本文记录第二阶段的功能修复（当时 1363 项测试通过）。后续已按用户要求完成一批遗留功能退役，包括下文发现的旧验证服务；当前删除清单和验证结果见 [retired-features.md](retired-features.md)。

## 范围与结果

本轮不按函数名字合并，而是沿实际功能链追踪业务判定来源。已处理：

1. 实时字段提示 → 点击分析 → 运行前字段检查。
2. 文件预览/批量转换 → 元数据扫描/版本校验和 → 分析输入文件发现。

本轮新增 43 项测试，修改前已有 1320 项，最终完整回归 **1363 passed**。Ruff（本轮涉及文件）与 `git diff --check` 通过。未进行真实硬件、大数据性能、交互式 GUI 或冻结打包验证。

## 一、输入校验：原功能链

```text
UIManager.init_lineedit
  ├─ textChanged → ValidationManager.validate_version
  ├─ textChanged → ValidationManager.validate_input_path
  └─ textChanged → ValidationManager.validate_required_fields

AnalysisRunner.run_analysis
  → _check_inputs
    → Main.checkinput
      → ValidationManager.checkinput
        → validate_fields → InputValidator.validate_all
        → _check_legacy_fields（旧的第二套规则）
  → _preflight_recipe（配方、版本、Profile 确认）
  → 后台分析与文件读取
```

### 已确认的功能冲突

| 问题 | 证据与影响 | 本轮处理 |
|---|---|---|
| Profile 在界面可选、旧校验却必填 | `UIManager.init_lineedit` 显示 Optional Test Profile XML；`_preflight_recipe` 已有无 Profile 的免责声明确认；旧字段表仍强制非空，导致该流程无法从真实运行入口到达 | 删除第二套字段规则，Profile 不再阻止通用字段校验；运行前确认保持不变 |
| Reported By / Version 的必填规则分裂 | 纯验证器漏查，旧 UI 校验补查；纯校验可能通过，最终入口仍失败 | 两项纳入纯验证器的唯一必填表；保留原入口的必填要求 |
| 存在的普通文件被当作目录 | 实时路径和纯验证器各自仅检查 exists | 统一复用目录判定，输入/输出都必须是已存在的目录 |
| 非法容量实时提示与运行判定不一致 | 实时逻辑只查非空，纯验证器要求计算容量/要求可用容量为正整数 | 实时反馈复用必填和正整数规则，0、负数、小数、非法文本提前高亮 |
| 共享规格标签被后续字段清空 | specification_type 与 specification_method 使用同一标签，逐字段设置样式会用另一个无错误字段清除红色 | 标签按所有关联字段的错误取并集；两个输入控件各自保留独立样式 |
| 必填字段只有空格时被视作填写 | 原非空判断允许空格文本 | 必填检查使用 strip 判空，不修改用户原始输入或路径 |
| 纯校验失败只显示 Validation failed | 很多必填错误仅在 field_errors，不在 errors | 无总错误列表时展示字段错误，Reporter 等缺失项可见；成功时清除旧高亮 |

### 修改后的职责

- `InputValidator`：业务规则权威来源，包括唯一必填表、条件构造方法、版本、容量、目录及老化范围。
- `ValidationFieldsMixin`：从 UI 取值，调用相同规则，展示实时样式/提示；不再自行判断目录是否存在或重新定义容量合法性。
- `ValidationFeedbackMixin`：只执行一份完整字段检查，再应用结果到界面；移除旧字段表以及 6 个相关方法（旧字段循环、结尾处理、标签重置、组合框/文本框非空判断、警告拼接）。
- `AnalysisRunner._preflight_recipe`：继续负责 NDAX 配方一致性、版本占用/校验和、可选 Profile 比对和用户确认，不与字段级校验合并。
- 后台文件读取：继续保留文件打开/解析异常处理，不假定前置校验能消除检查后的文件变化。

### 明确保留的行为

- Coin Cell 不需要构造方法，Pouch Cell 需要。
- Reported By、Version 仍必填，没有因为删除旧检查而放宽。
- Profile 可不选；未选择的确认流程和选择后不匹配的确认流程不变。
- 老化范围仍为 0–10。
- 计算容量、要求可用容量仍为正整数；本轮不擅自给样品数、Datasheet 容量增加新范围规则。
- 路径在实时提示通过后，到运行时仍重新验证；没有新增跨阶段校验缓存。
- `AnalysisRunner._check_inputs` 中错误诊断用的再次验证、路径空值防御与冷冻温度确认仍保留。没有为了减少调用次数而把不同阶段保护全部删掉。

### 回归证据

先加入测试、再修改实现：初始 20 项新测试中 19 项失败，复现 Profile 阻断、纯验证器漏判、目录类型、实时容量和高亮问题；修复后通过。之后补充 16 个必填字段一致性、两种电池构造条件、老化范围和目录删除后的重新检查，共 40 项输入流程测试。

测试文件：`tests/test_validation_workflow.py`。

## 二、NDAX 文件发现：同一功能两套选择规则

### 原实现

- `file_finder.scan_sorted_ndax`：`os.listdir` + 大小写不敏感扩展名 + 自然排序，供元数据扫描、校验和、运行预检、分析使用。
- `ndax.converter._get_ndax_files`：`Path.glob('*.ndax')` + 普通名称排序，供转换窗口预览和批量转换使用。
- 两者都可能把后缀为 .ndax 的目录当作数据文件；转换扫描的大小写匹配行为还取决于平台。

### 统一后的规则

权威实现为 `file_finder.scan_sorted_ndax`：

1. 非递归扫描目录。
2. 扩展名不区分大小写。
3. 仅选择实际文件（`DirEntry.is_file`，保持跟随文件符号链接的通常语义）。
4. 自然排序，例如 channel_2 在 channel_10 之前。
5. 使用 scandir 并关闭扫描迭代器，不额外缓存目录结果。

转换器 `_get_ndax_files` 只转换为 Path 列表，`get_ndax_files` 只转换为文件名列表；原有返回类型保留。转换器对不存在/非目录路径仍返回空列表；严格扫描入口遇到不存在目录仍抛出 FileNotFoundError，未把两种 API 的异常契约强行统一。

转换侧现在也采用自然排序，这是有意的可见行为对齐；批量并行任务的完成顺序仍不保证等于输入排序，未改进程调度。

回归测试：`tests/test_ndax_discovery_consistency.py`（3 项），覆盖混合大小写、自然顺序、伪装目录、非递归、返回类型、空目录及不存在目录的兼容行为。测试在修复前复现了伪装目录进入分析列表的问题。

## 三、发现但未在本轮合并的遗留功能

### 旧 ValidationService / ValidationController 的契约不匹配

仓库内搜索发现服务容器仍创建并暴露这两个对象，信号连接器仍连接 validation_error，但未找到实际分析入口调用它们的 validate_test_info / validate_input_data。

- `ValidationService.validate_test_info` 把索引 0/2/3/16 当成 Project Name/Battery Type/Rated Capacity/Software Version。
- 当前 `domain.TestInfo` 中，0/2/3/16 实际是 Battery Type/Specification Type/Specification Method/Version。
- 旧服务的电池类型白名单是化学体系（磷酸铁锂等），当前 UI/报告使用 Coin Cell/Pouch Cell 等形态分类。
- `ValidationController.validate_input_data` 仍查找 xlsx/csv，当前主分析以 NDAX 为输入。
- 旧服务容量范围为 0.1–10000 浮点数，当前运行字段中的计算容量/要求可用容量是正整数。

**第二阶段先保留；后续已按用户授权整条退役。**它不在实际运行链上，旧化学分类/浮点范围没有并入当前运行规则。旧服务、控制器、注册、导出和信号连接均已移除；外部脚本如曾直接使用该内部 API，需要迁移到当前字段校验和 NDAX 扫描入口，详见退役记录。

### 仍需继续的功能域

- 配置路径优先级、缓存失效与重载是否只有一个权威来源。
- 报告日期、路径、模板定位的重复准备工作。
- 分析统计结果是否在多个写入器中重复计算。
- 配方和时序是否重复解析；真实数据的耗时/峰值内存基准。

本轮改善的是规则一致性和错误反馈，未测得实际性能收益；测试耗时变化不能当作软件加速证据。原有未提交的 NDAX 引导、翻译等文件未被本轮覆盖，也未自动提交。
