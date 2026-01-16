# 代码重构计划

## 目录

### 错误(Error) - 需要立即修复
- **undefined-variable**: 使用了未定义的变量，可能导致运行时错误
- **access-member-before-definition**: 在定义前访问了成员变量

### 警告(Warning) - 建议修复
- **broad-exception-caught**: 捕获过于宽泛的 Exception，建议捕获更具体的异常类型
- **unused-import**: 导入了但未使用的模块，增加了不必要的加载时间
- **unused-variable**: 声明了但未使用的变量，应该删除
- **unused-argument**: 函数参数未使用，可能是遗漏或设计问题
- **redefined-outer-name**: 重新定义了外部作用域的变量名，可能导致混淆
- **global-statement**: 使用 global 关键字，可能破坏函数的封装性
- **deprecated-method**: 使用了已废弃的方法，应该使用替代方案
- **subprocess-run-check**: subprocess.run 未设置 check 参数，可能忽略错误
- **raise-missing-from**: 重新抛出异常时未使用 from 子句，丢失异常链
- **unnecessary-pass**: 使用了不必要的 pass 语句，可以用 ... 替代或重构
- **redefined-builtin**: 重新定义了 Python 内置函数，可能导致问题
- **attribute-defined-outside-init**: 属性在 __init__ 之外定义，应该在 __init__ 中初始化
- **unnecessary-ellipsis**: 不必要的省略号常量，在非抽象方法中应使用 pass 或删除
- **bare-except**: 使用了不带异常类型的 except，可能捕获意外异常
- **reimported**: 重复导入同一模块，应该避免
- **f-string-without-interpolation**: f-string 没有插值变量，应该使用普通字符串
- **locally-disabled**: 在代码中禁用了某个检查项的警告
- **suppressed-message**: 被抑制的消息
- **protected-access**: 访问了受保护的成员

### 规范(Convention) - 代码风格问题
- **wrong-import-order**: 导入顺序不正确，标准库应在最前，其次是第三方库，最后是本地库
- **wrong-import-position**: 导入语句位置不正确，应该放在模块顶部
- **import-outside-toplevel**: 在函数/方法内部进行导入，应该在模块顶部导入
- **missing-final-newline**: 文件末尾缺少换行符
- **trailing-newlines**: 文件末尾有多余的换行符
- **mixed-line-endings**: 混合使用不同的行尾符（LF 和 CRLF），应统一使用一种
- **ungrouped-imports**: 来自同一包的导入没有分组
- **use-implicit-booleaness-not-comparison-to-string**: 与空字符串比较应简化为隐式布尔值判断
- **use-implicit-booleaness-not-comparison-to-zero**: 与零比较应简化为隐式布尔值判断
- **consider-using-f-string**: 可以使用 f-string 格式化字符串
- **unspecified-encoding**: 打开文件时未明确指定编码
- **missing-module-docstring**: 缺少模块文档字符串
- **trailing-whitespace**: 行尾有多余的空格
- **consider-using-in**: 可以使用 'in' 操作符替代循环判断
- **use-symbolic-message-instead**: 使用符号消息替代数字代码
- **consider-using-with**: 可以使用 with 语句管理资源

### 重构(Refactor) - 代码结构优化
- **no-else-return**: return 语句后不必要的 else 块，可以简化
- **too-many-positional-arguments**: 函数位置参数过多，考虑使用命名参数或对象
- **too-many-branches**: 分支过多（超过12个），应考虑重构
- **too-many-statements**: 函数语句过多（超过50条），应拆分
- **too-many-nested-blocks**: 嵌套层数过多，应重构以减少嵌套
- **too-many-instance-attributes**: 实例属性过多（超过7个），应考虑拆分
- **too-many-public-methods**: 公开方法过多，应考虑封装
- **inconsistent-return-statements**: return 语句不一致，有些返回值有些不返回
- **consider-using-enumerate**: 迭代时可以使用 enumerate 替代 range(len())
- **use-dict-literal**: 可以使用字典字面量替代 dict() 调用
- **too-many-return-statements**: return 语句过多，应考虑简化
- **too-many-lines**: 模块行数过多（超过1000行），应考虑拆分
- **duplicate-code**: 存在重复代码片段，应考虑提取为函数或类
- **no-else-break**: break 语句后不必要的 else 块，可以简化
- **no-else-continue**: continue 语句后不必要的 else 块，可以简化

## 概述
- 分析日期: 2026-01-16 10:11:18
- 总文件数: 127
- 存在问题的文件数: 127

## 文件: scripts\build.py

### 问题统计
- 问题总数: 13
- 警告(Warning): 4
- 规范(Convention): 7
- 重构(Refactor): 2

### 详细问题
#### 行 50, 列 4
- 类型: warning
- 代码: W0237
- 描述: Parameter 'optionstr' has been renamed to 'option_str' in overriding 'CaseSensitiveConfigParser.optionxform' method
- 符号: arguments-renamed

#### 行 210, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (re)
- 符号: import-outside-toplevel

#### 行 324, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 331, 列 12
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'sys' from outer scope (line 5)
- 符号: redefined-outer-name

#### 行 331, 列 12
- 类型: warning
- 代码: W0404
- 描述: Reimport 'sys' (imported line 5)
- 符号: reimported

#### 行 331, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (sys)
- 符号: import-outside-toplevel

#### 行 333, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 374, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (7/5)
- 符号: too-many-positional-arguments

#### 行 422, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 423, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 475, 列 23
- 类型: convention
- 代码: C0209
- 描述: Formatting a regular string which could be an f-string
- 符号: consider-using-f-string

#### 行 611, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (ast)
- 符号: import-outside-toplevel

#### 行 733, 列 4
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (argparse)
- 符号: import-outside-toplevel

## 文件: scripts\compile_translations.py

### 问题统计
- 问题总数: 11
- 警告(Warning): 4
- 规范(Convention): 4
- 重构(Refactor): 3

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 59, 列 17
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 63, 列 11
- 类型: convention
- 代码: C1805
- 描述: "result.returncode == 0" can be simplified to "not result.returncode", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 68, 列 17
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 73, 列 11
- 类型: convention
- 代码: C1805
- 描述: "result.returncode == 0" can be simplified to "not result.returncode", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 179, 列 17
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 184, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 184, 列 11
- 类型: convention
- 代码: C1805
- 描述: "result.returncode == 0" can be simplified to "not result.returncode", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 196, 列 0
- 类型: refactor
- 代码: R1710
- 描述: Either all return statements in a function should return an expression, or none of them should.
- 符号: inconsistent-return-statements

#### 行 254, 列 4
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 263, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: scripts\extract_translations.py

### 问题统计
- 问题总数: 10
- 警告(Warning): 5
- 规范(Convention): 3
- 重构(Refactor): 2

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 76, 列 12
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'context'
- 符号: unused-variable

#### 行 125, 列 17
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 127, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 127, 列 11
- 类型: convention
- 代码: C1805
- 描述: "result.returncode == 0" can be simplified to "not result.returncode", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 325, 列 17
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 329, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 329, 列 11
- 类型: convention
- 代码: C1805
- 描述: "result.returncode == 0" can be simplified to "not result.returncode", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 345, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: scripts\po_translator.py

### 问题统计
- 问题总数: 4
- 警告(Warning): 1
- 规范(Convention): 2
- 重构(Refactor): 1

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 20, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.i18n import _ as main_translate, set_locale as main_set_locale, get_available_locales as main_get_available_locales, get_current_locale as main_get_current_locale, detect_system_locale as main_detect_system_locale" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 65, 列 4
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 109, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: scripts\run_pylint.py

### 问题统计
- 问题总数: 9
- 警告(Warning): 5
- 规范(Convention): 1
- 重构(Refactor): 3

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

#### 行 109, 列 11
- 类型: convention
- 代码: C1805
- 描述: "process.returncode == 0" can be simplified to "not process.returncode", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 175, 列 4
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'json_output'
- 符号: unused-variable

#### 行 285, 列 0
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 285, 列 0
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (106/50)
- 符号: too-many-statements

#### 行 356, 列 20
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 374, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 395, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

## 文件: scripts\run_tests.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 1
- 规范(Convention): 1
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

#### 行 57, 列 11
- 类型: convention
- 代码: C1805
- 描述: "result.returncode == 0" can be simplified to "not result.returncode", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

## 文件: scripts\setup_i18n.py

### 问题统计
- 问题总数: 7
- 警告(Warning): 5
- 规范(Convention): 2

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Dict imported from typing
- 符号: unused-import

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused List imported from typing
- 符号: unused-import

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 22, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.i18n import _" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 156, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'import_pattern'
- 符号: unused-variable

#### 行 380, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

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

## 文件: src\battery_analysis\application\usecases\analyze_data_use_case.py

### 问题统计
- 问题总数: 17
- 错误(Error): 11
- 警告(Warning): 5
- 重构(Refactor): 1

### 详细问题
#### 行 87, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (62/50)
- 符号: too-many-statements

#### 行 137, 列 35
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'datetime'
- 符号: undefined-variable

#### 行 148, 列 79
- 类型: error
- 代码: E1101
- 描述: Instance of 'Battery' has no 'model' member
- 符号: no-member

#### 行 206, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 224, 列 16
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 238, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 283, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 412, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 445, 列 15
- 类型: error
- 代码: E1123
- 描述: Unexpected keyword argument 'model' in constructor call
- 符号: unexpected-keyword-arg

#### 行 445, 列 15
- 类型: error
- 代码: E1123
- 描述: Unexpected keyword argument 'chemistry' in constructor call
- 符号: unexpected-keyword-arg

#### 行 445, 列 15
- 类型: error
- 代码: E1120
- 描述: No value for argument 'model_number' in constructor call
- 符号: no-value-for-parameter

#### 行 445, 列 15
- 类型: error
- 代码: E1120
- 描述: No value for argument 'production_date' in constructor call
- 符号: no-value-for-parameter

#### 行 445, 列 15
- 类型: error
- 代码: E1120
- 描述: No value for argument 'battery_type' in constructor call
- 符号: no-value-for-parameter

#### 行 445, 列 15
- 类型: error
- 代码: E1120
- 描述: No value for argument 'max_voltage' in constructor call
- 符号: no-value-for-parameter

#### 行 445, 列 15
- 类型: error
- 代码: E1120
- 描述: No value for argument 'min_voltage' in constructor call
- 符号: no-value-for-parameter

#### 行 445, 列 15
- 类型: error
- 代码: E1120
- 描述: No value for argument 'max_current' in constructor call
- 符号: no-value-for-parameter

#### 行 445, 列 15
- 类型: error
- 代码: E1120
- 描述: No value for argument 'weight' in constructor call
- 符号: no-value-for-parameter

## 文件: src\battery_analysis\application\usecases\calculate_battery_use_case.py

### 问题统计
- 问题总数: 12
- 错误(Error): 9
- 警告(Warning): 2
- 重构(Refactor): 1

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused List imported from typing
- 符号: unused-import

#### 行 16, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (12/7)
- 符号: too-many-instance-attributes

#### 行 112, 列 22
- 类型: error
- 代码: E1123
- 描述: Unexpected keyword argument 'model' in constructor call
- 符号: unexpected-keyword-arg

#### 行 112, 列 22
- 类型: error
- 代码: E1123
- 描述: Unexpected keyword argument 'chemistry' in constructor call
- 符号: unexpected-keyword-arg

#### 行 112, 列 22
- 类型: error
- 代码: E1120
- 描述: No value for argument 'model_number' in constructor call
- 符号: no-value-for-parameter

#### 行 112, 列 22
- 类型: error
- 代码: E1120
- 描述: No value for argument 'production_date' in constructor call
- 符号: no-value-for-parameter

#### 行 112, 列 22
- 类型: error
- 代码: E1120
- 描述: No value for argument 'battery_type' in constructor call
- 符号: no-value-for-parameter

#### 行 112, 列 22
- 类型: error
- 代码: E1120
- 描述: No value for argument 'max_voltage' in constructor call
- 符号: no-value-for-parameter

#### 行 112, 列 22
- 类型: error
- 代码: E1120
- 描述: No value for argument 'min_voltage' in constructor call
- 符号: no-value-for-parameter

#### 行 112, 列 22
- 类型: error
- 代码: E1120
- 描述: No value for argument 'max_current' in constructor call
- 符号: no-value-for-parameter

#### 行 112, 列 22
- 类型: error
- 代码: E1120
- 描述: No value for argument 'weight' in constructor call
- 符号: no-value-for-parameter

#### 行 138, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\application\usecases\generate_report_use_case.py

### 问题统计
- 问题总数: 9
- 警告(Warning): 9

### 详细问题
#### 行 167, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 198, 列 17
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

#### 行 199, 列 24
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 200, 列 24
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 216, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 261, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 307, 列 21
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

#### 行 308, 列 28
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 324, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\domain\entities\battery.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 1
- 重构(Refactor): 1

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused List imported from typing
- 符号: unused-import

#### 行 14, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (14/7)
- 符号: too-many-instance-attributes

## 文件: src\battery_analysis\domain\entities\configuration.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 1
- 重构(Refactor): 1

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 13, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (11/7)
- 符号: too-many-instance-attributes

## 文件: src\battery_analysis\domain\entities\test_profile.py

### 问题统计
- 问题总数: 1
- 重构(Refactor): 1

### 详细问题
#### 行 13, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (23/7)
- 符号: too-many-instance-attributes

## 文件: src\battery_analysis\domain\entities\test_result.py

### 问题统计
- 问题总数: 1
- 重构(Refactor): 1

### 详细问题
#### 行 14, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (17/7)
- 符号: too-many-instance-attributes

## 文件: src\battery_analysis\domain\repositories\battery_repository.py

### 问题统计
- 问题总数: 11
- 警告(Warning): 11

### 详细问题
#### 行 27, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 39, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 51, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 63, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 75, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 88, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 100, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 113, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 125, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 137, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 146, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\domain\repositories\configuration_repository.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 3

### 详细问题
#### 行 21, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 33, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 42, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\domain\repositories\test_profile_repository.py

### 问题统计
- 问题总数: 9
- 警告(Warning): 9

### 详细问题
#### 行 26, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 38, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 50, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 62, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 74, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 87, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 99, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 111, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 120, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\domain\repositories\test_result_repository.py

### 问题统计
- 问题总数: 8
- 警告(Warning): 8

### 详细问题
#### 行 27, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 39, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 51, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 64, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 77, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 89, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 101, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 113, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\domain\services\battery_analysis_service.py

### 问题统计
- 问题总数: 8
- 警告(Warning): 8

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 29, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 42, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 55, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 69, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 82, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 94, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 107, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\domain\services\impl\battery_analysis_service_impl.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 1
- 规范(Convention): 1

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 164, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.data_utils.detect_outliers)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\domain\services\impl\test_service_impl.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 1
- 重构(Refactor): 1

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 20, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (6/5)
- 符号: too-many-positional-arguments

## 文件: src\battery_analysis\domain\services\test_service.py

### 问题统计
- 问题总数: 10
- 警告(Warning): 9
- 重构(Refactor): 1

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused datetime imported from datetime
- 符号: unused-import

#### 行 20, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (6/5)
- 符号: too-many-positional-arguments

#### 行 35, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 48, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 60, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 72, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 84, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 96, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 110, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\i18n\__init__.py

### 问题统计
- 问题总数: 18
- 警告(Warning): 8
- 规范(Convention): 4
- 重构(Refactor): 6

### 详细问题
#### 行 21, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import sys" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 24, 列 21
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _MEIPASS of a client class
- 符号: protected-access

#### 行 133, 列 4
- 类型: warning
- 代码: W0603
- 描述: Using the global statement
- 符号: global-statement

#### 行 183, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 194, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (traceback)
- 符号: import-outside-toplevel

#### 行 240, 列 0
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (8/6)
- 符号: too-many-return-statements

#### 行 240, 列 0
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (20/12)
- 符号: too-many-branches

#### 行 251, 列 12
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'locale' from outer scope (line 9)
- 符号: redefined-outer-name

#### 行 251, 列 12
- 类型: warning
- 代码: W0404
- 描述: Reimport 'locale' (imported line 9)
- 符号: reimported

#### 行 251, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (locale)
- 符号: import-outside-toplevel

#### 行 257, 列 32
- 类型: warning
- 代码: W4902
- 描述: Using deprecated method getdefaultlocale()
- 符号: deprecated-method

#### 行 274, 列 15
- 类型: warning
- 代码: W0705
- 描述: Catching previously caught exception type ValueError
- 符号: duplicate-except

#### 行 285, 列 24
- 类型: convention
- 代码: C0207
- 描述: Use system_locale.split('_', maxsplit=1)[0] instead
- 符号: use-maxsplit-arg

#### 行 292, 列 16
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "elif" after "return", remove the leading "el" from "elif"
- 符号: no-else-return

#### 行 303, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "elif" after "return", remove the leading "el" from "elif"
- 符号: no-else-return

#### 行 352, 列 0
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 367, 列 28
- 类型: warning
- 代码: W4902
- 描述: Using deprecated method getdefaultlocale()
- 符号: deprecated-method

#### 行 384, 列 11
- 类型: warning
- 代码: W0705
- 描述: Catching previously caught exception type ValueError
- 符号: duplicate-except

## 文件: src\battery_analysis\i18n\language_manager.py

