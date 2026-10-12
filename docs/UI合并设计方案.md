# Battery Analysis UI 合并设计方案

## 一、功能分析

### 1.1 ndaxConverter 功能模块

```
ndaxConverter/
├── engine/                    # 核心转换引擎
│   └── converter.py           # NDAX → XLSX 转换逻辑
└── ui/                        # GUI 界面
    └── main_window.py         # 主窗口
```

**核心功能**：
- 选择包含 .ndax 文件的文件夹
- 批量转换 NDAX 文件为 XLSX 格式
- 显示转换进度和状态
- 支持取消操作
- 跳过已存在的文件

**UI 组件**：
- 文件夹选择按钮
- 文件列表表格（文件名、状态）
- 进度条
- 日志区域
- 开始/取消按钮

### 1.2 battery-analysis 功能模块

```
battery-analysis/
├── domain/                    # 领域层
│   └── entities/              # 实体类
├── i18n/                      # 国际化
├── main/                      # 主应用
│   ├── business_logic/        # 业务逻辑
│   ├── commands/              # 命令模式
│   ├── controllers/           # 控制器
│   ├── dialogs/               # 对话框
│   ├── factories/             # 工厂模式
│   ├── handlers/              # 处理器
│   ├── initialization/        # 初始化流程
│   ├── interfaces/            # 接口定义
│   ├── managers/              # 管理器
│   ├── presenters/            # 展示器
│   ├── services/              # 服务层
│   ├── ui_components/         # UI 组件
│   ├── utils/                 # 工具类
│   ├── visualization/         # 可视化
│   └── workers/               # 工作线程
├── resources/                 # 资源文件
├── templates/                 # 模板文件
├── ui/                        # UI 框架
└── utils/                     # 通用工具
    ├── processors/            # 处理器
    ├── readers/               # 读取器
    └── writers/               # 写入器
```

**核心功能**：
- 测试配置管理（Test Config）
- 电池配置管理（Battery Config）
- 路径管理（Path）
- 测试信息管理（Test Information）
- 数据导入（支持多种格式）
- 数据分析
- 图表可视化
- 报告生成
- 配置管理

**UI 组件**：
- 配置面板（可滚动）
- Run 按钮面板
- 图表区域（默认隐藏）
- 状态栏
- 菜单栏
- 工具栏

## 二、数据流分析

### 2.1 当前数据流

```
ndaxConverter:
用户选择文件夹 → 扫描 .ndax 文件 → 批量转换 → 生成 .xlsx 文件

battery-analysis:
配置测试参数 → 导入数据 → 数据分析 → 图表可视化 → 生成报告
```

### 2.2 合并后的数据流

```
合并后的完整工作流：
1. 数据采集阶段
   - 用户选择 NDAX 文件夹
   - 批量转换 NDAX → XLSX（ndaxConverter 功能）
   - 生成标准化的 XLSX 文件

2. 数据导入阶段
   - 导入 XLSX 文件到 battery-analysis
   - 数据验证和清洗
   - 存储到内部数据结构

3. 数据分析阶段
   - 测试配置匹配
   - 数据聚合和计算
   - 统计分析

4. 可视化阶段
   - 生成图表
   - 交互式探索
   - 导出图表

5. 报告生成阶段
   - 模板填充
   - 生成 Word/Excel 报告
   - 导出和分享
```

## 三、UI 合并设计方案

### 3.1 方案一：集成到现有 UI（推荐）

**设计理念**：将 ndaxConverter 功能作为 battery-analysis 的一个子模块集成到现有 UI 中。

