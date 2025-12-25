# 代码重构计划

## 概述
- 分析日期: 2025-12-25 11:15:50
- 总文件数: 22
- 存在问题的文件数: 22

## 文件: scripts\build.py

### 问题统计
- 问题总数: 20
- 错误(Error): 1
- 警告(Warning): 14
- 规范(Convention): 4
- 重构(Refactor): 1

### 详细问题
#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import tomllib
- 符号: unused-import

#### 行 22, 列 4
- 类型: error
- 代码: E0601
- 描述: Using variable 'logger' before assignment
- 符号: used-before-assignment

#### 行 50, 列 4
- 类型: warning
- 代码: W0237
- 描述: Parameter 'optionstr' has been renamed to 'option_str' in overriding 'CaseSensitiveConfigParser.optionxform' method
- 符号: arguments-renamed

#### 行 66, 列 8
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'e' from outer scope (line 21)
- 符号: redefined-outer-name

#### 行 66, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 152, 列 12
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'os' from outer scope (line 6)
- 符号: redefined-outer-name

#### 行 152, 列 12
- 类型: warning
- 代码: W0404
- 描述: Reimport 'os' (imported line 6)
- 符号: reimported

#### 行 152, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (os)
- 符号: import-outside-toplevel

#### 行 154, 列 8
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'e' from outer scope (line 21)
- 符号: redefined-outer-name

#### 行 154, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 315, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 451, 列 23
- 类型: convention
- 代码: C0209
- 描述: Formatting a regular string which could be a f-string
- 符号: consider-using-f-string

#### 行 536, 列 8
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'e' from outer scope (line 21)
- 符号: redefined-outer-name

#### 行 588, 列 21
- 类型: warning
- 代码: W0123
- 描述: Use of eval
- 符号: eval-used

#### 行 693, 列 4
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (argparse)
- 符号: import-outside-toplevel

#### 行 713, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 714, 列 4
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'e' from outer scope (line 21)
- 符号: redefined-outer-name

#### 行 714, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 715, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 720, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

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

## 文件: src\battery_analysis\main\controllers\__init__.py

### 问题统计
- 问题总数: 1
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

## 文件: src\battery_analysis\main\controllers\main_controller.py

### 问题统计
- 问题总数: 7
- 错误(Error): 6
- 警告(Warning): 1

### 详细问题
#### 行 156, 列 8
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

#### 行 160, 列 16
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

#### 行 162, 列 16
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

#### 行 164, 列 16
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

#### 行 165, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 166, 列 12
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

#### 行 167, 列 8
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

## 文件: src\battery_analysis\main\controllers\validation_controller.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 5

### 详细问题
#### 行 20, 列 4
- 类型: warning
- 代码: W0246
- 描述: Useless parent or super() delegation in method '__init__'
- 符号: useless-parent-delegation

#### 行 102, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 105, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 136, 列 17
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

#### 行 139, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\controllers\visualizer_controller.py

### 问题统计
- 问题总数: 19
- 警告(Warning): 16
- 重构(Refactor): 3

### 详细问题
#### 行 27, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (21/12)
- 符号: too-many-branches

#### 行 27, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (74/50)
- 符号: too-many-statements

#### 行 37, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 41, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 45, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 49, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 77, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 90, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 95, 列 28
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 98, 列 28
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 104, 列 36
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 112, 列 28
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 117, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 124, 列 20
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 131, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 134, 列 26
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'dirs'
- 符号: unused-variable

#### 行 137, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 144, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 163, 列 12
- 类型: warning
- 代码: W0719
- 描述: Raising too general exception: Exception
- 符号: broad-exception-raised

## 文件: src\battery_analysis\main\image_show.py

### 问题统计
- 问题总数: 97
- 错误(Error): 4
- 警告(Warning): 63
- 规范(Convention): 20
- 重构(Refactor): 10

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1388/1000)
- 符号: too-many-lines

#### 行 25, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QFileDialog' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 27, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from PyQt6.QtWidgets import QFileDialog"
- 符号: wrong-import-order

