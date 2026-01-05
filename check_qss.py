from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase

app = QApplication([])
try:
    with open('src/battery_analysis/ui/styles/battery_analyzer.qss', 'r', encoding='utf-8') as f:
        qss_content = f.read()
    app.setStyleSheet(qss_content)
    print('样式表解析成功')
except Exception as e:
    print(f'样式表解析失败: {e}')
finally:
    app.quit()