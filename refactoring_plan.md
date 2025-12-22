# 代码重构计划

## 概述
- 分析日期: 2025-12-19 17:03:30
- 总文件数: 19
- 存在问题的文件数: 19

## 文件: scripts\build.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 1
- 重构(Refactor): 2

### 详细问题
#### 行 41, 列 4
- 类型: warning
- 代码: W0237
- 描述: Parameter 'optionstr' has been renamed to 'option_str' in overriding 'CaseSensitiveConfigParser.optionxform' method
- 符号: arguments-renamed

#### 行 383, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (19/12)
- 符号: too-many-branches

#### 行 383, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (189/50)
- 符号: too-many-statements

## 文件: scripts\run_pylint.py

### 问题统计
- 问题总数: 23
- 错误(Error): 4
- 警告(Warning): 12
- 规范(Convention): 2
- 重构(Refactor): 5

### 详细问题
#### 行 92, 列 18
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 120, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 161, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 176, 列 4
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'json_output'
- 符号: unused-variable

#### 行 198, 列 0
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (15/12)
- 符号: too-many-branches

#### 行 202, 列 4
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (8/5)
- 符号: too-many-nested-blocks

#### 行 202, 列 4
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 209, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (importlib.util)
- 符号: import-outside-toplevel

#### 行 213, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (pkg_resources)
- 符号: import-outside-toplevel

#### 行 235, 列 46
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 241, 列 20
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 241, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 243, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 276, 列 28
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'background'
- 符号: undefined-variable

#### 行 276, 列 39
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'color'
- 符号: undefined-variable

#### 行 283, 列 28
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'background'
- 符号: undefined-variable

#### 行 283, 列 39
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'color'
- 符号: undefined-variable

#### 行 331, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 335, 列 0
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 342, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 360, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 381, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 398, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: scripts\run_tests.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 2
- 重构(Refactor): 1

### 详细问题
#### 行 42, 列 17
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 57, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 64, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\__init__.py

### 问题统计
- 问题总数: 1
- 规范(Convention): 1

### 详细问题
#### 行 17, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import battery_analysis.utils" should be placed at the top of the module
- 符号: wrong-import-position

## 文件: src\battery_analysis\main\controllers\main_controller.py

### 问题统计
- 问题总数: 1
- 警告(Warning): 1

### 详细问题
#### 行 6, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

## 文件: src\battery_analysis\main\controllers\validation_controller.py

### 问题统计
- 问题总数: 6
- 警告(Warning): 6

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import logging
- 符号: unused-import

#### 行 21, 列 4
- 类型: warning
- 代码: W0246
- 描述: Useless parent or super() delegation in method '__init__'
- 符号: useless-parent-delegation

#### 行 103, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 106, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 137, 列 17
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

#### 行 140, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\image_show.py

### 问题统计
- 问题总数: 85
- 警告(Warning): 53
- 规范(Convention): 17
- 重构(Refactor): 15

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1063/1000)
- 符号: too-many-lines

#### 行 25, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused BatteryAnalysisException imported from battery_analysis.utils.exception_type
- 符号: unused-import

#### 行 26, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from matplotlib.widgets import CheckButtons" should be placed before "from battery_analysis.utils.config_utils import find_config_file"
- 符号: wrong-import-order

#### 行 27, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from matplotlib.ticker import MultipleLocator" should be placed before "from battery_analysis.utils.config_utils import find_config_file"
- 符号: wrong-import-order

#### 行 28, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import matplotlib.pyplot as plt" should be placed before "from battery_analysis.utils.config_utils import find_config_file"
- 符号: wrong-import-order

#### 行 29, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "from matplotlib.widgets import CheckButtons"
- 符号: wrong-import-order

#### 行 30, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "from matplotlib.widgets import CheckButtons"
- 符号: wrong-import-order

#### 行 31, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "from matplotlib.widgets import CheckButtons"
- 符号: wrong-import-order

#### 行 31, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import sys
- 符号: unused-import

#### 行 32, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import math" should be placed before "from matplotlib.widgets import CheckButtons"
- 符号: wrong-import-order

#### 行 33, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import traceback" should be placed before "from matplotlib.widgets import CheckButtons"
- 符号: wrong-import-order

