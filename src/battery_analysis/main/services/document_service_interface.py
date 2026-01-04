# -*- coding: utf-8 -*-
"""
文档服务接口模块

定义文档操作相关的抽象接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from pathlib import Path


class IDocumentService(ABC):
    """
    文档服务接口
    提供Word、Excel等文档操作功能
    """
    
    @abstractmethod
    def create_word_document(self, template_path: Optional[str] = None) -> Any:
        """
        创建Word文档
        
        Args:
            template_path: Word模板文件路径
            
        Returns:
            Any: Word文档对象
        """
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
