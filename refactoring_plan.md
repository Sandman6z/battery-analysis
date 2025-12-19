# 代码重构计划

## 概述
- 分析日期: 2025-12-19 13:28:25
- 总文件数: 23
- 存在问题的文件数: 23

## 文件: scripts\build.py

### 问题统计
- 问题总数: 45
- 错误(Error): 7
- 警告(Warning): 21
- 规范(Convention): 14
- 重构(Refactor): 3

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 1, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused BuildException imported from battery_analysis.utils.exception_type
- 符号: unused-import

#### 行 2, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "from battery_analysis.utils.exception_type import BuildException"
- 符号: wrong-import-order

#### 行 3, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "from battery_analysis.utils.exception_type import BuildException"
- 符号: wrong-import-order

#### 行 4, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import shutil" should be placed before "from battery_analysis.utils.exception_type import BuildException"
- 符号: wrong-import-order

#### 行 5, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import datetime" should be placed before "from battery_analysis.utils.exception_type import BuildException"
- 符号: wrong-import-order

#### 行 5, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import datetime
- 符号: unused-import

#### 行 6, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import configparser" should be placed before "from battery_analysis.utils.exception_type import BuildException"
- 符号: wrong-import-order

#### 行 7, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import subprocess" should be placed before "from battery_analysis.utils.exception_type import BuildException"
- 符号: wrong-import-order

#### 行 8, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "from pathlib import Path" should be placed before "from battery_analysis.utils.exception_type import BuildException"
- 符号: wrong-import-order

#### 行 9, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from git import Repo" should be placed before "from battery_analysis.utils.exception_type import BuildException"
- 符号: wrong-import-order

#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Repo imported from git
- 符号: unused-import

#### 行 10, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from git import Repo"
- 符号: wrong-import-order

#### 行 37, 列 4
- 类型: warning
- 代码: W0237
- 描述: Parameter 'optionstr' has been renamed to 'option_str' in overriding 'CaseSensitiveConfigParser.optionxform' method
- 符号: arguments-renamed

#### 行 41, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (9/7)
- 符号: too-many-instance-attributes

#### 行 44, 列 23
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'build_type' from outer scope (line 786)
- 符号: redefined-outer-name

#### 行 53, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tomllib)
- 符号: import-outside-toplevel

#### 行 58, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 77, 列 23
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'build_type' from outer scope (line 786)
- 符号: redefined-outer-name

#### 行 111, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 139, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 187, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 303, 列 15
- 类型: error
- 代码: E1101
- 描述: Instance of 'BuildManager' has no 'git_repo' member
- 符号: no-member

#### 行 303, 列 36
- 类型: error
- 代码: E1101
- 描述: Instance of 'BuildManager' has no 'git_index' member
- 符号: no-member

#### 行 303, 列 58
- 类型: error
- 代码: E1101
- 描述: Instance of 'BuildManager' has no 'git' member
- 符号: no-member

#### 行 317, 列 23
- 类型: error
- 代码: E1101
- 描述: Instance of 'BuildManager' has no 'git_repo' member
- 符号: no-member

#### 行 317, 列 71
- 类型: error
- 代码: E1101
- 描述: Instance of 'BuildManager' has no 'git_repo' member
- 符号: no-member

#### 行 323, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 328, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 334, 列 18
- 类型: error
- 代码: E1101
- 描述: Instance of 'BuildManager' has no 'config_path' member
- 符号: no-member

#### 行 335, 列 12
- 类型: error
- 代码: E1101
- 描述: Instance of 'BuildManager' has no 'config' member
- 符号: no-member

#### 行 411, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (19/12)
- 符号: too-many-branches

#### 行 411, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (175/50)
- 符号: too-many-statements

#### 行 433, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'python_exe'
- 符号: unused-variable

#### 行 516, 列 12
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'subprocess' from outer scope (line 7)
- 符号: redefined-outer-name

#### 行 516, 列 12
- 类型: warning
- 代码: W0404
- 描述: Reimport 'subprocess' (imported line 7)
- 符号: reimported

#### 行 516, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (subprocess)
- 符号: import-outside-toplevel

#### 行 550, 列 16
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 558, 列 16
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 620, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 683, 列 8
- 类型: warning
- 代码: W0404
- 描述: Reimport 'subprocess' (imported line 7)
- 符号: reimported

