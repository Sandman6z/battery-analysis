"""
共享常量定义

独立模块，不依赖任何 battery_analysis 内部模块，避免循环导入。
"""

# Matplotlib 中文字体配置
# 注意：首个字体必须支持中文字形，后续为备选
CN_FONT_LIST = [
    'Microsoft YaHei',       # Windows 中文字体
    'SimHei',                # Windows 中文字体
    'Segoe UI Emoji',        # Windows emoji 支持
    'DengXian',              # Windows 等线字体
    'DejaVu Sans',           # matplotlib 内置备选
    'Arial', 'Times New Roman',
]

# 电池类型基础规格
BATTERY_TYPE_BASE = ["CoinCell", "ButtonCell", "Cylindrical", "Prismatic", "PouchCell"]

# 绘图颜色
PLT_COLOR_TYPE = ['#DF7040', '#0675BE', '#EDB120',
                  '#7E2F8E', '#32CD32', '#FF4500', '#000000', '#000000']
COLOR_NAME = ["red = ", "blue = ", "yellow = ",
              "violet = ", "green = ", "orange = ", "black1 = ", "black2 = "]

# 文件名常量
INFO_IMAGE_CSV = "Info_Image.csv"