### 问题统计
- 问题总数: 14
- 警告(Warning): 9
- 规范(Convention): 3
- 重构(Refactor): 2

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 11, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused List imported from typing
- 符号: unused-import

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import get_available_locales
- 符号: unused-import

#### 行 135, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 156, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 174, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (._po_translator)
- 符号: import-outside-toplevel

#### 行 219, 列 34
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'locale_code'
- 符号: unused-argument

#### 行 251, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 298, 列 34
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'locale_code'
- 符号: unused-argument

#### 行 298, 列 52
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'output_path'
- 符号: unused-argument

#### 行 310, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (json)
- 符号: import-outside-toplevel

#### 行 310, 列 12
- 类型: warning
- 代码: W0611
- 描述: Unused import json
- 符号: unused-import

#### 行 368, 列 4
- 类型: warning
- 代码: W0603
- 描述: Using the global statement
- 符号: global-statement

#### 行 375, 列 0
- 类型: convention
- 代码: C0305
- 描述: Trailing newlines
- 符号: trailing-newlines

## 文件: src\battery_analysis\i18n\preferences_dialog.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 4
- 重构(Refactor): 1

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused PyQt6.QtGui imported as QG
- 符号: unused-import

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import get_available_locales
- 符号: unused-import

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import set_locale
- 符号: unused-import

#### 行 19, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (13/7)
- 符号: too-many-instance-attributes

## 文件: src\battery_analysis\infrastructure\repositories\battery_repository_impl.py

### 问题统计
- 问题总数: 1
- 规范(Convention): 1

### 详细问题
#### 行 183, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\infrastructure\services\battery_analysis_service_impl.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 1
- 规范(Convention): 4

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 213, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 217, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.data_utils.detect_outliers)
- 符号: import-outside-toplevel

#### 行 225, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 252, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\application_initializer.py

### 问题统计
- 问题总数: 19
- 警告(Warning): 17
- 规范(Convention): 2

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import tempfile
- 符号: unused-import

#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import datetime
- 符号: unused-import

#### 行 25, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 42, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.error_report_generator.generate_error_report)
- 符号: import-outside-toplevel

#### 行 45, 列 20
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 46, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 47, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 74, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 75, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 87, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'qt_message_handler'
- 符号: unused-variable

#### 行 104, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.version.Version)
- 符号: import-outside-toplevel

#### 行 135, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 136, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 159, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 160, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 179, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 192, 列 35
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'window'
- 符号: unused-argument

#### 行 198, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\battery_chart_viewer.py

### 问题统计
- 问题总数: 72
- 警告(Warning): 28
- 规范(Convention): 21
- 重构(Refactor): 23

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (2183/1000)
- 符号: too-many-lines

#### 行 112, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (27/7)
- 符号: too-many-instance-attributes

#### 行 146, 列 23
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'data_path' from outer scope (line 2169)
- 符号: redefined-outer-name

#### 行 220, 列 28
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'data_path' from outer scope (line 2169)
- 符号: redefined-outer-name

#### 行 401, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 417, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 433, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 480, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 529, 列 15
- 类型: convention
- 代码: C1805
- 描述: "file_size == 0" can be simplified to "not file_size", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 538, 列 63
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'f' from outer scope (line 2141)
- 符号: redefined-outer-name

#### 行 556, 列 15
- 类型: convention
- 代码: C1805
- 描述: "self.intBatteryNum == 0" can be simplified to "not self.intBatteryNum", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 623, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (7/5)
- 符号: too-many-nested-blocks

#### 行 623, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 625, 列 15
- 类型: convention
- 代码: C1805
- 描述: "loop == 0" can be simplified to "not loop", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 639, 列 28
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 686, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (6/5)
- 符号: too-many-positional-arguments

#### 行 707, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 726, 列 27
- 类型: convention
- 代码: C1805
- 描述: "charge_diff == 0" can be simplified to "not charge_diff", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 739, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 769, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (67/50)
- 符号: too-many-statements

#### 行 919, 列 22
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'dirs'
- 符号: unused-variable

#### 行 931, 列 20
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 952, 列 20
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 962, 列 12
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'traceback' from outer scope (line 30)
- 符号: redefined-outer-name

#### 行 962, 列 12
- 类型: warning
- 代码: W0404
- 描述: Reimport 'traceback' (imported line 30)
- 符号: reimported

#### 行 962, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (traceback)
- 符号: import-outside-toplevel

#### 行 965, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (66/50)
- 符号: too-many-statements

#### 行 1049, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (datetime)
- 符号: import-outside-toplevel

#### 行 1098, 列 8
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'matplotlib' from outer scope (line 37)
- 符号: redefined-outer-name

#### 行 1098, 列 8
- 类型: warning
- 代码: W0404
- 描述: Reimport 'matplotlib' (imported line 37)
- 符号: reimported

#### 行 1098, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib)
- 符号: import-outside-toplevel

#### 行 1099, 列 8
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'plt' from outer scope (line 38)
- 符号: redefined-outer-name

#### 行 1099, 列 8
- 类型: warning
- 代码: W0404
- 描述: Reimport 'matplotlib.pyplot' (imported line 38)
- 符号: reimported

#### 行 1099, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib.pyplot)
- 符号: import-outside-toplevel

#### 行 1099, 列 8
- 类型: warning
- 代码: W0611
- 描述: Unused matplotlib.pyplot imported as plt
- 符号: unused-import

#### 行 1170, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (datetime)
- 符号: import-outside-toplevel

#### 行 1172, 列 12
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 行 1177, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.version.Version)
- 符号: import-outside-toplevel

#### 行 1217, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.version.Version)
- 符号: import-outside-toplevel

#### 行 1224, 列 4
- 类型: refactor
- 代码: R1710
- 描述: Either all return statements in a function should return an expression, or none of them should.
- 符号: inconsistent-return-statements

#### 行 1313, 列 12
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise ImportError(f'PyQt6依赖缺失: {e}. 请确保已正确安装PyQt6') from e'
- 符号: raise-missing-from

#### 行 1314, 列 15
- 类型: warning
- 代码: W0705
- 描述: Catching previously caught exception type ImportError
- 符号: duplicate-except

#### 行 1396, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (10/5)
- 符号: too-many-positional-arguments

#### 行 1514, 列 16
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 1561, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (threading)
- 符号: import-outside-toplevel

#### 行 1688, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (7/5)
- 符号: too-many-positional-arguments

#### 行 1731, 列 32
- 类型: warning
- 代码: W0108
- 描述: Lambda may not be necessary
- 符号: unnecessary-lambda

#### 行 1736, 列 32
- 类型: warning
- 代码: W0108
- 描述: Lambda may not be necessary
- 符号: unnecessary-lambda

#### 行 1742, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'file_button_states' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1765, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (7/5)
- 符号: too-many-positional-arguments

#### 行 1835, 列 0
- 类型: warning
- 代码: W0311
- 描述: Bad indentation. Found 24 spaces, expected 20
- 符号: bad-indentation

#### 行 1847, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'filter_button_state' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1896, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'battery_button_states' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1904, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (8/5)
- 符号: too-many-positional-arguments

#### 行 1904, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (56/50)
- 符号: too-many-statements

#### 行 1905, 列 38
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'check_filter'
- 符号: unused-argument

#### 行 1965, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1974, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1982, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1997, 列 0
- 类型: warning
- 代码: W0311
- 描述: Bad indentation. Found 24 spaces, expected 16
- 符号: bad-indentation

#### 行 2030, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (6/5)
- 符号: too-many-positional-arguments

#### 行 2037, 列 21
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"boxstyle": 'round,pad=0.5', "fc": 'yellow', "alpha": 0.7}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 2038, 列 27
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"arrowstyle": '->'}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 2043, 列 12
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (14/12)
- 符号: too-many-branches

#### 行 2044, 列 16
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 2079, 列 28
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 2115, 列 4
- 类型: warning
- 代码: W0105
- 描述: String statement has no effect
- 符号: pointless-string-statement

#### 行 2123, 列 4
- 类型: warning
- 代码: W0404
- 描述: Reimport 'sys' (imported line 26)
- 符号: reimported

#### 行 2123, 列 4
- 类型: convention
- 代码: C0412
- 描述: Imports from package sys are not grouped
- 符号: ungrouped-imports

#### 行 2124, 列 4
- 类型: convention
- 代码: C0412
- 描述: Imports from package PyQt6 are not grouped
- 符号: ungrouped-imports

#### 行 2131, 列 8
- 类型: convention
- 代码: C0412
- 描述: Imports from package battery_analysis are not grouped
- 符号: ungrouped-imports

#### 行 2131, 列 8
- 类型: warning
- 代码: W0611
- 描述: Unused apply_modern_theme imported from battery_analysis.ui.styles.style_manager
- 符号: unused-import

## 文件: src\battery_analysis\main\business_logic\battery_calculator.py

### 问题统计
- 问题总数: 1
- 重构(Refactor): 1

### 详细问题
#### 行 51, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

## 文件: src\battery_analysis\main\business_logic\data_processor.py

### 问题统计
- 问题总数: 13
- 错误(Error): 1
- 警告(Warning): 9
- 规范(Convention): 3

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import csv
- 符号: unused-import

#### 行 11, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Path imported from pathlib
- 符号: unused-import

#### 行 64, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 89, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (concurrent.futures.ProcessPoolExecutor, concurrent.futures.as_completed)
- 符号: import-outside-toplevel

#### 行 110, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 227, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 406, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.main_window.Checker)
- 符号: import-outside-toplevel

#### 行 406, 列 12
- 类型: error
- 代码: E0611
- 描述: No name 'Checker' in module 'battery_analysis.main.main_window'
- 符号: no-name-in-module

#### 行 465, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (concurrent.futures.ProcessPoolExecutor, concurrent.futures.as_completed)
- 符号: import-outside-toplevel

#### 行 487, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 539, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 613, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute '_error_option' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 637, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute '_error_option' defined outside __init__
- 符号: attribute-defined-outside-init

## 文件: src\battery_analysis\main\business_logic\environment_manager.py

### 问题统计
- 问题总数: 8
- 警告(Warning): 6
- 规范(Convention): 2

### 详细问题
#### 行 11, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused EnvironmentType imported from battery_analysis.utils.environment_utils
- 符号: unused-import

#### 行 34, 列 34
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_service of a client class
- 符号: protected-access

#### 行 50, 列 38
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_service of a client class
- 符号: protected-access

#### 行 55, 列 20
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'EnvironmentType' from outer scope (line 11)
- 符号: redefined-outer-name

#### 行 55, 列 20
- 类型: warning
- 代码: W0404
- 描述: Reimport 'EnvironmentType' (imported line 11)
- 符号: reimported

#### 行 55, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.environment_utils.EnvironmentType)
- 符号: import-outside-toplevel

#### 行 59, 列 16
- 类型: warning
- 代码: W0404
- 描述: Reimport 'EnvironmentType' (imported line 11)
- 符号: reimported

#### 行 59, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.environment_utils.EnvironmentType)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\business_logic\help_manager.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 3
- 规范(Convention): 2

### 详细问题
#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import subprocess
- 符号: unused-import

#### 行 11, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Path imported from pathlib
- 符号: unused-import

#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QtCore imported from PyQt6 as QC
- 符号: unused-import

#### 行 85, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtGui.QDesktopServices)
- 符号: import-outside-toplevel

#### 行 86, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtCore.QUrl)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\business_logic\user_settings_manager.py

### 问题统计
- 问题总数: 6
- 警告(Warning): 1
- 重构(Refactor): 5

### 详细问题
#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 39, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (14/12)
- 符号: too-many-branches

#### 行 39, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (53/50)
- 符号: too-many-statements

#### 行 152, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (25/12)
- 符号: too-many-branches

#### 行 152, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (65/50)
- 符号: too-many-statements

#### 行 156, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

## 文件: src\battery_analysis\main\business_logic\validation_manager.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 1
- 重构(Refactor): 2

### 详细问题
#### 行 16, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused PyQt6.QtWidgets imported as QW
- 符号: unused-import

#### 行 172, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (17/12)
- 符号: too-many-branches

#### 行 197, 列 12
- 类型: refactor
- 代码: R1723
- 描述: Unnecessary "elif" after "break", remove the leading "el" from "elif"
- 符号: no-else-break

## 文件: src\battery_analysis\main\business_logic\version_manager.py

### 问题统计
- 问题总数: 24
- 警告(Warning): 12
- 规范(Convention): 6
- 重构(Refactor): 6

### 详细问题
#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused List imported from typing
- 符号: unused-import

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 18, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused PyQt6.QtWidgets imported as QW
- 符号: unused-import

#### 行 21, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused _ imported from battery_analysis.i18n.language_manager
- 符号: unused-import

#### 行 39, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (14/12)
- 符号: too-many-branches

#### 行 39, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (67/50)
- 符号: too-many-statements

#### 行 59, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 59, 列 33
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 63, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.utils.file_utils.FileUtils)
- 符号: import-outside-toplevel

#### 行 65, 列 49
- 类型: convention
- 代码: C1805
- 描述: "os.path.getsize(strCsvMd5Path) != 0" can be simplified to "os.path.getsize(strCsvMd5Path)", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 67, 列 20
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 108, 列 20
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 117, 列 27
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_service of a client class
- 符号: protected-access

#### 行 123, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (win32api)
- 符号: import-outside-toplevel

#### 行 124, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (win32con)
- 符号: import-outside-toplevel

#### 行 131, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (23/12)
- 符号: too-many-branches

#### 行 131, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (80/50)
- 符号: too-many-statements

#### 行 183, 列 32
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'version_major'
- 符号: unused-variable

#### 行 184, 列 32
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'version_minor'
- 符号: unused-variable

#### 行 207, 列 35
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_service of a client class
- 符号: protected-access

#### 行 215, 列 28
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (win32api)
- 符号: import-outside-toplevel

#### 行 216, 列 28
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (win32con)
- 符号: import-outside-toplevel

#### 行 224, 列 23
- 类型: warning
- 代码: W0705
- 描述: Catching previously caught exception type PermissionError
- 符号: duplicate-except

#### 行 246, 列 23
- 类型: warning
- 代码: W0705
- 描述: Catching previously caught exception type PermissionError
- 符号: duplicate-except

## 文件: src\battery_analysis\main\business_logic\visualization_manager.py

### 问题统计
- 问题总数: 13
- 警告(Warning): 6
- 规范(Convention): 6
- 重构(Refactor): 1

### 详细问题
#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import matplotlib
- 符号: unused-import

#### 行 11, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "subprocess" should be placed before third party import "matplotlib"
- 符号: wrong-import-order

#### 行 12, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "sys" should be placed before third party import "matplotlib"
- 符号: wrong-import-order

#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import sys
- 符号: unused-import

#### 行 13, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "traceback" should be placed before third party import "matplotlib"
- 符号: wrong-import-order

#### 行 14, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "pathlib.Path" should be placed before third party import "matplotlib"
- 符号: wrong-import-order

#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Path imported from pathlib
- 符号: unused-import

#### 行 15, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "typing.Optional" should be placed before third party import "matplotlib"
- 符号: wrong-import-order

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 19, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QtCore imported from PyQt6 as QC
- 符号: unused-import

#### 行 20, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QtGui imported from PyQt6 as QG
- 符号: unused-import

#### 行 64, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (matplotlib.pyplot)
- 符号: import-outside-toplevel

#### 行 110, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (52/50)
- 符号: too-many-statements

## 文件: src\battery_analysis\main\commands\command.py

### 问题统计
- 问题总数: 47
- 错误(Error): 6
- 警告(Warning): 41

### 详细问题
#### 行 25, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 49, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 50, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 76, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 77, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 102, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 103, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 128, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 129, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 154, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 155, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 180, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 181, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 185, 列 0
- 类型: error
- 代码: E0102
- 描述: class already defined line 28
- 符号: function-redefined

#### 行 206, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 207, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 211, 列 0
- 类型: error
- 代码: E0102
- 描述: class already defined line 54
- 符号: function-redefined

#### 行 233, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 234, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 238, 列 0
- 类型: error
- 代码: E0102
- 描述: class already defined line 159
- 符号: function-redefined

#### 行 259, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 260, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 264, 列 0
- 类型: error
- 代码: E0102
- 描述: class already defined line 133
- 符号: function-redefined

#### 行 285, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 286, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 290, 列 0
- 类型: error
- 代码: E0102
- 描述: class already defined line 81
- 符号: function-redefined

#### 行 311, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 312, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 316, 列 0
- 类型: error
- 代码: E0102
- 描述: class already defined line 107
- 符号: function-redefined

#### 行 337, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 338, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 363, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 364, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 390, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 391, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 417, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 418, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 443, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 444, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 469, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 470, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 497, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 498, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 522, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 523, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 550, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 551, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

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
- 规范(Convention): 1

### 详细问题
#### 行 29, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.service_container.get_service_container)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\controllers\validation_controller.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 3
- 规范(Convention): 1
- 重构(Refactor): 1

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

#### 行 131, 列 17
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

## 文件: src\battery_analysis\main\controllers\visualizer_controller.py

### 问题统计
- 问题总数: 12
- 警告(Warning): 3
- 规范(Convention): 5
- 重构(Refactor): 4

### 详细问题
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

#### 行 118, 列 28
- 类型: convention
- 代码: C1804
- 描述: "xml_path != ''" can be simplified to "xml_path", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

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