#### 行 28, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "from pathlib import Path" should be placed before "from PyQt6.QtWidgets import QFileDialog"
- 符号: wrong-import-order

#### 行 29, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import configparser" should be placed before "from PyQt6.QtWidgets import QFileDialog"
- 符号: wrong-import-order

#### 行 30, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import traceback" should be placed before "from PyQt6.QtWidgets import QFileDialog"
- 符号: wrong-import-order

#### 行 31, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import math" should be placed before "from PyQt6.QtWidgets import QFileDialog"
- 符号: wrong-import-order

#### 行 31, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import math
- 符号: unused-import

#### 行 32, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "from PyQt6.QtWidgets import QFileDialog"
- 符号: wrong-import-order

#### 行 33, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "from PyQt6.QtWidgets import QFileDialog"
- 符号: wrong-import-order

#### 行 34, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "from PyQt6.QtWidgets import QFileDialog"
- 符号: wrong-import-order

#### 行 41, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import matplotlib.pyplot as plt" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 42, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from matplotlib.ticker import MultipleLocator" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 43, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from matplotlib.widgets import CheckButtons" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 44, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.utils.config_utils import find_config_file" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 59, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (22/7)
- 符号: too-many-instance-attributes

#### 行 93, 列 23
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'data_path' from outer scope (line 1371)
- 符号: redefined-outer-name

#### 行 144, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 149, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 149, 列 29
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 151, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 151, 列 32
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 160, 列 28
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'data_path' from outer scope (line 1371)
- 符号: redefined-outer-name

#### 行 167, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 171, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 196, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 230, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 341, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 349, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 357, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 366, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 373, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 385, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 401, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 416, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 421, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 440, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 527, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 614, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 641, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 689, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 692, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (64/50)
- 符号: too-many-statements

#### 行 723, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 738, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 759, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 792, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 805, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 822, 列 22
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'dirs'
- 符号: unused-variable

#### 行 829, 列 20
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 834, 列 20
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 842, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 844, 列 12
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'traceback' from outer scope (line 30)
- 符号: redefined-outer-name

#### 行 844, 列 12
- 类型: warning
- 代码: W0404
- 描述: Reimport 'traceback' (imported line 30)
- 符号: reimported

#### 行 844, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (traceback)
- 符号: import-outside-toplevel

#### 行 892, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (datetime)
- 符号: import-outside-toplevel

#### 行 920, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 953, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 954, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 955, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 958, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 970, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 985, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 1004, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 1004, 列 29
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1006, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1011, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib.backends.backend_tkagg.NavigationToolbar2Tk)
- 符号: import-outside-toplevel

#### 行 1011, 列 20
- 类型: warning
- 代码: W0611
- 描述: Unused NavigationToolbar2Tk imported from matplotlib.backends.backend_tkagg
- 符号: unused-import

#### 行 1015, 列 34
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'tk'
- 符号: undefined-variable

#### 行 1019, 列 36
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'tk'
- 符号: undefined-variable

#### 行 1026, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1031, 列 24
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib.widgets.Button)
- 符号: import-outside-toplevel

#### 行 1039, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1041, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1058, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1118, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1135, 列 24
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'label'
- 符号: unused-argument

#### 行 1167, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1207, 列 33
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'label'
- 符号: unused-argument

#### 行 1252, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1266, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1271, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1284, 列 21
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"boxstyle": 'round,pad=0.5', "fc": 'yellow', "alpha": 0.7}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 1285, 列 27
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"arrowstyle": '->'}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 1291, 列 16
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 1318, 列 35
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1350, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1357, 列 4
- 类型: warning
- 代码: W0105
- 描述: String statement has no effect
- 符号: pointless-string-statement

#### 行 1365, 列 4
- 类型: warning
- 代码: W0404
- 描述: Reimport 'sys' (imported line 34)
- 符号: reimported

#### 行 1366, 列 4
- 类型: error
- 代码: E0611
- 描述: No name 'QApplication' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 1366, 列 4
- 类型: convention
- 代码: C0412
- 描述: Imports from package PyQt6 are not grouped
- 符号: ungrouped-imports

