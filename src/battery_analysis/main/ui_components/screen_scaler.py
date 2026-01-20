"""
屏幕缩放管理器模块

这个模块实现了屏幕缩放相关的功能，包括：
- 屏幕分辨率检测
- 缩放因子计算
- 窗口缩放应用
"""

import logging
from PyQt6.QtWidgets import QApplication


class ScreenScaler:
    """
    屏幕缩放管理器类，负责屏幕分辨率检测和窗口缩放
    """
    
    def __init__(self, main_window):
        """
        初始化屏幕缩放管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.current_scale_factor = 1.0
        self.last_scale_factor = 0.0
        self.min_scale_change = 0.05  # 最小缩放变化阈值，避免微小变化导致的窗口跳动
        self.is_scaling = False  # 防止递归调用
    
    def get_current_screen(self):
        """
        获取当前窗口所在的屏幕
        
        Returns:
            QScreen: 当前屏幕对象
        """
        try:
            window_handle = self.main_window.windowHandle()
            if window_handle:
                return window_handle.screen()
            # 如果无法获取窗口句柄，返回主屏幕
            return QApplication.primaryScreen()
        except Exception as e:
            self.logger.warning("获取当前屏幕失败: %s", e)
            # 返回主屏幕作为备选
            return QApplication.primaryScreen()
    
    def calculate_scale_factor(self):
        """
        根据当前屏幕分辨率计算适当的缩放因子
        
        Returns:
            float: 缩放因子
        """
        try:
            screen = self.get_current_screen()
            if not screen:
                return 1.0
            
            # 获取屏幕可用尺寸
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            self.logger.debug(f"当前屏幕尺寸: {screen_width}x{screen_height}")
            
            # 基于屏幕尺寸计算缩放因子
            # 假设标准屏幕尺寸为1920x1080
            standard_width = 1920
            standard_height = 1080
            
            # 计算宽度和高度的缩放比例
            width_scale = screen_width / standard_width
            height_scale = screen_height / standard_height
            
            # 使用较小的缩放比例，确保窗口在屏幕上完全显示
            scale_factor = min(width_scale, height_scale)
            
            # 限制缩放因子范围，避免过小或过大
            scale_factor = max(0.6, min(scale_factor, 1.5))
            
            self.current_scale_factor = scale_factor
            self.logger.debug(f"计算的缩放因子: {scale_factor}")
            
            return scale_factor
        except Exception as e:
            self.logger.warning("计算缩放因子失败: %s", e)
            return 1.0
    
    def apply_scale(self):
        """
        应用缩放因子到窗口和UI组件
        """
        # 防止递归调用
        if self.is_scaling:
            return
        
        try:
            self.is_scaling = True
            
            scale_factor = self.calculate_scale_factor()
            
            # 检查缩放因子的变化是否超过阈值，避免微小变化导致的窗口跳动
            if abs(scale_factor - self.last_scale_factor) < self.min_scale_change:
                self.logger.debug(f"缩放因子变化过小，跳过调整: {scale_factor} vs {self.last_scale_factor}")
                return
            
            # 获取当前窗口尺寸
            current_width = self.main_window.width()
            current_height = self.main_window.height()
            
            # 计算新的窗口尺寸
            new_width = int(current_width * scale_factor)
            new_height = int(current_height * scale_factor)
            
            # 检查新尺寸是否与当前尺寸有显著差异，避免微小变化导致的窗口跳动
            if abs(new_width - current_width) < 10 and abs(new_height - current_height) < 10:
                self.logger.debug(f"窗口尺寸变化过小，跳过调整: {current_width}x{current_height} vs {new_width}x{new_height}")
                return
            
            # 设置最小尺寸为缩放后的合理值
            min_width = int(800 * scale_factor)
            min_height = int(600 * scale_factor)
            self.main_window.setMinimumSize(min_width, min_height)
            
            # 调整窗口尺寸
            self.main_window.resize(new_width, new_height)
            
            # 确保窗口不会超出屏幕边界
            screen = self.get_current_screen()
            if screen:
                screen_geometry = screen.availableGeometry()
                window_geometry = self.main_window.geometry()
                
                # 如果窗口超出屏幕右边界，调整位置
                if window_geometry.right() > screen_geometry.right():
                    new_x = screen_geometry.right() - window_geometry.width()
                    window_geometry.setX(max(0, new_x))
                
                # 如果窗口超出屏幕下边界，调整位置
                if window_geometry.bottom() > screen_geometry.bottom():
                    new_y = screen_geometry.bottom() - window_geometry.height()
                    window_geometry.setY(max(0, new_y))
                
                # 应用新的窗口位置
                self.main_window.setGeometry(window_geometry)
            
            self.last_scale_factor = scale_factor
            self.logger.info(f"应用缩放因子: {scale_factor}，新窗口尺寸: {new_width}x{new_height}")
        except Exception as e:
            self.logger.error("应用缩放失败: %s", e)
        finally:
            self.is_scaling = False