#### 行 34, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import configparser" should be placed before "from matplotlib.widgets import CheckButtons"
- 符号: wrong-import-order

#### 行 35, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "from pathlib import Path" should be placed before "from matplotlib.widgets import CheckButtons"
- 符号: wrong-import-order

#### 行 36, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from matplotlib.widgets import CheckButtons"
- 符号: wrong-import-order

#### 行 46, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (21/7)
- 符号: too-many-instance-attributes

#### 行 124, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 181, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 189, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 197, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 205, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 212, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 224, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 240, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 255, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 258, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (30/12)
- 符号: too-many-branches

#### 行 258, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (70/50)
- 符号: too-many-statements

#### 行 260, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 275, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 278, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listPlt' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 279, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listBatteryName' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 280, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listBatteryNameSplit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 281, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 283, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 283, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 283, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 283, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 283, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 293, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 295, 列 20
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listAxis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 296, 列 20
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listXTicks' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 300, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 303, 列 24
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listAxis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 304, 列 24
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listXTicks' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 337, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intCurrentLevelNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 338, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intMaxXaxis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 339, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listXTicks' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 340, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listAxis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 343, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception BaseException
- 符号: broad-exception-caught

#### 行 344, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'errorlog' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 370, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 377, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 391, 列 20
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 399, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 422, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 428, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 431, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 432, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 436, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 447, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listPlt' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 448, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listBatteryName' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 449, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listBatteryNameSplit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 519, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 546, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 594, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 624, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 639, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 654, 列 16
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'check_line1'
- 符号: unused-variable

#### 行 654, 列 29
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'check_line2'
- 符号: unused-variable

#### 行 660, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 670, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 726, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (datetime)
- 符号: import-outside-toplevel

#### 行 740, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 819, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 836, 列 24
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'label'
- 符号: unused-argument

#### 行 868, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 908, 列 33
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'label'
- 符号: unused-argument

#### 行 953, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 967, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 972, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 985, 列 21
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"boxstyle": 'round,pad=0.5', "fc": 'yellow', "alpha": 0.7}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 986, 列 27
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"arrowstyle": '->'}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 992, 列 16
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 1019, 列 35
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1051, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1058, 列 4
- 类型: warning
- 代码: W0105
- 描述: String statement has no effect
- 符号: pointless-string-statement

## 文件: src\battery_analysis\main\main_window.py

### 问题统计
- 问题总数: 67
- 警告(Warning): 20
- 规范(Convention): 24
- 重构(Refactor): 23

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (2168/1000)
- 符号: too-many-lines

#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused resources_rc imported from battery_analysis.resources
- 符号: unused-import

#### 行 17, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused version imported from battery_analysis.utils
- 符号: unused-import

#### 行 19, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 20, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import re" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 21, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 22, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 23, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import time" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 24, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import hashlib" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 25, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 26, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import warnings" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 27, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "from pathlib import Path" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 28, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import multiprocessing" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 31, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import PyQt6.QtGui as QG" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 32, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import PyQt6.QtCore as QC" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 33, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import PyQt6.QtWidgets as QW" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 34, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import win32api" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 35, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import win32con" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 36, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import matplotlib" should be placed before "from battery_analysis.resources import resources_rc"
- 符号: wrong-import-order

#### 行 135, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (25/7)
- 符号: too-many-instance-attributes

#### 行 135, 列 0
- 类型: refactor
- 代码: R0904
- 描述: Too many public methods (48/20)
- 符号: too-many-public-methods

#### 行 140, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.__version__)
- 符号: import-outside-toplevel

#### 行 167, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (ctypes)
- 符号: import-outside-toplevel

#### 行 230, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 247, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 310, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 395, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (18/12)
- 符号: too-many-branches

#### 行 470, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 568, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.__version__)
- 符号: import-outside-toplevel

#### 行 680, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (21/12)
- 符号: too-many-branches

#### 行 742, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 761, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 776, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 788, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 794, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 800, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 979, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1144, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (17/12)
- 符号: too-many-branches

#### 行 1166, 列 12
- 类型: refactor
- 代码: R1723
- 描述: Unnecessary "elif" after "break", remove the leading "el" from "elif"
- 符号: no-else-break

#### 行 1212, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 1212, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (54/50)
- 符号: too-many-statements