**UI 布局**：
```
┌─────────────────────────────────────────────────────────────────┐
│  Battery Analyzer                                    [_][□][X]  │
├─────────────────────────────────────────────────────────────────┤
│  菜单栏: [文件] [编辑] [视图] [工具] [帮助]                      │
├─────────────────────────────────────────────────────────────────┤
│  工具栏: [导入] [分析] [图表] [报告] [设置]                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────────────────────────┐  │
│  │ 配置面板         │  │ 主内容区域                           │  │
│  │                  │  │                                      │  │
│  │ ┌─────────────┐ │  │ ┌─────────────────────────────────┐ │  │
│  │ │ Test Config │ │  │ │ 标签页: [数据导入] [数据分析] [图表] │ │  │
│  │ ├─────────────┤ │  │ ├─────────────────────────────────┤ │  │
│  │ │ Battery     │ │  │ │                                 │ │  │
│  │ │ Config      │ │  │ │  (根据标签页显示不同内容)         │ │  │
│  │ ├─────────────┤ │  │ │                                 │ │  │
│  │ │ Path        │ │  │ │  数据导入标签页:                  │ │  │
│  │ ├─────────────┤ │  │ │  ┌─────────────────────────┐   │ │  │
│  │ │ Test Info   │ │  │ │  │ [NDAX导入] [Excel导入]   │   │ │  │
│  │ └─────────────┘ │  │ │  │ [CSV导入] [其他格式]     │   │ │  │
│  │                  │  │ │  └─────────────────────────┘   │ │  │
│  │ [Run] [Stop]    │  │ │                                 │ │  │
│  └─────────────────┘  │ └─────────────────────────────────┘ │  │
│                        └─────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  状态栏: [就绪] [进度: 0%] [内存: 1.2GB] [CPU: 15%]             │
└─────────────────────────────────────────────────────────────────┘
```

**优势**：
- 保持现有 UI 结构不变
- 用户熟悉的操作流程
- 开发工作量小
- 维护成本低

**实现步骤**：
1. 在现有 UI 中添加"数据导入"标签页
2. 在"数据导入"标签页中添加"NDAX导入"按钮
3. 点击按钮后弹出 ndaxConverter 的转换对话框
4. 转换完成后自动导入数据到 battery-analysis

### 3.2 方案二：独立窗口集成

**设计理念**：ndaxConverter 作为独立窗口，通过菜单或按钮调用。

**UI 布局**：
```
主窗口 (battery-analysis):
┌─────────────────────────────────────────────────────────────────┐
│  Battery Analyzer                                    [_][□][X]  │
├─────────────────────────────────────────────────────────────────┤
│  菜单栏: [文件] [编辑] [视图] [工具] [帮助]                      │
│         └─ [工具] → [NDAX转换器] ← 菜单项                       │
├─────────────────────────────────────────────────────────────────┤
│  ... (现有 UI) ...                                              │
└─────────────────────────────────────────────────────────────────┘

独立窗口 (ndaxConverter):
┌─────────────────────────────────────────────────────────────────┐
│  NDAX → XLSX 转换器                                    [_][□][X] │
├─────────────────────────────────────────────────────────────────┤
│  [选择文件夹]  [C:\...\BattData\1_ndax\]                        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 文件名                           状态                      │ │
│  │ ──────────────────────────────────────────────────────────│ │
│  │ BTS83_40_5_1_....ndax           就绪                      │ │
│  │ BTS83_40_5_2_....ndax           就绪                      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  [开始转换]  ████████████░░░░░░ 80% (3/5)                       │
│                                                                 │
│  日志:                                                          │
│  [2026-09-08 16:30] 开始批量转换...                              │
│  [2026-09-08 16:31] ✓ BTS83_40_5_1 转换成功                    │
│                                                                 │
│  [导入到 battery-analysis] [关闭]                               │
└─────────────────────────────────────────────────────────────────┘
```

**优势**：
- 保持 ndaxConverter 的独立性
- 不影响现有 UI 结构
- 可以独立使用
- 便于维护和更新

**实现步骤**：
1. 将 ndaxConverter 作为独立模块保留
2. 在 battery-analysis 的菜单中添加"NDAX转换器"菜单项
3. 点击菜单项后打开 ndaxConverter 窗口
4. 转换完成后提供"导入到 battery-analysis"按钮

### 3.3 方案三：向导式集成

**设计理念**：使用向导（Wizard）引导用户完成从数据导入到分析的完整流程。