## 文件: src\battery_analysis\main\dialogs\data_error_dialog.py

### 问题统计
- 问题总数: 6
- 警告(Warning): 4
- 规范(Convention): 1
- 重构(Refactor): 1

### 详细问题
#### 行 4, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QtCore imported from PyQt6 as QC
- 符号: unused-import

#### 行 20, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (52/50)
- 符号: too-many-statements

#### 行 56, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'retry_option' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 62, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'default_option' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 67, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'cancel_option' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 135, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (os)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\factories\visualizer_factory.py

### 问题统计
- 问题总数: 6
- 警告(Warning): 4
- 规范(Convention): 2

### 详细问题
#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 129, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _search_for_data_files of a client class
- 符号: protected-access

#### 行 133, 列 16
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _search_for_data_files of a client class
- 符号: protected-access

#### 行 140, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.controllers.main_controller.MainController)
- 符号: import-outside-toplevel

#### 行 140, 列 20
- 类型: warning
- 代码: W0611
- 描述: Unused MainController imported from battery_analysis.main.controllers.main_controller
- 符号: unused-import

#### 行 141, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.service_container.get_service_container)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\handlers\temperature_handler.py

### 问题统计
- 问题总数: 4
- 警告(Warning): 1
- 规范(Convention): 1
- 重构(Refactor): 2

### 详细问题
#### 行 43, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 47, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 59, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 86, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\initialization\initialization_orchestrator.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 3

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 83, 列 12
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 83, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\initialization\initialization_step.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 2

### 详细问题
#### 行 40, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 82, 列 26
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'main_window'
- 符号: unused-argument

## 文件: src\battery_analysis\main\initialization\steps\basic_attributes_step.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 4
- 规范(Convention): 1

### 详细问题
#### 行 29, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.__version__)
- 符号: import-outside-toplevel

#### 行 36, 列 12
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _services of a client class
- 符号: protected-access

#### 行 37, 列 12
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _controllers of a client class
- 符号: protected-access

#### 行 57, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 57, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\initialization\steps\battery_config_initialization_step.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 2

### 详细问题
#### 行 54, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 55, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

## 文件: src\battery_analysis\main\initialization\steps\command_manager_initialization_step.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 2

### 详细问题
#### 行 32, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 32, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\initialization\steps\environment_initialization_step.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 2
- 规范(Convention): 3

### 详细问题
#### 行 31, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 46, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 49, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (ctypes)
- 符号: import-outside-toplevel

#### 行 59, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 59, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\initialization\steps\handlers_initialization_step.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 2

### 详细问题
#### 行 49, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 49, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\initialization\steps\language_initialization_step.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 5

### 详细问题
#### 行 37, 列 16
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _initialize_environment_info of a client class
- 符号: protected-access

#### 行 40, 列 16
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _ensure_env_info_keys of a client class
- 符号: protected-access

#### 行 44, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 44, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 59, 列 70
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _on_language_changed of a client class
- 符号: protected-access

## 文件: src\battery_analysis\main\initialization\steps\managers_initialization_step.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 2

### 详细问题
#### 行 79, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 79, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\initialization\steps\presenters_initialization_step.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 2

### 详细问题
#### 行 33, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 33, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\initialization\steps\processors_initialization_step.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 2

### 详细问题
#### 行 32, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 32, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\initialization\steps\services_initialization_step.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 3

### 详细问题
#### 行 29, 列 12
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _service_container of a client class
- 符号: protected-access

#### 行 32, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 32, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\initialization\steps\styles_initialization_step.py

### 问题统计
- 问题总数: 1
- 规范(Convention): 1

### 详细问题
#### 行 28, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.ui.styles.style_manager)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\initialization\steps\ui_setup_step.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 3

### 详细问题
#### 行 29, 列 34
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_controller of a client class
- 符号: protected-access

#### 行 42, 列 8
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 42, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\interfaces\ivisualizer.py

### 问题统计
- 问题总数: 8
- 警告(Warning): 8

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 30, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 43, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 50, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 60, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 70, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 80, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 90, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\main\main_window.py

### 问题统计
- 问题总数: 19
- 警告(Warning): 14
- 规范(Convention): 1
- 重构(Refactor): 4

### 详细问题
#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import re
- 符号: unused-import

#### 行 17, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import time
- 符号: unused-import

#### 行 19, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Path imported from pathlib
- 符号: unused-import

#### 行 20, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 23, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import matplotlib
- 符号: unused-import

#### 行 29, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused get_language_manager imported from battery_analysis.i18n.language_manager
- 符号: unused-import

#### 行 32, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused resources_rc imported from battery_analysis.resources
- 符号: unused-import

#### 行 41, 列 0
- 类型: refactor
- 代码: R0904
- 描述: Too many public methods (45/20)
- 符号: too-many-public-methods

#### 行 67, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listCurrentLevel' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 70, 列 12
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listCurrentLevel' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 72, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'listVoltageLevel' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 120, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 232, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 308, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 314, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 320, 列 11
- 类型: refactor
- 代码: R1701
- 描述: Consider merging these isinstance calls to isinstance(focused_widget, (QW.QLineEdit, QW.QTextEdit))
- 符号: consider-merging-isinstance

#### 行 423, 列 42
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'index'
- 符号: unused-argument

#### 行 529, 列 4
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.application_initializer.ApplicationInitializer)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\managers\analysis_runner.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 2
- 规范(Convention): 1

### 详细问题
#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 95, 列 57
- 类型: convention
- 代码: C1805
- 描述: "self.main_window.spinBox_Temperature.value() == 0" can be simplified to "not self.main_window.spinBox_Temperature.value()", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 153, 列 26
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_controller of a client class
- 符号: protected-access

## 文件: src\battery_analysis\main\managers\command_manager.py

### 问题统计
- 问题总数: 4
- 警告(Warning): 4

### 详细问题
#### 行 87, 列 12
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 87, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 88, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 91, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

## 文件: src\battery_analysis\main\managers\environment_manager.py

### 问题统计
- 问题总数: 4
- 警告(Warning): 2
- 规范(Convention): 2

### 详细问题
#### 行 23, 列 34
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_service of a client class
- 符号: protected-access

#### 行 40, 列 38
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_service of a client class
- 符号: protected-access

#### 行 45, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.environment_utils.EnvironmentType)
- 符号: import-outside-toplevel

#### 行 49, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.environment_utils.EnvironmentType)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\managers\path_manager.py

### 问题统计
- 问题总数: 4
- 警告(Warning): 2
- 规范(Convention): 2

### 详细问题
#### 行 4, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Path imported from pathlib
- 符号: unused-import

#### 行 93, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 162, 列 11
- 类型: convention
- 代码: C1804
- 描述: "selected_dir != ''" can be simplified to "selected_dir", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

#### 行 175, 列 11
- 类型: convention
- 代码: C1804
- 描述: "selected_dir != ''" can be simplified to "selected_dir", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

## 文件: src\battery_analysis\main\managers\report_manager.py

### 问题统计
- 问题总数: 4
- 警告(Warning): 4

### 详细问题
#### 行 61, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 68, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 91, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 98, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

## 文件: src\battery_analysis\main\managers\test_profile_manager.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 1
- 规范(Convention): 1

### 详细问题
#### 行 90, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.handlers.temperature_handler.TemperatureType)
- 符号: import-outside-toplevel

#### 行 90, 列 12
- 类型: warning
- 代码: W0611
- 描述: Unused TemperatureType imported from battery_analysis.main.handlers.temperature_handler
- 符号: unused-import

## 文件: src\battery_analysis\main\managers\visualization_manager.py

### 问题统计
- 问题总数: 1
- 规范(Convention): 1

### 详细问题
#### 行 70, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.dialogs.data_error_dialog.DataErrorRecoveryDialog)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\presenters\main_presenter.py

### 问题统计
- 问题总数: 8
- 警告(Warning): 6
- 重构(Refactor): 2

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Dict imported from typing
- 符号: unused-import

#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused List imported from typing
- 符号: unused-import

#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused CalculateBatteryUseCase imported from battery_analysis.application.usecases.calculate_battery_use_case
- 符号: unused-import

#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused AnalyzeDataUseCase imported from battery_analysis.application.usecases.analyze_data_use_case
- 符号: unused-import

#### 行 11, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused GenerateReportUseCase imported from battery_analysis.application.usecases.generate_report_use_case
- 符号: unused-import

#### 行 14, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (18/7)
- 符号: too-many-instance-attributes

#### 行 257, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

## 文件: src\battery_analysis\main\services\__init__.py

### 问题统计
- 问题总数: 1
- 规范(Convention): 1

### 详细问题
#### 行 44, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\services\application_service.py

### 问题统计
- 问题总数: 9
- 警告(Warning): 7
- 规范(Convention): 1
- 重构(Refactor): 1

### 详细问题
#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Dict imported from typing
- 符号: unused-import

#### 行 11, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Path imported from pathlib
- 符号: unused-import

#### 行 17, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused get_environment_detector imported from battery_analysis.utils.environment_utils
- 符号: unused-import

#### 行 20, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (19/7)
- 符号: too-many-instance-attributes

#### 行 143, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.event_bus.EventType)
- 符号: import-outside-toplevel

#### 行 147, 列 12
- 类型: warning
- 代码: W0108
- 描述: Lambda may not be necessary
- 符号: unnecessary-lambda

#### 行 150, 列 12
- 类型: warning
- 代码: W0108
- 描述: Lambda may not be necessary
- 符号: unnecessary-lambda

#### 行 153, 列 12
- 类型: warning
- 代码: W0108
- 描述: Lambda may not be necessary
- 符号: unnecessary-lambda

#### 行 184, 列 37
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'event'
- 符号: unused-argument

## 文件: src\battery_analysis\main\services\config_service.py

### 问题统计
- 问题总数: 12
- 警告(Warning): 8
- 规范(Convention): 3
- 重构(Refactor): 1

### 详细问题
#### 行 48, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 66, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 78, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 87, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 123, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 139, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 168, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 187, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 206, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 210, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 222, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.config_utils.find_config_file)
- 符号: import-outside-toplevel

#### 行 227, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

## 文件: src\battery_analysis\main\services\config_service_interface.py

### 问题统计
- 问题总数: 10
- 警告(Warning): 8
- 规范(Convention): 2

### 详细问题
#### 行 31, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 45, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 55, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 68, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 78, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 91, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 104, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 106, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 118, 列 0
- 类型: convention
- 代码: C0327
- 描述: Mixed line endings LF and CRLF
- 符号: mixed-line-endings

#### 行 118, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\main\services\data_processing_service_interface.py

### 问题统计
- 问题总数: 14
- 警告(Warning): 14

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Path imported from pathlib
- 符号: unused-import

#### 行 32, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 45, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 60, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 76, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 91, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 106, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 119, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 132, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 136, 列 46
- 类型: warning
- 代码: W0622
- 描述: Redefining built-in 'format'
- 符号: redefined-builtin

#### 行 148, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 161, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 176, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\main\services\document_service_interface.py

### 问题统计
- 问题总数: 13
- 警告(Warning): 12
- 重构(Refactor): 1

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Union imported from typing
- 符号: unused-import

#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Path imported from pathlib
- 符号: unused-import

#### 行 30, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 44, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 60, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 76, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 89, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 103, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 118, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 121, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (8/5)
- 符号: too-many-positional-arguments

#### 行 139, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 156, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 170, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\main\services\environment_service.py

### 问题统计
- 问题总数: 4
- 警告(Warning): 4

### 详细问题
#### 行 79, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 86, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 93, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 100, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\main\services\event_bus.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 2

### 详细问题
#### 行 11, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Set imported from typing
- 符号: unused-import

#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QThread imported from PyQt6.QtCore
- 符号: unused-import

## 文件: src\battery_analysis\main\services\file_service.py

### 问题统计
- 问题总数: 6
- 警告(Warning): 1
- 规范(Convention): 4
- 重构(Refactor): 1

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 120, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 140, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (win32api)
- 符号: import-outside-toplevel

#### 行 141, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (win32con)
- 符号: import-outside-toplevel

#### 行 245, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (win32api)
- 符号: import-outside-toplevel

#### 行 246, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (win32con)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\services\file_service_interface.py

### 问题统计
- 问题总数: 10
- 警告(Warning): 10

### 详细问题
#### 行 30, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 44, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 58, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 71, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 85, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 98, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 111, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 125, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 139, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 152, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\main\services\i18n_service.py

### 问题统计
- 问题总数: 9
- 警告(Warning): 3
- 规范(Convention): 1
- 重构(Refactor): 5

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Dict imported from typing
- 符号: unused-import

#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 87, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.i18n.language_manager.get_language_manager)
- 符号: import-outside-toplevel

#### 行 118, 列 16
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 143, 列 16
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 167, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 184, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 202, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 212, 列 49
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'default_text'
- 符号: unused-argument

## 文件: src\battery_analysis\main\services\progress_service.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 2
- 重构(Refactor): 1

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 283, 列 12
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

## 文件: src\battery_analysis\main\services\service_container.py

### 问题统计
- 问题总数: 32
- 警告(Warning): 10
- 规范(Convention): 20
- 重构(Refactor): 2

### 详细问题
#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused List imported from typing
- 符号: unused-import

#### 行 37, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 51, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 64, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 77, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 90, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 100, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 103, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (8/7)
- 符号: too-many-instance-attributes

#### 行 163, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.config_service.ConfigService)
- 符号: import-outside-toplevel

#### 行 164, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.event_bus.EventBus)
- 符号: import-outside-toplevel

#### 行 165, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.environment_service.EnvironmentService)
- 符号: import-outside-toplevel

#### 行 166, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.file_service.FileService)
- 符号: import-outside-toplevel

#### 行 167, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.i18n_service.I18nService)
- 符号: import-outside-toplevel

#### 行 168, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.progress_service.ProgressService)
- 符号: import-outside-toplevel

#### 行 169, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.validation_service.ValidationService)
- 符号: import-outside-toplevel

#### 行 190, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.infrastructure.repositories.battery_repository_impl.BatteryRepositoryImpl)
- 符号: import-outside-toplevel

#### 行 191, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.infrastructure.services.battery_analysis_service_impl.BatteryAnalysisServiceImpl)
- 符号: import-outside-toplevel

#### 行 214, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.application.usecases.calculate_battery_use_case.CalculateBatteryUseCase)
- 符号: import-outside-toplevel

#### 行 215, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.application.usecases.analyze_data_use_case.AnalyzeDataUseCase)
- 符号: import-outside-toplevel

#### 行 216, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.application.usecases.generate_report_use_case.GenerateReportUseCase)
- 符号: import-outside-toplevel

#### 行 263, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.application_service.ApplicationService)
- 符号: import-outside-toplevel

#### 行 283, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.controllers.file_controller.FileController)
- 符号: import-outside-toplevel

#### 行 284, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.controllers.main_controller.MainController)
- 符号: import-outside-toplevel

#### 行 285, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.controllers.validation_controller.ValidationController)
- 符号: import-outside-toplevel

#### 行 286, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.controllers.visualizer_controller.VisualizerController)
- 符号: import-outside-toplevel

#### 行 418, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 523, 列 0
- 类型: convention
- 代码: C0206
- 描述: Consider iterating with .items()
- 符号: consider-using-dict-items

#### 行 523, 列 47
- 类型: convention
- 代码: C1805
- 描述: "in_degree[node] == 0" can be simplified to "not in_degree[node]", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 533, 列 19
- 类型: convention
- 代码: C1805
- 描述: "in_degree[neighbor] == 0" can be simplified to "not in_degree[neighbor]", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 609, 列 18
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'service_class'
- 符号: unused-variable

#### 行 710, 列 4
- 类型: warning
- 代码: W0603
- 描述: Using the global statement
- 符号: global-statement

#### 行 723, 列 4
- 类型: warning
- 代码: W0603
- 描述: Using the global statement
- 符号: global-statement

## 文件: src\battery_analysis\main\services\validation_service.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 2

### 详细问题
#### 行 11, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Dict imported from typing
- 符号: unused-import

#### 行 99, 列 59
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'f'
- 符号: unused-variable

## 文件: src\battery_analysis\main\services\validation_service_interface.py

### 问题统计
- 问题总数: 9
- 警告(Warning): 9

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Dict imported from typing
- 符号: unused-import

#### 行 29, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 42, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 55, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 70, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 83, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 96, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 109, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 122, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\main\ui\language_handler.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 1
- 规范(Convention): 2

### 详细问题
#### 行 96, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 110, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.i18n._)
- 符号: import-outside-toplevel

#### 行 161, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\ui_components\__init__.py

### 问题统计
- 问题总数: 1
- 规范(Convention): 1

### 详细问题
#### 行 35, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\ui_components\config_manager.py

### 问题统计
- 问题总数: 14
- 警告(Warning): 6
- 规范(Convention): 6
- 重构(Refactor): 2

### 详细问题
#### 行 13, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 15, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 21, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused safe_float_convert imported from battery_analysis.utils.config_parser
- 符号: unused-import

#### 行 21, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused safe_int_convert imported from battery_analysis.utils.config_parser
- 符号: unused-import

#### 行 56, 列 29
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_service of a client class
- 符号: protected-access

#### 行 63, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.config_utils.find_config_file)
- 符号: import-outside-toplevel