#### 行 1374, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 1381, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 1381, 列 21
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1384, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 1384, 列 21
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1387, 列 4
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 1387, 列 17
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

## 文件: src\battery_analysis\main\main_window.py

### 问题统计
- 问题总数: 90
- 警告(Warning): 37
- 规范(Convention): 28
- 重构(Refactor): 25

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (2385/1000)
- 符号: too-many-lines

#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused image_show imported from battery_analysis.main
- 符号: unused-import

#### 行 13, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused resources_rc imported from battery_analysis.resources
- 符号: unused-import

#### 行 20, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 21, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import re" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 22, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 23, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 24, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import time" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 25, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import hashlib" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 26, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 27, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import warnings" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 28, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "from pathlib import Path" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 29, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import multiprocessing" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 32, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import PyQt6.QtGui as QG" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 33, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import PyQt6.QtCore as QC" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 34, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import PyQt6.QtWidgets as QW" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 35, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import win32api" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 36, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import win32con" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 37, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import matplotlib" should be placed before "from battery_analysis.main import image_show"
- 符号: wrong-import-order

#### 行 56, 列 8
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'VisualizerController' from outer scope (line 17)
- 符号: redefined-outer-name

#### 行 56, 列 8
- 类型: warning
- 代码: W0404
- 描述: Reimport 'VisualizerController' (imported line 17)
- 符号: reimported

#### 行 56, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.controllers.visualizer_controller.VisualizerController)
- 符号: import-outside-toplevel

#### 行 65, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 67, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (traceback)
- 符号: import-outside-toplevel

#### 行 151, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (25/7)
- 符号: too-many-instance-attributes

#### 行 151, 列 0
- 类型: refactor
- 代码: R0904
- 描述: Too many public methods (51/20)
- 符号: too-many-public-methods

#### 行 156, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.__version__)
- 符号: import-outside-toplevel

#### 行 183, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (ctypes)
- 符号: import-outside-toplevel

#### 行 246, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 263, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 327, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 412, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (19/12)
- 符号: too-many-branches

#### 行 412, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (51/50)
- 符号: too-many-statements

#### 行 490, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 588, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.__version__)
- 符号: import-outside-toplevel

#### 行 718, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (22/12)
- 符号: too-many-branches

#### 行 783, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 802, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 817, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 829, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 835, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 841, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 909, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 911, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 922, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 929, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 931, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (traceback)
- 符号: import-outside-toplevel

#### 行 1070, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1102, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (14/12)
- 符号: too-many-branches

#### 行 1131, 列 59
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1137, 列 24
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1142, 列 24
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1148, 列 24
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1153, 列 24
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1157, 列 59
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1162, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (qdarkstyle)
- 符号: import-outside-toplevel

#### 行 1164, 列 63
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1206, 列 63
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1207, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1208, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 1351, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (17/12)
- 符号: too-many-branches

#### 行 1373, 列 12
- 类型: refactor
- 代码: R1723
- 描述: Unnecessary "elif" after "break", remove the leading "el" from "elif"
- 符号: no-else-break

#### 行 1425, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 1425, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (54/50)
- 符号: too-many-statements

#### 行 1502, 列 11
- 类型: refactor
- 代码: R1714
- 描述: Consider merging these comparisons with 'in' by using 'current_tester_location in (0, 1)'. Use a set instead if elements are hashable.
- 符号: consider-using-in

#### 行 1519, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (16/12)
- 符号: too-many-branches

#### 行 1519, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (64/50)
- 符号: too-many-statements

#### 行 1564, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1568, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1617, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (54/50)
- 符号: too-many-statements

#### 行 1659, 列 20
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 1664, 列 16
- 类型: warning
- 代码: W0632
- 描述: Possible unbalanced tuple unpacking with sequence defined at line 1658: left side has 4 labels, right side has 0 values
- 符号: unbalanced-tuple-unpacking