#### 行 683, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (subprocess)
- 符号: import-outside-toplevel

#### 行 721, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 726, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 774, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: scripts\run_pylint.py

### 问题统计
- 问题总数: 19
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

#### 行 227, 列 46
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 233, 列 20
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 233, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 235, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 313, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 317, 列 0
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 324, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 341, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 362, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 379, 列 11
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
- 问题总数: 2
- 规范(Convention): 2

### 详细问题
#### 行 17, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

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
- 描述: Too many lines in module (1054/1000)
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

#### 行 223, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 237, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 251, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 254, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (30/12)
- 符号: too-many-branches

#### 行 254, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (70/50)
- 符号: too-many-statements

#### 行 256, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 271, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 274, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listPlt' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 275, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listBatteryName' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 276, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listBatteryNameSplit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 277, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 279, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 279, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 279, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 279, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 279, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 289, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 291, 列 20
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listAxis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 292, 列 20
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listXTicks' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 296, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 299, 列 24
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listAxis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 300, 列 24
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listXTicks' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 333, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intCurrentLevelNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 334, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intMaxXaxis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 335, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listXTicks' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 336, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listAxis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 339, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception BaseException
- 符号: broad-exception-caught

#### 行 340, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'errorlog' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 366, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 373, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 387, 列 20
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 395, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 418, 列 16
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 424, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 427, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 428, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 432, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'intBatteryNum' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 443, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listPlt' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 444, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listBatteryName' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 445, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listBatteryNameSplit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 515, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 540, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 587, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 617, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 632, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 647, 列 16
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'check_line1'
- 符号: unused-variable

#### 行 647, 列 29
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'check_line2'
- 符号: unused-variable

#### 行 653, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 663, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 719, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (datetime)
- 符号: import-outside-toplevel

#### 行 733, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 814, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 830, 列 24
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'label'
- 符号: unused-argument

#### 行 862, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 902, 列 33
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'label'
- 符号: unused-argument

#### 行 945, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 959, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 964, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 977, 列 21
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"boxstyle": 'round,pad=0.5', "fc": 'yellow', "alpha": 0.7}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 978, 列 27
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"arrowstyle": '->'}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 984, 列 16
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 1010, 列 35
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1042, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1049, 列 4
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
- 描述: Too many lines in module (2150/1000)
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

#### 行 134, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (25/7)
- 符号: too-many-instance-attributes

#### 行 134, 列 0
- 类型: refactor
- 代码: R0904
- 描述: Too many public methods (48/20)
- 符号: too-many-public-methods

#### 行 139, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.__version__)
- 符号: import-outside-toplevel

#### 行 166, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (ctypes)
- 符号: import-outside-toplevel

#### 行 229, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 246, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 309, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 394, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (18/12)
- 符号: too-many-branches

#### 行 469, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 567, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.__version__)
- 符号: import-outside-toplevel

#### 行 679, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (21/12)
- 符号: too-many-branches

#### 行 741, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 760, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 775, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 787, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 793, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 799, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 978, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1142, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (17/12)
- 符号: too-many-branches

#### 行 1164, 列 12
- 类型: refactor
- 代码: R1723
- 描述: Unnecessary "elif" after "break", remove the leading "el" from "elif"
- 符号: no-else-break

#### 行 1204, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 1204, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (54/50)
- 符号: too-many-statements

#### 行 1281, 列 11
- 类型: refactor
- 代码: R1714
- 描述: Consider merging these comparisons with 'in' by using 'current_tester_location in (0, 1)'. Use a set instead if elements are hashable.
- 符号: consider-using-in

#### 行 1298, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (16/12)
- 符号: too-many-branches

#### 行 1298, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (64/50)
- 符号: too-many-statements

#### 行 1342, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1346, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1394, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (54/50)
- 符号: too-many-statements

#### 行 1436, 列 20
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 1441, 列 16
- 类型: warning
- 代码: W0632
- 描述: Possible unbalanced tuple unpacking with sequence defined at line 1435: left side has 4 labels, right side has 0 values
- 符号: unbalanced-tuple-unpacking

#### 行 1456, 列 20
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1474, 列 20
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 1535, 列 8
- 类型: warning
- 代码: W0105
- 描述: String statement has no effect
- 符号: pointless-string-statement