#### 行 69, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.config_utils.find_config_file)
- 符号: import-outside-toplevel

#### 行 107, 列 23
- 类型: convention
- 代码: C1804
- 描述: "item != ''" can be simplified to "item", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

#### 行 132, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (26/12)
- 符号: too-many-branches

#### 行 132, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (57/50)
- 符号: too-many-statements

#### 行 215, 列 34
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_controller of a client class
- 符号: protected-access

#### 行 226, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.i18n.language_manager._)
- 符号: import-outside-toplevel

#### 行 227, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets)
- 符号: import-outside-toplevel

#### 行 311, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.utils.Checker)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\ui_components\dialog_manager.py

### 问题统计
- 问题总数: 5
- 警告(Warning): 3
- 规范(Convention): 1
- 重构(Refactor): 1

### 详细问题
#### 行 16, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import traceback
- 符号: unused-import

#### 行 63, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (time)
- 符号: import-outside-toplevel

#### 行 168, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (52/50)
- 符号: too-many-statements

#### 行 239, 列 16
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _open_data_directory_dialog of a client class
- 符号: protected-access

#### 行 273, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\main\ui_components\dialogs.py

### 问题统计
- 问题总数: 12
- 警告(Warning): 6
- 规范(Convention): 5
- 重构(Refactor): 1

### 详细问题
#### 行 49, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.__version__)
- 符号: import-outside-toplevel

#### 行 64, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.i18n.preferences_dialog.PreferencesDialog)
- 符号: import-outside-toplevel

#### 行 90, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.ui.user_manual_dialog.UserManualDialog)
- 符号: import-outside-toplevel

#### 行 106, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtGui.QDesktopServices)
- 符号: import-outside-toplevel

#### 行 107, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtCore.QUrl)
- 符号: import-outside-toplevel

#### 行 183, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _open_report of a client class
- 符号: protected-access

#### 行 186, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _open_report_path of a client class
- 符号: protected-access

#### 行 189, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 277, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute '_error_option' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 283, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "elif" after "return", remove the leading "el" from "elif"
- 符号: no-else-return

#### 行 286, 列 16
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _open_data_directory_dialog of a client class
- 符号: protected-access

#### 行 303, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute '_error_option' defined outside __init__
- 符号: attribute-defined-outside-init

## 文件: src\battery_analysis\main\ui_components\menu_manager.py

### 问题统计
- 问题总数: 4
- 警告(Warning): 2
- 重构(Refactor): 2

### 详细问题
#### 行 18, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused PyQt6.QtWidgets imported as QW
- 符号: unused-import

#### 行 39, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (27/12)
- 符号: too-many-branches

#### 行 39, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (78/50)
- 符号: too-many-statements

#### 行 252, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\main\ui_components\message_manager.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 1
- 规范(Convention): 1

### 详细问题
#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused _ imported from battery_analysis.i18n.language_manager
- 符号: unused-import

#### 行 57, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\ui_components\progress_dialog.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 2

### 详细问题
#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import logging
- 符号: unused-import

#### 行 16, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused PyQt6.QtGui imported as QG
- 符号: unused-import

## 文件: src\battery_analysis\main\ui_components\table_manager.py

### 问题统计
- 问题总数: 2
- 规范(Convention): 2

### 详细问题
#### 行 111, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 118, 列 11
- 类型: convention
- 代码: C1804
- 描述: "self.main_window.test_information != ''" can be simplified to "self.main_window.test_information", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

## 文件: src\battery_analysis\main\ui_components\theme_manager.py

### 问题统计
- 问题总数: 12
- 警告(Warning): 10
- 规范(Convention): 1
- 重构(Refactor): 1

### 详细问题
#### 行 16, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused PyQt6.QtCore imported as QC
- 符号: unused-import

#### 行 74, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (13/12)
- 符号: too-many-branches

#### 行 95, 列 99
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 101, 列 24
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 106, 列 24
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 112, 列 24
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 117, 列 24
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 121, 列 98
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 126, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.ui.styles.style_manager)
- 符号: import-outside-toplevel

#### 行 128, 列 100
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 129, 列 16
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'e'
- 符号: unused-variable

#### 行 170, 列 107
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

## 文件: src\battery_analysis\main\ui_components\ui_manager.py

### 问题统计
- 问题总数: 10
- 警告(Warning): 4
- 规范(Convention): 3
- 重构(Refactor): 3

### 详细问题
#### 行 13, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import re
- 符号: unused-import

#### 行 48, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.ui_components.window_setup.WindowSetup)
- 符号: import-outside-toplevel

#### 行 57, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.ui_components.window_setup.WindowSetup)
- 符号: import-outside-toplevel

#### 行 59, 列 8
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _load_application_icon of a client class
- 符号: protected-access

#### 行 358, 列 8
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (6/5)
- 符号: too-many-positional-arguments

#### 行 406, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.__version__)
- 符号: import-outside-toplevel

#### 行 464, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (26/12)
- 符号: too-many-branches

#### 行 464, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (57/50)
- 符号: too-many-statements

#### 行 545, 列 34
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_controller of a client class
- 符号: protected-access

## 文件: src\battery_analysis\main\ui_components\window_setup.py

### 问题统计
- 问题总数: 2
- 警告(Warning): 1
- 规范(Convention): 1

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QtWidgets imported from PyQt6 as QW
- 符号: unused-import

#### 行 57, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (pathlib.Path)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\utils\__init__.py

### 问题统计
- 问题总数: 1
- 规范(Convention): 1

### 详细问题
#### 行 24, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\main\utils\environment_adapter.py

### 问题统计
- 问题总数: 4
- 警告(Warning): 2
- 规范(Convention): 2

### 详细问题
#### 行 38, 列 26
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_service of a client class
- 符号: protected-access

#### 行 54, 列 26
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_service of a client class
- 符号: protected-access

#### 行 59, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.environment_utils.EnvironmentType)
- 符号: import-outside-toplevel

#### 行 62, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.environment_utils.EnvironmentType)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\utils\file_utils.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 2
- 规范(Convention): 1

### 详细问题
#### 行 103, 列 46
- 类型: warning
- 代码: W0640
- 描述: Cell variable f defined in loop
- 符号: cell-var-from-loop

#### 行 108, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 110, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (logging)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\utils\service_locator.py

### 问题统计
- 问题总数: 11
- 警告(Warning): 10
- 规范(Convention): 1

### 详细问题
#### 行 37, 列 31
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _services of a client class
- 符号: protected-access

#### 行 39, 列 16
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _services of a client class
- 符号: protected-access

#### 行 39, 列 59
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _service_container of a client class
- 符号: protected-access

#### 行 42, 列 16
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _services of a client class
- 符号: protected-access

#### 行 43, 列 15
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _services of a client class
- 符号: protected-access

#### 行 55, 列 34
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _controllers of a client class
- 符号: protected-access

#### 行 57, 列 16
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _controllers of a client class
- 符号: protected-access

#### 行 57, 列 65
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _service_container of a client class
- 符号: protected-access

#### 行 60, 列 16
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _controllers of a client class
- 符号: protected-access

#### 行 61, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

#### 行 61, 列 15
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _controllers of a client class
- 符号: protected-access

## 文件: src\battery_analysis\main\utils\signal_connector.py

### 问题统计
- 问题总数: 11
- 警告(Warning): 7
- 规范(Convention): 3
- 重构(Refactor): 1

### 详细问题
#### 行 13, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Any imported from typing
- 符号: unused-import

#### 行 57, 列 15
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_controller of a client class
- 符号: protected-access

#### 行 61, 列 15
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _get_service of a client class
- 符号: protected-access

#### 行 103, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.services.event_bus.EventType)
- 符号: import-outside-toplevel

#### 行 146, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (54/50)
- 符号: too-many-statements

#### 行 161, 列 15
- 类型: convention
- 代码: C1805
- 描述: "stateindex == 0" can be simplified to "not stateindex", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 182, 列 16
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'ok_button'
- 符号: unused-variable

#### 行 191, 列 24
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _open_report of a client class
- 符号: protected-access

#### 行 195, 列 24
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _open_report_path of a client class
- 符号: protected-access

#### 行 343, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 352, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.main.ui_components.progress_dialog.ProgressDialog)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\main\workers\analysis_worker.py

### 问题统计
- 问题总数: 17
- 警告(Warning): 6
- 规范(Convention): 6
- 重构(Refactor): 5

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
- 代码: R0911
- 描述: Too many return statements (17/6)
- 符号: too-many-return-statements

#### 行 69, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (49/12)
- 符号: too-many-branches

#### 行 69, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (172/50)
- 符号: too-many-statements

#### 行 87, 列 15
- 类型: warning
- 代码: W0705
- 描述: Catching previously caught exception type RuntimeError
- 符号: duplicate-except

#### 行 90, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 107, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.battery_analysis)
- 符号: import-outside-toplevel

#### 行 131, 列 15
- 类型: convention
- 代码: C1804
- 描述: "self.str_error_battery == ''" can be simplified to "not self.str_error_battery", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

#### 行 274, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.file_writer)
- 符号: import-outside-toplevel

#### 行 301, 列 23
- 类型: convention
- 代码: C1804
- 描述: "self.str_error_xlsx != ''" can be simplified to "self.str_error_xlsx", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

#### 行 346, 列 19
- 类型: convention
- 代码: C1804
- 描述: "self.str_error_battery != ''" can be simplified to "self.str_error_battery", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

#### 行 349, 列 23
- 类型: convention
- 代码: C1804
- 描述: "self.str_error_xlsx != ''" can be simplified to "self.str_error_xlsx", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

#### 行 357, 列 19
- 类型: warning
- 代码: W0705
- 描述: Catching previously caught exception type RuntimeError
- 符号: duplicate-except

#### 行 377, 列 15
- 类型: warning
- 代码: W0705
- 描述: Catching previously caught exception type RuntimeError
- 符号: duplicate-except

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
- 问题总数: 24
- 警告(Warning): 3
- 规范(Convention): 21

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Dict imported from typing
- 符号: unused-import

#### 行 24, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QApplication)
- 符号: import-outside-toplevel

#### 行 48, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QMainWindow)
- 符号: import-outside-toplevel

#### 行 64, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QProgressDialog)
- 符号: import-outside-toplevel

#### 行 87, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QMessageBox)
- 符号: import-outside-toplevel

#### 行 122, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QFileDialog)
- 符号: import-outside-toplevel

#### 行 139, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QLabel)
- 符号: import-outside-toplevel

#### 行 152, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QPushButton)
- 符号: import-outside-toplevel

#### 行 165, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QLineEdit)
- 符号: import-outside-toplevel

#### 行 181, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QTableWidget)
- 符号: import-outside-toplevel

#### 行 222, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter)
- 符号: import-outside-toplevel

#### 行 243, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter)
- 符号: import-outside-toplevel

#### 行 244, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter.ttk)
- 符号: import-outside-toplevel

#### 行 274, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter)
- 符号: import-outside-toplevel

#### 行 274, 列 12
- 类型: warning
- 代码: W0611
- 描述: Unused tkinter imported as tk
- 符号: unused-import

#### 行 275, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter.messagebox)
- 符号: import-outside-toplevel

#### 行 306, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter.filedialog)
- 符号: import-outside-toplevel

#### 行 327, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter)
- 符号: import-outside-toplevel

#### 行 340, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter)
- 符号: import-outside-toplevel

#### 行 353, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter)
- 符号: import-outside-toplevel

#### 行 373, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter)
- 符号: import-outside-toplevel

#### 行 373, 列 12
- 类型: warning
- 代码: W0611
- 描述: Unused tkinter imported as tk
- 符号: unused-import

#### 行 374, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (tkinter.ttk)
- 符号: import-outside-toplevel

#### 行 417, 列 11
- 类型: convention
- 代码: C1804
- 描述: "entry.get() == ''" can be simplified to "not entry.get()", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

## 文件: src\battery_analysis\ui\interfaces\iuiframework.py

### 问题统计
- 问题总数: 12
- 警告(Warning): 12

### 详细问题
#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Dict imported from typing
- 符号: unused-import

#### 行 39, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 48, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 60, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 79, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 98, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 111, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 124, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 137, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 151, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 161, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 173, 列 8
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

## 文件: src\battery_analysis\ui\styles\style_manager.py

### 问题统计
- 问题总数: 15
- 警告(Warning): 11
- 规范(Convention): 3
- 重构(Refactor): 1

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 12, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QVBoxLayout imported from PyQt6.QtWidgets
- 符号: unused-import

#### 行 14, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused QFontDatabase imported from PyQt6.QtGui
- 符号: unused-import

#### 行 35, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (58/50)
- 符号: too-many-statements

#### 行 248, 列 16
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'QFontDatabase' from outer scope (line 14)
- 符号: redefined-outer-name

#### 行 248, 列 16
- 类型: warning
- 代码: W0404
- 描述: Reimport 'QFontDatabase' (imported line 14)
- 符号: reimported

#### 行 248, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtGui.QFontDatabase)
- 符号: import-outside-toplevel

#### 行 277, 列 8
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'QPushButton' from outer scope (line 12)
- 符号: redefined-outer-name

#### 行 277, 列 8
- 类型: warning
- 代码: W0404
- 描述: Reimport 'QPushButton' (imported line 12)
- 符号: reimported

#### 行 277, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QPushButton)
- 符号: import-outside-toplevel

#### 行 300, 列 8
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'QGroupBox' from outer scope (line 12)
- 符号: redefined-outer-name

#### 行 300, 列 8
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'QVBoxLayout' from outer scope (line 12)
- 符号: redefined-outer-name

#### 行 300, 列 8
- 类型: warning
- 代码: W0404
- 描述: Reimport 'QGroupBox' (imported line 12)
- 符号: reimported

#### 行 300, 列 8
- 类型: warning
- 代码: W0404
- 描述: Reimport 'QVBoxLayout' (imported line 12)
- 符号: reimported

#### 行 300, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets.QGroupBox, PyQt6.QtWidgets.QVBoxLayout)
- 符号: import-outside-toplevel

## 文件: src\battery_analysis\ui\ui_main_window.py

### 问题统计
- 问题总数: 135
- 警告(Warning): 129
- 规范(Convention): 2
- 重构(Refactor): 4

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1561/1000)
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
- 描述: Too many instance attributes (129/7)
- 符号: too-many-instance-attributes

#### 行 13, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (1131/50)
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

#### 行 51, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_10' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 55, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 58, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TemperatureType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 72, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 121, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 123, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 137, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'spinBox_Temperature' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 149, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 153, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 167, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'spinBox_AcceleratedAging' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 186, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_2' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 191, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 194, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_5' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 198, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 202, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 216, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Manufacturer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 265, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 268, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 282, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_BatchDateCode' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 301, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 304, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 318, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_SamplesQty' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 337, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 347, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 350, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_7' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 354, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 357, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 371, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_BatteryType' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 421, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 424, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 438, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_ConstructionMethod' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 487, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Specification' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 491, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Specification' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 505, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 510, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Specification_Method' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 559, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_Specification_Type' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 611, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_4' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 616, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_6' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 619, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_9' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 623, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 626, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 640, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_RequiredUseableCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 659, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 662, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 676, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_CalculationNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 694, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 697, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 711, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_DatasheetNominalCapacity' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 734, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_TestConfig' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 751, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget_8' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 758, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 762, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 776, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 800, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_TestProfile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 814, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayoutWidget' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 817, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 821, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 826, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 840, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_TesterLocation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 892, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 897, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 911, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_TestedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 959, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_Path' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 966, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget_2' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 969, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_6' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 973, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 976, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 990, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1014, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_InputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1029, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1032, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1046, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1070, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_OutputPath' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1080, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'groupBox_TestInformation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1090, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'scrollArea' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1094, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'scrollAreaWidgetContents' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1102, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_3' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1104, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'tableWidget_TestInformation' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1188, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_RunButton' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1198, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayoutWidget' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1204, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout_RunAndVersion' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1208, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_7' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1217, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'pushButton_Run' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1261, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'frame_6' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1271, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'progressBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1281, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'verticalLayout' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1283, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1287, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1300, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'lineEdit_Version' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1322, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'horizontalLayout_ReportedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1325, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'label_ReportedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1339, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'comboBox_ReportedBy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1389, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'statusBar_BatteryAnalysis' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1392, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuBar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1395, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuFile' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1397, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuEdit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1399, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuView' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1401, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuTools' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1403, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'menuHelp' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1406, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionNew' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1408, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOpen' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1410, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1412, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionSave_As' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1414, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionExport_Report' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1416, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionExit' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1418, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionUndo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1420, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionRedo' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1422, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCut' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1424, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCopy' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1426, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionPaste' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1428, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionPreferences' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1430, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionShow_Toolbar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1432, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionShow_Statusbar' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1434, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionZoom_In' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1436, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionZoom_Out' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1438, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionReset_Zoom' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1440, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionCalculate_Battery' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1442, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionAnalyze_Data' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1444, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionGenerate_Report' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1446, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionBatch_Processing' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1448, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionUser_Mannual' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1450, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionOnline_Help' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1452, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionAbout' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1454, 列 8
- 类型: warning
- 代码: W0201
- 描述: Attribute 'actionBatteryChartViewer' defined outside __init__
- 符号: attribute-defined-outside-init