#### 行 1289, 列 11
- 类型: refactor
- 代码: R1714
- 描述: Consider merging these comparisons with 'in' by using 'current_tester_location in (0, 1)'. Use a set instead if elements are hashable.
- 符号: consider-using-in

#### 行 1306, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (16/12)
- 符号: too-many-branches

#### 行 1306, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (64/50)
- 符号: too-many-statements

#### 行 1351, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1355, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1404, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (54/50)
- 符号: too-many-statements

#### 行 1446, 列 20
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 1451, 列 16
- 类型: warning
- 代码: W0632
- 描述: Possible unbalanced tuple unpacking with sequence defined at line 1445: left side has 4 labels, right side has 0 values
- 符号: unbalanced-tuple-unpacking

#### 行 1466, 列 20
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1484, 列 20
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 1545, 列 8
- 类型: warning
- 代码: W0105
- 描述: String statement has no effect
- 符号: pointless-string-statement

#### 行 1627, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1690, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (21/12)
- 符号: too-many-branches

#### 行 1690, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (83/50)
- 符号: too-many-statements

#### 行 1791, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 1793, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (16/12)
- 符号: too-many-branches

#### 行 1793, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (77/50)
- 符号: too-many-statements

#### 行 1954, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (21/12)
- 符号: too-many-branches

#### 行 1954, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (74/50)
- 符号: too-many-statements

#### 行 1985, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1993, 列 20
- 类型: warning
- 代码: W0632
- 描述: Possible unbalanced tuple unpacking with sequence defined at line 1960: left side has 4 labels, right side has 0 values
- 符号: unbalanced-tuple-unpacking

#### 行 2031, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2037, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2054, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2059, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2063, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\workers\analysis_worker.py

### 问题统计
- 问题总数: 21
- 警告(Warning): 14
- 规范(Convention): 3
- 重构(Refactor): 4

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import time
- 符号: unused-import

#### 行 15, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (11/7)
- 符号: too-many-instance-attributes

#### 行 69, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (39/12)
- 符号: too-many-branches

#### 行 69, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (140/50)
- 符号: too-many-statements

#### 行 87, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 90, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 107, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.battery_analysis)
- 符号: import-outside-toplevel

#### 行 165, 列 24
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 行 188, 列 32
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 行 196, 列 36
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 行 199, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 223, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 236, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.file_writer)
- 符号: import-outside-toplevel

#### 行 268, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 270, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 274, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 293, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 315, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.version.Version)
- 符号: import-outside-toplevel

#### 行 317, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 339, 列 20
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 343, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\resources\resources_rc.py

### 问题统计
- 问题总数: 1
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

## 文件: src\battery_analysis\ui\ui_main_window.py

### 问题统计
- 问题总数: 133
- 警告(Warning): 127
- 规范(Convention): 2
- 重构(Refactor): 4

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1701/1000)
- 符号: too-many-lines

#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 12, 列 0
- 类型: refactor
- 代码: R0205
- 描述: Class 'Ui_MainWindow' inherits from object, can be safely removed from bases in python3
- 符号: useless-object-inheritance

#### 行 12, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (127/7)
- 符号: too-many-instance-attributes

#### 行 13, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (1032/50)
- 符号: too-many-statements

