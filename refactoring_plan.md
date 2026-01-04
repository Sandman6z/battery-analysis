# 代码重构计划

## 概述
- 分析日期: 2026-01-04 10:38:20
- 总文件数: 65
- 存在问题的文件数: 65

## 文件: scripts\build.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: scripts\build.py: Fatal error while checking 'scripts\build.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-49.txt'.
- 符号: astroid-error

#### 行 720, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: scripts\compile_translations.py

### 问题统计
- 问题总数: 7
- 规范(Convention): 6

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: scripts\compile_translations.py: Fatal error while checking 'scripts\compile_translations.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-49.txt'.
- 符号: astroid-error

#### 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package sys are not grouped
- 符号: ungrouped-imports

#### 行 11, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package subprocess are not grouped
- 符号: ungrouped-imports

#### 行 12, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 13, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package pathlib are not grouped
- 符号: ungrouped-imports

#### 行 263, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: scripts\extract_translations.py

### 问题统计
- 问题总数: 7
- 规范(Convention): 6

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: scripts\extract_translations.py: Fatal error while checking 'scripts\extract_translations.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-50.txt'.
- 符号: astroid-error

#### 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package sys are not grouped
- 符号: ungrouped-imports

#### 行 11, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package subprocess are not grouped
- 符号: ungrouped-imports

#### 行 12, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 13, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package pathlib are not grouped
- 符号: ungrouped-imports

#### 行 345, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: scripts\fix_logging_fstrings.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 1
- 规范(Convention): 1

### 详细问题
#### 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

## 文件: scripts\po_translator.py

### 问题统计
- 问题总数: 8
- 警告(Warning): 5
- 规范(Convention): 1
- 重构(Refactor): 2

### 详细问题
#### 行 7, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import sys
- 符号: unused-import

#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 52, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 83, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 130, 列 17
- 类型: warning
- 代码: W4902
- 描述: Using deprecated method getdefaultlocale()
- 符号: deprecated-method

#### 行 134, 列 4
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 行 151, 列 4
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 195, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: scripts\refactor_by_type.py

### 问题统计
- 问题总数: 6
- 警告(Warning): 6

### 详细问题
#### 行 23, 列 4
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'overview' from outer scope (line 121)
- 符号: redefined-outer-name

#### 行 33, 列 4
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'issues_by_type' from outer scope (line 121)
- 符号: redefined-outer-name

#### 行 68, 列 28
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'overview' from outer scope (line 121)
- 符号: redefined-outer-name

#### 行 68, 列 38
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'issues_by_type' from outer scope (line 121)
- 符号: redefined-outer-name

#### 行 96, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 106, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

## 文件: scripts\run_pylint.py

### 问题统计
- 问题总数: 11
- 警告(Warning): 9
- 重构(Refactor): 2

### 详细问题
#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 91, 列 18
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 119, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 160, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 175, 列 4
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'json_output'
- 符号: unused-variable

#### 行 281, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 285, 列 0
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 292, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 310, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 331, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 347, 列 11
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

## 文件: scripts\setup_i18n.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: scripts\setup_i18n.py: Fatal error while checking 'scripts\setup_i18n.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-50.txt'.
- 符号: astroid-error

#### 行 372, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\__init__.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 2

### 详细问题
#### 行 3, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 17, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import battery_analysis.utils" should be placed at the top of the module
- 符号: wrong-import-position

## 文件: src\battery_analysis\chart\interfaces\ichart_manager.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\chart\interfaces\ichart_manager.py: Fatal error while checking 'src\battery_analysis\chart\interfaces\ichart_manager.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-50.txt'.
- 符号: astroid-error

#### 行 160, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\data\interfaces\idataprocessor.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\data\interfaces\idataprocessor.py: Fatal error while checking 'src\battery_analysis\data\interfaces\idataprocessor.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-51.txt'.
- 符号: astroid-error

#### 行 220, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\i18n\__init__.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\i18n\__init__.py: Fatal error while checking 'src\battery_analysis\i18n\__init__.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-51.txt'.
- 符号: astroid-error

#### 行 342, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\i18n\language_manager.py

### 问题统计
- 问题总数: 5
- 规范(Convention): 4

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\i18n\language_manager.py: Fatal error while checking 'src\battery_analysis\i18n\language_manager.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-51.txt'.
- 符号: astroid-error

#### 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package pathlib are not grouped
- 符号: ungrouped-imports

#### 行 387, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\i18n\preferences_dialog.py

### 问题统计
- 问题总数: 3
- 规范(Convention): 2

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\i18n\preferences_dialog.py: Fatal error while checking 'src\battery_analysis\i18n\preferences_dialog.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-51.txt'.
- 符号: astroid-error

#### 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 360, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\battery_chart_viewer.py

### 问题统计
- 问题总数: 16
- 错误(Error): 3
- 规范(Convention): 12

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (2136/1000)
- 符号: too-many-lines

#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\battery_chart_viewer.py: Fatal error while checking 'src\battery_analysis\main\battery_chart_viewer.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-52.txt'.
- 符号: astroid-error

#### 行 25, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QFileDialog' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 25, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QMessageBox' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 27, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'Qt' in module 'PyQt6.QtCore'
- 符号: no-name-in-module

#### 行 28, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import sys" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 行 29, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 行 29, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 30, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "from pathlib import Path" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 行 30, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package pathlib are not grouped
- 符号: ungrouped-imports

#### 行 31, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import configparser" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 行 32, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import traceback" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 行 33, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import math" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 行 34, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import csv" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 行 35, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import os" should be placed before "from PyQt6.QtWidgets import QFileDialog, QMessageBox"
- 符号: wrong-import-order

#### 行 35, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

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

## 文件: src\battery_analysis\main\controllers\file_controller.py

### 问题统计
- 问题总数: 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\controllers\file_controller.py: Fatal error while checking 'src\battery_analysis\main\controllers\file_controller.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-52.txt'.
- 符号: astroid-error

## 文件: src\battery_analysis\main\controllers\main_controller.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 1
- 规范(Convention): 4

### 详细问题
#### 行 6, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import logging" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 6, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "import logging" should be placed before "from PyQt6 import QtCore as QC"
- 符号: wrong-import-order

#### 行 7, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from PyQt6 import QtCore as QC" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 8, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.main.workers.analysis_worker import AnalysisWorker" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 166, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\controllers\validation_controller.py

### 问题统计
- 问题总数: 9
- 警告(Warning): 5
- 规范(Convention): 2
- 重构(Refactor): 2

### 详细问题
#### 行 7, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import re
- 符号: unused-import

#### 行 27, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.service_container.get_service_container)
- 符号: import-outside-toplevel

#### 行 43, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 57, 列 4
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (7/6)
- 符号: too-many-return-statements

#### 行 97, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 100, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 131, 列 17
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

#### 行 134, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 185, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\controllers\visualizer_controller.py

### 问题统计
- 问题总数: 14
- 警告(Warning): 4
- 规范(Convention): 6
- 重构(Refactor): 4

### 详细问题
#### 行 23, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 40, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 99, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (33/12)
- 符号: too-many-branches

#### 行 99, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (108/50)
- 符号: too-many-statements

#### 行 109, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 109, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 111, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib)
- 符号: import-outside-toplevel

#### 行 253, 列 26
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'dirs'
- 符号: unused-variable

#### 行 282, 列 12
- 类型: warning
- 代码: W0719
- 描述: Raising too general exception: Exception
- 符号: broad-exception-raised

#### 行 314, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib)
- 符号: import-outside-toplevel

#### 行 315, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib.pyplot)
- 符号: import-outside-toplevel

#### 行 315, 列 8
- 类型: warning
- 代码: W0611
- 描述: Unused matplotlib.pyplot imported as plt
- 符号: unused-import

#### 行 356, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib.pyplot)
- 符号: import-outside-toplevel

#### 行 373, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\factories\visualizer_factory.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\factories\visualizer_factory.py: Fatal error while checking 'src\battery_analysis\main\factories\visualizer_factory.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-55.txt'.
- 符号: astroid-error

#### 行 232, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\interfaces\ivisualizer.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\interfaces\ivisualizer.py: Fatal error while checking 'src\battery_analysis\main\interfaces\ivisualizer.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-55.txt'.
- 符号: astroid-error

#### 行 90, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\main_window.py

### 问题统计
- 问题总数: 3
- 规范(Convention): 2

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (3024/1000)
- 符号: too-many-lines

#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\main_window.py: Fatal error while checking 'src\battery_analysis\main\main_window.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-56.txt'.
- 符号: astroid-error

#### 行 14, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

## 文件: src\battery_analysis\main\services\application_service.py

### 问题统计
- 问题总数: 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\application_service.py: Fatal error while checking 'src\battery_analysis\main\services\application_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-56.txt'.
- 符号: astroid-error

## 文件: src\battery_analysis\main\services\config_service.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\config_service.py: Fatal error while checking 'src\battery_analysis\main\services\config_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-56.txt'.
- 符号: astroid-error

#### 行 299, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\services\config_service_interface.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\config_service_interface.py: Fatal error while checking 'src\battery_analysis\main\services\config_service_interface.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-56.txt'.
- 符号: astroid-error

#### 行 117, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\services\data_processing_service_interface.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\data_processing_service_interface.py: Fatal error while checking 'src\battery_analysis\main\services\data_processing_service_interface.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-56.txt'.
- 符号: astroid-error

#### 行 176, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\services\document_service_interface.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\document_service_interface.py: Fatal error while checking 'src\battery_analysis\main\services\document_service_interface.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-57.txt'.
- 符号: astroid-error

#### 行 170, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\services\environment_service.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\environment_service.py: Fatal error while checking 'src\battery_analysis\main\services\environment_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-57.txt'.
- 符号: astroid-error

#### 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

## 文件: src\battery_analysis\main\services\event_bus.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\event_bus.py: Fatal error while checking 'src\battery_analysis\main\services\event_bus.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-57.txt'.
- 符号: astroid-error

#### 行 272, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\services\file_service.py

### 问题统计
- 问题总数: 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\file_service.py: Fatal error while checking 'src\battery_analysis\main\services\file_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-57.txt'.
- 符号: astroid-error

## 文件: src\battery_analysis\main\services\file_service_interface.py

### 问题统计
- 问题总数: 3
- 规范(Convention): 2

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\file_service_interface.py: Fatal error while checking 'src\battery_analysis\main\services\file_service_interface.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-57.txt'.
- 符号: astroid-error

#### 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package abc are not grouped
- 符号: ungrouped-imports

#### 行 152, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\services\i18n_service.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\i18n_service.py: Fatal error while checking 'src\battery_analysis\main\services\i18n_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-57.txt'.
- 符号: astroid-error

#### 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

## 文件: src\battery_analysis\main\services\progress_service.py

### 问题统计
- 问题总数: 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\progress_service.py: Fatal error while checking 'src\battery_analysis\main\services\progress_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-58.txt'.
- 符号: astroid-error

## 文件: src\battery_analysis\main\services\service_container.py

### 问题统计
- 问题总数: 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\service_container.py: Fatal error while checking 'src\battery_analysis\main\services\service_container.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-48.txt'.
- 符号: astroid-error

## 文件: src\battery_analysis\main\services\validation_service.py

### 问题统计
- 问题总数: 4
- 规范(Convention): 3

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\validation_service.py: Fatal error while checking 'src\battery_analysis\main\services\validation_service.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-58.txt'.
- 符号: astroid-error

#### 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 266, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\services\validation_service_interface.py

### 问题统计
- 问题总数: 3
- 规范(Convention): 2

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\main\services\validation_service_interface.py: Fatal error while checking 'src\battery_analysis\main\services\validation_service_interface.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-58.txt'.
- 符号: astroid-error

#### 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package abc are not grouped
- 符号: ungrouped-imports

#### 行 122, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

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

## 文件: src\battery_analysis\ui\frameworks\pyqt6_ui_framework.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\frameworks\pyqt6_ui_framework.py: Fatal error while checking 'src\battery_analysis\ui\frameworks\pyqt6_ui_framework.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-59.txt'.
- 符号: astroid-error

#### 行 419, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\ui\interfaces\iuiframework.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\interfaces\iuiframework.py: Fatal error while checking 'src\battery_analysis\ui\interfaces\iuiframework.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-38-00.txt'.
- 符号: astroid-error

#### 行 173, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\ui\modern_battery_viewer.py

### 问题统计
- 问题总数: 3
- 规范(Convention): 2

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\modern_battery_viewer.py: Fatal error while checking 'src\battery_analysis\ui\modern_battery_viewer.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-38-00.txt'.
- 符号: astroid-error

#### 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 755, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\ui\modern_battery_viewer_refactored.py

### 问题统计
- 问题总数: 6
- 规范(Convention): 5

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\modern_battery_viewer_refactored.py: Fatal error while checking 'src\battery_analysis\ui\modern_battery_viewer_refactored.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-38-00.txt'.
- 符号: astroid-error

#### 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package os are not grouped
- 符号: ungrouped-imports

#### 行 10, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package sys are not grouped
- 符号: ungrouped-imports

#### 行 11, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package pathlib are not grouped
- 符号: ungrouped-imports

#### 行 637, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\ui\modern_chart_widget.py

### 问题统计
- 问题总数: 33
- 错误(Error): 16
- 警告(Warning): 13
- 规范(Convention): 3
- 重构(Refactor): 1

### 详细问题
#### 行 8, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package sys are not grouped
- 符号: ungrouped-imports

#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import sys
- 符号: unused-import

#### 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QWidget' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QVBoxLayout' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QHBoxLayout' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QPushButton' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QLabel' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QComboBox' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QCheckBox' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QGroupBox' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QFrame' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 10, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QSizePolicy' in module 'PyQt6.QtWidgets'
- 符号: no-name-in-module