#### 行 1499, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (63/50)
- 符号: too-many-statements

## 文件: src\battery_analysis\utils\__init__.py

### 问题统计
- 问题总数: 6
- 警告(Warning): 3
- 规范(Convention): 3

### 详细问题
#### 行 114, 列 10
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'max_size'
- 符号: unused-argument

#### 行 114, 列 32
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'ttl'
- 符号: unused-argument

#### 行 129, 列 18
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _generate_key of a client class
- 符号: protected-access

#### 行 162, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.utils.log_manager import get_logger, get_log_directory, clear_old_logs" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 167, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.utils.error_report_generator import generate_error_report, get_report_info" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 182, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\utils\base_service.py

### 问题统计
- 问题总数: 4
- 警告(Warning): 3
- 规范(Convention): 1

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 61, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 62, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 87, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\utils\battery_analysis.py

### 问题统计
- 问题总数: 30
- 警告(Warning): 5
- 规范(Convention): 13
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
- 描述: third party import "xlrd" should be placed before first party imports "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.utils.data_utils.generate_current_type_string" 
- 符号: wrong-import-order

#### 行 4, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "os" should be placed before third party import "xlrd" and first party imports "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.utils.data_utils.generate_current_type_string" 
- 符号: wrong-import-order

#### 行 5, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "csv" should be placed before third party import "xlrd" and first party imports "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.utils.data_utils.generate_current_type_string" 
- 符号: wrong-import-order

#### 行 6, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "datetime" should be placed before third party import "xlrd" and first party imports "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.utils.data_utils.generate_current_type_string" 
- 符号: wrong-import-order

#### 行 7, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "traceback" should be placed before third party import "xlrd" and first party imports "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.utils.data_utils.generate_current_type_string" 
- 符号: wrong-import-order

#### 行 8, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "logging" should be placed before third party import "xlrd" and first party imports "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.utils.data_utils.generate_current_type_string" 
- 符号: wrong-import-order

#### 行 9, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "re" should be placed before third party import "xlrd" and first party imports "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.utils.data_utils.generate_current_type_string" 
- 符号: wrong-import-order

#### 行 10, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "multiprocessing" should be placed before third party import "xlrd" and first party imports "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.utils.data_utils.generate_current_type_string" 
- 符号: wrong-import-order

#### 行 11, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "sys" should be placed before third party import "xlrd" and first party imports "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.utils.data_utils.generate_current_type_string" 
- 符号: wrong-import-order

#### 行 12, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "concurrent.futures" should be placed before third party import "xlrd" and first party imports "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.utils.data_utils.generate_current_type_string" 
- 符号: wrong-import-order

#### 行 24, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (18/7)
- 符号: too-many-instance-attributes

#### 行 25, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (16/12)
- 符号: too-many-branches

#### 行 25, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (79/50)
- 符号: too-many-statements

#### 行 114, 列 20
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (battery_analysis.utils.resource_manager.ResourceManager)
- 符号: import-outside-toplevel

#### 行 140, 列 32
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise BatteryAnalysisException(f'处理失败: {str(e)}') from e'
- 符号: raise-missing-from

#### 行 156, 列 28
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise BatteryAnalysisException(f'并行处理失败: {str(e)}') from e'
- 符号: raise-missing-from

#### 行 187, 列 4
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (8/6)
- 符号: too-many-return-statements

#### 行 187, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (32/12)
- 符号: too-many-branches

#### 行 187, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (76/50)
- 符号: too-many-statements

#### 行 197, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (12/5)
- 符号: too-many-nested-blocks

#### 行 197, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (11/5)
- 符号: too-many-nested-blocks

#### 行 197, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (12/5)
- 符号: too-many-nested-blocks

#### 行 197, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (11/5)
- 符号: too-many-nested-blocks

#### 行 332, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (22/12)
- 符号: too-many-branches

#### 行 332, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (114/50)
- 符号: too-many-statements

#### 行 429, 列 56
- 类型: convention
- 代码: C1805
- 描述: "listLevelToRow[c_idx][v_idx] == 0" can be simplified to "not listLevelToRow[c_idx][v_idx]", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 443, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 457, 列 20
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 496, 列 20
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

## 文件: src\battery_analysis\utils\config_manager.py

### 问题统计
- 问题总数: 12
- 警告(Warning): 11
- 重构(Refactor): 1

### 详细问题
#### 行 9, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Path imported from pathlib
- 符号: unused-import

#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 39, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 42, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 61, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 64, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 91, 列 16
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "elif" after "return", remove the leading "el" from "elif"
- 符号: no-else-return

#### 行 103, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 138, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 161, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 180, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 193, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

## 文件: src\battery_analysis\utils\config_parser.py

### 问题统计
- 问题总数: 10
- 警告(Warning): 8
- 重构(Refactor): 2

### 详细问题
#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Union imported from typing
- 符号: unused-import

#### 行 10, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Optional imported from typing
- 符号: unused-import

#### 行 16, 列 4
- 类型: warning
- 代码: W0107
- 描述: Unnecessary pass statement
- 符号: unnecessary-pass

#### 行 93, 列 4
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "elif" after "return", remove the leading "el" from "elif"
- 符号: no-else-return

#### 行 102, 列 0
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (6/5)
- 符号: too-many-positional-arguments

#### 行 102, 列 22
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'config' from outer scope (line 211)
- 符号: redefined-outer-name

#### 行 160, 列 8
- 类型: warning
- 代码: W0707
- 描述: Consider explicitly re-raising using 'raise ConfigParseError(f'解析配置 {section}/{option} 失败: {e}') from e'
- 符号: raise-missing-from

#### 行 163, 列 31
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'config' from outer scope (line 211)
- 符号: redefined-outer-name

#### 行 184, 列 25
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'config' from outer scope (line 211)
- 符号: redefined-outer-name

#### 行 208, 列 4
- 类型: warning
- 代码: W0404
- 描述: Reimport 'ConfigParser' (imported line 11)
- 符号: reimported

## 文件: src\battery_analysis\utils\config_utils.py

### 问题统计
- 问题总数: 3
- 警告(Warning): 3

### 详细问题
#### 行 7, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused import os
- 符号: unused-import

#### 行 81, 列 4
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'paths'
- 符号: unused-variable

#### 行 134, 列 4
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'paths'
- 符号: unused-variable

## 文件: src\battery_analysis\utils\csv_utils.py

### 问题统计
- 问题总数: 5
- 规范(Convention): 5

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

#### 行 11, 列 15
- 类型: convention
- 代码: C1805
- 描述: "_strMessage[_i] != 0" can be simplified to "_strMessage[_i]", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

## 文件: src\battery_analysis\utils\data_utils.py

### 问题统计
- 问题总数: 12
- 错误(Error): 4
- 警告(Warning): 1
- 规范(Convention): 5
- 重构(Refactor): 2

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 1, 列 0
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (16/12)
- 符号: too-many-branches

#### 行 1, 列 0
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (73/50)
- 符号: too-many-statements

#### 行 4, 列 4
- 类型: warning
- 代码: W0613
- 描述: Unused argument 'times'
- 符号: unused-argument

#### 行 16, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (numpy)
- 符号: import-outside-toplevel

#### 行 31, 列 45
- 类型: convention
- 代码: C1805
- 描述: "charge_diff != 0" can be simplified to "charge_diff", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 49, 列 16
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

#### 行 64, 列 27
- 类型: convention
- 代码: C1805
- 描述: "charge_diff == 0" can be simplified to "not charge_diff", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 76, 列 24
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

#### 行 94, 列 20
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

#### 行 108, 列 27
- 类型: convention
- 代码: C1805
- 描述: "charge_diff == 0" can be simplified to "not charge_diff", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 120, 列 24
- 类型: error
- 代码: E0602
- 描述: Undefined variable 'logging'
- 符号: undefined-variable

## 文件: src\battery_analysis\utils\environment_utils.py

### 问题统计
- 问题总数: 9
- 警告(Warning): 3
- 规范(Convention): 3
- 重构(Refactor): 3

### 详细问题
#### 行 70, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "elif" after "return", remove the leading "el" from "elif"
- 符号: no-else-return

#### 行 170, 列 4
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (7/6)
- 符号: too-many-return-statements

#### 行 177, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtWidgets)
- 符号: import-outside-toplevel

#### 行 177, 列 12
- 类型: warning
- 代码: W0611
- 描述: Unused PyQt6.QtWidgets imported as QW
- 符号: unused-import

#### 行 178, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (PyQt6.QtGui.QGuiApplication)
- 符号: import-outside-toplevel

#### 行 223, 列 16
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (ctypes)
- 符号: import-outside-toplevel

#### 行 228, 列 12
- 类型: warning
- 代码: W0702
- 描述: No exception type(s) specified
- 符号: bare-except

#### 行 266, 列 8
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it
- 符号: no-else-return

#### 行 320, 列 4
- 类型: warning
- 代码: W0603
- 描述: Using the global statement
- 符号: global-statement

## 文件: src\battery_analysis\utils\error_report_generator.py

### 问题统计
- 问题总数: 37
- 警告(Warning): 29
- 规范(Convention): 6
- 重构(Refactor): 2

### 详细问题
#### 行 15, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "zipfile" should be placed before third party import "psutil"
- 符号: wrong-import-order

#### 行 16, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "tempfile" should be placed before third party import "psutil"
- 符号: wrong-import-order

#### 行 17, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "pathlib.Path" should be placed before third party import "psutil"
- 符号: wrong-import-order

#### 行 29, 列 4
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (8/6)
- 符号: too-many-return-statements

#### 行 39, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (subprocess)
- 符号: import-outside-toplevel

#### 行 40, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (winreg)
- 符号: import-outside-toplevel

#### 行 62, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 67, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 74, 列 25
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 82, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 83, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 87, 列 25
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 93, 列 16
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "elif" after "return", remove the leading "el" from "elif"
- 符号: no-else-return

#### 行 99, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 100, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 103, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 104, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 117, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (winreg)
- 符号: import-outside-toplevel

#### 行 123, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 124, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 174, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 175, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 201, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 202, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 224, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 225, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 226, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 227, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 228, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 284, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 285, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 326, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 327, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 328, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 344, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 351, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 352, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

## 文件: src\battery_analysis\utils\excel_utils.py

### 问题统计
- 问题总数: 4
- 规范(Convention): 4

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

#### 行 11, 列 43
- 类型: convention
- 代码: C1805
- 描述: "_strMessage != 0" can be simplified to "_strMessage", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

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
- 问题总数: 86
- 警告(Warning): 25
- 规范(Convention): 50
- 重构(Refactor): 11

### 详细问题
#### 行 1, 列 0
- 类型: convention
- 代码: C0302
- 描述: Too many lines in module (1671/1000)
- 符号: too-many-lines

#### 行 1, 列 0
- 类型: convention
- 代码: C0114
- 描述: Missing module docstring
- 符号: missing-module-docstring

#### 行 9, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "docx.shared.Pt" should be placed before first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 10, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "docx.enum.text.WD_LINE_SPACING" should be placed before first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 11, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "docx.enum.table.WD_TABLE_ALIGNMENT" should be placed before first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 12, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "docx.Document" should be placed before first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 13, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "matplotlib.ticker.MultipleLocator" should be placed before first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 14, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "matplotlib.pyplot" should be placed before first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 15, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "re" should be placed before third party imports "docx.shared.Pt", "docx.enum.text.WD_LINE_SPACING", "docx.enum.table.WD_TABLE_ALIGNMENT", "docx.Document", "matplotlib.ticker.MultipleLocator", "matplotlib.pyplot" and first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 16, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "pathlib.Path" should be placed before third party imports "docx.shared.Pt", "docx.enum.text.WD_LINE_SPACING", "docx.enum.table.WD_TABLE_ALIGNMENT", "docx.Document", "matplotlib.ticker.MultipleLocator", "matplotlib.pyplot" and first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 16, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Path imported from pathlib
- 符号: unused-import

#### 行 22, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import xlsxwriter as xwt" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 22, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "xlsxwriter" should be placed before first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 23, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import os" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 23, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "os" should be placed before third party imports "docx.shared.Pt", "docx.enum.text.WD_LINE_SPACING", "docx.enum.table.WD_TABLE_ALIGNMENT" (...) "matplotlib.ticker.MultipleLocator", "matplotlib.pyplot", "xlsxwriter" and first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 24, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import csv" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 24, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "csv" should be placed before third party imports "docx.shared.Pt", "docx.enum.text.WD_LINE_SPACING", "docx.enum.table.WD_TABLE_ALIGNMENT" (...) "matplotlib.ticker.MultipleLocator", "matplotlib.pyplot", "xlsxwriter" and first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 25, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import json" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 25, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "json" should be placed before third party imports "docx.shared.Pt", "docx.enum.text.WD_LINE_SPACING", "docx.enum.table.WD_TABLE_ALIGNMENT" (...) "matplotlib.ticker.MultipleLocator", "matplotlib.pyplot", "xlsxwriter" and first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 26, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import math" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 26, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "math" should be placed before third party imports "docx.shared.Pt", "docx.enum.text.WD_LINE_SPACING", "docx.enum.table.WD_TABLE_ALIGNMENT" (...) "matplotlib.ticker.MultipleLocator", "matplotlib.pyplot", "xlsxwriter" and first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 27, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import datetime" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 27, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "datetime" should be placed before third party imports "docx.shared.Pt", "docx.enum.text.WD_LINE_SPACING", "docx.enum.table.WD_TABLE_ALIGNMENT" (...) "matplotlib.ticker.MultipleLocator", "matplotlib.pyplot", "xlsxwriter" and first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 28, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import traceback" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 28, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "traceback" should be placed before third party imports "docx.shared.Pt", "docx.enum.text.WD_LINE_SPACING", "docx.enum.table.WD_TABLE_ALIGNMENT" (...) "matplotlib.ticker.MultipleLocator", "matplotlib.pyplot", "xlsxwriter" and first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 29, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import configparser" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 29, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "configparser" should be placed before third party imports "docx.shared.Pt", "docx.enum.text.WD_LINE_SPACING", "docx.enum.table.WD_TABLE_ALIGNMENT" (...) "matplotlib.ticker.MultipleLocator", "matplotlib.pyplot", "xlsxwriter" and first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 30, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import logging" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 30, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "logging" should be placed before third party imports "docx.shared.Pt", "docx.enum.text.WD_LINE_SPACING", "docx.enum.table.WD_TABLE_ALIGNMENT" (...) "matplotlib.ticker.MultipleLocator", "matplotlib.pyplot", "xlsxwriter" and first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.excel_utils", "battery_analysis.utils.numeric_utils", "battery_analysis.utils.exception_type.BatteryAnalysisException" 
- 符号: wrong-import-order

#### 行 33, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis import __version__" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 33, 列 0
- 类型: convention
- 代码: C0412
- 描述: Imports from package battery_analysis are not grouped
- 符号: ungrouped-imports

#### 行 34, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "from battery_analysis.utils.config_utils import find_config_file" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 37, 列 0
- 类型: convention
- 代码: C0413
- 描述: Import "import matplotlib" should be placed at the top of the module
- 符号: wrong-import-position

#### 行 37, 列 0
- 类型: convention
- 代码: C0411
- 描述: third party import "matplotlib" should be placed before first party imports "battery_analysis.utils.csv_utils", "battery_analysis.utils.plot_utils", "battery_analysis.utils.data_utils" (...) "battery_analysis.utils.exception_type.BatteryAnalysisException", "battery_analysis.__version__", "battery_analysis.utils.config_utils.find_config_file" 
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
- 描述: Too many branches (36/12)
- 符号: too-many-branches

#### 行 42, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (140/50)
- 符号: too-many-statements

#### 行 236, 列 8
- 类型: warning
- 代码: W0621
- 描述: Redefining name 'Path' from outer scope (line 16)
- 符号: redefined-outer-name

#### 行 236, 列 8
- 类型: warning
- 代码: W0404
- 描述: Reimport 'Path' (imported line 16)
- 符号: reimported

#### 行 236, 列 8
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (pathlib.Path)
- 符号: import-outside-toplevel

#### 行 301, 列 4
- 类型: refactor
- 代码: R0912
- 描述: Too many branches (131/12)
- 符号: too-many-branches

#### 行 301, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (467/50)
- 符号: too-many-statements

#### 行 530, 列 12
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 544, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 545, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 546, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 555, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 561, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 562, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 563, 列 12
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 751, 列 23
- 类型: convention
- 代码: C1805
- 描述: "self.listBatteryCharge[b][i] != 0" can be simplified to "self.listBatteryCharge[b][i]", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 799, 列 8
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 884, 列 19
- 类型: convention
- 代码: C1805
- 描述: "c == 0" can be simplified to "not c", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 884, 列 30
- 类型: convention
- 代码: C1805
- 描述: "v == 0" can be simplified to "not v", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 895, 列 21
- 类型: convention
- 代码: C1805
- 描述: "c == 0" can be simplified to "not c", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 897, 列 55
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 911, 列 31
- 类型: convention
- 代码: C1805
- 描述: "v == 0" can be simplified to "not v", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 913, 列 55
- 类型: warning
- 代码: W1309
- 描述: Using an f-string that does not have any interpolated variables
- 符号: f-string-without-interpolation

