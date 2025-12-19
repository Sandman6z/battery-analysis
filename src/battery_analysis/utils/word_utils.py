"""电池分析报告生成的Word工具类。

该模块提供了使用python-docx操作Word文档的工具函数，
包括表格背景色设置、配置项检索和超链接创建等功能。
"""
import logging
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE


def table_set_bg_color(_cell, _RGBColor: str) -> None:
    # 访问受保护成员_tc是必要的，用于修改表格单元格背景色
    # 因为python-docx的公共API未暴露此功能
    # pylint: disable-next=protected-access
    tc = _cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'pct100')
    shd.set(qn('w:fill'), f'{_RGBColor}')
    tcPr.append(shd)

def get_item(config, _strSection: str, _strItem: str, _intBlankspaceNum: int = 0) -> str:
    try:
        # 检查section是否存在
        if not config.has_section(_strSection):
            logging.warning("配置中找不到section '%s'，返回空字符串", _strSection)
            return ""

        # 检查item是否存在
        if not config.has_option(_strSection, _strItem):
            logging.warning(
                "配置中找不到section '%s'中的选项 '%s'，返回空字符串", _strSection, _strItem)
            return ""

        # 获取值并处理
        _listItem = config.get(_strSection, _strItem).split(",")
        _strBlankSpace = " " * _intBlankspaceNum
        _listItem = [item.strip() for item in _listItem]
        if not _listItem:
            return ""
        _strValue = _listItem[0]
        if len(_listItem) > 1:
            _strValue += "".join([f"\n{_strBlankSpace}{item}" for item in _listItem[1:]])
        return _strValue
    except (AttributeError, ValueError, IndexError) as e:
        logging.error(
            "获取section '%s'中的配置项 '%s'时出错: %s", _strSection, _strItem, e)
        return ""


def add_hyperlink(_pParagraph, _strUrl: str, _strText: str):
    # 此操作获取document.xml.rels文件的访问权限并获取新的关系id值
    _part = _pParagraph.part
    _rId = _part.relate_to(
        _strUrl, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    # 创建w:hyperlink标签并添加所需值
    _hyperlink = OxmlElement('w:hyperlink')
    _hyperlink.set(qn('r:id'), _rId)

    # 创建w:r元素
    _run = OxmlElement('w:r')

    # 创建新的w:rPr元素
    _rPr = OxmlElement('w:rPr')

    # 创建w:rStyle元素并将其值设置为'Hyperlink'
    _rStyle = OxmlElement('w:rStyle')
    _rStyle.set(qn('w:val'), 'Hyperlink')
    _rPr.append(_rStyle)

    # 设置字体颜色为蓝色（蓝色的十六进制值为0000FF）
    _color = OxmlElement('w:color')
    _color.set(qn('w:val'), '0000FF')
    _rPr.append(_color)

    # 设置下划线
    _u = OxmlElement('w:u')
    _u.set(qn('w:val'), 'single')
    _rPr.append(_u)

    # 设置字体大小为"小五"（Word中的9pt，对应Word XML中的18）
    _sz = OxmlElement('w:sz')
    _sz.set(qn('w:val'), '18')
    _szCs = OxmlElement('w:szCs')
    _szCs.set(qn('w:val'), '18')
    _rPr.append(_sz)
    _rPr.append(_szCs)

    # 将rPr元素添加到run
    _run.append(_rPr)

    # 创建w:t元素并添加文本内容
    _text = OxmlElement('w:t')
    _text.text = _strText

    # 将文本元素添加到run
    _run.append(_text)

    # 将run元素添加到超链接
    _hyperlink.append(_run)

    # 访问受保护成员_p是必要的，用于添加超链接元素
    # 因为python-docx的公共API未暴露此功能
    # pylint: disable-next=protected-access
    _pParagraph._p.append(_hyperlink)