#### 行 13, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'Qt' in module 'PyQt6.QtCore'
- 符号: no-name-in-module

#### 行 13, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'pyqtSignal' in module 'PyQt6.QtCore'
- 符号: no-name-in-module

#### 行 13, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QSize' in module 'PyQt6.QtCore'
- 符号: no-name-in-module

#### 行 14, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QFont' in module 'PyQt6.QtGui'
- 符号: no-name-in-module

#### 行 14, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QIcon' in module 'PyQt6.QtGui'
- 符号: no-name-in-module

#### 行 14, 列 0
- 类型: error
- 代码: E0611
- 描述: No name 'QPixmap' in module 'PyQt6.QtGui'
- 符号: no-name-in-module

#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QIcon imported from PyQt6.QtGui
- 符号: unused-import

#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QPixmap imported from PyQt6.QtGui
- 符号: unused-import

#### 行 16, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused matplotlib.pyplot imported as plt
- 符号: unused-import

#### 行 17, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import matplotlib
- 符号: unused-import

#### 行 26, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (17/7)
- 符号: too-many-instance-attributes

#### 行 185, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 310, 列 12
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _style_axes of a client class
- 符号: protected-access

#### 行 322, 列 8
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _style_axes of a client class
- 符号: protected-access

#### 行 383, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 404, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 413, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'chart_styles'
- 符号: unused-variable

#### 行 487, 列 37
- 类型: warning
- 代码: W0622
- 描述: Redefining built-in 'format'
- 符号: redefined-builtin

#### 行 496, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 515, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\ui\modern_theme.py

### 问题统计
- 问题总数: 5
- 错误(Error): 1
- 警告(Warning): 1
- 规范(Convention): 1
- 重构(Refactor): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\modern_theme.py: Fatal error while checking 'src\battery_analysis\ui\modern_theme.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-38-06.txt'.
- 符号: astroid-error

#### 行 116, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 117, 列 12
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

#### 行 160, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "elif" after "return", remove the leading "el" from "elif"
- 符号: no-else-return

#### 行 272, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\ui\styles\__init__.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 2

### 详细问题
#### 行 8, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from .style_manager import StyleManager, style_manager, apply_modern_theme, create_styled_button, create_styled_groupbox" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 22, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\ui\styles\style_manager.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\ui\styles\style_manager.py: Fatal error while checking 'src\battery_analysis\ui\styles\style_manager.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-38-06.txt'.
- 符号: astroid-error

#### 行 252, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\ui\ui_main_window.py

### 问题统计
- 问题总数: 128
- 警告(Warning): 122
- 规范(Convention): 2
- 重构(Refactor): 4

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1384/1000)
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
- 描述: Too many instance attributes (122/7)
- 符号: too-many-instance-attributes

#### 行 13, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (1012/50)
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
- 描述: Attribute 'statusBar_BatteryAnalysis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1217, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1220, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuFile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1222, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuEdit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1224, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuView' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1226, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuTools' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1228, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuHelp' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1231, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionNew' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1233, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOpen' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1235, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1237, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave_As' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1239, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionExport_Report' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1241, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionExit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1243, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionUndo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1245, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionRedo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1247, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCut' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1249, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCopy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1251, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionPaste' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1253, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionPreferences' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1255, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionShow_Toolbar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1257, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionShow_Statusbar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1259, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionZoom_In' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1261, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionZoom_Out' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1263, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionReset_Zoom' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1265, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCalculate_Battery' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1267, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionAnalyze_Data' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1269, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionGenerate_Report' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1271, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionBatch_Processing' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1273, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionUser_Mannual' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1275, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOnline_Help' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1277, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionAbout' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1279, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionBatteryChartViewer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1324, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (61/50)
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

## 文件: src\battery_analysis\utils\config_parser.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\utils\config_parser.py: Fatal error while checking 'src\battery_analysis\utils\config_parser.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-38-08.txt'.
- 符号: astroid-error

#### 行 230, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\utils\config_utils.py

### 问题统计
- 问题总数: 7
- 错误(Error): 1
- 警告(Warning): 5
- 规范(Convention): 1

### 详细问题
#### 行 7, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 9, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 80, 列 4
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'paths'
- 符号: unused-variable

#### 行 121, 列 47
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'sys'
- 符号: undefined-variable

#### 行 133, 列 4
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'paths'
- 符号: unused-variable

#### 行 187, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 219, 列 11
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

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

## 文件: src\battery_analysis\utils\environment_utils.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\utils\environment_utils.py: Fatal error while checking 'src\battery_analysis\utils\environment_utils.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-38-09.txt'.
- 符号: astroid-error

#### 行 338, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

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
- 问题总数: 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\utils\file_writer.py: Fatal error while checking 'src\battery_analysis\utils\file_writer.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-37-49.txt'.
- 符号: astroid-error

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

## 文件: src\battery_analysis\utils\test_environment_detection.py

### 问题统计
- 问题总数: 1
- 错误(Error): 1

### 详细问题
#### 行 417, 列 119
- 类型: error
- 代码: E0001
- 描述: Parsing failed: 'invalid decimal literal (<unknown>, line 417)'
- 符号: syntax-error

## 文件: src\battery_analysis\utils\test_environment_final.py

### 问题统计
- 问题总数: 1
- 错误(Error): 1

### 详细问题
#### 行 504, 列 149
- 类型: error
- 代码: E0001
- 描述: Parsing failed: 'invalid decimal literal (<unknown>, line 504)'
- 符号: syntax-error

## 文件: src\battery_analysis\utils\test_environment_scenarios.py

### 问题统计
- 问题总数: 1
- 错误(Error): 1

### 详细问题
#### 行 473, 列 128
- 类型: error
- 代码: E0001
- 描述: Parsing failed: 'invalid decimal literal (<unknown>, line 473)'
- 符号: syntax-error

## 文件: src\battery_analysis\utils\version.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 1
- 信息(Info): 1

### 详细问题
#### 行 1, 列 0
- 类型: fatal
- 代码: F0002
- 描述: src\battery_analysis\utils\version.py: Fatal error while checking 'src\battery_analysis\utils\version.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in 'C:\Users\boe\AppData\Local\pylint\pylint\Cache\pylint-crash-2026-01-04-10-38-11.txt'.
- 符号: astroid-error

#### 行 74, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 133, 列 0
- 类型: info
- 代码: I0011
- 描述: Locally disabling protected-access (W0212)
- 符号: locally-disabled

## 文件: src\battery_analysis\utils\word_utils.py

### 问题统计
- 问题总数: 9
- 信息(Info): 4
- 规范(Convention): 5

### 详细问题
#### 行 6, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import logging" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 6, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package logging are not grouped
- 符号: ungrouped-imports

#### 行 7, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from docx.oxml import OxmlElement" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 8, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from docx.oxml.ns import qn" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 9, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from docx.opc.constants import RELATIONSHIP_TYPE" should be placed at the top of the module
- 符号: wrong-import-position

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

## 文件: tests\battery_analysis\utils\test_file_writer.py

### 问题统计
- 问题总数: 68
- 重构(Refactor): 68

### 详细问题
#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis.i18n.__init__:[30:67]
==po_translator:[20:57]
        self.translations = {}
        self.current_locale = 'en'

    def parse_po_file(self, po_file_path):
        """Parse a .po file and extract translations"""
        translations = {}

        try:
            with open(po_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple regex-based parsing
            msgid_pattern = r'msgid\s+"([^"]*)"'
            msgstr_pattern = r'msgstr\s+"([^"]*)"'

            msgid_matches = list(re.finditer(msgid_pattern, content))
            msgstr_matches = list(re.finditer(msgstr_pattern, content))

            for i in range(min(len(msgid_matches), len(msgstr_matches))):
                msgid = msgid_matches[i].group(1)
                msgstr = msgstr_matches[i].group(1)

                # Skip empty msgid (header)
                if not msgid.strip():
                    continue

                translations[msgid] = msgstr

            logger.info("Parsed %s translations from %s", len(translations), po_file_path)
            return translations

        except Exception as e:
            logger.error("Error parsing %s: %s", po_file_path, e)
            return {}

    def load_locale(self, locale_code):
        """Load translations for a specific locale"""
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[207:235]
==modern_battery_viewer_refactored:[183:211]
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["折线图", "散点图", "面积图", "对比图"])
        self.chart_type_combo.currentTextChanged.connect(self._on_chart_type_changed)

        chart_type_layout.addWidget(chart_type_label)
        chart_type_layout.addWidget(self.chart_type_combo)

        # 显示选项
        self.show_filtered_checkbox = QCheckBox("显示过滤数据")
        self.show_filtered_checkbox.setChecked(True)
        self.show_filtered_checkbox.stateChanged.connect(self._on_display_option_changed)

        self.show_raw_checkbox = QCheckBox("显示原始数据")
        self.show_raw_checkbox.setChecked(False)
        self.show_raw_checkbox.stateChanged.connect(self._on_display_option_changed)

        self.show_grid_checkbox = QCheckBox("显示网格")
        self.show_grid_checkbox.setChecked(True)
        self.show_grid_checkbox.stateChanged.connect(self._on_display_option_changed)

        self.show_legend_checkbox = QCheckBox("显示图例")
        self.show_legend_checkbox.setChecked(True)
        self.show_legend_checkbox.stateChanged.connect(self._on_display_option_changed)

        # 电池选择
        battery_layout = QHBoxLayout()

        battery_label = QLabel("电池选择:")
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[51:79]
==modern_battery_viewer_refactored:[34:62]
    data_loaded = pyqtSignal(str)  # 数据加载完成信号
    visualization_changed = pyqtSignal(str)  # 可视化变化信号

    def __init__(self, data_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.colors = ModernColorScheme()
        self.data_path = data_path
        self.current_viewer = None
        self.chart_widget = None

        # 数据存储
        self.raw_data = {}
        self.processed_data = {}
        self.battery_names = []

        # UI组件
        self.tabs = None
        self.chart_area = None
        self.control_panel = None
        self.data_info_panel = None

        self._setup_ui()
        self._setup_menus()
        self._setup_toolbars()
        self._setup_statusbar()
        self._connect_signals()

        # 如果提供了数据路径，自动加载
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[237:266]
==modern_battery_viewer_refactored:[213:242]
        self.battery_filter_combo = QComboBox()
        self.battery_filter_combo.setEditable(True)
        self.battery_filter_combo.currentTextChanged.connect(self._on_battery_filter_changed)

        battery_layout.addWidget(battery_label)
        battery_layout.addWidget(self.battery_filter_combo)

        # 添加到布局
        layout.addLayout(chart_type_layout)
        layout.addWidget(self.show_filtered_checkbox)
        layout.addWidget(self.show_raw_checkbox)
        layout.addWidget(self.show_grid_checkbox)
        layout.addWidget(self.show_legend_checkbox)
        layout.addLayout(battery_layout)

        parent.addWidget(group)

    def _create_processing_control_group(self, parent):
        """创建数据处理控制组"""

        # 使用样式管理器创建主题化分组框
        group = create_styled_groupbox(self, "⚙️ 数据处理", "processing")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # 过滤参数
        filter_layout = QHBoxLayout()

        filter_label = QLabel("过滤强度:")
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[131:167]
==modern_battery_viewer_refactored:[104:140]
        control_frame.setMaximumWidth(350)
        control_frame.setMinimumWidth(300)

        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(12)

        # 数据加载控制
        self._create_data_control_group(control_layout)

        # 图表显示控制
        self._create_display_control_group(control_layout)

        # 数据处理控制
        self._create_processing_control_group(control_layout)

        # 数据信息面板
        self._create_data_info_panel(control_layout)

        # 添加弹簧
        control_layout.addStretch()

        parent.addWidget(control_frame)

    def _create_data_control_group(self, parent):
        """创建数据控制组"""

        # 使用样式管理器创建主题化分组框
        group = create_styled_groupbox(self, "📁 数据管理", "data")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)

        # 数据路径选择
        path_layout = QHBoxLayout()

        self.path_label = QLabel("数据路径:")
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[496:521]
==modern_battery_viewer_refactored:[480:506]
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择数据目录",
            self.path_combo.currentText() or ".",
            QFileDialog.Option.ShowDirsOnly
        )

        if directory:
            self.path_combo.setCurrentText(directory)

    @pyqtSlot()
    def load_data(self, data_path: Optional[str] = None):
        """加载数据"""

        if data_path is None:
            data_path = self.path_combo.currentText()

        if not data_path or not os.path.exists(data_path):
            QMessageBox.warning(self, "警告", "请选择有效的数据路径")
            return

        try:
            self.statusBar().showMessage('正在加载数据...')

            # 这里实现数据加载逻辑
            # 目前作为示例，只更新状态
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[103:130]
==modern_battery_viewer_refactored:[77:104]
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # 左侧控制面板
        self._create_control_panel(splitter)

        # 右侧图表区域
        self._create_chart_area(splitter)

        # 设置分割器比例
        splitter.setStretchFactor(0, 1)  # 控制面板
        splitter.setStretchFactor(1, 3)  # 图表区域

    def _create_control_panel(self, parent):
        """创建左侧控制面板"""

        control_frame = QFrame()
        control_frame.setObjectName("control_frame")
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis.i18n.__init__:[69:97]
==po_translator:[60:82]
        if not po_file.exists():
            logger.warning("Translation file not found: %s", po_file)
            return False

        self.translations = self.parse_po_file(po_file)
        self.current_locale = locale_code

        logger.info("Loaded %s translations for %s", len(self.translations), locale_code)
        return True

    def _(self, text: str, context: Optional[str] = None):
        """Get translation for text"""
        if context:
            # Handle context-aware translations if needed
            key = f"{context}:{text}"
        else:
            key = text

        return self.translations.get(key, text)