#### 行 1154, 列 52
- 类型: convention
- 代码: C0207
- 描述: Use listStrContent[18].rsplit('\\', maxsplit=1)[-1] instead
- 符号: use-maxsplit-arg

#### 行 1239, 列 51
- 类型: convention
- 代码: C0207
- 描述: Use listStrContent[18].rsplit('\\', maxsplit=1)[-1] instead
- 符号: use-maxsplit-arg

#### 行 1363, 列 8
- 类型: refactor
- 代码: R1702
- 描述: Too many nested blocks (6/5)
- 符号: too-many-nested-blocks

#### 行 1366, 列 12
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1381, 列 16
- 类型: convention
- 代码: C0200
- 描述: Consider using enumerate instead of iterating with range and len
- 符号: consider-using-enumerate

#### 行 1386, 列 31
- 类型: convention
- 代码: C1805
- 描述: "i == 0" can be simplified to "not i", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 1396, 列 28
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _element of a client class
- 符号: protected-access

#### 行 1396, 列 66
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _element of a client class
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

#### 行 1424, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1424, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1427, 列 20
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _p of a client class
- 符号: protected-access

#### 行 1427, 列 41
- 类型: warning
- 代码: W0212
- 描述: Access to a protected member _tbl of a client class
- 符号: protected-access

#### 行 1446, 列 4
- 类型: refactor
- 代码: R0915
- 描述: Too many statements (56/50)
- 符号: too-many-statements

#### 行 1451, 列 24
- 类型: refactor
- 代码: R1735
- 描述: Consider using '{"linewidth": 1, "color": 'red'}' instead of a call to 'dict'.
- 符号: use-dict-literal

#### 行 1478, 列 12
- 类型: refactor
- 代码: R1732
- 描述: Consider using 'with' for resource-allocating operations
- 符号: consider-using-with

#### 行 1484, 列 15
- 类型: convention
- 代码: C1805
- 描述: "loop != 0" can be simplified to "loop", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 1538, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (13/7)
- 符号: too-many-instance-attributes

#### 行 1549, 列 16
- 类型: warning
- 代码: W0719
- 描述: Raising too general exception: Exception
- 符号: broad-exception-raised

#### 行 1580, 列 12
- 类型: warning
- 代码: W0612
- 描述: Unused variable 'v'
- 符号: unused-variable

#### 行 1595, 列 19
- 类型: convention
- 代码: C1805
- 描述: "j % len(self.listVoltageLevel) == 0" can be simplified to "not j % len(self.listVoltageLevel)", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 1597, 列 19
- 类型: convention
- 代码: C1805
- 描述: "value != 0" can be simplified to "value", if it is strictly an int, as 0 is falsey
- 符号: use-implicit-booleaness-not-comparison-to-zero

#### 行 1597, 列 34
- 类型: convention
- 代码: C1804
- 描述: "self.listBatteryVoltage[j % len(self.listBatteryVoltage)] != ''" can be simplified to "self.listBatteryVoltage[j % len(self.listBatteryVoltage)]", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

#### 行 1656, 列 13
- 类型: warning
- 代码: W1514
- 描述: Using open without explicitly specifying an encoding
- 符号: unspecified-encoding

## 文件: src\battery_analysis\utils\log_manager.py

### 问题统计
- 问题总数: 37
- 警告(Warning): 31
- 规范(Convention): 4
- 重构(Refactor): 2

### 详细问题
#### 行 18, 列 0
- 类型: convention
- 代码: C0411
- 描述: standard import "pathlib.Path" should be placed before third party import "psutil"
- 符号: wrong-import-order

#### 行 96, 列 4
- 类型: refactor
- 代码: R0911
- 描述: Too many return statements (8/6)
- 符号: too-many-return-statements

#### 行 106, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (subprocess)
- 符号: import-outside-toplevel

#### 行 107, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (winreg)
- 符号: import-outside-toplevel

#### 行 129, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 134, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 141, 列 25
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 149, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 150, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 154, 列 25
- 类型: warning
- 代码: W1510
- 描述: 'subprocess.run' used without explicitly defining the value for 'check'.
- 符号: subprocess-run-check

#### 行 160, 列 16
- 类型: refactor
- 代码: R1705
- 描述: Unnecessary "elif" after "return", remove the leading "el" from "elif"
- 符号: no-else-return

#### 行 166, 列 19
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 167, 列 16
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 170, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 171, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 184, 列 12
- 类型: convention
- 代码: C0415
- 描述: Import outside toplevel (winreg)
- 符号: import-outside-toplevel

#### 行 190, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 191, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 198, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 199, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 203, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 204, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 206, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 207, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 211, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 212, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 213, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 216, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 217, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 220, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 221, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 222, 列 8
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 268, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 269, 列 27
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 270, 列 24
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

#### 行 271, 列 15
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 272, 列 12
- 类型: warning
- 代码: W1203
- 描述: Use lazy % formatting in logging functions
- 符号: logging-fstring-interpolation

## 文件: src\battery_analysis\utils\parallel_utils.py

### 问题统计
- 问题总数: 7
- 警告(Warning): 3
- 规范(Convention): 1
- 重构(Refactor): 3

### 详细问题
#### 行 8, 列 0
- 类型: warning
- 代码: W0611
- 描述: Unused Tuple imported from typing
- 符号: unused-import

#### 行 17, 列 0
- 类型: refactor
- 代码: R0902
- 描述: Too many instance attributes (9/7)
- 符号: too-many-instance-attributes

#### 行 22, 列 23
- 类型: warning
- 代码: W0622
- 描述: Redefining built-in 'id'
- 符号: redefined-builtin

#### 行 126, 列 23
- 类型: warning
- 代码: W0718
- 描述: Catching too general exception Exception
- 符号: broad-exception-caught

#### 行 168, 列 4
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (7/5)
- 符号: too-many-positional-arguments

#### 行 270, 列 0
- 类型: refactor
- 代码: R0917
- 描述: Too many positional arguments (6/5)
- 符号: too-many-positional-arguments

#### 行 302, 列 0
- 类型: convention
- 代码: C0304
- 描述: Final newline missing
- 符号: missing-final-newline

## 文件: src\battery_analysis\utils\version.py

### 问题统计
- 问题总数: 2
- 信息(Info): 2

### 详细问题
#### 行 138, 列 0
- 类型: info
- 代码: I0011
- 描述: Locally disabling protected-access (W0212)
- 符号: locally-disabled

#### 行 138, 列 0
- 类型: info
- 代码: I0020
- 描述: Suppressed 'protected-access' (from line 138)
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

## 文件: tests\battery_analysis\main\test_main_window.py

### 问题统计
- 问题总数: 3
- 信息(Info): 3

### 详细问题
#### 行 7, 列 0
- 类型: info
- 代码: I0011
- 描述: Locally disabling import-error (E0401)
- 符号: locally-disabled

#### 行 7, 列 0
- 类型: info
- 代码: I0023
- 描述: 'E0401' is cryptic: use '# pylint: disable=import-error' instead
- 符号: use-symbolic-message-instead

#### 行 7, 列 0
- 类型: info
- 代码: I0021
- 描述: Useless suppression of 'import-error'
- 符号: useless-suppression

## 文件: tests\battery_analysis\utils\test_file_writer.py

### 问题统计
- 问题总数: 73
- 规范(Convention): 1
- 重构(Refactor): 72

