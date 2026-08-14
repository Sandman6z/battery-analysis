"""
图表样式模块

提供现代化按钮样式配置和图表样式应用方法
"""

import logging
import threading

logger = logging.getLogger(__name__)

# 现代化按钮样式配置 - 增强版 v4.1
MODERN_BUTTON_STYLE = {
    'active_color': '#4CAF50',
    'inactive_color': '#FAFAFA',
    'hover_color': '#66BB6A',
    'pressed_color': '#2E7D32',

    'active_text_color': '#FFFFFF',
    'inactive_text_color': '#424242',
    'hover_text_color': '#FFFFFF',
    'pressed_text_color': '#FFFFFF',

    'border_color': '#E0E0E0',
    'border_width': 1.5,
    'border_radius': 8,

    'shadow_color': '0.15',
    'shadow_offset': (0, 2),
    'shadow_blur': 3,

    'font_size': 9,
    'font_weight': '600',

    'padding': 4,
    'spacing': 2,

    'gradient_start': 'rgba(255,255,255,0.9)',
    'gradient_end': 'rgba(250,250,250,0.9)',
    'active_gradient_start': 'rgba(76,175,80,0.9)',
    'active_gradient_end': 'rgba(102,187,106,0.9)',

    'success_color': '#4CAF50',
    'warning_color': '#FF9800',
    'info_color': '#2196F3',
    'danger_color': '#F44336',

    'selected_indicator': '#FFD54F',
    'focus_outline': '#2196F3',
}


class ChartStylingMixin:
    """图表样式混入类，提供现代化样式应用方法"""

    def _apply_modern_plot_style(self, fig, ax):
        """为图表应用现代化样式"""
        try:
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')

            if hasattr(ax, 'title'):
                ax.title.set_fontsize(18)
                ax.title.set_fontweight('bold')
                ax.title.set_color(MODERN_BUTTON_STYLE['active_color'])

            ax.tick_params(colors='#6c757d', labelsize=10)
            ax.spines['top'].set_color('#e9ecef')
            ax.spines['right'].set_color('#e9ecef')
            ax.spines['bottom'].set_color('#e9ecef')
            ax.spines['left'].set_color('#e9ecef')

            ax.grid(True, alpha=0.3, color='#e9ecef', linestyle='-', linewidth=0.5)

            logger.info("Modern chart style applied")
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("Failed to apply modern chart style: %s", e)

    def _apply_window_modern_style(self, window):
        """为PyQt6窗口应用现代化样式"""
        try:
            modern_style = """
                QMainWindow {
                    background-color: #f8f9fa;
                    color: #212529;
                    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                }
            """
            window.setStyleSheet(modern_style)
            logger.info("Modern window style applied")
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("Failed to apply modern window style: %s", e)

    def _apply_menubar_style(self, menubar):
        """为菜单栏应用现代化样式"""
        try:
            menubar_style = """
                QMenuBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff,
                        stop:1 #f8f9fa);
                    border-bottom: 1px solid #e9ecef;
                    padding: 2px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 6px 12px;
                    border-radius: 4px;
                    color: #495057;
                    font-weight: 500;
                    font-size: 12px;
                }
                QMenuBar::item:hover {
                    background-color: #e9ecef;
                    color: #495057;
                }
                QMenuBar::item:selected {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db,
                        stop:1 #2980b9);
                    color: white;
                }
            """
            menubar.setStyleSheet(menubar_style)
            logger.info("Modern menubar style applied")
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("Failed to apply modern menubar style: %s", e)

    def _apply_menu_style(self, menu):
        """为菜单应用现代化样式"""
        try:
            menu_style = """
                QMenu {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff,
                        stop:1 #f8f9fa);
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    padding: 5px;
                    min-width: 150px;
                }
                QMenu::item {
                    padding: 6px 20px;
                    border-radius: 3px;
                    color: #495057;
                }
                QMenu::item:hover {
                    background-color: #3498db;
                    color: white;
                }
                QMenu::item:selected {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db,
                        stop:1 #2980b9);
                    color: white;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #e9ecef;
                    margin: 4px 8px;
                }
            """
            menu.setStyleSheet(menu_style)
            logger.info("Modern menu style applied")
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("Failed to apply modern menu style: %s", e)

    def _update_button_style(self, state, pressed=False, hover=False):
        """更新按钮样式 - 增强版 v4.1"""
        try:
            state['bg'].set_linewidth(MODERN_BUTTON_STYLE['border_width'])
            state['bg'].set_edgecolor(MODERN_BUTTON_STYLE['border_color'])

            try:
                if hasattr(state['bg'], 'set_boxstyle'):
                    state['bg'].set_boxstyle(
                        f"round,pad={MODERN_BUTTON_STYLE['padding']/100}")
            except (AttributeError, TypeError, ValueError):
                pass

            if pressed:
                state['bg'].set_facecolor(MODERN_BUTTON_STYLE['pressed_color'])
                state['text'].set_color(MODERN_BUTTON_STYLE['pressed_text_color'])
                state['text'].set_weight(MODERN_BUTTON_STYLE['font_weight'])
                state['bg'].set_linewidth(MODERN_BUTTON_STYLE['border_width'] + 0.5)
                state['bg'].set_edgecolor(MODERN_BUTTON_STYLE['pressed_color'])
            elif hover:
                if state['active']:
                    state['bg'].set_facecolor(MODERN_BUTTON_STYLE['hover_color'])
                    state['text'].set_color(MODERN_BUTTON_STYLE['hover_text_color'])
                else:
                    state['bg'].set_facecolor('#F5F5F5')
                    state['text'].set_color(MODERN_BUTTON_STYLE['inactive_text_color'])
                state['text'].set_weight(MODERN_BUTTON_STYLE['font_weight'])
                state['bg'].set_edgecolor('#BDBDBD')
            elif state['active']:
                state['bg'].set_facecolor(MODERN_BUTTON_STYLE['active_color'])
                state['text'].set_color(MODERN_BUTTON_STYLE['active_text_color'])
                state['text'].set_weight(MODERN_BUTTON_STYLE['font_weight'])
                state['bg'].set_edgecolor(MODERN_BUTTON_STYLE['active_color'])
            else:
                state['bg'].set_facecolor(MODERN_BUTTON_STYLE['inactive_color'])
                state['text'].set_color(MODERN_BUTTON_STYLE['inactive_text_color'])
                state['text'].set_weight('normal')
                state['bg'].set_edgecolor(MODERN_BUTTON_STYLE['border_color'])

            state['bg'].set_alpha(0.95)
        except (AttributeError, TypeError, ValueError) as e:
            logger.error("Error updating button style: %s", e)

    def _reset_button_after_delay(self, state, delay=0.1):
        """延迟重置按钮状态"""
        timer = threading.Timer(delay, lambda: self._update_button_style(state))
        timer.start()