#### 行 1617, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1680, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (21/12)
- 符号: too-many-branches

#### 行 1680, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (83/50)
- 符号: too-many-statements

#### 行 1780, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 1782, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (16/12)
- 符号: too-many-branches

#### 行 1782, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (77/50)
- 符号: too-many-statements

#### 行 1943, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (21/12)
- 符号: too-many-branches

#### 行 1943, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (74/50)
- 符号: too-many-statements

#### 行 1974, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1982, 列 20
- 类型: warning
- 代码: W0632
- 描述: Possible unbalanced tuple unpacking with sequence defined at line 1949: left side has 4 labels, right side has 0 values
- 符号: unbalanced-tuple-unpacking

#### 行 2020, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2026, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2043, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2048, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2052, 列 15
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

#### 行 186, 列 32
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 行 194, 列 36
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 行 197, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 220, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 233, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.file_writer)
- 符号: import-outside-toplevel

#### 行 265, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 267, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 271, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 290, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 312, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.version.Version)
- 符号: import-outside-toplevel

#### 行 314, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 336, 列 20
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 340, 列 23
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
- 问题总数: 27
- 警告(Warning): 2
- 规范(Convention): 13
- 重构(Refactor): 12

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 2, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import xlrd as rd" should be placed before "from battery_analysis.utils.exception_type import BatteryAnalysisException"
- 符号: wrong-import-order

#### 行 3, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 4, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 5, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import datetime" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 6, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import traceback" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 7, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 8, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import re" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 9, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import multiprocessing" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 10, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 11, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import concurrent.futures" should be placed before "import xlrd as rd"
- 符号: wrong-import-order

#### 行 23, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (18/7)
- 符号: too-many-instance-attributes

#### 行 24, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (15/12)
- 符号: too-many-branches

#### 行 24, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (72/50)
- 符号: too-many-statements

#### 行 29, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 96, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.resource_manager.ResourceManager)
- 符号: import-outside-toplevel

#### 行 114, 列 32
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise BatteryAnalysisException(f'处理失败: {str(e)}') from e'
- 符号: raise-missing-from

#### 行 127, 列 28
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise BatteryAnalysisException(f'并行处理失败: {str(e)}') from e'
- 符号: raise-missing-from

#### 行 157, 列 4
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (8/6)
- 符号: too-many-return-statements

#### 行 157, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (32/12)
- 符号: too-many-branches

#### 行 157, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (76/50)
- 符号: too-many-statements

#### 行 167, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (12/5)
- 符号: too-many-nested-blocks

#### 行 167, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (11/5)
- 符号: too-many-nested-blocks

#### 行 167, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (12/5)
- 符号: too-many-nested-blocks

#### 行 167, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (11/5)
- 符号: too-many-nested-blocks

#### 行 294, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (19/12)
- 符号: too-many-branches

#### 行 294, 列 4
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

#### 行 4, 列 4
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
- 问题总数: 85
- 警告(Warning): 36
- 规范(Convention): 37
- 重构(Refactor): 12

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1555/1000)
- 符号: too-many-lines

#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 8, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.shared import Pt, Cm" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 9, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.oxml.ns import qn" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused qn imported from docx.oxml.ns
- 符号: unused-import

#### 行 10, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.oxml import OxmlElement" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused OxmlElement imported from docx.oxml
- 符号: unused-import

#### 行 11, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.opc.constants import RELATIONSHIP_TYPE" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 11, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused RELATIONSHIP_TYPE imported from docx.opc.constants
- 符号: unused-import

#### 行 12, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.enum.text import WD_LINE_SPACING" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 13, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 14, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.enum.dml import MSO_THEME_COLOR_INDEX" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused MSO_THEME_COLOR_INDEX imported from docx.enum.dml
- 符号: unused-import

#### 行 15, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx import Document" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 16, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from openpyxl.utils import get_column_letter" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 16, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused get_column_letter imported from openpyxl.utils
- 符号: unused-import

#### 行 17, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from matplotlib.ticker import MultipleLocator" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 18, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import matplotlib.pyplot as plt" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 19, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import xlsxwriter as xwt" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 20, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import numpy as np" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 20, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused numpy imported as np
- 符号: unused-import

#### 行 21, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 22, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 23, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 23, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import sys
- 符号: unused-import