#### 行 26, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'centralwidget' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 35, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_BatteryConfig' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 44, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 50, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_5' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 53, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_8' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 57, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 61, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 79, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 115, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 119, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 138, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'spinBox_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 163, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_2' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 168, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 171, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_5' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 175, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 179, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 197, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 245, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 249, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 267, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 291, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 295, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 313, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 336, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 341, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 344, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_7' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 348, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 352, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 370, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 424, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 429, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 448, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 505, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Specification' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 509, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Specification' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 527, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 533, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Specification_Method' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 588, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Specification_Type' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 647, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 652, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_6' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 655, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_9' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 659, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 664, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 684, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 710, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 715, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 728, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 752, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 757, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 777, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 807, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_TestConfig' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 820, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_8' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 829, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 834, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 852, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 883, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 903, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_10' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 913, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 918, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 936, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 980, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_9' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 989, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 994, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1013, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1066, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_Path' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1073, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_11' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1083, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1088, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1106, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1129, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1147, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_12' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1157, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1162, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1173, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1196, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1208, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_TestInformation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1220, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'scrollArea' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1225, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'scrollAreaWidgetContents' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1235, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1238, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'tableWidget_TestInformation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1336, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_RunButton' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1341, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1348, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_RunAndVersion' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1353, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_7' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1357, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_Run' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1403, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_6' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1415, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'progressBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1427, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1429, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1434, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1450, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1475, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'toolBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1481, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'statusBar_BatteryAnalysis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1486, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1489, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuFile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1491, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuEdit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1493, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuView' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1495, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuTools' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1497, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuHelp' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1500, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionNew' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1502, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOpen' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1504, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1506, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave_As' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1508, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionExport_Report' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1510, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionExit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1512, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionUndo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1514, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionRedo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1516, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCut' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1518, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCopy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1520, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionPaste' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1522, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionPreferences' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1524, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionShow_Toolbar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1528, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionRun_Analysis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1530, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOpen_File' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1532, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave_Results' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1534, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSettings' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1536, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionHelp' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1538, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionShow_Statusbar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1542, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionZoom_In' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1544, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionZoom_Out' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1546, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionReset_Zoom' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1548, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCalculate_Battery' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1550, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionAnalyze_Data' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1552, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionGenerate_Report' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1554, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionBatch_Processing' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1556, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionUser_Mannual' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1558, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOnline_Help' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1560, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionAbout' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1608, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (69/50)
- 符号: too-many-statements

## 文件: src\battery_analysis\utils\battery_analysis.py

### 问题统计
- 问题总数: 26
- 警告(Warning): 2
- 规范(Convention): 12
- 重构(Refactor): 12

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 3, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import xlrd as rd" should be placed before "from battery_analysis.utils.exception_type import BatteryAnalysisException"
- 符号: wrong-import-order

#### 行 4, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 5, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 6, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import datetime" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 7, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import traceback" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 8, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 9, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import re" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 10, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import multiprocessing" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 11, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 12, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import concurrent.futures" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 24, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (18/7)
- 符号: too-many-instance-attributes

#### 行 25, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (14/12)
- 符号: too-many-branches

#### 行 25, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (70/50)
- 符号: too-many-statements

#### 行 97, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.resource_manager.ResourceManager)
- 符号: import-outside-toplevel

#### 行 123, 列 32
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise BatteryAnalysisException(f'处理失败: {str(e)}') from e'
- 符号: raise-missing-from

#### 行 139, 列 28
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise BatteryAnalysisException(f'并行处理失败: {str(e)}') from e'
- 符号: raise-missing-from

#### 行 170, 列 4
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (8/6)
- 符号: too-many-return-statements

#### 行 170, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (32/12)
- 符号: too-many-branches

#### 行 170, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (76/50)
- 符号: too-many-statements

#### 行 180, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (12/5)
- 符号: too-many-nested-blocks

#### 行 180, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (11/5)
- 符号: too-many-nested-blocks

#### 行 180, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (12/5)
- 符号: too-many-nested-blocks

#### 行 180, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (11/5)
- 符号: too-many-nested-blocks

#### 行 315, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (19/12)
- 符号: too-many-branches

#### 行 315, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (95/50)
- 符号: too-many-statements

## 文件: src\battery_analysis\utils\csv_utils.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 1
- 规范(Convention): 4

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 1, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import csv
- 符号: unused-import

#### 行 6, 列 7
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 符号: unidiomatic-typecheck

#### 行 9, 列 9
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 符号: unidiomatic-typecheck

#### 行 11, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

## 文件: src\battery_analysis\utils\data_utils.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 2

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 10, 列 4
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

## 文件: src\battery_analysis\utils\excel_utils.py

### 问题统计
- 问题总数: 3
- 规范(Convention): 3

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 10, 列 7
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 符号: unidiomatic-typecheck

#### 行 10, 列 35
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 符号: unidiomatic-typecheck

## 文件: src\battery_analysis\utils\exception_type.py

### 问题统计
- 问题总数: 1
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

## 文件: src\battery_analysis\utils\file_writer.py