#### 行 1679, 列 20
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1697, 列 20
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 1758, 列 8
- 类型: warning
- 代码: W0105
- 描述: String statement has no effect
- 符号: pointless-string-statement

#### 行 1840, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1903, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (21/12)
- 符号: too-many-branches

#### 行 1903, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (83/50)
- 符号: too-many-statements

#### 行 2004, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 2006, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (16/12)
- 符号: too-many-branches

#### 行 2006, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (77/50)
- 符号: too-many-statements

#### 行 2167, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (21/12)
- 符号: too-many-branches

#### 行 2167, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (74/50)
- 符号: too-many-statements

#### 行 2198, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2206, 列 20
- 类型: warning
- 代码: W0632
- 描述: Possible unbalanced tuple unpacking with sequence defined at line 2173: left side has 4 labels, right side has 0 values
- 符号: unbalanced-tuple-unpacking

#### 行 2244, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2250, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2267, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2272, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 2276, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\workers\analysis_worker.py

### 问题统计
- 问题总数: 20
- 警告(Warning): 14
- 规范(Convention): 2
- 重构(Refactor): 4

### 详细问题
#### 行 6, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import sys
- 符号: unused-import

#### 行 7, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import re
- 符号: unused-import

#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import subprocess
- 符号: unused-import

#### 行 14, 列 0
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

#### 行 313, 列 15
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
- 问题总数: 140
- 警告(Warning): 134
- 规范(Convention): 2
- 重构(Refactor): 4

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1442/1000)
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
- 描述: Too many instance attributes (134/7)
- 符号: too-many-instance-attributes

#### 行 13, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (1054/50)
- 符号: too-many-statements

#### 行 24, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'centralwidget' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 31, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_BatteryConfig' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 38, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 44, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_5' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 47, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_8' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 50, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 53, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 67, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 95, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 98, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 112, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'spinBox_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 131, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_2' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 136, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 139, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_5' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 142, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 145, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 159, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 203, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 206, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 220, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 239, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 242, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 256, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 275, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 280, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 283, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_7' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 286, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 289, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 303, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 353, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 356, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 370, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 419, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Specification' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 422, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Specification' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 436, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 441, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Specification_Method' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 490, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Specification_Type' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 542, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 547, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_6' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 550, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_9' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 553, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 556, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 570, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 589, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 592, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 601, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 619, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 622, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 636, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 659, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_TestConfig' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 671, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_8' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 678, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 681, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 695, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 719, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 733, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_10' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 740, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 743, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 757, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 799, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_9' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 806, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 809, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 823, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 870, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_Path' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 877, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_11' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 884, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 887, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 901, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 920, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 934, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_12' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 941, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 944, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 953, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 972, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 981, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_TestInformation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 991, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'scrollArea' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 995, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'scrollAreaWidgetContents' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1003, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1005, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'tableWidget_TestInformation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1093, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_RunButton' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1098, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1104, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_RunAndVersion' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1107, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_7' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1111, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_Run' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1153, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_6' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1163, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'progressBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1173, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1175, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1179, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1192, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1214, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'toolBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1219, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'statusBar_BatteryAnalysis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1222, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1225, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuFile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1227, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuEdit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1229, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuView' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1231, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuTools' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1233, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuHelp' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1236, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuTheme' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1238, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionNew' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1240, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOpen' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1242, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1244, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave_As' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1246, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionExport_Report' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1248, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionExit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1250, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionUndo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1252, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionRedo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1254, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCut' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1256, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCopy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1258, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionPaste' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1260, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionPreferences' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1262, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionShow_Toolbar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1266, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionRun_Analysis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1268, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOpen_File' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1270, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave_Results' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1272, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSettings' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1274, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionHelp' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1276, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionShow_Statusbar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1280, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionZoom_In' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1282, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionZoom_Out' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1284, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionReset_Zoom' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1286, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSystem_Default' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1288, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionWindows_11' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1290, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionWindows_Vista' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1292, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionFusion' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1294, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionDark_Theme' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1296, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCalculate_Battery' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1298, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionAnalyze_Data' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1300, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionGenerate_Report' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1302, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionBatch_Processing' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1304, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionUser_Mannual' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1306, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOnline_Help' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1308, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionAbout' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1310, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionVisualizer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1366, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (77/50)
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
- 问题总数: 4
- 规范(Convention): 4

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 5, 列 7
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 符号: unidiomatic-typecheck

