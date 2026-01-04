#!/usr/bin/env python3
"""
为refactoring.md文件中的目录项添加中文注释
"""

import re

def main():
    # 定义问题类型的中文描述映射
    issue_descriptions = {
        "broad-exception-caught": "捕获了过于通用的异常Exception",
        "attribute-defined-outside-init": "在__init__方法外定义了属性",
        "unnecessary-pass": "不必要的pass语句",
        "unused-import": "未使用的导入",
        "import-outside-toplevel": "在顶级作用域之外导入",
        "wrong-import-order": "导入顺序错误",
        "use-implicit-booleaness-not-comparison-to-string": "使用隐式布尔值而非与字符串比较",
        "use-implicit-booleaness-not-comparison-to-zero": "使用隐式布尔值而非与零比较",
        "no-else-return": "return后不必要的else语句",
        "missing-final-newline": "文件末尾缺少换行符",
        "f-string-without-interpolation": "f-string中没有插值表达式",
        "too-many-branches": "分支过多",
        "too-many-statements": "语句过多",
        "redefined-outer-name": "重新定义了外部名称",
        "consider-using-enumerate": "考虑使用enumerate",
        "wrong-import-position": "导入位置错误",
        "protected-access": "访问受保护成员",
        "reimported": "重复导入",
        "unused-variable": "未使用的变量",
        "too-many-instance-attributes": "实例属性过多",
        "unused-argument": "未使用的参数",
        "too-many-positional-arguments": "位置参数过多",
        "ungrouped-imports": "导入未分组",
        "too-many-nested-blocks": "嵌套块过多",
        "missing-module-docstring": "缺少模块文档字符串",
        "relative-beyond-top-level": "相对导入超出顶层",
        "bare-except": "裸露的except语句",
        "subprocess-run-check": "subprocess.run缺少check参数",
        "consider-using-with": "考虑使用with语句",
        "undefined-variable": "未定义的变量",
        "redefined-builtin": "重新定义了内置函数",
        "global-statement": "使用了global语句",
        "too-many-lines": "函数行数过多",
        "raise-missing-from": "raise缺少from子句",
        "unidiomatic-typecheck": "非惯用的类型检查",
        "deprecated-method": "使用了已弃用的方法",
        "use-dict-literal": "使用字典字面量而非dict()",
        "pointless-string-statement": "无意义的字符串语句",
        "too-many-return-statements": "return语句过多",
        "broad-exception-raised": "抛出了过于通用的异常",
        "consider-merging-isinstance": "考虑合并isinstance检查",
        "syntax-error": "语法错误",
        "locally-disabled": "局部禁用了检查",
        "suppressed-message": "抑制了消息",
        "inconsistent-return-statements": "return语句不一致",
        "unnecessary-lambda": "不必要的lambda表达式",
        "unspecified-encoding": "未指定编码",
        "mixed-line-endings": "混合的行结束符",
        "consider-using-in": "考虑使用in操作符",
        "unbalanced-tuple-unpacking": "元组解包不平衡",
        "logging-too-many-args": "logging参数过多",
        "use-maxsplit-arg": "使用maxsplit参数",
        "used-before-assignment": "赋值前使用",
        "arguments-renamed": "参数被重命名",
        "consider-using-f-string": "考虑使用f-string",
        "eval-used": "使用了eval",
        "function-redefined": "函数被重新定义",
        "useless-parent-delegation": "无用的父类委托",
        "assignment-from-no-return": "从无返回值的函数赋值",
        "unsubscriptable-object": "不可订阅的对象",
        "too-many-public-methods": "公共方法过多",
        "no-else-break": "break后不必要的else语句",
        "no-member": "对象没有该成员",
        "consider-using-from-import": "考虑使用from...import",
        "useless-object-inheritance": "无用的object继承",
        "access-member-before-definition": "在定义前访问成员",
        "import-error": "导入错误"
    }
    
    # 读取文件内容
    with open('refactoring.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义正则表达式匹配目录项
    pattern = r'(\d+\. \[(\w[-\w]+)\]\(#问题类型-\2\))'
    
    # 替换每个目录项，添加中文注释
    def replace_func(match):
        full_item = match.group(1)
        issue_type = match.group(2)
        if issue_type in issue_descriptions:
            return f"{full_item}  # {issue_descriptions[issue_type]}"
        return full_item
    
    new_content = re.sub(pattern, replace_func, content)
    
    # 写回文件
    with open('refactoring.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("已成功为目录中的所有问题类型添加中文注释")

if __name__ == "__main__":
    main()