### 问题统计
- 问题总数: 84
- 警告(Warning): 36
- 规范(Convention): 36
- 重构(Refactor): 12

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1659/1000)
- 符号: too-many-lines

#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 9, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.shared import Pt, Cm" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 10, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.oxml.ns import qn" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused qn imported from docx.oxml.ns
- 符号: unused-import

#### 行 11, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.oxml import OxmlElement" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 11, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused OxmlElement imported from docx.oxml
- 符号: unused-import

#### 行 12, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.opc.constants import RELATIONSHIP_TYPE" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused RELATIONSHIP_TYPE imported from docx.opc.constants
- 符号: unused-import

#### 行 13, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.enum.text import WD_LINE_SPACING" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 14, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 15, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.enum.dml import MSO_THEME_COLOR_INDEX" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused MSO_THEME_COLOR_INDEX imported from docx.enum.dml
- 符号: unused-import

#### 行 16, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx import Document" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 17, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from openpyxl.utils import get_column_letter" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 17, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused get_column_letter imported from openpyxl.utils
- 符号: unused-import

#### 行 18, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from matplotlib.ticker import MultipleLocator" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 19, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import matplotlib.pyplot as plt" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 20, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import xlsxwriter as xwt" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 21, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import numpy as np" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 21, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused numpy imported as np
- 符号: unused-import

#### 行 22, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 23, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 24, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 24, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import sys
- 符号: unused-import

#### 行 25, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import json" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 26, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import math" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 27, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import datetime" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 28, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import traceback" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 29, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import configparser" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 30, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 33, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package battery_analysis are not grouped
- 符号: ungrouped-imports

#### 行 37, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import matplotlib" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 37, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package matplotlib are not grouped
- 符号: ungrouped-imports

#### 行 41, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (31/7)
- 符号: too-many-instance-attributes

#### 行 42, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (38/12)
- 符号: too-many-branches

#### 行 42, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (141/50)
- 符号: too-many-statements

#### 行 72, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 120, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (re)
- 符号: import-outside-toplevel

#### 行 235, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (pathlib.Path)
- 符号: import-outside-toplevel

#### 行 266, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 279, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 297, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (131/12)
- 符号: too-many-branches

#### 行 297, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (467/50)
- 符号: too-many-statements

#### 行 526, 列 12
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 540, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 541, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 542, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 550, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 551, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 557, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 558, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 559, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 567, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 568, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 795, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 893, 列 55
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 909, 列 55
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1359, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 1362, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1377, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1392, 列 28
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _element of a client class
- 符号: protected-access

#### 行 1392, 列 66
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _element of a client class
- 符号: protected-access

#### 行 1414, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1414, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1417, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1417, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1420, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1420, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1423, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1423, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1442, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (56/50)
- 符号: too-many-statements

#### 行 1447, 列 24
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"linewidth": 1, "color": 'red'}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 1474, 列 12
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 1534, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (13/7)
- 符号: too-many-instance-attributes

#### 行 1545, 列 16
- 类型: warning
- 代码: W0719
- 描述: Raising too general exception: Exception
- 符号: broad-exception-raised

#### 行 1546, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1574, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1580, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 1600, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1621, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1630, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1644, 列 13
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

#### 行 1654, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception BaseException
- 符号: broad-exception-caught

## 文件: src\battery_analysis\utils\plot_utils.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 1
- 规范(Convention): 2

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 6, 列 0
- 类型: warning
- 代码: W0105
- 描述: String statement has no effect
- 符号: pointless-string-statement

#### 行 46, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

## 文件: src\battery_analysis\utils\word_utils.py

### 问题统计
- 问题总数: 4
- 信息(Info): 4

### 详细问题
#### 行 16, 列 0
- 类型: info
- 代码: I0011
- 描述: Locally disabling protected-access (W0212)
- 符号: locally-disabled

#### 行 16, 列 0
- 类型: info
- 代码: I0020
- 描述: Suppressed 'protected-access' (from line 16)
- 符号: suppressed-message

#### 行 107, 列 0
- 类型: info
- 代码: I0011
- 描述: Locally disabling protected-access (W0212)
- 符号: locally-disabled

#### 行 107, 列 0
- 类型: info
- 代码: I0020
- 描述: Suppressed 'protected-access' (from line 107)
- 符号: suppressed-message