#### 行 8, 列 9
- 类型: convention
- 代码: C0123
- 描述: Use isinstance() rather than type() for a typecheck.
- 符号: unidiomatic-typecheck

#### 行 10, 列 8
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
- 问题总数: 82
- 警告(Warning): 29
- 规范(Convention): 41
- 重构(Refactor): 12

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1657/1000)
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
- 描述: third party import "from docx.enum.text import WD_LINE_SPACING" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 11, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 12, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from docx import Document" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 13, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "from matplotlib.ticker import MultipleLocator" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 14, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import matplotlib.pyplot as plt" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 20, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import xlsxwriter as xwt" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 20, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import xlsxwriter as xwt" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 21, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import os" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 21, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 22, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import csv" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 22, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 23, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import json" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 23, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import json" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 24, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import math" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 24, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import math" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 25, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import datetime" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 25, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import datetime" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 26, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import traceback" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 26, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import traceback" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 27, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import configparser" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 27, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import configparser" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 28, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import logging" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 28, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from docx.shared import Pt, Cm"
- 符号: wrong-import-order

#### 行 31, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis import __version__" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 31, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package battery_analysis are not grouped
- 符号: ungrouped-imports

#### 行 32, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.utils.config_utils import find_config_file" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 35, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import matplotlib" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 35, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "import matplotlib" should be placed before "from battery_analysis.utils import csv_utils"
- 符号: wrong-import-order

#### 行 35, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package matplotlib are not grouped
- 符号: ungrouped-imports

#### 行 39, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (31/7)
- 符号: too-many-instance-attributes

#### 行 40, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (38/12)
- 符号: too-many-branches

#### 行 40, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (141/50)
- 符号: too-many-statements

#### 行 70, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 118, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (re)
- 符号: import-outside-toplevel

#### 行 233, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (pathlib.Path)
- 符号: import-outside-toplevel

#### 行 264, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 277, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 295, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (131/12)
- 符号: too-many-branches

#### 行 295, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (467/50)
- 符号: too-many-statements

#### 行 524, 列 12
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 538, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 539, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 540, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 548, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 549, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 555, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 556, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 557, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 565, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 566, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 793, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 891, 列 55
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 907, 列 55
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1357, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 1360, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1375, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1390, 列 28
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _element of a client class
- 符号: protected-access

#### 行 1390, 列 66
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _element of a client class
- 符号: protected-access

#### 行 1412, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1412, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1415, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1415, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1418, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1418, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1421, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1421, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1440, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (56/50)
- 符号: too-many-statements

#### 行 1445, 列 24
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"linewidth": 1, "color": 'red'}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 1472, 列 12
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 1532, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (13/7)
- 符号: too-many-instance-attributes

#### 行 1543, 列 16
- 类型: warning
- 代码: W0719
- 描述: Raising too general exception: Exception
- 符号: broad-exception-raised

#### 行 1544, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1572, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1578, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 1598, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1619, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1628, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 1642, 列 13
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

#### 行 1652, 列 15
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

#### 行 8, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.utils.exception_type import BatteryAnalysisException" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 11, 列 0
- 类型: warning
- 代码: W0105
- 描述: String statement has no effect
- 符号: pointless-string-statement

## 文件: src\battery_analysis\utils\version.py

### 问题统计
- 问题总数: 2
- 信息(Info): 2

### 详细问题
#### 行 82, 列 0
- 类型: info
- 代码: I0011
- 描述: Locally disabling protected-access (W0212)
- 符号: locally-disabled

#### 行 82, 列 0
- 类型: info
- 代码: I0020
- 描述: Suppressed 'protected-access' (from line 82)
- 符号: suppressed-message

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