**UI 布局**：
```
向导窗口:
┌─────────────────────────────────────────────────────────────────┐
│  数据导入向导                                          [_][□][X] │
├─────────────────────────────────────────────────────────────────┤
│  步骤: [1. 选择数据源] → [2. 数据转换] → [3. 数据导入] → [4. 完成] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  步骤 1: 选择数据源                                             │
│                                                                 │
│  请选择数据源类型:                                               │
│                                                                 │
│  ○ NDAX 文件（新威电池测试系统）                                 │
│  ○ Excel 文件（.xlsx, .xls）                                    │
│  ○ CSV 文件                                                     │
│  ○ 其他格式                                                     │
│                                                                 │
│  [下一步] [取消]                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**优势**：
- 用户体验好
- 流程清晰
- 适合新用户
- 减少操作错误

**实现步骤**：
1. 创建数据导入向导类
2. 实现多步骤向导界面
3. 根据用户选择的数据源类型显示不同的步骤
4. 完成后自动导入数据

## 四、文件结构建议

### 4.1 合并后的项目结构

```
battery-analysis/
├── src/
│   └── battery_analysis/
│       ├── converters/                # 数据转换器模块（新增）
│       │   ├── __init__.py
│       │   ├── base.py               # 转换器基类
│       │   ├── ndax_converter.py     # NDAX 转换器
│       │   ├── excel_converter.py    # Excel 转换器
│       │   └── csv_converter.py      # CSV 转换器
│       ├── domain/                    # 领域层
│       ├── i18n/                      # 国际化
│       ├── main/                      # 主应用
│       │   ├── ui_components/         # UI 组件
│       │   │   ├── import_wizard/     # 导入向导（新增）
│       │   │   │   ├── __init__.py
│       │   │   │   ├── wizard.py      # 向导主类
│       │   │   │   ├── source_page.py # 数据源选择页
│       │   │   │   ├── convert_page.py # 转换页
│       │   │   │   └── import_page.py # 导入页
│       │   │   └── ... (现有组件)
│       │   └── ... (现有模块)
│       ├── resources/                 # 资源文件
│       ├── templates/                 # 模板文件
│       ├── ui/                        # UI 框架
│       └── utils/                     # 通用工具
│           ├── readers/               # 读取器
│           │   ├── __init__.py
│           │   ├── base.py           # 读取器基类
│           │   ├── ndax_reader.py    # NDAX 读取器
│           │   ├── excel_reader.py   # Excel 读取器
│           │   └── csv_reader.py     # CSV 读取器
│           └── writers/               # 写入器
└── tests/
    └── converters/                    # 转换器测试（新增）
```

### 4.2 模块依赖关系

```
用户界面层
    ↓
┌─────────────────────────────────────────┐
│  UI 组件层                               │
│  - ImportWizard (导入向导)               │
│  - MainWindow (主窗口)                   │
│  - ConfigDialog (配置对话框)             │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  控制器层                                │
│  - ImportController (导入控制器)         │
│  - AnalysisController (分析控制器)       │
│  - VisualizationController (可视化控制器)│
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  服务层                                  │
│  - ConversionService (转换服务)          │
│  - DataImportService (数据导入服务)      │
│  - AnalysisService (分析服务)            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  转换器层                                │
│  - NDAXConverter (NDAX 转换器)           │
│  - ExcelConverter (Excel 转换器)         │
│  - CSVConverter (CSV 转换器)             │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  数据层                                  │
│  - NewareNDA (NDAX 解析库)               │
│  - pandas (数据处理)                     │
│  - xlsxwriter (Excel 写入)              │
└─────────────────────────────────────────┘
```

## 五、实现建议

### 5.1 推荐方案：方案一（集成到现有 UI）

**理由**：
1. **用户体验一致**：保持现有 UI 结构，用户无需学习新的操作方式
2. **开发成本低**：只需在现有 UI 中添加新功能模块
3. **维护成本低**：统一的代码结构和依赖管理
4. **功能完整**：可以实现从数据导入到分析的完整流程

**实现步骤**：

**阶段 1：模块化 ndaxConverter（1-2 周）**
1. 提取 `engine/converter.py` 为独立模块
2. 添加到 `battery_analysis/converters/` 目录
3. 实现统一的转换器接口

**阶段 2：UI 集成（2-3 周）**
1. 在现有 UI 中添加"数据导入"标签页
2. 实现 NDAX 导入对话框
3. 集成转换进度和状态显示

**阶段 3：数据流整合（1-2 周）**
1. 实现转换后的数据自动导入
2. 集成到现有数据分析流程
3. 测试完整工作流

**阶段 4：优化和完善（1 周）**
1. 性能优化
2. 错误处理
3. 用户文档

### 5.2 关键代码示例

**转换器接口**：
```python
# battery_analysis/converters/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

