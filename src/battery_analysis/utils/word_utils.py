from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE
import logging

def table_set_bg_color(_cell, _RGBColor: str) -> None:
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
            logging.warning(f"配置中找不到section '{_strSection}'，返回空字符串")
            return ""
        
        # 检查item是否存在
        if not config.has_option(_strSection, _strItem):
            logging.warning(f"配置中找不到选项 '{_strItem}' in section '{_strSection}'，返回空字符串")
            return ""
        
        # 获取值并处理
        _listItem = config.get(_strSection, _strItem).split(",")
        _strBlankSpace = " " * _intBlankspaceNum
        for _i in range(len(_listItem)):
            _listItem[_i] = _listItem[_i].strip()
        _strValue = _listItem[0]
        for _i in range(1, len(_listItem)):
            _strValue += f"\n{_strBlankSpace}{_listItem[_i]}"
        return _strValue
    except Exception as e:
        logging.error(f"获取配置项 '{_strItem}' from section '{_strSection}'时出错: {e}")
        return ""

def add_hyperlink(_pParagraph, _strUrl: str, _strText: str):
    # This gets access to the document.xml.rels file and gets a new relation id value
    _part = _pParagraph.part
    _rId = _part.relate_to(_strUrl, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    # Create the w:hyperlink tag and add needed values
    _hyperlink = OxmlElement('w:hyperlink')
    _hyperlink.set(qn('r:id'), _rId, )

    # Create a w:r element
    _run = OxmlElement('w:r')

    # Create a new w:rPr element
    _rPr = OxmlElement('w:rPr')
    