#### 行 24, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import json" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 25, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import math" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 26, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import datetime" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 27, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import traceback" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 28, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import configparser" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 29, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 32, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package battery_analysis are not grouped
- 符号: ungrouped-imports

#### 行 36, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import matplotlib" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 36, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package matplotlib are not grouped
- 符号: ungrouped-imports

#### 行 40, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (31/7)
- 符号: too-many-instance-attributes

#### 行 41, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (38/12)
- 符号: too-many-branches

#### 行 41, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (141/50)
- 符号: too-many-statements

#### 行 67, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 111, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (re)
- 符号: import-outside-toplevel

#### 行 200, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (pathlib.Path)
- 符号: import-outside-toplevel

#### 行 224, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 237, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 250, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (131/12)
- 符号: too-many-branches

#### 行 250, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (467/50)
- 符号: too-many-statements

#### 行 479, 列 12
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 493, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 494, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 495, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 503, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 504, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 510, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 511, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 512, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 520, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 521, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 738, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 793, 列 55
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 807, 列 55
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1252, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 1255, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1270, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1285, 列 28
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _element of a client class
- 符号: protected-access

#### 行 1285, 列 66
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _element of a client class
- 符号: protected-access

#### 行 1307, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1307, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1310, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1310, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1313, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1313, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1316, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1316, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1335, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (56/50)
- 符号: too-many-statements

#### 行 1340, 列 24
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"linewidth": 1, "color": 'red'}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 1367, 列 12
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 1427, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (13/7)
- 符号: too-many-instance-attributes

#### 行 1438, 列 16
- 类型: warning
- 代码: W0719
- 描述: Raising too general exception: Exception
- 符号: broad-exception-raised

#### 行 1439, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1463, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1471, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1477, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 1497, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1517, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1526, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1540, 列 13
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

#### 行 1550, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception BaseException
- 符号: broad-exception-caught

## 文件: src\battery_analysis\utils\numeric_utils.py

### 问题统计
- 问题总数: 6
- 规范(Convention): 1
- 重构(Refactor): 5

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 5, 列 4
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 12, 列 4
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 19, 列 4
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 26, 列 4
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 33, 列 4
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

## 文件: src\battery_analysis\utils\plot_utils.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1
- 重构(Refactor): 1

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 6, 列 0
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (18/12)
- 符号: too-many-branches

## 文件: src\battery_analysis\utils\resource_manager.py

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

#### 行 29, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (psutil)
- 符号: import-outside-toplevel

#### 行 60, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\utils\word_utils.py

### 问题统计
- 问题总数: 6
- 警告(Warning): 3
- 规范(Convention): 3

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 4, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from docx.oxml import OxmlElement"
- 符号: wrong-import-order

#### 行 8, 列 9
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tc of a client class
- 符号: protected-access

#### 行 32, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 38, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 97, 列 4
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

## 文件: tests\battery_analysis\main\test_main_window.py

### 问题统计
- 问题总数: 6
- 错误(Error): 1
- 规范(Convention): 4
- 重构(Refactor): 1

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 2, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import json" should be placed before "import pytest"
- 符号: wrong-import-order

#### 行 3, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "import pytest"
- 符号: wrong-import-order

#### 行 5, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QApplication' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 5, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from PyQt6.QtWidgets import QApplication" should be placed before "from battery_analysis.main.main_window import Main"
- 符号: wrong-import-order

#### 行 49, 列 19
- 类型: refactor
- 代码: R1721
- 描述: Unnecessary use of a comprehension, use list(reported_by_mapping.items()) instead.
- 符号: unnecessary-comprehension

## 文件: tests\battery_analysis\utils\test_file_writer.py

### 问题统计
- 问题总数: 1
- 重构(Refactor): 1

### 详细问题
#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis.utils.battery_analysis:[25:34]
==battery_analysis.utils.file_writer:[1459:1467]
        self.listCurrentLevel = listTestInfo[14]
        self.listVoltageLevel = listTestInfo[15]
        self.strFileCurrentType = ""
        for c in range(len(self.listCurrentLevel)):
            self.strFileCurrentType = self.strFileCurrentType + \
                f"{self.listCurrentLevel[c]}-"
        self.strFileCurrentType = self.strFileCurrentType[:-1]
        # 使用os.path.join确保路径分隔符一致性
- 符号: duplicate-code

