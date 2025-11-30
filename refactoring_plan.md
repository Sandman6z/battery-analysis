# 代码重构计划

## 概述

通过代码审查，发现项目中存在多个过长的代码文件，这些文件功能过于集中，不符合单一职责原则，降低了代码的可维护性、可读性和可测试性。本计划提出对这些长文件的拆分和重构方案。

## 1. main_window.py (2022行)

### 问题分析
- UI初始化与业务逻辑混合
- 线程管理直接嵌入到主窗口类
- 大量事件处理和验证逻辑混合在一起
- 违反单一职责原则

### 拆分建议

#### 1.1 创建文件结构
```
main/
├── main_window.py         # 仅保留窗口初始化和UI相关逻辑
├── controllers/
│   ├── __init__.py
│   ├── main_controller.py # 业务逻辑控制器
│   ├── file_controller.py # 文件操作控制器
│   └── validation_controller.py # 表单验证控制器
├── models/
│   ├── __init__.py
│   └── battery_model.py   # 电池数据模型
└── workers/
    ├── __init__.py
    └── analysis_worker.py # 后台分析线程
```

#### 1.2 实现方式
1. **main_window.py**
   - 移除Thread类，改用QThreadPool和QRunnable
   - 保留UI初始化、信号连接等纯界面逻辑
   - 通过控制器委托业务逻辑

2. **main_controller.py**
   - 实现核心业务逻辑
   - 协调各个组件之间的交互
   - 处理应用程序状态管理

3. **analysis_worker.py**
   - 将原Thread类重构为QRunnable
   - 专注于后台分析任务
   - 使用信号与主线程通信

## 2. file_writer.py (1555行)

### 问题分析
- 多种文件格式(XLSX、Word、CSV、图片)写入逻辑混合
- 报告生成与数据处理混合
- 缺少清晰的功能模块划分

### 拆分建议

#### 2.1 创建文件结构
```
utils/
├── file_writer.py         # 主入口，协调不同的写入器
├── writers/
│   ├── __init__.py
│   ├── excel_writer.py    # Excel文件写入
│   ├── word_writer.py     # Word报告写入
│   ├── csv_writer.py      # CSV数据写入
│   └── image_generator.py # 图表生成器
└── templates/
    ├── __init__.py
    ├── excel_template.py  # Excel模板处理
    └── word_template.py   # Word模板处理
```

#### 2.2 实现方式
1. **file_writer.py**
   - 简化为工厂类或协调器角色
   - 根据需要创建并调用特定的写入器
   - 管理共享配置和资源

2. **writers/下的文件**
   - 每个写入器专注于一种文件格式
   - 实现统一的接口方法
   - 独立处理各自文件格式的细节

## 3. image_show.py (1020行)

### 问题分析
- 图片处理、显示和数据绑定混合
- UI和图像处理逻辑交织

### 拆分建议

#### 3.1 创建文件结构
```
main/
├── image_show.py          # 主窗口类，仅负责UI
├── image_processing/
│   ├── __init__.py
│   ├── image_loader.py    # 图片加载和处理
│   ├── image_analyzer.py  # 图片分析功能
│   └── visualization.py   # 可视化逻辑
└── models/
    └── image_model.py     # 图片数据模型
```

#### 3.2 实现方式
1. **image_show.py**
   - 保持为主要UI入口
   - 委托图像处理逻辑到专门的处理器
   - 负责用户交互和显示

2. **image_processing/下的文件**
   - 将图像处理、分析功能分离到独立模块
   - 提高代码复用性
   - 便于单独测试

## 4. build.py (768行)

### 问题分析
- 构建流程过于集中
- 缺少清晰的任务分解
- 可维护性较差

### 拆分建议

#### 4.1 创建文件结构
```
scripts/
├── build.py               # 主构建脚本，协调各构建步骤
├── builders/
│   ├── __init__.py
│   ├── base_builder.py    # 构建器基类
│   ├── pyinstaller_builder.py # PyInstaller构建
│   ├── resource_builder.py # 资源文件处理
│   └── dependency_manager.py # 依赖管理
└── utils/
    ├── __init__.py
    ├── build_config.py    # 构建配置
    └── build_utils.py     # 构建工具函数
```

#### 4.2 实现方式
1. **build.py**
   - 简化为协调器角色
   - 按顺序调用各个构建器
   - 处理构建流程控制

2. **builders/下的文件**
   - 每个构建器负责特定的构建任务
   - 实现共同的接口
   - 独立处理各自领域的细节

## 重构优势

1. **提高可维护性**
   - 代码职责更明确，便于定位问题
   - 模块化设计使修改影响范围更小

2. **增强可读性**
   - 每个文件专注于单一职责
   - 文件大小适中，便于理解

3. **提升可测试性**
   - 模块间依赖减少，易于单元测试
   - 功能边界清晰，测试覆盖更全面

4. **促进团队协作**
   - 减少代码冲突
   - 新成员更容易理解代码结构

## 重构注意事项

1. **渐进式重构**
   - 建议一次重构一个文件
   - 确保每次重构后测试通过

2. **保持向后兼容**
   - 避免破坏现有功能
   - 必要时提供适配层

3. **文档更新**
   - 及时更新相关文档
   - 为新模块添加适当的注释

4. **版本控制策略**
   - 使用分支进行重构
   - 提交粒度要小，便于回滚

## 实施计划

1. 先重构影响最大的**main_window.py**
2. 其次重构**file_writer.py**
3. 然后处理**image_show.py**
4. 最后优化**build.py**

每个文件重构完成后进行测试，确保功能正常运行。