"""Rebuild en/zh_CN .po catalogs from source _() msgids + Chinese dict.

Usage:  python scripts/rebuild_po.py
Prereq: 源码中不得残留模块级双参 _("key", "fallback") 调用
（Task 1.3-1.5 已清理）。language_handler.py 中 self._("key", "default")
遗留调用仍会被提取，属预期行为（Phase 3 会删除该模块）。
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
LOCALE_DIR = ROOT / "locale"

# msgid(英文) -> 中文译文
CHINESE = {
    # ——— 来自双参 _() 的 fallback（fallback 为中文的取原值；为英文的取新译）———
    "New Project": "新建项目",
    "Open Project": "打开项目",
    "Save Settings": "保存设置",
    "Save As": "另存为",
    "Exit": "退出应用",
    "Undo": "撤销操作",
    "Redo": "重做操作",
    "Cut": "剪切选中内容",
    "Copy": "复制选中内容",
    "Paste": "粘贴内容",
    "Zoom In": "放大界面",
    "Zoom Out": "缩小界面",
    "Reset Zoom": "重置界面缩放",
    "Show/Hide Toolbar": "显示/隐藏工具栏",
    "Show/Hide Status Bar": "显示/隐藏状态栏",
    "Calculate Battery Parameters": "计算电池参数",
    "Analyze Data": "分析数据",
    "Generate Report": "生成报告",
    "Open Battery Chart Viewer": "打开电池图表查看器",
    "Batch Process Data": "批量处理数据",
    "Manage Data Dictionary": "配置管理系统数据字典",
    "Preferences": "首选项",
    "Open User Manual": "打开用户手册",
    "Open Online Help": "打开在线帮助",
    "About": "关于应用",
    "Export Report": "导出报告",
    "Ready": "就绪",
    "Use System Default Theme": "使用系统默认主题",
    "Use Windows 11 Style Theme": "使用Windows 11风格主题",
    "Use Windows Vista Style Theme": "使用Windows Vista风格主题",
    "Use Cross-platform Fusion Theme": "使用跨平台Fusion主题",
    "Use Dark Theme for Night Use": "使用深色主题，适合夜间使用",
    "Switched to System Default theme": "已切换到系统默认主题",
    "Switched to Fusion theme": "已切换到Fusion主题",
    "Switched to Dark theme": "已切换到深色主题",
    "Switched to Simple Dark theme": "已切换到简单深色主题",
    "Confirm Exit": "确认退出",
    "Are you sure you want to exit the application?": "确定要退出应用程序吗？",
    "About Battery Analyzer": "关于电池分析器",
    "Error": "错误",
    "Warning": "警告",
    "Data Load Error - Recovery Options": "数据加载错误 - 恢复选项",
    "Unable to load battery data. Choose how to continue:": "无法加载电池数据，请选择如何继续:",
    "Choose one of the following recovery options:": "请选择以下恢复选项之一:",
    "Reselect Data Directory": "重新选择数据目录",
    "Restart with Default Configuration": "使用默认配置重新启动",
    "Cancel Operation": "取消操作",
    "OK": "确定",
    "Cancel": "取消",
    "Opening data directory selector...": "正在打开数据目录选择...",
    "Restarting with default configuration...": "使用默认配置重新启动...",
    "Restart": "重新启动",
    "The application will restart with the default configuration.\n\nPlease make sure you have valid data files available.": "应用将使用默认配置重新启动。\n\n请确保您有有效的数据文件可用。",
    "Operation canceled": "操作已取消",
    "Canceled": "取消",
    "Operation canceled. You can retry via the 'File -> Open Data' menu.": "操作已取消。您可以通过菜单 'File -> Open Data' 重新尝试。",
    "[Error]: Input path has no data": "[Error]: 输入路径没有数据",
    "Please set the input path first.": "请先设置输入路径。",
    "Analyzing data...": "分析数据...",
    "Analysis Result": "分析结果",
    "Battery Analysis Progress": "电池分析进度",
    "Ready to start analysis...": "准备开始分析...",
    "Task canceled...": "任务已取消...",
    "No Excel files found.": "没有找到Excel文件。",
    "Data analysis failed: {}": "数据分析失败: {}",
    "Failed to open online help.": "无法打开在线帮助。",
    "App icon not found; using default icon.": "未找到应用图标文件，使用默认图标",
    "Input Validation Failed": "输入验证失败",
    "Input data path cannot be empty": "输入数据路径不能为空",
    "Output path cannot be empty": "输出路径不能为空",
    "Start Failed": "启动失败",
    "Cannot start the analysis task": "无法启动分析任务",
    "Test Config": "测试配置",
    "Battery Config": "电池配置",
    "Select Test Profile": "选择测试文件",
    "Select Input Path": "选择输入路径",
    "Select Output Path": "选择输出路径",
    "Run Analysis": "运行分析",
    "Test Information Table": "测试信息表格",
    # ——— Preferences 各项（原 fallback 为英文，补充中文）———
    "General Settings": "常规设置",
    "Auto-save settings": "自动保存设置",
    "Automatically save settings when changes are made": "更改时自动保存设置",
    "Confirm before exiting": "退出前确认",
    "Show confirmation dialog when exiting the application": "退出应用程序时显示确认对话框",
    "Display Settings": "显示设置",
    "Theme:": "主题:",
    "Light": "浅色",
    "Dark": "深色",
    "System": "跟随系统",
    "Font Size:": "字体大小:",
    "General": "常规",
    "Language Settings": "语言设置",
    "Current Language:": "当前语言:",
    "Select Language:": "选择语言:",
    "Apply Language": "应用语言",
    "Translation Status": "翻译状态",
    "Translation information will be displayed here.": "翻译信息将显示在这里。",
    "Language": "语言",
    "Configuration File Settings": "配置文件设置",
    "Current Config Path:": "当前配置路径:",
    "Not loaded": "未加载",
    "Custom Config Path:": "自定义配置路径:",
    "Enter custom configuration file path...": "输入自定义配置文件路径...",
    "Browse...": "浏览...",
    "Validate Configuration": "校验配置",
    "Required Sections in Config File": "配置文件必需部分",
    "Reset to Default": "重置为默认",
    "Config": "配置",
    "Select Configuration File": "选择配置文件",
    "Please enter a configuration file path": "请输入配置文件路径",
    "File does not exist": "文件不存在",
    "JSON root must be an object": "JSON 根必须是对象",
    "Configuration file is valid!": "配置文件有效！",
    "INI format is deprecated; consider migrating to config.json": "INI 格式已弃用，建议迁移到 config.json",
    "Apply": "应用",
    "Using default paths": "使用默认路径",
    "Failed to change language": "切换语言失败",
    "Language change error": "切换语言错误",
    "Settings apply error": "设置应用错误",
    "Failed to save configuration": "保存配置失败",
    "Failed to show preferences dialog": "显示首选项对话框失败",
    "Cannot open user manual": "无法打开用户手册",
    "Version format is invalid. Expected x.y.z format": "版本号格式不正确，应为 x.y.z 格式",
    "Input path does not exist": "输入路径不存在",
    "The following required fields are empty": "以下必填字段为空",
    # ——— ui_manager 无障碍名称/描述与 tooltip（Task 1.5 引入）———
    "Start battery analysis": "开始电池分析",
    "Select battery type": "选择电池类型",
    "Select battery construction method": "选择电池构造方法",
    "Select battery specification type": "选择电池规格类型",
    "Select battery specification method": "选择电池规格方法",
    "Select battery manufacturer": "选择电池制造商",
    "Enter battery batch date code": "输入电池批次日期代码",
    "Enter number of samples": "输入样品数量",
    "Enter freezing temperature value": "输入冷冻温度值",
    "Enter datasheet nominal capacity": "输入数据手册中的标称容量",
    "Enter calculated nominal capacity": "输入计算得出的标称容量",
    "Enter accelerated aging days": "输入加速老化天数",
    "Enter required usable capacity": "输入所需可用容量",
    "Enter version number": "输入版本号",
    "Select tester location": "选择测试地点",
    "Select tested-by": "选择测试人员",
    "Select reported-by": "选择报告人员",
    "Select temperature type": "选择温度类型",
    "Test profile file path": "测试配置文件路径",
    "Select test profile file": "选择测试配置文件",
    "Input data file path": "输入数据文件路径",
    "Select input data file path": "选择输入数据文件路径",
    "Output result file path": "输出结果文件路径",
    "Select output result file path": "选择输出结果文件路径",
    "Settings related to the test configuration": "包含测试相关配置的设置",
    "Settings related to the battery configuration": "包含电池相关配置的设置",
    "Select battery test profile file": "选择电池测试配置文件",
    "Select analysis output path": "选择分析结果输出路径",
    "Table containing test equipment and software version information": "包含测试设备和软件版本信息的表格",
    "Test config group - settings related to the test configuration": "测试配置组 - 包含测试相关配置的设置",
    "Battery config group - settings related to the battery configuration": "电池配置组 - 包含电池相关配置的设置",
    "Test information table - contains test equipment and software version information": "测试信息表格 - 包含测试设备和软件版本信息",
    "✓ Translation is complete": "✓ 翻译完整",
    "⚠ Some translations are missing": "⚠ 部分翻译缺失",
    # ——— Config 对话框分类（Phase 2 使用）———
    "Equipment": "设备",
    "Reset Defaults": "恢复默认",
    "Save": "保存",
    "Reset all configuration to default values? This cannot be undone.": "将所有配置恢复为默认值？此操作不可撤销。",
    "Configuration": "配置",
    "Battery": "电池",
    "Test": "测试",
    "Test Data Dictionary": "测试数据字典",
    "Test Parameters": "测试参数",
    "Battery Types": "电池类型",
    "Construction Methods": "构造方式",
    "Specification Methods": "规格方式",
    "Manufacturers": "制造商",
    "Rules": "规则",
    "Specifications": "规格型号",
    "Pulse Currents": "脉冲电流",
    "Cut-off Voltages": "截止电压",
    "Tested By": "测试人员",
}

# 只匹配独立 _("...") 调用，排除 __init__(、self._( 等误报
MSGID_RE = re.compile(r'(?<![\w._])_\s*\(\s*"((?:[^"\\]|\\.)*)"')


def extract_msgids(src_dir: Path) -> "list[str]":
    msgids: "list[str]" = []
    for path in sorted(src_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for m in MSGID_RE.finditer(text):
            # msgid 约定：不得含字面反斜杠序列（仅允许 \n 换行转义）。
            # 顺序敏感的 unescape 会把 _("Save to C:\\temp") 里的 \\ 破坏。
            msgid = m.group(1).replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
            if msgid and msgid not in msgids:
                msgids.append(msgid)
    return msgids


def parse_po(path: Path) -> dict:
    if not path.exists():
        return {}
    entries = {}
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n{2,}", text)
    for block in blocks:
        m = re.search(r'^msgid\s+"((?:[^"\\]|\\.)*)"\s*$', block, re.MULTILINE)
        s = re.search(r'^msgstr\s+"((?:[^"\\]|\\.)*)"\s*$', block, re.MULTILINE)
        if m and s:
            # 与 extract_msgids 相同的 unescape 约定：仅 \n 换行转义，
            # msgid/msgstr 不得含字面反斜杠序列。
            msgid = m.group(1).replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
            msgstr = s.group(1).replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
            if msgid:
                entries[msgid] = msgstr
    return entries


def _po_quote(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def render_po(lang: str, entries: list) -> str:
    lines = [
        f'# {lang} translations for Battery Analysis application',
        f'# Language: {lang}',
        'msgid ""',
        'msgstr ""',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"',
        "",
    ]
    for msgid, msgstr in entries:
        lines.append(f'msgid "{_po_quote(msgid)}"')
        lines.append(f'msgstr "{_po_quote(msgstr)}"')
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    msgids = extract_msgids(SRC_DIR)
    existing_zh = parse_po(LOCALE_DIR / "zh_CN" / "LC_MESSAGES" / "messages.po")

    en_entries = [(m, m) for m in msgids]
    zh_entries = []
    for m in msgids:
        zh_entries.append((m, CHINESE.get(m, existing_zh.get(m, m))))

    (LOCALE_DIR / "en" / "LC_MESSAGES" / "messages.po").write_text(
        render_po("en", en_entries), encoding="utf-8")
    (LOCALE_DIR / "zh_CN" / "LC_MESSAGES" / "messages.po").write_text(
        render_po("zh_CN", zh_entries), encoding="utf-8")
    print(f"Rebuilt en.po ({len(msgids)} entries) and zh_CN.po ({len(msgids)} entries)")


if __name__ == "__main__":
    main()