class BaseConverter(ABC):
    """数据转换器基类"""
    
    @abstractmethod
    def convert(self, input_path: Path, output_path: Path) -> Path:
        """转换单个文件"""
        pass
    
    @abstractmethod
    def convert_batch(self, input_dir: Path) -> Dict[str, List[str]]:
        """批量转换"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名"""
        pass
```

**NDAX 转换器实现**：
```python
# battery_analysis/converters/ndax_converter.py
from pathlib import Path
from typing import Dict, List
from .base import BaseConverter

class NDAXConverter(BaseConverter):
    """NDAX 文件转换器"""
    
    def convert(self, input_path: Path, output_path: Path) -> Path:
        """转换单个 NDAX 文件"""
        # 复用 ndaxConverter 的核心逻辑
        pass
    
    def convert_batch(self, input_dir: Path) -> Dict[str, List[str]]:
        """批量转换 NDAX 文件"""
        pass
    
    def get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名"""
        return ['.ndax']
```

**导入控制器**：
```python
# battery_analysis/main/controllers/import_controller.py
from pathlib import Path
from typing import Dict, List
from PyQt6.QtCore import QObject, pyqtSignal

from battery_analysis.converters.ndax_converter import NDAXConverter

class ImportController(QObject):
    """数据导入控制器"""
    
    # 信号
    progress_updated = pyqtSignal(int, int)  # current, total
    file_status_updated = pyqtSignal(int, str)  # row_index, status
    conversion_completed = pyqtSignal(dict)  # result
    
    def __init__(self):
        super().__init__()
        self.converters = {
            '.ndax': NDAXConverter(),
            # 可以添加更多转换器
        }
    
    def import_files(self, input_dir: Path, file_type: str) -> None:
        """导入文件"""
        converter = self.converters.get(file_type)
        if converter:
            result = converter.convert_batch(input_dir)
            self.conversion_completed.emit(result)
```

### 5.3 测试策略

**单元测试**：
```python
# tests/converters/test_ndax_converter.py
import pytest
from pathlib import Path
from battery_analysis.converters.ndax_converter import NDAXConverter

class TestNDAXConverter:
    def test_convert_single_file(self):
        """测试单个文件转换"""
        converter = NDAXConverter()
        # 测试逻辑
        pass
    
    def test_convert_batch(self):
        """测试批量转换"""
        converter = NDAXConverter()
        # 测试逻辑
        pass
```

**集成测试**：
```python
# tests/test_import_flow.py
import pytest
from battery_analysis.main.controllers.import_controller import ImportController

class TestImportFlow:
    def test_ndax_import_flow(self):
        """测试 NDAX 导入流程"""
        controller = ImportController()
        # 测试完整导入流程
        pass
```

## 六、总结

### 6.1 推荐方案

**方案一（集成到现有 UI）** 是最佳选择，因为：
1. 保持现有 UI 结构和用户习惯
2. 开发和维护成本最低
3. 可以实现完整的数据导入到分析流程
4. 代码结构清晰，易于扩展

### 6.2 实施计划

| 阶段 | 时间 | 任务 |
|------|------|------|
| 阶段 1 | 1-2 周 | 模块化 ndaxConverter |
| 阶段 2 | 2-3 周 | UI 集成 |
| 阶段 3 | 1-2 周 | 数据流整合 |
| 阶段 4 | 1 周 | 优化和完善 |
| **总计** | **5-8 周** | **完成合并** |

### 6.3 关键成功因素

1. **模块化设计**：保持 ndaxConverter 的核心逻辑独立
2. **接口统一**：定义统一的转换器接口
3. **渐进式集成**：分阶段实施，降低风险
4. **充分测试**：确保功能完整性和稳定性

---

**文档版本**：v1.0  
**创建日期**：2026-09-08  
**作者**：AI Assistant