### 详细问题
#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis.utils.error_report_generator:[34:132]
==battery_analysis.utils.log_manager:[101:195]
        if platform.system() != 'Windows':
            return "非Windows系统"

        try:
            import subprocess
            import winreg

            # 方法1: 尝试从注册表获取激活状态
            try:
                # 尝试从注册表获取激活状态，但不记录过多调试日志
                # 只在成功获取时记录，失败时直接尝试其他方法
                try:
                    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform"
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, access=winreg.KEY_READ) as key:
                        license_status = winreg.QueryValueEx(key, "LicenseStatus")[0]

                        status_map = {
                            0: "未激活",
                            1: "已激活",
                            2: "OOBGrace",
                            3: "OOTGrace",
                            4: "NonGenuineGrace",
                            5: "Notification",
                            6: "ExtendedGrace"
                        }

                        return f"Windows 激活状态: {status_map.get(license_status, f'未知状态 ({license_status})')}"
                except Exception:
                    # 注册表访问失败，不记录详细日志，直接尝试下一种方法
                    pass

                # 不尝试Wow6432Node路径，减少不必要的日志
            except Exception:
                # 捕获所有注册表相关异常，不记录详细日志
                pass

            # 方法2: 尝试使用cscript执行slmgr.vbs
            try:
                slmgr_path = "C:\\Windows\\System32\\slmgr.vbs"
                result = subprocess.run(
                    ['cscript', slmgr_path, '/xpr'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return result.stdout.strip() if result.stdout.strip() else "无法获取激活状态"
            except Exception as slmgr_error:
                self.logger.debug(f"使用slmgr获取激活状态失败: {slmgr_error}")

            # 方法3: 尝试使用wmic命令
            try:
                result = subprocess.run(
                    ['wmic', 'path', 'SoftwareLicensingProduct', 'where', 'ApplicationID="55c92734-d682-4d71-983e-d6ec3f16059f"', 'get', 'LicenseStatus', '/value'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if "LicenseStatus=1" in result.stdout:
                    return "Windows 已激活"
                elif "LicenseStatus=0" in result.stdout:
                    return "Windows 未激活"
                else:
                    return "无法获取激活状态"
            except Exception as wmic_error:
                self.logger.debug(f"使用wmic获取激活状态失败: {wmic_error}")

            return "无法获取激活状态"
        except Exception as e:
            self.logger.debug(f"获取Windows激活状态失败: {e}")
            return "获取激活状态失败"

    def _get_windows_edition(self):
        """获取Windows系统版本类型

        Returns:
            str: 系统版本类型
        """
        if platform.system() != 'Windows':
            return "非Windows系统"

        try:
            import winreg
            # 从注册表获取系统版本
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                return product_name
        except Exception as e:
            self.logger.debug(f"获取Windows版本类型失败: {e}")
            return "获取版本类型失败"

    def _log_environment_info(self):
        """记录应用程序运行环境信息"""
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ui_components.config_manager:[135:208]
==ui_components.ui_manager:[467:538]
        try:
            # 使用用户设置管理器加载配置
            user_config = self.user_settings_manager.load_user_settings()

            # 更新UI控件
            # 电池类型相关设置
            if user_config.get("BatteryType"):
                index = self.main_window.comboBox_BatteryType.findText(user_config["BatteryType"])
                if index >= 0:
                    self.main_window.comboBox_BatteryType.setCurrentIndex(index)

            if user_config.get("ConstructionMethod"):
                index = self.main_window.comboBox_ConstructionMethod.findText(
                    user_config["ConstructionMethod"])
                if index >= 0:
                    self.main_window.comboBox_ConstructionMethod.setCurrentIndex(index)

            if user_config.get("SpecificationType"):
                index = self.main_window.comboBox_Specification_Type.findText(
                    user_config["SpecificationType"])
                if index >= 0:
                    self.main_window.comboBox_Specification_Type.setCurrentIndex(index)

            if user_config.get("SpecificationMethod"):
                index = self.main_window.comboBox_Specification_Method.findText(
                    user_config["SpecificationMethod"])
                if index >= 0:
                    self.main_window.comboBox_Specification_Method.setCurrentIndex(
                        index)

            if user_config.get("Manufacturer"):
                index = self.main_window.comboBox_Manufacturer.findText(user_config["Manufacturer"])
                if index >= 0:
                    self.main_window.comboBox_Manufacturer.setCurrentIndex(index)

            if user_config.get("TesterLocation"):
                index = self.main_window.comboBox_TesterLocation.findText(
                    user_config["TesterLocation"])
                if index >= 0:
                    self.main_window.comboBox_TesterLocation.setCurrentIndex(index)

            if user_config.get("TestedBy"):
                index = self.main_window.comboBox_TestedBy.findText(user_config["TestedBy"])
                if index >= 0:
                    self.main_window.comboBox_TestedBy.setCurrentIndex(index)
                else:
                    # 如果找不到匹配项，直接设置文本（用于自定义输入的情况）
                    self.main_window.comboBox_TestedBy.setCurrentText(user_config["TestedBy"])

            if user_config.get("ReportedBy"):
                index = self.main_window.comboBox_ReportedBy.findText(user_config["ReportedBy"])
                if index >= 0:
                    self.main_window.comboBox_ReportedBy.setCurrentIndex(index)
                else:
                    # 如果找不到匹配项，直接设置文本（用于自定义输入的情况）
                    self.main_window.comboBox_ReportedBy.setCurrentText(user_config["ReportedBy"])

            # 加载温度设置
            if user_config.get("TemperatureType"):
                self.main_window.comboBox_Temperature.setCurrentText(user_config["TemperatureType"])
                # 同时更新spinBox的启用状态
                if user_config["TemperatureType"] == "Freezer Temperature":
                    self.main_window.spinBox_Temperature.setEnabled(True)
                else:
                    self.main_window.spinBox_Temperature.setEnabled(False)

            # 加载冷冻温度数值设置
            if user_config.get("FreezerTemperature"):
                try:
                    self.main_window.spinBox_Temperature.setValue(int(user_config["FreezerTemperature"]))
                except (ValueError, TypeError):
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==business_logic.visualization_manager:[197:240]
==dialogs.data_error_dialog:[107:149]
            else:
                # 取消操作
                self.main_window.statusBar_BatteryAnalysis.showMessage("操作已取消")
                QW.QMessageBox.information(
                    self.main_window,
                    "取消",
                    "操作已取消。您可以通过菜单 'File -> Open Data' 重新尝试。",
                    QW.QMessageBox.StandardButton.Ok
                )
        else:
            self.main_window.statusBar_BatteryAnalysis.showMessage("操作已取消")

    def _open_data_directory_dialog(self):
        """打开数据目录选择对话框"""
        try:
            # 打开目录选择对话框
            directory = QW.QFileDialog.getExistingDirectory(
                self.main_window,
                "选择包含电池数据的目录",
                "",
                QW.QFileDialog.Option.ShowDirsOnly | QW.QFileDialog.Option.DontResolveSymlinks
            )

            if directory:
                self.main_window.statusBar_BatteryAnalysis.showMessage(f"已选择目录: {directory}")

                # 检查目录中是否有Info_Image.csv文件
                import os
                info_image_path = os.path.join(directory, "Info_Image.csv")
                if os.path.exists(info_image_path):
                    QW.QMessageBox.information(
                        self.main_window,
                        "数据目录确认",
                        f"找到数据文件: {info_image_path}\n\n应用将尝试使用此数据重新启动可视化工具。",
                        QW.QMessageBox.StandardButton.Ok
                    )

                    # 更新界面上的配置路径
                    if hasattr(self.main_window, 'lineEdit_TestProfile'):
                        self.main_window.lineEdit_TestProfile.setText(directory)

                    # 重新运行可视化工具
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==business_logic.environment_manager:[13:63]
==managers.environment_manager:[4:59]
class EnvironmentManager:
    """环境信息管理器"""

    def __init__(self, main_window):
        """
        初始化环境管理器

        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

    def initialize_environment_info(self):
        """
        初始化环境信息
        """
        try:
            environment_service = self.main_window._get_service("environment")
            if environment_service:
                if hasattr(environment_service, 'env_info'):
                    self.main_window.env_info = environment_service.env_info
                elif hasattr(environment_service, 'initialize'):
                    if environment_service.initialize() and hasattr(environment_service, 'env_info'):
                        self.main_window.env_info = environment_service.env_info
        except (AttributeError, TypeError, ImportError, OSError) as e:
            self.logger.warning("Failed to initialize environment service: %s", e)

    def ensure_env_info_keys(self):
        """
        确保环境信息包含必要的键
        """
        # 确保environment_type键存在
        if 'environment_type' not in self.main_window.env_info:
            try:
                environment_service = self.main_window._get_service("environment")
                if environment_service and hasattr(environment_service, 'EnvironmentType'):
                    self.main_window.env_info['environment_type'] = environment_service.EnvironmentType.DEVELOPMENT
                else:
                    # 降级到直接导入
                    from battery_analysis.utils.environment_utils import EnvironmentType
                    self.main_window.env_info['environment_type'] = EnvironmentType.DEVELOPMENT
            except (AttributeError, TypeError, ImportError) as e:
                self.logger.warning("Failed to get EnvironmentType: %s", e)
                from battery_analysis.utils.environment_utils import EnvironmentType
                self.main_window.env_info['environment_type'] = EnvironmentType.DEVELOPMENT

        # 确保gui_available键存在
        if 'gui_available' not in self.main_window.env_info:
            self.main_window.env_info['gui_available'] = True

    def initialize_all(self):
        """
        初始化所有环境信息
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis_service_impl:[70:121]
==impl.battery_analysis_service_impl:[41:85]
        if not test_results:
            return {
                "total_cycles": 0,
                "average_capacity": 0.0,
                "capacity_fade_rate": 0.0,
                "estimated_remaining_cycles": 0
            }

        # 按循环次数排序
        sorted_results = sorted(test_results, key=lambda x: x.cycle_count)

        # 计算总循环次数
        total_cycles = sorted_results[-1].cycle_count

        # 计算平均容量
        average_capacity = sum(result.capacity for result in test_results) / len(test_results)

        # 计算容量衰减率
        initial_capacity = sorted_results[0].capacity if sorted_results else 0.0
        final_capacity = sorted_results[-1].capacity if sorted_results else 0.0
        capacity_fade = initial_capacity - final_capacity
        capacity_fade_rate = (capacity_fade / initial_capacity) * 100 if initial_capacity > 0 else 0.0

        # 估算剩余循环次数（简单模型）
        # 假设当容量衰减到80%时，电池寿命结束
        remaining_capacity_percent = (final_capacity / battery.nominal_capacity) * 100
        estimated_remaining_cycles = 0

        if remaining_capacity_percent > 80 and capacity_fade_rate > 0:
            remaining_capacity_needed = remaining_capacity_percent - 80
            estimated_remaining_cycles = int((remaining_capacity_needed / capacity_fade_rate) * total_cycles)

        return {
            "total_cycles": total_cycles,
            "average_capacity": round(average_capacity, 2),
            "capacity_fade_rate": round(capacity_fade_rate, 2),
            "estimated_remaining_cycles": estimated_remaining_cycles
        }

    def validate_test_result(self, test_result: TestResult, test_profile: TestProfile, battery: Battery) -> Dict[str, Any]:
        """
        验证测试结果是否符合测试配置要求

        Args:
            test_result: 测试结果实体
            test_profile: 测试配置实体
            battery: 电池实体

        Returns:
            验证结果，包含是否通过和详细信息
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==business_logic.visualization_manager:[161:195]
==dialogs.data_error_dialog:[71:105]
        button_layout = QW.QHBoxLayout()

        ok_button = QW.QPushButton("确定")
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QW.QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # 显示对话框
        if dialog.exec() == QW.QDialog.DialogCode.Accepted:
            selected_id = button_group.checkedId()

            if selected_id == 1:
                # 重新选择数据目录
                self.main_window.statusBar_BatteryAnalysis.showMessage("正在打开数据目录选择...")
                self._open_data_directory_dialog()

            elif selected_id == 2:
                # 使用默认配置重新启动
                self.main_window.statusBar_BatteryAnalysis.showMessage("使用默认配置重新启动...")
                QW.QMessageBox.information(
                    self.main_window,
                    "重新启动",
                    "应用将使用默认配置重新启动。\n\n请确保您有有效的数据文件可用。",
                    QW.QMessageBox.StandardButton.Ok
                )
                # 清空配置字段并重新启动
                if hasattr(self.main_window, 'lineEdit_TestProfile'):
                    self.main_window.lineEdit_TestProfile.clear()
                # 递归调用，但使用默认配置
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis_service_impl:[123:166]
==impl.battery_analysis_service_impl:[85:123]
        validation_results = {
            "is_valid": True,
            "details": [],
            "failed_checks": []
        }

        # 检查温度范围
        if test_result.temperature < test_profile.min_temperature or test_result.temperature > test_profile.max_temperature:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("temperature_range")
            validation_results["details"].append(f"温度 {test_result.temperature}°C 超出允许范围 [{test_profile.min_temperature}, {test_profile.max_temperature}]°C")

        # 检查电压范围
        if test_result.voltage > test_profile.test_voltage * 1.1 or test_result.voltage < test_profile.test_voltage * 0.9:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("voltage_range")
            validation_results["details"].append(f"电压 {test_result.voltage}V 超出允许范围 [{test_profile.test_voltage * 0.9}, {test_profile.test_voltage * 1.1}]V")

        # 检查电流范围
        if abs(test_result.current) > test_profile.test_current * 1.2:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("current_range")
            validation_results["details"].append(f"电流 {test_result.current}A 超出允许范围 [-{test_profile.test_current * 1.2}, {test_profile.test_current * 1.2}]A")

        # 检查容量是否在合理范围内
        if test_result.capacity < battery.nominal_capacity * 0.5 or test_result.capacity > battery.nominal_capacity * 1.2:
            validation_results["is_valid"] = False
            validation_results["failed_checks"].append("capacity_range")
            validation_results["details"].append(f"容量 {test_result.capacity}Ah 超出合理范围 [{battery.nominal_capacity * 0.5}, {battery.nominal_capacity * 1.2}]Ah")

        return validation_results

    def calculate_performance_metrics(self, test_result: TestResult, battery: Battery) -> Dict[str, float]:
        """计算电池性能指标

        计算各种电池性能指标
        """
        # 计算健康状态
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==business_logic.visualization_manager:[241:260]
==dialogs.data_error_dialog:[150:169]
                else:
                    QW.QMessageBox.warning(
                        self.main_window,
                        "数据目录无效",
                        f"在选择的目录中没有找到 Info_Image.csv 文件:\n\n{directory}\n\n请确保选择的目录包含有效的电池数据文件。",
                        QW.QMessageBox.StandardButton.Ok
                    )
                    self.main_window.statusBar_BatteryAnalysis.showMessage("无效的数据目录")
            else:
                self.main_window.statusBar_BatteryAnalysis.showMessage("未选择目录")

        except (OSError, TypeError, ValueError, RuntimeError, PermissionError, FileNotFoundError) as e:
            self.logger.error("打开数据目录对话框时出错: %s", str(e))
            QW.QMessageBox.critical(
                self.main_window,
                "错误",
                f"打开目录选择对话框时出错:\n\n{str(e)}",
                QW.QMessageBox.StandardButton.Ok
            )
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==business_logic.visualization_manager:[117:145]
==dialogs.data_error_dialog:[27:55]
        dialog = QW.QDialog(self.main_window)
        dialog.setWindowTitle("数据加载错误 - 恢复选项")
        dialog.setModal(True)
        dialog.resize(500, 300)

        layout = QW.QVBoxLayout(dialog)

        # 错误信息标签
        error_label = QW.QLabel("无法加载电池数据，请选择如何继续:")
        error_label.setWordWrap(True)
        error_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(error_label)

        # 详细错误信息
        details_label = QW.QLabel(f"错误详情: {error_msg}")
        details_label.setWordWrap(True)
        details_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(details_label)

        # 恢复选项说明
        help_label = QW.QLabel("请选择以下恢复选项之一:")
        help_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        layout.addWidget(help_label)

        # 按钮组
        button_group = QW.QButtonGroup(dialog)

        # 选项1: 重新选择数据目录
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==business_logic.validation_manager:[377:393]
==ui_components.ui_manager:[559:575]
            self.main_window.label_BatteryType,
            self.main_window.label_ConstructionMethod,
            self.main_window.label_Specification,
            self.main_window.label_Manufacturer,
            self.main_window.label_BatchDateCode,
            self.main_window.label_SamplesQty,
            self.main_window.label_Temperature,
            self.main_window.label_DatasheetNominalCapacity,
            self.main_window.label_CalculationNominalCapacity,
            self.main_window.label_AcceleratedAging,
            self.main_window.label_RequiredUseableCapacity,
            self.main_window.label_TesterLocation,
            self.main_window.label_TestedBy,
            self.main_window.label_TestProfile,
            self.main_window.label_InputPath,
            self.main_window.label_OutputPath,
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis_service_impl:[169:201]
==impl.battery_analysis_service_impl:[123:150]
        soh = self.calculate_state_of_health(test_result, battery)

        # 计算充电效率（简单模型）
        charge_efficiency = 100.0 - (test_result.internal_resistance * 0.1)  # 内阻越大，效率越低
        charge_efficiency = max(0.0, min(100.0, charge_efficiency))

        # 计算能量密度 (Wh/kg)
        energy = test_result.capacity * test_result.voltage  # Wh
        energy_density = energy / battery.weight if battery.weight > 0 else 0.0

        # 计算功率密度 (W/kg)
        power = test_result.voltage * test_result.current  # W
        power_density = power / battery.weight if battery.weight > 0 else 0.0

        return {
            "soh": round(soh, 2),
            "charge_efficiency": round(charge_efficiency, 2),
            "energy_density": round(energy_density, 2),
            "power_density": round(power_density, 2),
            "temperature_stability": round(100.0 - abs(test_result.temperature - 25.0) * 2, 2)  # 越接近25°C，稳定性越高
        }

    def detect_anomalies(self, test_results: List[TestResult]) -> List[Dict[str, Any]]:
        """检测测试结果中的异常

        识别测试结果中的异常值
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis_service_impl:[241:252]
==impl.battery_analysis_service_impl:[197:208]
        return {
            "test_id_1": test_result1.test_id,
            "test_id_2": test_result2.test_id,
            "cycle_count_difference": test_result2.cycle_count - test_result1.cycle_count,
            "capacity_difference": round(test_result2.capacity - test_result1.capacity, 3),
            "capacity_difference_percent": round(((test_result2.capacity - test_result1.capacity) / test_result1.capacity * 100) if test_result1.capacity > 0 else 0, 2),
            "internal_resistance_difference": round(test_result2.internal_resistance - test_result1.internal_resistance, 3),
            "temperature_difference": round(test_result2.temperature - test_result1.temperature, 2),
            "voltage_difference": round(test_result2.voltage - test_result1.voltage, 3),
            "current_difference": round(test_result2.current - test_result1.current, 3)
        }
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[26:146]
==services.data_processing_service_interface:[31:176]
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
==ui_components.menu_manager:[205:225]
==ui_components.window_setup:[82:104]
        if hasattr(self.main_window, 'actionShow_Toolbar') and hasattr(self.main_window, 'toolBar'):
            self.main_window.toolBar.setVisible(self.main_window.actionShow_Toolbar.isChecked())
        elif hasattr(self.main_window, 'toolBar'):
            # 如果没有actionShow_Toolbar，只是切换显示状态
            self.main_window.toolBar.setVisible(not self.main_window.toolBar.isVisible())

    def toggle_statusbar_safe(self):
        """
        安全地切换状态栏的显示/隐藏状态
        """
        if hasattr(self.main_window, 'actionShow_Statusbar') and hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            self.main_window.statusBar_BatteryAnalysis.setVisible(
                self.main_window.actionShow_Statusbar.isChecked())
        elif hasattr(self.main_window, 'statusBar_BatteryAnalysis'):
            # 如果没有actionShow_Statusbar，只是切换显示状态
            self.main_window.statusBar_BatteryAnalysis.setVisible(
                not self.main_window.statusBar_BatteryAnalysis.isVisible())

    def zoom_in(self):
        """放大界面元素"""
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.document_service_interface:[29:170]
==services.file_service_interface:[29:152]
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
==battery_repository:[38:146]
==services.data_processing_service_interface:[31:175]
        pass

    @abstractmethod
    def find_by_model_number(self, model_number: str) -> List[Battery]:
        """根据型号查找电池

        Args:
            model_number: 电池型号

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池

        Args:
            manufacturer: 制造商

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息

        Args:
            battery: 电池实体对象

        Returns:
            更新后的电池实体对象
        """
        pass

    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池信息

        Args:
            serial_number: 电池序列号

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """统计电池数量

        Returns:
            电池数量
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[26:145]
==services.data_processing_service_interface:[44:176]
        pass

    @abstractmethod
    def find_by_serial_number(self, serial_number: str) -> Optional[Battery]:
        """根据序列号查找电池

        Args:
            serial_number: 电池序列号

        Returns:
            电池实体对象，或None
        """
        pass

    @abstractmethod
    def find_by_model_number(self, model_number: str) -> List[Battery]:
        """根据型号查找电池

        Args:
            model_number: 电池型号

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池

        Args:
            manufacturer: 制造商

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息

        Args:
            battery: 电池实体对象

        Returns:
            更新后的电池实体对象
        """
        pass

    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池信息

        Args:
            serial_number: 电池序列号

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """统计电池数量

        Returns:
            电池数量
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==iuiframework:[38:160]
==services.file_service_interface:[43:152]
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
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.document_service_interface:[43:170]
==services.file_service_interface:[29:151]
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
==services.data_processing_service_interface:[59:176]
==services.document_service_interface:[29:169]
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
==battery_repository:[50:146]
==services.data_processing_service_interface:[31:160]
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
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[26:136]
==test_profile_repository:[25:120]
        pass

    @abstractmethod
    def find_by_serial_number(self, serial_number: str) -> Optional[Battery]:
        """根据序列号查找电池

        Args:
            serial_number: 电池序列号

        Returns:
            电池实体对象，或None
        """
        pass

    @abstractmethod
    def find_by_model_number(self, model_number: str) -> List[Battery]:
        """根据型号查找电池

        Args:
            model_number: 电池型号

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池

        Args:
            manufacturer: 制造商

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息

        Args:
            battery: 电池实体对象

        Returns:
            更新后的电池实体对象
        """
        pass

    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池信息

        Args:
            serial_number: 电池序列号

        Returns:
            是否删除成功
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==iuiframework:[38:150]
==services.file_service_interface:[57:152]
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
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==iuiframework:[78:173]
==services.file_service_interface:[29:138]
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
==services.data_processing_service_interface:[44:160]
==services.validation_service_interface:[28:122]
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
==services.data_processing_service_interface:[75:176]
==services.document_service_interface:[29:155]
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
==services.data_processing_service_interface:[31:147]
==services.document_service_interface:[59:170]
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
==business_logic.visualization_manager:[98:117]
==managers.visualization_manager:[72:85]
            else:
                # 对于其他错误，显示标准错误对话框
                QW.QMessageBox.critical(
                    self.main_window,
                    "错误",
                    f"启动可视化工具时出错:\n\n{error_msg}\n\n请检查配置文件或联系技术支持。",
                    QW.QMessageBox.StandardButton.Ok
                )

            self.main_window.statusBar_BatteryAnalysis.showMessage("状态:就绪")

    def _handle_data_error_recovery(self, error_msg: str):
        """
        处理数据相关错误的恢复选项

        Args:
            error_msg: 错误信息
        """
        # 创建自定义对话框
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis_service_impl:[203:219]
==impl.battery_analysis_service_impl:[150:167]
        anomalies = []

        if len(test_results) < 3:  # 数据不足，无法检测异常
            return anomalies

        # 计算各项指标的平均值和标准差
        capacities = [result.capacity for result in test_results]
        voltages = [result.voltage for result in test_results]
        currents = [result.current for result in test_results]
        temperatures = [result.temperature for result in test_results]
        internal_resistances = [result.internal_resistance for result in test_results]

        # 使用公共工具函数进行异常检测
        from battery_analysis.utils.data_utils import detect_outliers as common_detect_outliers

        # 预计算各项指标的统计量，避免重复计算
        def precompute_stats(data):
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[50:145]
==services.config_service_interface:[30:118]
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池

        Args:
            manufacturer: 制造商

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息

        Args:
            battery: 电池实体对象

        Returns:
            更新后的电池实体对象
        """
        pass

    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池信息

        Args:
            serial_number: 电池序列号

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """统计电池数量

        Returns:
            电池数量
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[38:136]
==test_result_repository:[26:113]
        pass

    @abstractmethod
    def find_by_model_number(self, model_number: str) -> List[Battery]:
        """根据型号查找电池

        Args:
            model_number: 电池型号

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池

        Args:
            manufacturer: 制造商

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息

        Args:
            battery: 电池实体对象

        Returns:
            更新后的电池实体对象
        """
        pass

    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池信息

        Args:
            serial_number: 电池序列号

        Returns:
            是否删除成功
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[62:146]
==test_profile_repository:[25:119]
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息

        Args:
            battery: 电池实体对象

        Returns:
            更新后的电池实体对象
        """
        pass

    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池信息

        Args:
            serial_number: 电池序列号

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """统计电池数量

        Returns:
            电池数量
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[26:124]
==test_profile_repository:[37:120]
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> List[TestProfile]:
        """根据名称查找测试配置文件

        Args:
            name: 测试配置文件名称

        Returns:
            测试配置文件实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[TestProfile]:
        """根据电池类型查找测试配置文件

        Args:
            battery_type: 电池类型

        Returns:
            测试配置文件实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[TestProfile]:
        """根据制造商查找测试配置文件

        Args:
            manufacturer: 制造商

        Returns:
            测试配置文件实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[TestProfile]:
        """查找所有测试配置文件

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            测试配置文件实体对象列表
        """
        pass

    @abstractmethod
    def update(self, test_profile: TestProfile) -> TestProfile:
        """更新测试配置文件

        Args:
            test_profile: 测试配置文件实体对象

        Returns:
            更新后的测试配置文件实体对象
        """
        pass

    @abstractmethod
    def delete(self, profile_id: str) -> bool:
        """删除测试配置文件

        Args:
            profile_id: 测试配置文件ID

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """统计测试配置文件数量

        Returns:
            测试配置文件数量
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==ui_components.config_manager:[211:219]
==ui_components.ui_manager:[541:549]
            if user_config.get("OutputPath"):
                self.main_window.lineEdit_OutputPath.setText(user_config["OutputPath"])
                # 更新控制器的输出路径
                main_controller = self.main_window._get_controller("main_controller")
                if main_controller:
                    main_controller.set_project_context(
                        output_path=user_config["OutputPath"])
        except (AttributeError, TypeError, KeyError, OSError) as e:
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.file_service_interface:[70:152]
==services.validation_service_interface:[28:121]
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
==services.file_service_interface:[29:124]
==services.validation_service_interface:[41:122]
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
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.data_processing_service_interface:[90:176]
==services.document_service_interface:[29:138]
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
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.data_processing_service_interface:[31:131]
==services.document_service_interface:[75:170]
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
==services.config_service_interface:[30:117]
==test_result_repository:[38:113]
        pass

    @abstractmethod
    def set_config_value(self, key: str, value: Any) -> bool:
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def save_config(self) -> bool:
        """
        保存配置到文件

        Returns:
            bool: 保存是否成功
        """
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
    def find_config_file(self, file_name: str = "setting.ini", use_cache: bool = False) -> Optional[Path]:
        """
        查找配置文件路径

        Args:
            file_name: 配置文件名称
            use_cache: 是否使用缓存的配置文件路径，默认为False

        Returns:
            Optional[Path]: 配置文件路径，如果未找到则返回None
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.config_service_interface:[44:118]
==test_result_repository:[26:112]
        pass

    @abstractmethod
    def find_by_id(self, test_id: str) -> Optional[TestResult]:
        """根据ID查找测试结果

        Args:
            test_id: 测试结果ID

        Returns:
            测试结果实体对象，或None
        """
        pass

    @abstractmethod
    def find_by_battery_serial(self, serial_number: str) -> List[TestResult]:
        """根据电池序列号查找测试结果

        Args:
            serial_number: 电池序列号

        Returns:
            测试结果实体对象列表
        """
        pass

    @abstractmethod
    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TestResult]:
        """根据日期范围查找测试结果

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            测试结果实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[TestResult]:
        """查找所有测试结果

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            测试结果实体对象列表
        """
        pass

    @abstractmethod
    def update(self, test_result: TestResult) -> TestResult:
        """更新测试结果

        Args:
            test_result: 测试结果实体对象

        Returns:
            更新后的测试结果实体对象
        """
        pass

    @abstractmethod
    def delete(self, test_id: str) -> bool:
        """删除测试结果

        Args:
            test_id: 测试结果ID

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count_by_battery_serial(self, serial_number: str) -> int:
        """统计电池的测试结果数量

        Args:
            serial_number: 电池序列号

        Returns:
            测试结果数量
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[62:145]
==interfaces.ivisualizer:[29:90]
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
==battery_repository:[50:136]
==test_service:[34:110]
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池

        Args:
            manufacturer: 制造商

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息

        Args:
            battery: 电池实体对象

        Returns:
            更新后的电池实体对象
        """
        pass

    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池信息

        Args:
            serial_number: 电池序列号

        Returns:
            是否删除成功
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis_service:[28:107]
==battery_repository:[38:124]
        pass

    @abstractmethod
    def find_by_model_number(self, model_number: str) -> List[Battery]:
        """根据型号查找电池

        Args:
            model_number: 电池型号

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池

        Args:
            manufacturer: 制造商

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息

        Args:
            battery: 电池实体对象

        Returns:
            更新后的电池实体对象
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[74:146]
==test_profile_repository:[25:110]
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息

        Args:
            battery: 电池实体对象

        Returns:
            更新后的电池实体对象
        """
        pass

    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池信息

        Args:
            serial_number: 电池序列号

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """统计电池数量

        Returns:
            电池数量
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[26:112]
==test_profile_repository:[49:120]
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[TestProfile]:
        """根据电池类型查找测试配置文件

        Args:
            battery_type: 电池类型

        Returns:
            测试配置文件实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[TestProfile]:
        """根据制造商查找测试配置文件

        Args:
            manufacturer: 制造商

        Returns:
            测试配置文件实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[TestProfile]:
        """查找所有测试配置文件

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            测试配置文件实体对象列表
        """
        pass

    @abstractmethod
    def update(self, test_profile: TestProfile) -> TestProfile:
        """更新测试配置文件

        Args:
            test_profile: 测试配置文件实体对象

        Returns:
            更新后的测试配置文件实体对象
        """
        pass

    @abstractmethod
    def delete(self, profile_id: str) -> bool:
        """删除测试配置文件

        Args:
            profile_id: 测试配置文件ID

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """统计测试配置文件数量

        Returns:
            测试配置文件数量
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==iuiframework:[38:123]
==services.validation_service_interface:[54:122]
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
==iuiframework:[110:173]
==services.validation_service_interface:[28:108]
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
==services.document_service_interface:[88:170]
==services.file_service_interface:[29:110]
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
==services.document_service_interface:[29:117]
==services.file_service_interface:[84:152]
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
==services.config_service_interface:[54:118]
==services.data_processing_service_interface:[31:118]
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
    def find_config_file(self, file_name: str = "setting.ini", use_cache: bool = False) -> Optional[Path]:
        """
        查找配置文件路径

        Args:
            file_name: 配置文件名称
            use_cache: 是否使用缓存的配置文件路径，默认为False

        Returns:
            Optional[Path]: 配置文件路径，如果未找到则返回None
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.config_service_interface:[30:103]
==services.data_processing_service_interface:[105:176]
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
==interfaces.ivisualizer:[29:89]
==test_service:[47:110]
        pass

    @abstractmethod
    def validate_test_profile(self, test_profile: TestProfile) -> Dict[str, Any]:
        """验证测试配置是否有效

        Args:
            test_profile: 测试配置实体

        Returns:
            验证结果，包含是否有效和详细信息
        """
        pass

    @abstractmethod
    def generate_test_id(self, battery: Battery) -> str:
        """生成测试ID

        Args:
            battery: 电池实体

        Returns:
            生成的测试ID
        """
        pass

    @abstractmethod
    def get_test_summary(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """获取测试结果摘要

        Args:
            test_results: 测试结果列表

        Returns:
            测试结果摘要
        """
        pass

    @abstractmethod
    def calculate_test_statistics(self, test_results: List[TestResult]) -> Dict[str, float]:
        """计算测试统计信息

        Args:
            test_results: 测试结果列表

        Returns:
            测试统计信息
        """
        pass

    @abstractmethod
    def group_test_results_by_criteria(self, test_results: List[TestResult],
                                      criteria: str) -> Dict[str, List[TestResult]]:
        """按指定条件分组测试结果

        Args:
            test_results: 测试结果列表
            criteria: 分组条件 (如: 'date', 'battery_type', 'operator')

        Returns:
            按条件分组的测试结果
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==interfaces.ivisualizer:[42:90]
==test_service:[34:109]
        pass

    @abstractmethod
    def update_test_result(self, test_result: TestResult, test_data: Dict[str, Any]) -> TestResult:
        """更新测试结果

        Args:
            test_result: 测试结果实体
            test_data: 更新的测试数据

        Returns:
            更新后的测试结果实体
        """
        pass

    @abstractmethod
    def validate_test_profile(self, test_profile: TestProfile) -> Dict[str, Any]:
        """验证测试配置是否有效

        Args:
            test_profile: 测试配置实体

        Returns:
            验证结果，包含是否有效和详细信息
        """
        pass

    @abstractmethod
    def generate_test_id(self, battery: Battery) -> str:
        """生成测试ID

        Args:
            battery: 电池实体

        Returns:
            生成的测试ID
        """
        pass

    @abstractmethod
    def get_test_summary(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """获取测试结果摘要

        Args:
            test_results: 测试结果列表

        Returns:
            测试结果摘要
        """
        pass

    @abstractmethod
    def calculate_test_statistics(self, test_results: List[TestResult]) -> Dict[str, float]:
        """计算测试统计信息

        Args:
            test_results: 测试结果列表

        Returns:
            测试统计信息
        """
        pass

    @abstractmethod
    def group_test_results_by_criteria(self, test_results: List[TestResult],
                                      criteria: str) -> Dict[str, List[TestResult]]:
        """按指定条件分组测试结果

        Args:
            test_results: 测试结果列表
            criteria: 分组条件 (如: 'date', 'battery_type', 'operator')

        Returns:
            按条件分组的测试结果
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis_service:[28:106]
==test_result_repository:[50:113]
        pass

    @abstractmethod
    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TestResult]:
        """根据日期范围查找测试结果

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            测试结果实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[TestResult]:
        """查找所有测试结果

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            测试结果实体对象列表
        """
        pass

    @abstractmethod
    def update(self, test_result: TestResult) -> TestResult:
        """更新测试结果

        Args:
            test_result: 测试结果实体对象

        Returns:
            更新后的测试结果实体对象
        """
        pass

    @abstractmethod
    def delete(self, test_id: str) -> bool:
        """删除测试结果

        Args:
            test_id: 测试结果ID

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count_by_battery_serial(self, serial_number: str) -> int:
        """统计电池的测试结果数量

        Args:
            serial_number: 电池序列号

        Returns:
            测试结果数量
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis_service:[41:107]
==test_result_repository:[26:100]
        pass

    @abstractmethod
    def analyze_cycle_life(self, test_results: List[TestResult], battery: Battery) -> Dict[str, Any]:
        """分析电池循环寿命

        Args:
            test_results: 测试结果列表
            battery: 电池实体

        Returns:
            循环寿命分析结果
        """
        pass

    @abstractmethod
    def validate_test_result(self, test_result: TestResult, test_profile: TestProfile, battery: Battery) -> Dict[str, Any]:
        """验证测试结果是否符合测试配置要求

        Args:
            test_result: 测试结果实体
            test_profile: 测试配置实体
            battery: 电池实体

        Returns:
            验证结果，包含是否通过和详细信息
        """
        pass

    @abstractmethod
    def calculate_performance_metrics(self, test_result: TestResult, battery: Battery) -> Dict[str, float]:
        """计算电池性能指标

        Args:
            test_result: 测试结果实体
            battery: 电池实体

        Returns:
            性能指标字典
        """
        pass

    @abstractmethod
    def detect_anomalies(self, test_results: List[TestResult]) -> List[Dict[str, Any]]:
        """检测测试结果中的异常

        Args:
            test_results: 测试结果列表

        Returns:
            异常列表
        """
        pass

    @abstractmethod
    def compare_test_results(self, test_result1: TestResult, test_result2: TestResult) -> Dict[str, Any]:
        """比较两个测试结果

        Args:
            test_result1: 第一个测试结果
            test_result2: 第二个测试结果

        Returns:
            比较结果
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[38:112]
==services.service_container:[36:102]
        pass

    @abstractmethod
    def find_by_model_number(self, model_number: str) -> List[Battery]:
        """根据型号查找电池

        Args:
            model_number: 电池型号

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池

        Args:
            manufacturer: 制造商

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[87:146]
==test_profile_repository:[25:98]
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Battery]:
        """查找所有电池

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def update(self, battery: Battery) -> Battery:
        """更新电池信息

        Args:
            battery: 电池实体对象

        Returns:
            更新后的电池实体对象
        """
        pass

    @abstractmethod
    def delete(self, serial_number: str) -> bool:
        """删除电池信息

        Args:
            serial_number: 电池序列号

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """统计电池数量

        Returns:
            电池数量
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[26:99]
==test_profile_repository:[61:120]
        pass

    @abstractmethod
    def find_by_serial_number(self, serial_number: str) -> Optional[Battery]:
        """根据序列号查找电池

        Args:
            serial_number: 电池序列号

        Returns:
            电池实体对象，或None
        """
        pass

    @abstractmethod
    def find_by_model_number(self, model_number: str) -> List[Battery]:
        """根据型号查找电池

        Args:
            model_number: 电池型号

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池

        Args:
            manufacturer: 制造商

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Battery]:
        """根据状态查找电池

        Args:
            status: 电池状态

        Returns:
            电池实体对象列表
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.service_container:[50:102]
==services.validation_service_interface:[28:95]
        pass

    @abstractmethod
    def get(self, name: str) -> Optional[T]:
        """
        获取服务

        Args:
            name: 服务名称

        Returns:
            T: 服务实例，如果不存在则返回None
        """
        pass

    @abstractmethod
    def has(self, name: str) -> bool:
        """
        检查服务是否存在

        Args:
            name: 服务名称

        Returns:
            bool: 服务是否存在
        """
        pass

    @abstractmethod
    def unregister(self, name: str) -> bool:
        """
        注销服务

        Args:
            name: 服务名称

        Returns:
            bool: 注销是否成功
        """
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """
        关闭容器

        Returns:
            bool: 关闭是否成功
        """
        pass


- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.service_container:[36:99]
==services.validation_service_interface:[69:122]
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
==services.document_service_interface:[102:170]
==services.file_service_interface:[29:97]
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
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.document_service_interface:[29:102]
==services.file_service_interface:[97:152]
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
==services.config_service_interface:[67:118]
==services.data_processing_service_interface:[31:105]
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
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==services.config_service_interface:[30:90]
==services.data_processing_service_interface:[118:176]
        pass

    @abstractmethod
    def set_config_value(self, key: str, value: Any) -> bool:
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def save_config(self) -> bool:
        """
        保存配置到文件

        Returns:
            bool: 保存是否成功
        """
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
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==interfaces.ivisualizer:[29:79]
==test_service:[59:110]
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
==interfaces.ivisualizer:[49:90]
==test_service:[34:95]
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
==battery_analysis_service:[28:93]
==test_result_repository:[63:113]
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[TestResult]:
        """查找所有测试结果

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            测试结果实体对象列表
        """
        pass

    @abstractmethod
    def update(self, test_result: TestResult) -> TestResult:
        """更新测试结果

        Args:
            test_result: 测试结果实体对象

        Returns:
            更新后的测试结果实体对象
        """
        pass

    @abstractmethod
    def delete(self, test_id: str) -> bool:
        """删除测试结果

        Args:
            test_id: 测试结果ID

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def count_by_battery_serial(self, serial_number: str) -> int:
        """统计电池的测试结果数量

        Args:
            serial_number: 电池序列号

        Returns:
            测试结果数量
        """
        pass
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_analysis_service:[54:107]
==test_result_repository:[26:88]
        pass

    @abstractmethod
    def find_by_id(self, test_id: str) -> Optional[TestResult]:
        """根据ID查找测试结果

        Args:
            test_id: 测试结果ID

        Returns:
            测试结果实体对象，或None
        """
        pass

    @abstractmethod
    def find_by_battery_serial(self, serial_number: str) -> List[TestResult]:
        """根据电池序列号查找测试结果

        Args:
            serial_number: 电池序列号

        Returns:
            测试结果实体对象列表
        """
        pass

    @abstractmethod
    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[TestResult]:
        """根据日期范围查找测试结果

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            测试结果实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[TestResult]:
        """查找所有测试结果

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            测试结果实体对象列表
        """
        pass

    @abstractmethod
    def update(self, test_result: TestResult) -> TestResult:
        """更新测试结果

        Args:
            test_result: 测试结果实体对象

        Returns:
            更新后的测试结果实体对象
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[99:146]
==test_profile_repository:[25:86]
        pass

    @abstractmethod
    def find_by_id(self, profile_id: str) -> Optional[TestProfile]:
        """根据ID查找测试配置文件

        Args:
            profile_id: 测试配置文件ID

        Returns:
            测试配置文件实体对象，或None
        """
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> List[TestProfile]:
        """根据名称查找测试配置文件

        Args:
            name: 测试配置文件名称

        Returns:
            测试配置文件实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[TestProfile]:
        """根据电池类型查找测试配置文件

        Args:
            battery_type: 电池类型

        Returns:
            测试配置文件实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[TestProfile]:
        """根据制造商查找测试配置文件

        Args:
            manufacturer: 制造商

        Returns:
            测试配置文件实体对象列表
        """
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[TestProfile]:
        """查找所有测试配置文件

        Args:
            limit: 返回结果数量限制
            offset: 返回结果偏移量

        Returns:
            测试配置文件实体对象列表
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==battery_repository:[26:87]
==test_profile_repository:[73:120]
        pass

    @abstractmethod
    def find_by_serial_number(self, serial_number: str) -> Optional[Battery]:
        """根据序列号查找电池

        Args:
            serial_number: 电池序列号

        Returns:
            电池实体对象，或None
        """
        pass

    @abstractmethod
    def find_by_model_number(self, model_number: str) -> List[Battery]:
        """根据型号查找电池

        Args:
            model_number: 电池型号

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_manufacturer(self, manufacturer: str) -> List[Battery]:
        """根据制造商查找电池

        Args:
            manufacturer: 制造商

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_battery_type(self, battery_type: str) -> List[Battery]:
        """根据电池类型查找电池

        Args:
            battery_type: 电池类型

        Returns:
            电池实体对象列表
        """
        pass

    @abstractmethod
    def find_by_production_date_range(self, start_date: datetime, end_date: datetime) -> List[Battery]:
        """根据生产日期范围查找电池

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            电池实体对象列表
        """
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==analyze_data_use_case:[395:400]
==business_logic.data_processor:[477:482]
                        'total_records': len(df),
                        'columns': df.columns.tolist(),
                        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                        'non_numeric_columns': df.select_dtypes(exclude=['number']).columns.tolist(),
                        'missing_values': df.isnull().sum().to_dict(),
- 符号: duplicate-code

#### 行 1, 列 0
- 类型: refactor
- 代码: R0801
- 描述: Similar lines in 2 files
==po_translator:[82:87]
==setup_i18n:[226:231]
    test_strings = [
        "battery-analyzer",
        "Preferences",
        "Language",
        "OK",
- 符号: duplicate-code

#### 行 67, 列 11
- 类型: convention
- 代码: C1804
- 描述: "str_reported_by == ''" can be simplified to "not str_reported_by", if it is strictly a string, as an empty string is falsey
- 符号: use-implicit-booleaness-not-comparison-to-string