def get_available_locales() -> List[str]:
    """
    Get list of available locales with translation files.

    Returns:
        List of available locale codes
    """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[344:366]
==modern_battery_viewer_refactored:[322:344]
        self.chart_widget = ModernChartWidget()
        self.chart_widget.data_changed.connect(self._on_chart_data_changed)
        self.tabs.addTab(self.chart_widget, "📊 数据图表")

        # 分析标签页
        analysis_widget = self._create_analysis_widget()
        self.tabs.addTab(analysis_widget, "📈 数据分析")

        chart_layout.addWidget(self.tabs)

        parent.addWidget(chart_frame)

    def _create_analysis_widget(self):
        """创建分析面板"""

        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)

        # 分析控制
        analysis_control_layout = QHBoxLayout()

        analysis_type_label = QLabel("分析类型:")
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==idataprocessor:[72:219]
==interfaces.iuiframework:[38:173]
        pass

    @abstractmethod
    def create_main_window(self) -> Any:
        """创建主窗口

        Returns:
            Any: 主窗口实例
        """
        pass

    @abstractmethod
    def create_progress_dialog(self, parent: Optional[Any] = None) -> Any:
        """创建进度对话框

        Args:
            parent: 父窗口

        Returns:
            Any: 进度对话框实例
        """
        pass

    @abstractmethod
    def show_message_box(self,
                        parent: Optional[Any],
                        title: str,
                        message: str,
                        msg_type: MessageBoxType) -> Any:
        """显示消息框

        Args:
            parent: 父窗口
            title: 窗口标题
            message: 消息内容
            msg_type: 消息类型

        Returns:
            Any: 消息框实例
        """
        pass

    @abstractmethod
    def create_file_dialog(self,
                          parent: Optional[Any],
                          caption: str,
                          directory: str = "",
                          filter_pattern: str = "") -> Any:
        """创建文件选择对话框

        Args:
            parent: 父窗口
            caption: 对话框标题
            directory: 默认目录
            filter_pattern: 文件过滤器

        Returns:
            Any: 文件对话框实例
        """
        pass

    @abstractmethod
    def create_label(self, parent: Any, text: str) -> Any:
        """创建标签控件

        Args:
            parent: 父控件
            text: 标签文本

        Returns:
            Any: 标签控件实例
        """
        pass

    @abstractmethod
    def create_button(self, parent: Any, text: str) -> Any:
        """创建按钮控件

        Args:
            parent: 父控件
            text: 按钮文本

        Returns:
            Any: 按钮控件实例
        """
        pass

    @abstractmethod
    def create_input_field(self, parent: Any, placeholder: str = "") -> Any:
        """创建输入框控件

        Args:
            parent: 父控件
            placeholder: 占位符文本

        Returns:
            Any: 输入框控件实例
        """
        pass

    @abstractmethod
    def create_table_widget(self, parent: Any, rows: int, columns: int) -> Any:
        """创建表格控件

        Args:
            parent: 父控件
            rows: 行数
            columns: 列数

        Returns:
            Any: 表格控件实例
        """
        pass

    @abstractmethod
    def set_layout(self, parent: Any, layout: Any) -> None:
        """设置布局管理器

        Args:
            parent: 父控件
            layout: 布局管理器
        """
        pass

    @abstractmethod
    def exec_application(self, app: Any) -> int:
        """运行应用程序

        Args:
            app: 应用程序实例

        Returns:
            int: 退出代码
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[31:176]
==idataprocessor:[60:206]
        pass

    @abstractmethod
    def analyze_battery_performance(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析电池性能

        Args:
            data: 电池数据列表

        Returns:
            Dict[str, Any]: 分析结果
        """
        pass

    @abstractmethod
    def calculate_statistics(self, data: List[Union[float, int]],
                           statistics: List[str] = None) -> Dict[str, float]:
        """
        计算统计数据

        Args:
            data: 数据列表
            statistics: 统计类型列表（如["mean", "std", "min", "max"]）

        Returns:
            Dict[str, float]: 统计数据
        """
        pass

    @abstractmethod
    def smooth_data(self, data: List[float], method: str = "moving_average",
                   window_size: int = 5) -> List[float]:
        """
        数据平滑处理

        Args:
            data: 原始数据
            method: 平滑方法（"moving_average", "gaussian", "savgol"）
            window_size: 窗口大小

        Returns:
            List[float]: 平滑后的数据
        """
        pass

    @abstractmethod
    def detect_outliers(self, data: List[Union[float, int]],
                       method: str = "iqr") -> List[int]:
        """
        检测异常值

        Args:
            data: 数据列表
            method: 检测方法（"iqr", "zscore", "isolation_forest"）

        Returns:
            List[int]: 异常值的索引列表
        """
        pass

    @abstractmethod
    def generate_mock_data(self, battery_count: int = 1,
                          data_points: int = 100) -> List[Dict[str, Any]]:
        """
        生成模拟电池数据

        Args:
            battery_count: 电池数量
            data_points: 数据点数量

        Returns:
            List[Dict[str, Any]]: 模拟数据
        """
        pass

    @abstractmethod
    def validate_data_integrity(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证数据完整性

        Args:
            data: 待验证的数据

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        pass

    @abstractmethod
    def process_csv_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        处理CSV数据文件

        Args:
            csv_path: CSV文件路径

        Returns:
            List[Dict[str, Any]]: 解析后的数据
        """
        pass

    @abstractmethod
    def export_processed_data(self, data: List[Dict[str, Any]],
                            output_path: str, format: str = "csv") -> bool:
        """
        导出处理后的数据

        Args:
            data: 要导出的数据
            output_path: 输出文件路径
            format: 导出格式（"csv", "json", "excel"）

        Returns:
            bool: 导出是否成功
        """
        pass

    @abstractmethod
    def merge_battery_data(self, data_list: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        合并多个电池数据集

        Args:
            data_list: 数据集列表

        Returns:
            List[Dict[str, Any]]: 合并后的数据
        """
        pass

    @abstractmethod
    def extract_features(self, data: List[Dict[str, Any]],
                        feature_types: List[str]) -> Dict[str, Any]:
        """
        提取数据特征

        Args:
            data: 原始数据
            feature_types: 特征类型列表

        Returns:
            Dict[str, Any]: 提取的特征
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[46:160]
==idataprocessor:[45:193]
        pass

    @abstractmethod
    def save_data(self, data: Any, file_path: str, format: DataFormat, **kwargs) -> bool:
        """保存数据文件

        Args:
            data: 数据对象
            file_path: 保存路径
            format: 数据格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def create_dataframe(self, data: Optional[Union[Dict, List, Any]] = None) -> Any:
        """创建数据框

        Args:
            data: 初始数据

        Returns:
            Any: 数据框对象
        """
        pass

    @abstractmethod
    def filter_data(self, data: Any, conditions: Dict[str, Any]) -> Any:
        """过滤数据

        Args:
            data: 数据对象
            conditions: 过滤条件

        Returns:
            Any: 过滤后的数据
        """
        pass

    @abstractmethod
    def group_data(self, data: Any, by: Union[str, List[str]]) -> Any:
        """分组数据

        Args:
            data: 数据对象
            by: 分组字段

        Returns:
            Any: 分组后的数据
        """
        pass

    @abstractmethod
    def aggregate_data(self, data: Any, aggregations: Dict[str, Dict[str, str]]) -> Any:
        """聚合数据

        Args:
            data: 数据对象
            aggregations: 聚合规则

        Returns:
            Any: 聚合后的数据
        """
        pass

    @abstractmethod
    def sort_data(self, data: Any, by: Union[str, List[str]], ascending: bool = True) -> Any:
        """排序数据

        Args:
            data: 数据对象
            by: 排序字段
            ascending: 是否升序

        Returns:
            Any: 排序后的数据
        """
        pass

    @abstractmethod
    def merge_data(self, left: Any, right: Any, on: Union[str, List[str]], how: str = "inner") -> Any:
        """合并数据

        Args:
            left: 左数据
            right: 右数据
            on: 合并字段
            how: 合并方式

        Returns:
            Any: 合并后的数据
        """
        pass

    @abstractmethod
    def get_column_names(self, data: Any) -> List[str]:
        """获取列名

        Args:
            data: 数据对象

        Returns:
            List[str]: 列名列表
        """
        pass

    @abstractmethod
    def get_column_data(self, data: Any, column: str) -> Any:
        """获取列数据

        Args:
            data: 数据对象
            column: 列名

        Returns:
            Any: 列数据
        """
        pass

    @abstractmethod
    def set_column_data(self, data: Any, column: str, values: Any) -> bool:
        """设置列数据

        Args:
            data: 数据对象
            column: 列名
            values: 新数据

        Returns:
            bool: 是否设置成功
        """
        pass

    @abstractmethod
    def convert_data_type(self, data: Any, column: str, data_type: DataType) -> bool:
        """转换数据类型

        Args:
            data: 数据对象
            column: 列名
            data_type: 目标类型

        Returns:
            bool: 是否转换成功
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[376:397]
==modern_battery_viewer_refactored:[358:379]
        analysis_control_layout.addWidget(analysis_type_label)
        analysis_control_layout.addWidget(self.analysis_type_combo)
        analysis_control_layout.addWidget(self.run_analysis_button)

        # 分析结果
        self.analysis_result_text = QTextEdit()
        self.analysis_result_text.setReadOnly(True)

        layout.addLayout(analysis_control_layout)
        layout.addWidget(self.analysis_result_text)

        return analysis_widget

    def _setup_menus(self):
        """设置菜单栏"""

        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')

- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[44:176]
==interfaces.iuiframework:[38:172]
        pass

    @abstractmethod
    def create_main_window(self) -> Any:
        """创建主窗口

        Returns:
            Any: 主窗口实例
        """
        pass

    @abstractmethod
    def create_progress_dialog(self, parent: Optional[Any] = None) -> Any:
        """创建进度对话框

        Args:
            parent: 父窗口

        Returns:
            Any: 进度对话框实例
        """
        pass

    @abstractmethod
    def show_message_box(self,
                        parent: Optional[Any],
                        title: str,
                        message: str,
                        msg_type: MessageBoxType) -> Any:
        """显示消息框

        Args:
            parent: 父窗口
            title: 窗口标题
            message: 消息内容
            msg_type: 消息类型

        Returns:
            Any: 消息框实例
        """
        pass

    @abstractmethod
    def create_file_dialog(self,
                          parent: Optional[Any],
                          caption: str,
                          directory: str = "",
                          filter_pattern: str = "") -> Any:
        """创建文件选择对话框

        Args:
            parent: 父窗口
            caption: 对话框标题
            directory: 默认目录
            filter_pattern: 文件过滤器

        Returns:
            Any: 文件对话框实例
        """
        pass

    @abstractmethod
    def create_label(self, parent: Any, text: str) -> Any:
        """创建标签控件

        Args:
            parent: 父控件
            text: 标签文本

        Returns:
            Any: 标签控件实例
        """
        pass

    @abstractmethod
    def create_button(self, parent: Any, text: str) -> Any:
        """创建按钮控件

        Args:
            parent: 父控件
            text: 按钮文本

        Returns:
            Any: 按钮控件实例
        """
        pass

    @abstractmethod
    def create_input_field(self, parent: Any, placeholder: str = "") -> Any:
        """创建输入框控件

        Args:
            parent: 父控件
            placeholder: 占位符文本

        Returns:
            Any: 输入框控件实例
        """
        pass

    @abstractmethod
    def create_table_widget(self, parent: Any, rows: int, columns: int) -> Any:
        """创建表格控件

        Args:
            parent: 父控件
            rows: 行数
            columns: 列数

        Returns:
            Any: 表格控件实例
        """
        pass

    @abstractmethod
    def set_layout(self, parent: Any, layout: Any) -> None:
        """设置布局管理器

        Args:
            parent: 父控件
            layout: 布局管理器
        """
        pass

    @abstractmethod
    def exec_application(self, app: Any) -> int:
        """运行应用程序

        Args:
            app: 应用程序实例

        Returns:
            int: 退出代码
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[31:175]
==interfaces.iuiframework:[47:173]
        pass

    @abstractmethod
    def analyze_battery_performance(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析电池性能

        Args:
            data: 电池数据列表

        Returns:
            Dict[str, Any]: 分析结果
        """
        pass

    @abstractmethod
    def calculate_statistics(self, data: List[Union[float, int]],
                           statistics: List[str] = None) -> Dict[str, float]:
        """
        计算统计数据

        Args:
            data: 数据列表
            statistics: 统计类型列表（如["mean", "std", "min", "max"]）

        Returns:
            Dict[str, float]: 统计数据
        """
        pass

    @abstractmethod
    def smooth_data(self, data: List[float], method: str = "moving_average",
                   window_size: int = 5) -> List[float]:
        """
        数据平滑处理

        Args:
            data: 原始数据
            method: 平滑方法（"moving_average", "gaussian", "savgol"）
            window_size: 窗口大小

        Returns:
            List[float]: 平滑后的数据
        """
        pass

    @abstractmethod
    def detect_outliers(self, data: List[Union[float, int]],
                       method: str = "iqr") -> List[int]:
        """
        检测异常值

        Args:
            data: 数据列表
            method: 检测方法（"iqr", "zscore", "isolation_forest"）

        Returns:
            List[int]: 异常值的索引列表
        """
        pass

    @abstractmethod
    def generate_mock_data(self, battery_count: int = 1,
                          data_points: int = 100) -> List[Dict[str, Any]]:
        """
        生成模拟电池数据

        Args:
            battery_count: 电池数量
            data_points: 数据点数量

        Returns:
            List[Dict[str, Any]]: 模拟数据
        """
        pass

    @abstractmethod
    def validate_data_integrity(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证数据完整性

        Args:
            data: 待验证的数据

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        pass

    @abstractmethod
    def process_csv_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        处理CSV数据文件

        Args:
            csv_path: CSV文件路径

        Returns:
            List[Dict[str, Any]]: 解析后的数据
        """
        pass

    @abstractmethod
    def export_processed_data(self, data: List[Dict[str, Any]],
                            output_path: str, format: str = "csv") -> bool:
        """
        导出处理后的数据

        Args:
            data: 要导出的数据
            output_path: 输出文件路径
            format: 导出格式（"csv", "json", "excel"）

        Returns:
            bool: 导出是否成功
        """
        pass

    @abstractmethod
    def merge_battery_data(self, data_list: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        合并多个电池数据集

        Args:
            data_list: 数据集列表

        Returns:
            List[Dict[str, Any]]: 合并后的数据
        """
        pass

    @abstractmethod
    def extract_features(self, data: List[Dict[str, Any]],
                        feature_types: List[str]) -> Dict[str, Any]:
        """
        提取数据特征

        Args:
            data: 原始数据
            feature_types: 特征类型列表

        Returns:
            Dict[str, Any]: 提取的特征
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==file_service_interface:[29:152]
==idataprocessor:[72:206]
        pass

    @abstractmethod
    def delete_directory(self, path: Union[str, Path], recursive: bool = False) -> Tuple[bool, str]:
        """
        删除目录

        Args:
            path: 目录路径
            recursive: 是否递归删除

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def list_files(self, directory: Union[str, Path], pattern: Optional[str] = None) -> List[str]:
        """
        列出目录中的文件

        Args:
            directory: 目录路径
            pattern: 文件名模式

        Returns:
            List[str]: 文件名列表
        """
        pass

    @abstractmethod
    def get_file_size(self, file_path: Union[str, Path]) -> Optional[int]:
        """
        获取文件大小

        Args:
            file_path: 文件路径

        Returns:
            Optional[int]: 文件大小，失败返回None
        """
        pass

    @abstractmethod
    def set_file_attributes(self, file_path: Union[str, Path], attributes: dict) -> Tuple[bool, str]:
        """
        设置文件属性

        Args:
            file_path: 文件路径
            attributes: 属性字典

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def hide_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        隐藏文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def is_file_hidden(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否隐藏

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否隐藏
        """
        pass

    @abstractmethod
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        复制文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        移动文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==document_service_interface:[29:170]
==idataprocessor:[60:193]
        pass

    @abstractmethod
    def save_word_document(self, document: Any, output_path: str) -> bool:
        """
        保存Word文档

        Args:
            document: Word文档对象
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def add_table_to_word(self, document: Any, table_data: List[List[str]],
                         table_style: Optional[str] = None) -> bool:
        """
        向Word文档添加表格

        Args:
            document: Word文档对象
            table_data: 表格数据，二维列表
            table_style: 表格样式

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def add_image_to_word(self, document: Any, image_path: str,
                         width: Optional[float] = None) -> bool:
        """
        向Word文档添加图片

        Args:
            document: Word文档对象
            image_path: 图片文件路径
            width: 图片宽度

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def create_excel_workbook(self, template_path: Optional[str] = None) -> Any:
        """
        创建Excel工作簿

        Args:
            template_path: Excel模板文件路径

        Returns:
            Any: Excel工作簿对象
        """
        pass

    @abstractmethod
    def save_excel_workbook(self, workbook: Any, output_path: str) -> bool:
        """
        保存Excel工作簿

        Args:
            workbook: Excel工作簿对象
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def add_sheet_to_excel(self, workbook: Any, sheet_name: str, data: List[List[Any]]) -> bool:
        """
        向Excel工作簿添加工作表

        Args:
            workbook: Excel工作簿对象
            sheet_name: 工作表名称
            data: 工作表数据

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def set_cell_style(self, worksheet: Any, row: int, col: int,
                      font_name: Optional[str] = None, font_size: Optional[int] = None,
                      bold: Optional[bool] = None, background_color: Optional[str] = None) -> bool:
        """
        设置单元格样式

        Args:
            worksheet: Excel工作表对象
            row: 行号
            col: 列号
            font_name: 字体名称
            font_size: 字体大小
            bold: 是否加粗
            background_color: 背景色

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def generate_report(self, report_type: str, data: Dict[str, Any],
                       output_path: str, template_path: Optional[str] = None) -> bool:
        """
        生成报告

        Args:
            report_type: 报告类型（如"word", "excel"）
            data: 报告数据
            output_path: 输出文件路径
            template_path: 模板文件路径

        Returns:
            bool: 生成是否成功
        """
        pass

    @abstractmethod
    def set_cell_background_color(self, cell: Any, color: str) -> bool:
        """
        设置单元格背景色

        Args:
            cell: 单元格对象
            color: 颜色值（十六进制或颜色名称）

        Returns:
            bool: 设置是否成功
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[59:160]
==idataprocessor:[45:179]
        pass

    @abstractmethod
    def set_chart_title(self, chart: Any, title: str) -> None:
        """设置图表标题

        Args:
            chart: 图表实例
            title: 标题文本
        """
        pass

    @abstractmethod
    def set_axis_labels(self, chart: Any, x_label: str, y_label: str) -> None:
        """设置坐标轴标签

        Args:
            chart: 图表实例
            x_label: X轴标签
            y_label: Y轴标签
        """
        pass

    @abstractmethod
    def add_legend(self, chart: Any) -> None:
        """添加图例

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def save_chart(self, chart: Any, file_path: str, format: ChartFormat = ChartFormat.PNG, **kwargs) -> bool:
        """保存图表

        Args:
            chart: 图表实例
            file_path: 保存路径
            format: 保存格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def show_chart(self, chart: Any) -> bool:
        """显示图表

        Args:
            chart: 图表实例

        Returns:
            bool: 是否显示成功
        """
        pass

    @abstractmethod
    def close_chart(self, chart: Any) -> None:
        """关闭图表

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def create_subplot(self, rows: int, columns: int, index: int = 1) -> Any:
        """创建子图

        Args:
            rows: 行数
            columns: 列数
            index: 子图索引

        Returns:
            Any: 子图实例
        """
        pass

    @abstractmethod
    def set_grid(self, chart: Any, show: bool = True) -> None:
        """设置网格

        Args:
            chart: 图表实例
            show: 是否显示网格
        """
        pass

    @abstractmethod
    def set_colors(self, chart: Any, colors: List[str]) -> None:
        """设置颜色

        Args:
            chart: 图表实例
            colors: 颜色列表
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[46:159]
==idataprocessor:[98:220]
        pass

    @abstractmethod
    def set_chart_data(self, chart: Any, data: Dict[str, Any]) -> bool:
        """设置图表数据

        Args:
            chart: 图表实例
            data: 数据字典

        Returns:
            bool: 是否设置成功
        """
        pass

    @abstractmethod
    def set_chart_title(self, chart: Any, title: str) -> None:
        """设置图表标题

        Args:
            chart: 图表实例
            title: 标题文本
        """
        pass

    @abstractmethod
    def set_axis_labels(self, chart: Any, x_label: str, y_label: str) -> None:
        """设置坐标轴标签

        Args:
            chart: 图表实例
            x_label: X轴标签
            y_label: Y轴标签
        """
        pass

    @abstractmethod
    def add_legend(self, chart: Any) -> None:
        """添加图例

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def save_chart(self, chart: Any, file_path: str, format: ChartFormat = ChartFormat.PNG, **kwargs) -> bool:
        """保存图表

        Args:
            chart: 图表实例
            file_path: 保存路径
            format: 保存格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def show_chart(self, chart: Any) -> bool:
        """显示图表

        Args:
            chart: 图表实例

        Returns:
            bool: 是否显示成功
        """
        pass

    @abstractmethod
    def close_chart(self, chart: Any) -> None:
        """关闭图表

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def create_subplot(self, rows: int, columns: int, index: int = 1) -> Any:
        """创建子图

        Args:
            rows: 行数
            columns: 列数
            index: 子图索引

        Returns:
            Any: 子图实例
        """
        pass

    @abstractmethod
    def set_grid(self, chart: Any, show: bool = True) -> None:
        """设置网格

        Args:
            chart: 图表实例
            show: 是否显示网格
        """
        pass

    @abstractmethod
    def set_colors(self, chart: Any, colors: List[str]) -> None:
        """设置颜色

        Args:
            chart: 图表实例
            colors: 颜色列表
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[169:182]
==modern_battery_viewer_refactored:[142:155]
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.setMinimumWidth(150)

        self.browse_button = QPushButton("浏览")
        self.browse_button.setMaximumWidth(60)
        self.browse_button.clicked.connect(self._browse_data_path)

        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_combo)
        path_layout.addWidget(self.browse_button)

        # 加载按钮 - 使用样式管理器创建
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==file_service_interface:[43:152]
==interfaces.iuiframework:[38:160]
        pass

    @abstractmethod
    def list_files(self, directory: Union[str, Path], pattern: Optional[str] = None) -> List[str]:
        """
        列出目录中的文件

        Args:
            directory: 目录路径
            pattern: 文件名模式

        Returns:
            List[str]: 文件名列表
        """
        pass

    @abstractmethod
    def get_file_size(self, file_path: Union[str, Path]) -> Optional[int]:
        """
        获取文件大小

        Args:
            file_path: 文件路径

        Returns:
            Optional[int]: 文件大小，失败返回None
        """
        pass

    @abstractmethod
    def set_file_attributes(self, file_path: Union[str, Path], attributes: dict) -> Tuple[bool, str]:
        """
        设置文件属性

        Args:
            file_path: 文件路径
            attributes: 属性字典

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def hide_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        隐藏文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def is_file_hidden(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否隐藏

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否隐藏
        """
        pass

    @abstractmethod
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        复制文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        移动文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==file_service_interface:[29:151]
==interfaces.iuiframework:[59:173]
        pass

    @abstractmethod
    def show_message_box(self,
                        parent: Optional[Any],
                        title: str,
                        message: str,
                        msg_type: MessageBoxType) -> Any:
        """显示消息框

        Args:
            parent: 父窗口
            title: 窗口标题
            message: 消息内容
            msg_type: 消息类型

        Returns:
            Any: 消息框实例
        """
        pass

    @abstractmethod
    def create_file_dialog(self,
                          parent: Optional[Any],
                          caption: str,
                          directory: str = "",
                          filter_pattern: str = "") -> Any:
        """创建文件选择对话框

        Args:
            parent: 父窗口
            caption: 对话框标题
            directory: 默认目录
            filter_pattern: 文件过滤器

        Returns:
            Any: 文件对话框实例
        """
        pass

    @abstractmethod
    def create_label(self, parent: Any, text: str) -> Any:
        """创建标签控件

        Args:
            parent: 父控件
            text: 标签文本

        Returns:
            Any: 标签控件实例
        """
        pass

    @abstractmethod
    def create_button(self, parent: Any, text: str) -> Any:
        """创建按钮控件

        Args:
            parent: 父控件
            text: 按钮文本

        Returns:
            Any: 按钮控件实例
        """
        pass

    @abstractmethod
    def create_input_field(self, parent: Any, placeholder: str = "") -> Any:
        """创建输入框控件

        Args:
            parent: 父控件
            placeholder: 占位符文本

        Returns:
            Any: 输入框控件实例
        """
        pass

    @abstractmethod
    def create_table_widget(self, parent: Any, rows: int, columns: int) -> Any:
        """创建表格控件

        Args:
            parent: 父控件
            rows: 行数
            columns: 列数

        Returns:
            Any: 表格控件实例
        """
        pass

    @abstractmethod
    def set_layout(self, parent: Any, layout: Any) -> None:
        """设置布局管理器

        Args:
            parent: 父控件
            layout: 布局管理器
        """
        pass

    @abstractmethod
    def exec_application(self, app: Any) -> int:
        """运行应用程序

        Args:
            app: 应用程序实例

        Returns:
            int: 退出代码
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[59:176]
==document_service_interface:[29:169]
        pass

    @abstractmethod
    def save_word_document(self, document: Any, output_path: str) -> bool:
        """
        保存Word文档

        Args:
            document: Word文档对象
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def add_table_to_word(self, document: Any, table_data: List[List[str]],
                         table_style: Optional[str] = None) -> bool:
        """
        向Word文档添加表格

        Args:
            document: Word文档对象
            table_data: 表格数据，二维列表
            table_style: 表格样式

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def add_image_to_word(self, document: Any, image_path: str,
                         width: Optional[float] = None) -> bool:
        """
        向Word文档添加图片

        Args:
            document: Word文档对象
            image_path: 图片文件路径
            width: 图片宽度

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def create_excel_workbook(self, template_path: Optional[str] = None) -> Any:
        """
        创建Excel工作簿

        Args:
            template_path: Excel模板文件路径

        Returns:
            Any: Excel工作簿对象
        """
        pass

    @abstractmethod
    def save_excel_workbook(self, workbook: Any, output_path: str) -> bool:
        """
        保存Excel工作簿

        Args:
            workbook: Excel工作簿对象
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def add_sheet_to_excel(self, workbook: Any, sheet_name: str, data: List[List[Any]]) -> bool:
        """
        向Excel工作簿添加工作表

        Args:
            workbook: Excel工作簿对象
            sheet_name: 工作表名称
            data: 工作表数据

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def set_cell_style(self, worksheet: Any, row: int, col: int,
                      font_name: Optional[str] = None, font_size: Optional[int] = None,
                      bold: Optional[bool] = None, background_color: Optional[str] = None) -> bool:
        """
        设置单元格样式

        Args:
            worksheet: Excel工作表对象
            row: 行号
            col: 列号
            font_name: 字体名称
            font_size: 字体大小
            bold: 是否加粗
            background_color: 背景色

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def generate_report(self, report_type: str, data: Dict[str, Any],
                       output_path: str, template_path: Optional[str] = None) -> bool:
        """
        生成报告

        Args:
            report_type: 报告类型（如"word", "excel"）
            data: 报告数据
            output_path: 输出文件路径
            template_path: 模板文件路径

        Returns:
            bool: 生成是否成功
        """
        pass

    @abstractmethod
    def set_cell_background_color(self, cell: Any, color: str) -> bool:
        """
        设置单元格背景色

        Args:
            cell: 单元格对象
            color: 颜色值（十六进制或颜色名称）

        Returns:
            bool: 设置是否成功
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[31:160]
==document_service_interface:[43:170]
        pass

    @abstractmethod
    def add_table_to_word(self, document: Any, table_data: List[List[str]],
                         table_style: Optional[str] = None) -> bool:
        """
        向Word文档添加表格

        Args:
            document: Word文档对象
            table_data: 表格数据，二维列表
            table_style: 表格样式

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def add_image_to_word(self, document: Any, image_path: str,
                         width: Optional[float] = None) -> bool:
        """
        向Word文档添加图片

        Args:
            document: Word文档对象
            image_path: 图片文件路径
            width: 图片宽度

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def create_excel_workbook(self, template_path: Optional[str] = None) -> Any:
        """
        创建Excel工作簿

        Args:
            template_path: Excel模板文件路径

        Returns:
            Any: Excel工作簿对象
        """
        pass

    @abstractmethod
    def save_excel_workbook(self, workbook: Any, output_path: str) -> bool:
        """
        保存Excel工作簿

        Args:
            workbook: Excel工作簿对象
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def add_sheet_to_excel(self, workbook: Any, sheet_name: str, data: List[List[Any]]) -> bool:
        """
        向Excel工作簿添加工作表

        Args:
            workbook: Excel工作簿对象
            sheet_name: 工作表名称
            data: 工作表数据

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def set_cell_style(self, worksheet: Any, row: int, col: int,
                      font_name: Optional[str] = None, font_size: Optional[int] = None,
                      bold: Optional[bool] = None, background_color: Optional[str] = None) -> bool:
        """
        设置单元格样式

        Args:
            worksheet: Excel工作表对象
            row: 行号
            col: 列号
            font_name: 字体名称
            font_size: 字体大小
            bold: 是否加粗
            background_color: 背景色

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def generate_report(self, report_type: str, data: Dict[str, Any],
                       output_path: str, template_path: Optional[str] = None) -> bool:
        """
        生成报告

        Args:
            report_type: 报告类型（如"word", "excel"）
            data: 报告数据
            output_path: 输出文件路径
            template_path: 模板文件路径

        Returns:
            bool: 生成是否成功
        """
        pass

    @abstractmethod
    def set_cell_background_color(self, cell: Any, color: str) -> bool:
        """
        设置单元格背景色

        Args:
            cell: 单元格对象
            color: 颜色值（十六进制或颜色名称）

        Returns:
            bool: 设置是否成功
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[69:160]
==idataprocessor:[45:165]
        pass

    @abstractmethod
    def save_data(self, data: Any, file_path: str, format: DataFormat, **kwargs) -> bool:
        """保存数据文件

        Args:
            data: 数据对象
            file_path: 保存路径
            format: 数据格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def create_dataframe(self, data: Optional[Union[Dict, List, Any]] = None) -> Any:
        """创建数据框

        Args:
            data: 初始数据

        Returns:
            Any: 数据框对象
        """
        pass

    @abstractmethod
    def filter_data(self, data: Any, conditions: Dict[str, Any]) -> Any:
        """过滤数据

        Args:
            data: 数据对象
            conditions: 过滤条件

        Returns:
            Any: 过滤后的数据
        """
        pass

    @abstractmethod
    def group_data(self, data: Any, by: Union[str, List[str]]) -> Any:
        """分组数据

        Args:
            data: 数据对象
            by: 分组字段

        Returns:
            Any: 分组后的数据
        """
        pass

    @abstractmethod
    def aggregate_data(self, data: Any, aggregations: Dict[str, Dict[str, str]]) -> Any:
        """聚合数据

        Args:
            data: 数据对象
            aggregations: 聚合规则

        Returns:
            Any: 聚合后的数据
        """
        pass

    @abstractmethod
    def sort_data(self, data: Any, by: Union[str, List[str]], ascending: bool = True) -> Any:
        """排序数据

        Args:
            data: 数据对象
            by: 排序字段
            ascending: 是否升序

        Returns:
            Any: 排序后的数据
        """
        pass

    @abstractmethod
    def merge_data(self, left: Any, right: Any, on: Union[str, List[str]], how: str = "inner") -> Any:
        """合并数据

        Args:
            left: 左数据
            right: 右数据
            on: 合并字段
            how: 合并方式

        Returns:
            Any: 合并后的数据
        """
        pass

    @abstractmethod
    def get_column_names(self, data: Any) -> List[str]:
        """获取列名

        Args:
            data: 数据对象

        Returns:
            List[str]: 列名列表
        """
        pass

    @abstractmethod
    def get_column_data(self, data: Any, column: str) -> Any:
        """获取列数据

        Args:
            data: 数据对象
            column: 列名

        Returns:
            Any: 列数据
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[46:149]
==idataprocessor:[111:220]
        pass

    @abstractmethod
    def sort_data(self, data: Any, by: Union[str, List[str]], ascending: bool = True) -> Any:
        """排序数据

        Args:
            data: 数据对象
            by: 排序字段
            ascending: 是否升序

        Returns:
            Any: 排序后的数据
        """
        pass

    @abstractmethod
    def merge_data(self, left: Any, right: Any, on: Union[str, List[str]], how: str = "inner") -> Any:
        """合并数据

        Args:
            left: 左数据
            right: 右数据
            on: 合并字段
            how: 合并方式

        Returns:
            Any: 合并后的数据
        """
        pass

    @abstractmethod
    def get_column_names(self, data: Any) -> List[str]:
        """获取列名

        Args:
            data: 数据对象

        Returns:
            List[str]: 列名列表
        """
        pass

    @abstractmethod
    def get_column_data(self, data: Any, column: str) -> Any:
        """获取列数据

        Args:
            data: 数据对象
            column: 列名

        Returns:
            Any: 列数据
        """
        pass

    @abstractmethod
    def set_column_data(self, data: Any, column: str, values: Any) -> bool:
        """设置列数据

        Args:
            data: 数据对象
            column: 列名
            values: 新数据

        Returns:
            bool: 是否设置成功
        """
        pass

    @abstractmethod
    def convert_data_type(self, data: Any, column: str, data_type: DataType) -> bool:
        """转换数据类型

        Args:
            data: 数据对象
            column: 列名
            data_type: 目标类型

        Returns:
            bool: 是否转换成功
        """
        pass

    @abstractmethod
    def get_statistics(self, data: Any, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """获取统计信息

        Args:
            data: 数据对象
            columns: 指定列（None表示所有列）

        Returns:
            Dict[str, Any]: 统计信息
        """
        pass

    @abstractmethod
    def handle_missing_values(self, data: Any, strategy: str = "drop") -> Any:
        """处理缺失值

        Args:
            data: 数据对象
            strategy: 处理策略（drop、fill、interpolate等）

        Returns:
            Any: 处理后的数据
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[326:341]
==modern_battery_viewer_refactored:[305:322]
        layout.addWidget(self.data_status_label)
        layout.addWidget(self.data_details_text)
        layout.addWidget(self.stats_label)

        parent.addWidget(group)

    def _create_chart_area(self, parent):
        """创建右侧图表区域"""

        chart_frame = QFrame()
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(5, 5, 5, 5)

        # 标签页控件
        self.tabs = QTabWidget()

        # 图表标签页
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[268:280]
==modern_battery_viewer_refactored:[244:256]
        self.filter_strength_spinbox = QSpinBox()
        self.filter_strength_spinbox.setRange(1, 10)
        self.filter_strength_spinbox.setValue(3)
        self.filter_strength_spinbox.valueChanged.connect(self._on_filter_parameter_changed)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_strength_spinbox)

        # 采样间隔
        sampling_layout = QHBoxLayout()

        sampling_label = QLabel("采样间隔:")
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[188:205]
==modern_battery_viewer_refactored:[164:181]
        layout.addLayout(path_layout)
        layout.addWidget(self.load_button)

        parent.addWidget(group)

    def _create_display_control_group(self, parent):
        """创建显示控制组"""

        # 使用样式管理器创建主题化分组框
        group = create_styled_groupbox(self, "🎨 显示控制", "display")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # 图表类型
        chart_type_layout = QHBoxLayout()

        chart_type_label = QLabel("图表类型:")
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==file_service_interface:[57:152]
==interfaces.iuiframework:[38:150]
        pass

    @abstractmethod
    def get_file_size(self, file_path: Union[str, Path]) -> Optional[int]:
        """
        获取文件大小

        Args:
            file_path: 文件路径

        Returns:
            Optional[int]: 文件大小，失败返回None
        """
        pass

    @abstractmethod
    def set_file_attributes(self, file_path: Union[str, Path], attributes: dict) -> Tuple[bool, str]:
        """
        设置文件属性

        Args:
            file_path: 文件路径
            attributes: 属性字典

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def hide_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        隐藏文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def is_file_hidden(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否隐藏

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否隐藏
        """
        pass

    @abstractmethod
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        复制文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        移动文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==file_service_interface:[29:138]
==interfaces.iuiframework:[78:173]
        pass

    @abstractmethod
    def delete_directory(self, path: Union[str, Path], recursive: bool = False) -> Tuple[bool, str]:
        """
        删除目录

        Args:
            path: 目录路径
            recursive: 是否递归删除

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def list_files(self, directory: Union[str, Path], pattern: Optional[str] = None) -> List[str]:
        """
        列出目录中的文件

        Args:
            directory: 目录路径
            pattern: 文件名模式

        Returns:
            List[str]: 文件名列表
        """
        pass

    @abstractmethod
    def get_file_size(self, file_path: Union[str, Path]) -> Optional[int]:
        """
        获取文件大小

        Args:
            file_path: 文件路径

        Returns:
            Optional[int]: 文件大小，失败返回None
        """
        pass

    @abstractmethod
    def set_file_attributes(self, file_path: Union[str, Path], attributes: dict) -> Tuple[bool, str]:
        """
        设置文件属性

        Args:
            file_path: 文件路径
            attributes: 属性字典

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def hide_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        隐藏文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def is_file_hidden(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否隐藏

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否隐藏
        """
        pass

    @abstractmethod
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        复制文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        移动文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[75:176]
==document_service_interface:[29:155]
        pass

    @abstractmethod
    def detect_outliers(self, data: List[Union[float, int]],
                       method: str = "iqr") -> List[int]:
        """
        检测异常值

        Args:
            data: 数据列表
            method: 检测方法（"iqr", "zscore", "isolation_forest"）

        Returns:
            List[int]: 异常值的索引列表
        """
        pass

    @abstractmethod
    def generate_mock_data(self, battery_count: int = 1,
                          data_points: int = 100) -> List[Dict[str, Any]]:
        """
        生成模拟电池数据

        Args:
            battery_count: 电池数量
            data_points: 数据点数量

        Returns:
            List[Dict[str, Any]]: 模拟数据
        """
        pass

    @abstractmethod
    def validate_data_integrity(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证数据完整性

        Args:
            data: 待验证的数据

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        pass

    @abstractmethod
    def process_csv_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        处理CSV数据文件

        Args:
            csv_path: CSV文件路径

        Returns:
            List[Dict[str, Any]]: 解析后的数据
        """
        pass

    @abstractmethod
    def export_processed_data(self, data: List[Dict[str, Any]],
                            output_path: str, format: str = "csv") -> bool:
        """
        导出处理后的数据

        Args:
            data: 要导出的数据
            output_path: 输出文件路径
            format: 导出格式（"csv", "json", "excel"）

        Returns:
            bool: 导出是否成功
        """
        pass

    @abstractmethod
    def merge_battery_data(self, data_list: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        合并多个电池数据集

        Args:
            data_list: 数据集列表

        Returns:
            List[Dict[str, Any]]: 合并后的数据
        """
        pass

    @abstractmethod
    def extract_features(self, data: List[Dict[str, Any]],
                        feature_types: List[str]) -> Dict[str, Any]:
        """
        提取数据特征

        Args:
            data: 原始数据
            feature_types: 特征类型列表

        Returns:
            Dict[str, Any]: 提取的特征
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[31:147]
==document_service_interface:[59:170]
        pass

    @abstractmethod
    def add_image_to_word(self, document: Any, image_path: str,
                         width: Optional[float] = None) -> bool:
        """
        向Word文档添加图片

        Args:
            document: Word文档对象
            image_path: 图片文件路径
            width: 图片宽度

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def create_excel_workbook(self, template_path: Optional[str] = None) -> Any:
        """
        创建Excel工作簿

        Args:
            template_path: Excel模板文件路径

        Returns:
            Any: Excel工作簿对象
        """
        pass

    @abstractmethod
    def save_excel_workbook(self, workbook: Any, output_path: str) -> bool:
        """
        保存Excel工作簿

        Args:
            workbook: Excel工作簿对象
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def add_sheet_to_excel(self, workbook: Any, sheet_name: str, data: List[List[Any]]) -> bool:
        """
        向Excel工作簿添加工作表

        Args:
            workbook: Excel工作簿对象
            sheet_name: 工作表名称
            data: 工作表数据

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def set_cell_style(self, worksheet: Any, row: int, col: int,
                      font_name: Optional[str] = None, font_size: Optional[int] = None,
                      bold: Optional[bool] = None, background_color: Optional[str] = None) -> bool:
        """
        设置单元格样式

        Args:
            worksheet: Excel工作表对象
            row: 行号
            col: 列号
            font_name: 字体名称
            font_size: 字体大小
            bold: 是否加粗
            background_color: 背景色

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def generate_report(self, report_type: str, data: Dict[str, Any],
                       output_path: str, template_path: Optional[str] = None) -> bool:
        """
        生成报告

        Args:
            report_type: 报告类型（如"word", "excel"）
            data: 报告数据
            output_path: 输出文件路径
            template_path: 模板文件路径

        Returns:
            bool: 生成是否成功
        """
        pass

    @abstractmethod
    def set_cell_background_color(self, cell: Any, color: str) -> bool:
        """
        设置单元格背景色

        Args:
            cell: 单元格对象
            color: 颜色值（十六进制或颜色名称）

        Returns:
            bool: 设置是否成功
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[69:159]
==validation_service_interface:[28:122]
        pass

    @abstractmethod
    def set_axis_labels(self, chart: Any, x_label: str, y_label: str) -> None:
        """设置坐标轴标签

        Args:
            chart: 图表实例
            x_label: X轴标签
            y_label: Y轴标签
        """
        pass

    @abstractmethod
    def add_legend(self, chart: Any) -> None:
        """添加图例

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def save_chart(self, chart: Any, file_path: str, format: ChartFormat = ChartFormat.PNG, **kwargs) -> bool:
        """保存图表

        Args:
            chart: 图表实例
            file_path: 保存路径
            format: 保存格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def show_chart(self, chart: Any) -> bool:
        """显示图表

        Args:
            chart: 图表实例

        Returns:
            bool: 是否显示成功
        """
        pass

    @abstractmethod
    def close_chart(self, chart: Any) -> None:
        """关闭图表

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def create_subplot(self, rows: int, columns: int, index: int = 1) -> Any:
        """创建子图

        Args:
            rows: 行数
            columns: 列数
            index: 子图索引

        Returns:
            Any: 子图实例
        """
        pass

    @abstractmethod
    def set_grid(self, chart: Any, show: bool = True) -> None:
        """设置网格

        Args:
            chart: 图表实例
            show: 是否显示网格
        """
        pass

    @abstractmethod
    def set_colors(self, chart: Any, colors: List[str]) -> None:
        """设置颜色

        Args:
            chart: 图表实例
            colors: 颜色列表
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==config_service_interface:[30:117]
==ichart_manager:[59:149]
        pass

    @abstractmethod
    def set_chart_title(self, chart: Any, title: str) -> None:
        """设置图表标题

        Args:
            chart: 图表实例
            title: 标题文本
        """
        pass

    @abstractmethod
    def set_axis_labels(self, chart: Any, x_label: str, y_label: str) -> None:
        """设置坐标轴标签

        Args:
            chart: 图表实例
            x_label: X轴标签
            y_label: Y轴标签
        """
        pass

    @abstractmethod
    def add_legend(self, chart: Any) -> None:
        """添加图例

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def save_chart(self, chart: Any, file_path: str, format: ChartFormat = ChartFormat.PNG, **kwargs) -> bool:
        """保存图表

        Args:
            chart: 图表实例
            file_path: 保存路径
            format: 保存格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def show_chart(self, chart: Any) -> bool:
        """显示图表

        Args:
            chart: 图表实例

        Returns:
            bool: 是否显示成功
        """
        pass

    @abstractmethod
    def close_chart(self, chart: Any) -> None:
        """关闭图表

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def create_subplot(self, rows: int, columns: int, index: int = 1) -> Any:
        """创建子图

        Args:
            rows: 行数
            columns: 列数
            index: 子图索引

        Returns:
            Any: 子图实例
        """
        pass

    @abstractmethod
    def set_grid(self, chart: Any, show: bool = True) -> None:
        """设置网格

        Args:
            chart: 图表实例
            show: 是否显示网格
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[80:160]
==idataprocessor:[45:152]
        pass

    @abstractmethod
    def save_data(self, data: Any, file_path: str, format: DataFormat, **kwargs) -> bool:
        """保存数据文件

        Args:
            data: 数据对象
            file_path: 保存路径
            format: 数据格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def create_dataframe(self, data: Optional[Union[Dict, List, Any]] = None) -> Any:
        """创建数据框

        Args:
            data: 初始数据

        Returns:
            Any: 数据框对象
        """
        pass

    @abstractmethod
    def filter_data(self, data: Any, conditions: Dict[str, Any]) -> Any:
        """过滤数据

        Args:
            data: 数据对象
            conditions: 过滤条件

        Returns:
            Any: 过滤后的数据
        """
        pass

    @abstractmethod
    def group_data(self, data: Any, by: Union[str, List[str]]) -> Any:
        """分组数据

        Args:
            data: 数据对象
            by: 分组字段

        Returns:
            Any: 分组后的数据
        """
        pass

    @abstractmethod
    def aggregate_data(self, data: Any, aggregations: Dict[str, Dict[str, str]]) -> Any:
        """聚合数据

        Args:
            data: 数据对象
            aggregations: 聚合规则

        Returns:
            Any: 聚合后的数据
        """
        pass

    @abstractmethod
    def sort_data(self, data: Any, by: Union[str, List[str]], ascending: bool = True) -> Any:
        """排序数据

        Args:
            data: 数据对象
            by: 排序字段
            ascending: 是否升序

        Returns:
            Any: 排序后的数据
        """
        pass

    @abstractmethod
    def merge_data(self, left: Any, right: Any, on: Union[str, List[str]], how: str = "inner") -> Any:
        """合并数据

        Args:
            left: 左数据
            right: 右数据
            on: 合并字段
            how: 合并方式

        Returns:
            Any: 合并后的数据
        """
        pass

    @abstractmethod
    def get_column_names(self, data: Any) -> List[str]:
        """获取列名

        Args:
            data: 数据对象

        Returns:
            List[str]: 列名列表
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[46:139]
==idataprocessor:[125:220]
        pass

    @abstractmethod
    def set_chart_data(self, chart: Any, data: Dict[str, Any]) -> bool:
        """设置图表数据

        Args:
            chart: 图表实例
            data: 数据字典

        Returns:
            bool: 是否设置成功
        """
        pass

    @abstractmethod
    def set_chart_title(self, chart: Any, title: str) -> None:
        """设置图表标题

        Args:
            chart: 图表实例
            title: 标题文本
        """
        pass

    @abstractmethod
    def set_axis_labels(self, chart: Any, x_label: str, y_label: str) -> None:
        """设置坐标轴标签

        Args:
            chart: 图表实例
            x_label: X轴标签
            y_label: Y轴标签
        """
        pass

    @abstractmethod
    def add_legend(self, chart: Any) -> None:
        """添加图例

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def save_chart(self, chart: Any, file_path: str, format: ChartFormat = ChartFormat.PNG, **kwargs) -> bool:
        """保存图表

        Args:
            chart: 图表实例
            file_path: 保存路径
            format: 保存格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def show_chart(self, chart: Any) -> bool:
        """显示图表

        Args:
            chart: 图表实例

        Returns:
            bool: 是否显示成功
        """
        pass

    @abstractmethod
    def close_chart(self, chart: Any) -> None:
        """关闭图表

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def create_subplot(self, rows: int, columns: int, index: int = 1) -> Any:
        """创建子图

        Args:
            rows: 行数
            columns: 列数
            index: 子图索引

        Returns:
            Any: 子图实例
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[298:313]
==modern_battery_viewer_refactored:[277:292]
        layout.addLayout(filter_layout)
        layout.addLayout(sampling_layout)
        layout.addWidget(self.apply_button)

        parent.addWidget(group)

    def _create_data_info_panel(self, parent):
        """创建数据信息面板"""

        # 使用样式管理器创建主题化分组框
        group = create_styled_groupbox(self, "📊 数据信息", "info")
        layout = QVBoxLayout(group)

        # 数据状态
        self.data_status_label = QLabel("未加载数据")
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[282:292]
==modern_battery_viewer_refactored:[258:268]
        self.sampling_spinbox = QSpinBox()
        self.sampling_spinbox.setRange(1, 100)
        self.sampling_spinbox.setValue(5)
        self.sampling_spinbox.setSuffix(" ms")
        self.sampling_spinbox.valueChanged.connect(self._on_filter_parameter_changed)

        sampling_layout.addWidget(sampling_label)
        sampling_layout.addWidget(self.sampling_spinbox)

        # 应用按钮
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==interfaces.iuiframework:[38:136]
==validation_service_interface:[41:122]
        pass

    @abstractmethod
    def create_main_window(self) -> Any:
        """创建主窗口

        Returns:
            Any: 主窗口实例
        """
        pass

    @abstractmethod
    def create_progress_dialog(self, parent: Optional[Any] = None) -> Any:
        """创建进度对话框

        Args:
            parent: 父窗口

        Returns:
            Any: 进度对话框实例
        """
        pass

    @abstractmethod
    def show_message_box(self,
                        parent: Optional[Any],
                        title: str,
                        message: str,
                        msg_type: MessageBoxType) -> Any:
        """显示消息框

        Args:
            parent: 父窗口
            title: 窗口标题
            message: 消息内容
            msg_type: 消息类型

        Returns:
            Any: 消息框实例
        """
        pass

    @abstractmethod
    def create_file_dialog(self,
                          parent: Optional[Any],
                          caption: str,
                          directory: str = "",
                          filter_pattern: str = "") -> Any:
        """创建文件选择对话框

        Args:
            parent: 父窗口
            caption: 对话框标题
            directory: 默认目录
            filter_pattern: 文件过滤器

        Returns:
            Any: 文件对话框实例
        """
        pass

    @abstractmethod
    def create_label(self, parent: Any, text: str) -> Any:
        """创建标签控件

        Args:
            parent: 父控件
            text: 标签文本

        Returns:
            Any: 标签控件实例
        """
        pass

    @abstractmethod
    def create_button(self, parent: Any, text: str) -> Any:
        """创建按钮控件

        Args:
            parent: 父控件
            text: 按钮文本

        Returns:
            Any: 按钮控件实例
        """
        pass

    @abstractmethod
    def create_input_field(self, parent: Any, placeholder: str = "") -> Any:
        """创建输入框控件

        Args:
            parent: 父控件
            placeholder: 占位符文本

        Returns:
            Any: 输入框控件实例
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==interfaces.iuiframework:[97:173]
==validation_service_interface:[28:121]
        pass

    @abstractmethod
    def create_label(self, parent: Any, text: str) -> Any:
        """创建标签控件

        Args:
            parent: 父控件
            text: 标签文本

        Returns:
            Any: 标签控件实例
        """
        pass

    @abstractmethod
    def create_button(self, parent: Any, text: str) -> Any:
        """创建按钮控件

        Args:
            parent: 父控件
            text: 按钮文本

        Returns:
            Any: 按钮控件实例
        """
        pass

    @abstractmethod
    def create_input_field(self, parent: Any, placeholder: str = "") -> Any:
        """创建输入框控件

        Args:
            parent: 父控件
            placeholder: 占位符文本

        Returns:
            Any: 输入框控件实例
        """
        pass

    @abstractmethod
    def create_table_widget(self, parent: Any, rows: int, columns: int) -> Any:
        """创建表格控件

        Args:
            parent: 父控件
            rows: 行数
            columns: 列数

        Returns:
            Any: 表格控件实例
        """
        pass

    @abstractmethod
    def set_layout(self, parent: Any, layout: Any) -> None:
        """设置布局管理器

        Args:
            parent: 父控件
            layout: 布局管理器
        """
        pass

    @abstractmethod
    def exec_application(self, app: Any) -> int:
        """运行应用程序

        Args:
            app: 应用程序实例

        Returns:
            int: 退出代码
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==document_service_interface:[75:170]
==file_service_interface:[29:124]
        pass

    @abstractmethod
    def create_excel_workbook(self, template_path: Optional[str] = None) -> Any:
        """
        创建Excel工作簿

        Args:
            template_path: Excel模板文件路径

        Returns:
            Any: Excel工作簿对象
        """
        pass

    @abstractmethod
    def save_excel_workbook(self, workbook: Any, output_path: str) -> bool:
        """
        保存Excel工作簿

        Args:
            workbook: Excel工作簿对象
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def add_sheet_to_excel(self, workbook: Any, sheet_name: str, data: List[List[Any]]) -> bool:
        """
        向Excel工作簿添加工作表

        Args:
            workbook: Excel工作簿对象
            sheet_name: 工作表名称
            data: 工作表数据

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def set_cell_style(self, worksheet: Any, row: int, col: int,
                      font_name: Optional[str] = None, font_size: Optional[int] = None,
                      bold: Optional[bool] = None, background_color: Optional[str] = None) -> bool:
        """
        设置单元格样式

        Args:
            worksheet: Excel工作表对象
            row: 行号
            col: 列号
            font_name: 字体名称
            font_size: 字体大小
            bold: 是否加粗
            background_color: 背景色

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def generate_report(self, report_type: str, data: Dict[str, Any],
                       output_path: str, template_path: Optional[str] = None) -> bool:
        """
        生成报告

        Args:
            report_type: 报告类型（如"word", "excel"）
            data: 报告数据
            output_path: 输出文件路径
            template_path: 模板文件路径

        Returns:
            bool: 生成是否成功
        """
        pass

    @abstractmethod
    def set_cell_background_color(self, cell: Any, color: str) -> bool:
        """
        设置单元格背景色

        Args:
            cell: 单元格对象
            color: 颜色值（十六进制或颜色名称）

        Returns:
            bool: 设置是否成功
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==document_service_interface:[29:138]
==file_service_interface:[70:152]
        pass

    @abstractmethod
    def set_file_attributes(self, file_path: Union[str, Path], attributes: dict) -> Tuple[bool, str]:
        """
        设置文件属性

        Args:
            file_path: 文件路径
            attributes: 属性字典

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def hide_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        隐藏文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def is_file_hidden(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否隐藏

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否隐藏
        """
        pass

    @abstractmethod
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        复制文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        移动文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==config_service_interface:[44:117]
==data_processing_service_interface:[31:131]
        pass

    @abstractmethod
    def analyze_battery_performance(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析电池性能

        Args:
            data: 电池数据列表

        Returns:
            Dict[str, Any]: 分析结果
        """
        pass

    @abstractmethod
    def calculate_statistics(self, data: List[Union[float, int]],
                           statistics: List[str] = None) -> Dict[str, float]:
        """
        计算统计数据

        Args:
            data: 数据列表
            statistics: 统计类型列表（如["mean", "std", "min", "max"]）

        Returns:
            Dict[str, float]: 统计数据
        """
        pass

    @abstractmethod
    def smooth_data(self, data: List[float], method: str = "moving_average",
                   window_size: int = 5) -> List[float]:
        """
        数据平滑处理

        Args:
            data: 原始数据
            method: 平滑方法（"moving_average", "gaussian", "savgol"）
            window_size: 窗口大小

        Returns:
            List[float]: 平滑后的数据
        """
        pass

    @abstractmethod
    def detect_outliers(self, data: List[Union[float, int]],
                       method: str = "iqr") -> List[int]:
        """
        检测异常值

        Args:
            data: 数据列表
            method: 检测方法（"iqr", "zscore", "isolation_forest"）

        Returns:
            List[int]: 异常值的索引列表
        """
        pass

    @abstractmethod
    def generate_mock_data(self, battery_count: int = 1,
                          data_points: int = 100) -> List[Dict[str, Any]]:
        """
        生成模拟电池数据

        Args:
            battery_count: 电池数量
            data_points: 数据点数量

        Returns:
            List[Dict[str, Any]]: 模拟数据
        """
        pass

    @abstractmethod
    def validate_data_integrity(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证数据完整性

        Args:
            data: 待验证的数据

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        pass

    @abstractmethod
    def process_csv_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        处理CSV数据文件

        Args:
            csv_path: CSV文件路径

        Returns:
            List[Dict[str, Any]]: 解析后的数据
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==config_service_interface:[30:116]
==data_processing_service_interface:[90:176]
        pass

    @abstractmethod
    def generate_mock_data(self, battery_count: int = 1,
                          data_points: int = 100) -> List[Dict[str, Any]]:
        """
        生成模拟电池数据

        Args:
            battery_count: 电池数量
            data_points: 数据点数量

        Returns:
            List[Dict[str, Any]]: 模拟数据
        """
        pass

    @abstractmethod
    def validate_data_integrity(self, data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证数据完整性

        Args:
            data: 待验证的数据

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        pass

    @abstractmethod
    def process_csv_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        处理CSV数据文件

        Args:
            csv_path: CSV文件路径

        Returns:
            List[Dict[str, Any]]: 解析后的数据
        """
        pass

    @abstractmethod
    def export_processed_data(self, data: List[Dict[str, Any]],
                            output_path: str, format: str = "csv") -> bool:
        """
        导出处理后的数据

        Args:
            data: 要导出的数据
            output_path: 输出文件路径
            format: 导出格式（"csv", "json", "excel"）

        Returns:
            bool: 导出是否成功
        """
        pass

    @abstractmethod
    def merge_battery_data(self, data_list: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        合并多个电池数据集

        Args:
            data_list: 数据集列表

        Returns:
            List[Dict[str, Any]]: 合并后的数据
        """
        pass

    @abstractmethod
    def extract_features(self, data: List[Dict[str, Any]],
                        feature_types: List[str]) -> Dict[str, Any]:
        """
        提取数据特征

        Args:
            data: 原始数据
            feature_types: 特征类型列表

        Returns:
            Dict[str, Any]: 提取的特征
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[59:139]
==ivisualizer:[29:90]
        pass

    @abstractmethod
    def set_chart_title(self, chart: Any, title: str) -> None:
        """设置图表标题

        Args:
            chart: 图表实例
            title: 标题文本
        """
        pass

    @abstractmethod
    def set_axis_labels(self, chart: Any, x_label: str, y_label: str) -> None:
        """设置坐标轴标签

        Args:
            chart: 图表实例
            x_label: X轴标签
            y_label: Y轴标签
        """
        pass

    @abstractmethod
    def add_legend(self, chart: Any) -> None:
        """添加图例

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def save_chart(self, chart: Any, file_path: str, format: ChartFormat = ChartFormat.PNG, **kwargs) -> bool:
        """保存图表

        Args:
            chart: 图表实例
            file_path: 保存路径
            format: 保存格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def show_chart(self, chart: Any) -> bool:
        """显示图表

        Args:
            chart: 图表实例

        Returns:
            bool: 是否显示成功
        """
        pass

    @abstractmethod
    def close_chart(self, chart: Any) -> None:
        """关闭图表

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def create_subplot(self, rows: int, columns: int, index: int = 1) -> Any:
        """创建子图

        Args:
            rows: 行数
            columns: 列数
            index: 子图索引

        Returns:
            Any: 子图实例
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[89:160]
==idataprocessor:[45:140]
        pass

    @abstractmethod
    def save_data(self, data: Any, file_path: str, format: DataFormat, **kwargs) -> bool:
        """保存数据文件

        Args:
            data: 数据对象
            file_path: 保存路径
            format: 数据格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def create_dataframe(self, data: Optional[Union[Dict, List, Any]] = None) -> Any:
        """创建数据框

        Args:
            data: 初始数据

        Returns:
            Any: 数据框对象
        """
        pass

    @abstractmethod
    def filter_data(self, data: Any, conditions: Dict[str, Any]) -> Any:
        """过滤数据

        Args:
            data: 数据对象
            conditions: 过滤条件

        Returns:
            Any: 过滤后的数据
        """
        pass

    @abstractmethod
    def group_data(self, data: Any, by: Union[str, List[str]]) -> Any:
        """分组数据

        Args:
            data: 数据对象
            by: 分组字段

        Returns:
            Any: 分组后的数据
        """
        pass

    @abstractmethod
    def aggregate_data(self, data: Any, aggregations: Dict[str, Dict[str, str]]) -> Any:
        """聚合数据

        Args:
            data: 数据对象
            aggregations: 聚合规则

        Returns:
            Any: 聚合后的数据
        """
        pass

    @abstractmethod
    def sort_data(self, data: Any, by: Union[str, List[str]], ascending: bool = True) -> Any:
        """排序数据

        Args:
            data: 数据对象
            by: 排序字段
            ascending: 是否升序

        Returns:
            Any: 排序后的数据
        """
        pass

    @abstractmethod
    def merge_data(self, left: Any, right: Any, on: Union[str, List[str]], how: str = "inner") -> Any:
        """合并数据

        Args:
            left: 左数据
            right: 右数据
            on: 合并字段
            how: 合并方式

        Returns:
            Any: 合并后的数据
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[46:125]
==idataprocessor:[140:220]
        pass

    @abstractmethod
    def get_column_names(self, data: Any) -> List[str]:
        """获取列名

        Args:
            data: 数据对象

        Returns:
            List[str]: 列名列表
        """
        pass

    @abstractmethod
    def get_column_data(self, data: Any, column: str) -> Any:
        """获取列数据

        Args:
            data: 数据对象
            column: 列名

        Returns:
            Any: 列数据
        """
        pass

    @abstractmethod
    def set_column_data(self, data: Any, column: str, values: Any) -> bool:
        """设置列数据

        Args:
            data: 数据对象
            column: 列名
            values: 新数据

        Returns:
            bool: 是否设置成功
        """
        pass

    @abstractmethod
    def convert_data_type(self, data: Any, column: str, data_type: DataType) -> bool:
        """转换数据类型

        Args:
            data: 数据对象
            column: 列名
            data_type: 目标类型

        Returns:
            bool: 是否转换成功
        """
        pass

    @abstractmethod
    def get_statistics(self, data: Any, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """获取统计信息

        Args:
            data: 数据对象
            columns: 指定列（None表示所有列）

        Returns:
            Dict[str, Any]: 统计信息
        """
        pass

    @abstractmethod
    def handle_missing_values(self, data: Any, strategy: str = "drop") -> Any:
        """处理缺失值

        Args:
            data: 数据对象
            strategy: 处理策略（drop、fill、interpolate等）

        Returns:
            Any: 处理后的数据
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==file_service_interface:[84:152]
==validation_service_interface:[28:108]
        pass

    @abstractmethod
    def hide_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        隐藏文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def is_file_hidden(self, file_path: Union[str, Path]) -> bool:
        """
        检查文件是否隐藏

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否隐藏
        """
        pass

    @abstractmethod
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        复制文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Tuple[bool, str]:
        """
        移动文件

        Args:
            source: 源文件路径
            destination: 目标文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否成功, 错误消息)
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==file_service_interface:[29:110]
==validation_service_interface:[54:122]
        pass

    @abstractmethod
    def validate_numeric_value(self, value: Any, min_val: float = None, max_val: float = None) -> Tuple[bool, str]:
        """
        验证数值是否在有效范围内

        Args:
            value: 要验证的值
            min_val: 最小值
            max_val: 最大值

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """
        验证邮箱地址格式

        Args:
            email: 邮箱地址

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """
        验证电话号码格式

        Args:
            phone: 电话号码

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_battery_type(self, battery_type: str) -> Tuple[bool, str]:
        """
        验证电池类型是否有效

        Args:
            battery_type: 电池类型

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_capacity_value(self, capacity: str) -> Tuple[bool, str]:
        """
        验证容量值是否有效

        Args:
            capacity: 容量值

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[105:176]
==document_service_interface:[29:117]
        pass

    @abstractmethod
    def save_word_document(self, document: Any, output_path: str) -> bool:
        """
        保存Word文档

        Args:
            document: Word文档对象
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def add_table_to_word(self, document: Any, table_data: List[List[str]],
                         table_style: Optional[str] = None) -> bool:
        """
        向Word文档添加表格

        Args:
            document: Word文档对象
            table_data: 表格数据，二维列表
            table_style: 表格样式

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def add_image_to_word(self, document: Any, image_path: str,
                         width: Optional[float] = None) -> bool:
        """
        向Word文档添加图片

        Args:
            document: Word文档对象
            image_path: 图片文件路径
            width: 图片宽度

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def create_excel_workbook(self, template_path: Optional[str] = None) -> Any:
        """
        创建Excel工作簿

        Args:
            template_path: Excel模板文件路径

        Returns:
            Any: Excel工作簿对象
        """
        pass

    @abstractmethod
    def save_excel_workbook(self, workbook: Any, output_path: str) -> bool:
        """
        保存Excel工作簿

        Args:
            workbook: Excel工作簿对象
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def add_sheet_to_excel(self, workbook: Any, sheet_name: str, data: List[List[Any]]) -> bool:
        """
        向Excel工作簿添加工作表

        Args:
            workbook: Excel工作簿对象
            sheet_name: 工作表名称
            data: 工作表数据

        Returns:
            bool: 添加是否成功
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[31:118]
==document_service_interface:[88:170]
        pass

    @abstractmethod
    def save_excel_workbook(self, workbook: Any, output_path: str) -> bool:
        """
        保存Excel工作簿

        Args:
            workbook: Excel工作簿对象
            output_path: 输出文件路径

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def add_sheet_to_excel(self, workbook: Any, sheet_name: str, data: List[List[Any]]) -> bool:
        """
        向Excel工作簿添加工作表

        Args:
            workbook: Excel工作簿对象
            sheet_name: 工作表名称
            data: 工作表数据

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def set_cell_style(self, worksheet: Any, row: int, col: int,
                      font_name: Optional[str] = None, font_size: Optional[int] = None,
                      bold: Optional[bool] = None, background_color: Optional[str] = None) -> bool:
        """
        设置单元格样式

        Args:
            worksheet: Excel工作表对象
            row: 行号
            col: 列号
            font_name: 字体名称
            font_size: 字体大小
            bold: 是否加粗
            background_color: 背景色

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def generate_report(self, report_type: str, data: Dict[str, Any],
                       output_path: str, template_path: Optional[str] = None) -> bool:
        """
        生成报告

        Args:
            report_type: 报告类型（如"word", "excel"）
            data: 报告数据
            output_path: 输出文件路径
            template_path: 模板文件路径

        Returns:
            bool: 生成是否成功
        """
        pass

    @abstractmethod
    def set_cell_background_color(self, cell: Any, color: str) -> bool:
        """
        设置单元格背景色

        Args:
            cell: 单元格对象
            color: 颜色值（十六进制或颜色名称）

        Returns:
            bool: 设置是否成功
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==config_service_interface:[30:103]
==ivisualizer:[42:90]
        pass

    @abstractmethod
    def clear_data(self) -> None:
        """
        清除所有数据，回到初始状态
        """
        pass

    @abstractmethod
    def is_data_loaded(self) -> bool:
        """
        检查是否有数据已加载

        Returns:
            bool: 是否已加载数据
        """
        pass

    @abstractmethod
    def get_status_info(self) -> dict:
        """
        获取状态信息

        Returns:
            dict: 状态信息字典
        """
        pass

    @abstractmethod
    def set_config(self, config: dict) -> None:
        """
        设置配置

        Args:
            config: 配置字典
        """
        pass

    @abstractmethod
    def get_config(self) -> dict:
        """
        获取当前配置

        Returns:
            dict: 当前配置字典
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==config_service_interface:[54:117]
==ivisualizer:[29:89]
        pass

    @abstractmethod
    def load_config(self, config_path: Optional[str] = None) -> bool:
        """
        从文件加载配置

        Args:
            config_path: 配置文件路径，None表示使用默认路径

        Returns:
            bool: 加载是否成功
        """
        pass

    @abstractmethod
    def get_config_sections(self) -> List[str]:
        """
        获取所有配置节名称

        Returns:
            List[str]: 配置节名称列表
        """
        pass

    @abstractmethod
    def get_section_config(self, section: str) -> Dict[str, Any]:
        """
        获取指定配置节的所有键值对

        Args:
            section: 配置节名称

        Returns:
            Dict[str, Any]: 配置节内容
        """
        pass

    @abstractmethod
    def has_config_key(self, key: str) -> bool:
        """
        检查配置键是否存在

        Args:
            key: 配置键

        Returns:
            bool: 键是否存在
        """
        pass

    @abstractmethod
    def find_config_file(self, file_name: str = "setting.ini") -> Optional[Path]:
        """
        查找配置文件路径

        Args:
            file_name: 配置文件名称

        Returns:
            Optional[Path]: 配置文件路径，如果未找到则返回None
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[104:160]
==idataprocessor:[45:125]
        pass

    @abstractmethod
    def save_data(self, data: Any, file_path: str, format: DataFormat, **kwargs) -> bool:
        """保存数据文件

        Args:
            data: 数据对象
            file_path: 保存路径
            format: 数据格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def create_dataframe(self, data: Optional[Union[Dict, List, Any]] = None) -> Any:
        """创建数据框

        Args:
            data: 初始数据

        Returns:
            Any: 数据框对象
        """
        pass

    @abstractmethod
    def filter_data(self, data: Any, conditions: Dict[str, Any]) -> Any:
        """过滤数据

        Args:
            data: 数据对象
            conditions: 过滤条件

        Returns:
            Any: 过滤后的数据
        """
        pass

    @abstractmethod
    def group_data(self, data: Any, by: Union[str, List[str]]) -> Any:
        """分组数据

        Args:
            data: 数据对象
            by: 分组字段

        Returns:
            Any: 分组后的数据
        """
        pass

    @abstractmethod
    def aggregate_data(self, data: Any, aggregations: Dict[str, Dict[str, str]]) -> Any:
        """聚合数据

        Args:
            data: 数据对象
            aggregations: 聚合规则

        Returns:
            Any: 聚合后的数据
        """
        pass

    @abstractmethod
    def sort_data(self, data: Any, by: Union[str, List[str]], ascending: bool = True) -> Any:
        """排序数据

        Args:
            data: 数据对象
            by: 排序字段
            ascending: 是否升序

        Returns:
            Any: 排序后的数据
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[46:116]
==idataprocessor:[152:220]
        pass

    @abstractmethod
    def set_chart_data(self, chart: Any, data: Dict[str, Any]) -> bool:
        """设置图表数据

        Args:
            chart: 图表实例
            data: 数据字典

        Returns:
            bool: 是否设置成功
        """
        pass

    @abstractmethod
    def set_chart_title(self, chart: Any, title: str) -> None:
        """设置图表标题

        Args:
            chart: 图表实例
            title: 标题文本
        """
        pass

    @abstractmethod
    def set_axis_labels(self, chart: Any, x_label: str, y_label: str) -> None:
        """设置坐标轴标签

        Args:
            chart: 图表实例
            x_label: X轴标签
            y_label: Y轴标签
        """
        pass

    @abstractmethod
    def add_legend(self, chart: Any) -> None:
        """添加图例

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def save_chart(self, chart: Any, file_path: str, format: ChartFormat = ChartFormat.PNG, **kwargs) -> bool:
        """保存图表

        Args:
            chart: 图表实例
            file_path: 保存路径
            format: 保存格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def show_chart(self, chart: Any) -> bool:
        """显示图表

        Args:
            chart: 图表实例

        Returns:
            bool: 是否显示成功
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[650:665]
==modern_battery_viewer_refactored:[567:580]
        self.statusBar().showMessage('视图已刷新')

    @pyqtSlot()
    def _toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    @pyqtSlot()
    def _show_about(self):
        """显示关于信息"""
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==modern_battery_viewer:[476:496]
==modern_battery_viewer_refactored:[454:470]
        self.statusBar().addPermanentWidget(self.data_status_indicator)

        # 添加进度条（隐藏状态）
        self.progress_label = QLabel()
        self.statusBar().addPermanentWidget(self.progress_label)

    def _connect_signals(self):
        """连接信号和槽"""

        if self.chart_widget:
            self.chart_widget.data_changed.connect(self._on_chart_data_changed)

    def _apply_styles(self):
        """应用现代化样式"""

        # 使用样式管理器应用全局样式
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==file_service_interface:[97:152]
==validation_service_interface:[28:95]
        pass

    @abstractmethod
    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """
        验证文件路径的有效性

        Args:
            file_path: 文件路径

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_directory_path(self, directory_path: str) -> Tuple[bool, str]:
        """
        验证目录路径的有效性

        Args:
            directory_path: 目录路径

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_numeric_value(self, value: Any, min_val: float = None, max_val: float = None) -> Tuple[bool, str]:
        """
        验证数值是否在有效范围内

        Args:
            value: 要验证的值
            min_val: 最小值
            max_val: 最大值

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """
        验证邮箱地址格式

        Args:
            email: 邮箱地址

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """
        验证电话号码格式

        Args:
            phone: 电话号码

        Returns:
            tuple: (是否有效, 错误消息)
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==file_service_interface:[29:97]
==validation_service_interface:[69:122]
        pass

    @abstractmethod
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """
        验证邮箱地址格式

        Args:
            email: 邮箱地址

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_phone_number(self, phone: str) -> Tuple[bool, str]:
        """
        验证电话号码格式

        Args:
            phone: 电话号码

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_battery_type(self, battery_type: str) -> Tuple[bool, str]:
        """
        验证电池类型是否有效

        Args:
            battery_type: 电池类型

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass

    @abstractmethod
    def validate_capacity_value(self, capacity: str) -> Tuple[bool, str]:
        """
        验证容量值是否有效

        Args:
            capacity: 容量值

        Returns:
            tuple: (是否有效, 错误消息)
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[118:176]
==document_service_interface:[29:102]
        pass

    @abstractmethod
    def process_csv_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        处理CSV数据文件

        Args:
            csv_path: CSV文件路径

        Returns:
            List[Dict[str, Any]]: 解析后的数据
        """
        pass

    @abstractmethod
    def export_processed_data(self, data: List[Dict[str, Any]],
                            output_path: str, format: str = "csv") -> bool:
        """
        导出处理后的数据

        Args:
            data: 要导出的数据
            output_path: 输出文件路径
            format: 导出格式（"csv", "json", "excel"）

        Returns:
            bool: 导出是否成功
        """
        pass

    @abstractmethod
    def merge_battery_data(self, data_list: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        合并多个电池数据集

        Args:
            data_list: 数据集列表

        Returns:
            List[Dict[str, Any]]: 合并后的数据
        """
        pass

    @abstractmethod
    def extract_features(self, data: List[Dict[str, Any]],
                        feature_types: List[str]) -> Dict[str, Any]:
        """
        提取数据特征

        Args:
            data: 原始数据
            feature_types: 特征类型列表

        Returns:
            Dict[str, Any]: 提取的特征
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==data_processing_service_interface:[31:105]
==document_service_interface:[102:170]
        pass

    @abstractmethod
    def add_sheet_to_excel(self, workbook: Any, sheet_name: str, data: List[List[Any]]) -> bool:
        """
        向Excel工作簿添加工作表

        Args:
            workbook: Excel工作簿对象
            sheet_name: 工作表名称
            data: 工作表数据

        Returns:
            bool: 添加是否成功
        """
        pass

    @abstractmethod
    def set_cell_style(self, worksheet: Any, row: int, col: int,
                      font_name: Optional[str] = None, font_size: Optional[int] = None,
                      bold: Optional[bool] = None, background_color: Optional[str] = None) -> bool:
        """
        设置单元格样式

        Args:
            worksheet: Excel工作表对象
            row: 行号
            col: 列号
            font_name: 字体名称
            font_size: 字体大小
            bold: 是否加粗
            background_color: 背景色

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def generate_report(self, report_type: str, data: Dict[str, Any],
                       output_path: str, template_path: Optional[str] = None) -> bool:
        """
        生成报告

        Args:
            report_type: 报告类型（如"word", "excel"）
            data: 报告数据
            output_path: 输出文件路径
            template_path: 模板文件路径

        Returns:
            bool: 生成是否成功
        """
        pass

    @abstractmethod
    def set_cell_background_color(self, cell: Any, color: str) -> bool:
        """
        设置单元格背景色

        Args:
            cell: 单元格对象
            color: 颜色值（十六进制或颜色名称）

        Returns:
            bool: 设置是否成功
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==config_service_interface:[30:90]
==ivisualizer:[49:90]
        pass

    @abstractmethod
    def is_data_loaded(self) -> bool:
        """
        检查是否有数据已加载

        Returns:
            bool: 是否已加载数据
        """
        pass

    @abstractmethod
    def get_status_info(self) -> dict:
        """
        获取状态信息

        Returns:
            dict: 状态信息字典
        """
        pass

    @abstractmethod
    def set_config(self, config: dict) -> None:
        """
        设置配置

        Args:
            config: 配置字典
        """
        pass

    @abstractmethod
    def get_config(self) -> dict:
        """
        获取当前配置

        Returns:
            dict: 当前配置字典
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==config_service_interface:[67:117]
==ivisualizer:[29:79]
        pass

    @abstractmethod
    def load_data(self, data_path: str) -> bool:
        """
        加载数据

        Args:
            data_path: 数据路径

        Returns:
            bool: 是否成功加载数据
        """
        pass

    @abstractmethod
    def clear_data(self) -> None:
        """
        清除所有数据，回到初始状态
        """
        pass

    @abstractmethod
    def is_data_loaded(self) -> bool:
        """
        检查是否有数据已加载

        Returns:
            bool: 是否已加载数据
        """
        pass

    @abstractmethod
    def get_status_info(self) -> dict:
        """
        获取状态信息

        Returns:
            dict: 状态信息字典
        """
        pass

    @abstractmethod
    def set_config(self, config: dict) -> None:
        """
        设置配置

        Args:
            config: 配置字典
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_chart_viewer:[1062:1073]
==controllers.visualizer_controller:[313:324]
        import matplotlib
        import matplotlib.pyplot as plt

        # 重置Matplotlib的内部状态（不关闭当前图表，避免事件绑定失效）
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)

        # 重新配置中文字体支持，避免重置后丢失
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial', 'Times New Roman']
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        # 根据环境选择合适的后端
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[116:160]
==idataprocessor:[45:111]
        pass

    @abstractmethod
    def save_data(self, data: Any, file_path: str, format: DataFormat, **kwargs) -> bool:
        """保存数据文件

        Args:
            data: 数据对象
            file_path: 保存路径
            format: 数据格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def create_dataframe(self, data: Optional[Union[Dict, List, Any]] = None) -> Any:
        """创建数据框

        Args:
            data: 初始数据

        Returns:
            Any: 数据框对象
        """
        pass

    @abstractmethod
    def filter_data(self, data: Any, conditions: Dict[str, Any]) -> Any:
        """过滤数据

        Args:
            data: 数据对象
            conditions: 过滤条件

        Returns:
            Any: 过滤后的数据
        """
        pass

    @abstractmethod
    def group_data(self, data: Any, by: Union[str, List[str]]) -> Any:
        """分组数据

        Args:
            data: 数据对象
            by: 分组字段

        Returns:
            Any: 分组后的数据
        """
        pass

    @abstractmethod
    def aggregate_data(self, data: Any, aggregations: Dict[str, Dict[str, str]]) -> Any:
        """聚合数据

        Args:
            data: 数据对象
            aggregations: 聚合规则

        Returns:
            Any: 聚合后的数据
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ichart_manager:[46:104]
==idataprocessor:[165:220]
        pass

    @abstractmethod
    def set_chart_data(self, chart: Any, data: Dict[str, Any]) -> bool:
        """设置图表数据

        Args:
            chart: 图表实例
            data: 数据字典

        Returns:
            bool: 是否设置成功
        """
        pass

    @abstractmethod
    def set_chart_title(self, chart: Any, title: str) -> None:
        """设置图表标题

        Args:
            chart: 图表实例
            title: 标题文本
        """
        pass

    @abstractmethod
    def set_axis_labels(self, chart: Any, x_label: str, y_label: str) -> None:
        """设置坐标轴标签

        Args:
            chart: 图表实例
            x_label: X轴标签
            y_label: Y轴标签
        """
        pass

    @abstractmethod
    def add_legend(self, chart: Any) -> None:
        """添加图例

        Args:
            chart: 图表实例
        """
        pass

    @abstractmethod
    def save_chart(self, chart: Any, file_path: str, format: ChartFormat = ChartFormat.PNG, **kwargs) -> bool:
        """保存图表

        Args:
            chart: 图表实例
            file_path: 保存路径
            format: 保存格式
            **kwargs: 保存参数

        Returns:
            bool: 是否保存成功
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==po_translator:[168:173]
==setup_i18n:[218:223]
    test_strings = [
        "battery-analyzer",
        "Preferences",
        "Language",
        "OK",
- 符号: duplicate-code

