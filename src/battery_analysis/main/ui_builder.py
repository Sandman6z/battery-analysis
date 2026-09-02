"""
主窗口 UI 构建器

将 Qt Designer .ui 文件转换为纯代码构建，恢复原始水平布局：
左侧配置面板（可滚动）+ 右侧 Run 按钮面板 + 图表区域（默认隐藏）。
"""

import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW

from battery_analysis.i18n import _


# 通用字体：Microsoft JhengHei 9pt（与旧版 .ui 一致）
_FONT = QG.QFont("Microsoft JhengHei", 9)


def _make_label(text: str, parent=None) -> QW.QLabel:
    """创建标准标签（最小宽度策略 + 通用字体）"""
    lbl = QW.QLabel(text, parent)
    lbl.setFont(_FONT)
    sp = QW.QSizePolicy(QW.QSizePolicy.Policy.Minimum, QW.QSizePolicy.Policy.Preferred)
    lbl.setSizePolicy(sp)
    return lbl


def _make_combobox(parent=None, editable=False) -> QW.QComboBox:
    """创建标准下拉框（PointingHandCursor + NoFocus + 通用字体 + 固定高度30px）"""
    cb = QW.QComboBox(parent)
    cb.setFont(_FONT)
    cb.setCursor(QG.QCursor(QC.Qt.CursorShape.PointingHandCursor))
    cb.setFocusPolicy(QC.Qt.FocusPolicy.NoFocus)
    cb.setEditable(editable)
    cb.setFixedHeight(30)
    return cb


def _make_lineedit(parent=None, readonly=False) -> QW.QLineEdit:
    """创建标准输入框（ClickFocus + 通用字体）"""
    le = QW.QLineEdit(parent)
    le.setFont(_FONT)
    le.setFocusPolicy(QC.Qt.FocusPolicy.ClickFocus)
    le.setReadOnly(readonly)
    return le


def _make_button(text: str, parent=None) -> QW.QPushButton:
    """创建标准按钮（PointingHandCursor + NoFocus + 通用字体）"""
    btn = QW.QPushButton(text, parent)
    btn.setFont(_FONT)
    btn.setCursor(QG.QCursor(QC.Qt.CursorShape.PointingHandCursor))
    btn.setFocusPolicy(QC.Qt.FocusPolicy.NoFocus)
    return btn


class UIBuilder:
    """主窗口 UI 构建器"""

    def __init__(self, main_window: QW.QMainWindow):
        self.main_window = main_window

    def build_ui(self) -> None:
        """构建主窗口 UI"""
        mw = self.main_window
        mw.setWindowTitle(_("Battery Analyzer"))
        mw.setMinimumSize(200, 200)
        mw.resize(917, 754)
        mw.setCursor(QG.QCursor(QC.Qt.CursorShape.ArrowCursor))
        mw.setTabShape(QW.QTabWidget.TabShape.Rounded)

        # 中心部件
        mw.centralwidget = QW.QWidget(mw)
        mw.centralwidget.setSizePolicy(
            QW.QSizePolicy.Policy.Expanding,
            QW.QSizePolicy.Policy.Expanding,
        )
        mw.setCentralWidget(mw.centralwidget)

        # 主垂直布局
        main_layout = QW.QVBoxLayout(mw.centralwidget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # ── 顶部操作栏（Run + Version + ReportedBy + 进度条）──
        self._build_top_bar(main_layout)

        # ── 分界线 ────────────────────────────────────────
        separator = QW.QFrame()
        separator.setFrameShape(QW.QFrame.Shape.HLine)
        separator.setFrameShadow(QW.QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #c0b8a8;")
        main_layout.addWidget(separator)

        # ── 配置面板（4 个 group box，可滚动）────────────
        content = QW.QWidget()
        content_layout = QW.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)

        self._build_test_config(content, content_layout)
        self._build_path(content, content_layout)
        self._build_battery_config(content, content_layout)
        self._build_test_information(content, content_layout)

        scroll = QW.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QW.QFrame.Shape.NoFrame)
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)  # stretch=1，配置面板占据剩余空间

        # ── 图表嵌入区域（默认隐藏）──────────────────────
        self._build_chart_area()

        # ── 状态栏 ────────────────────────────────────────
        self._build_status_bar()

        # ── 窗口居中（直接调用，窗口 show 前设置好几何参数）──
        self._adjust_window_size()

    # ─────────────────────────────────────────────────────
    #  Test Config（TesterLocation + TestedBy + TestProfile）
    # ─────────────────────────────────────────────────────
    def _build_test_config(self, parent, parent_layout) -> None:
        mw = self.main_window
        groupBox = QW.QGroupBox(_("Test Config"), parent)
        groupBox.setObjectName("groupBox_TestConfig")
        groupBox.setFont(QG.QFont("Microsoft YaHei UI", 9))
        groupBox.setMinimumHeight(110)
        groupBox.setSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)

        outer = QW.QVBoxLayout(groupBox)
        outer.setContentsMargins(5, 15, 5, 5)
        outer.setSpacing(5)

        # 行 1：TesterLocation + TestedBy（水平排列）
        row1 = QW.QHBoxLayout()
        row1.setContentsMargins(5, 5, 5, 5)
        row1.setSpacing(5)

        # TesterLocation
        hl_loc = QW.QHBoxLayout()
        hl_loc.setContentsMargins(5, 5, 5, 5)
        hl_loc.setSpacing(5)
        mw.label_TesterLocation = _make_label(_("Tester Location"))
        mw.label_TesterLocation.setObjectName("label_TesterLocation")
        hl_loc.addWidget(mw.label_TesterLocation)
        hl_loc.addSpacerItem(QW.QSpacerItem(5, 0, QW.QSizePolicy.Policy.Minimum))
        mw.comboBox_TesterLocation = _make_combobox()
        mw.comboBox_TesterLocation.setObjectName("comboBox_TesterLocation")
        sp = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.comboBox_TesterLocation.setSizePolicy(sp)
        hl_loc.addWidget(mw.comboBox_TesterLocation)
        hl_loc.setStretch(0, 1)
        hl_loc.setStretch(2, 10)
        row1.addLayout(hl_loc)

        row1.addSpacerItem(QW.QSpacerItem(5, 0, QW.QSizePolicy.Policy.Preferred))

        # TestedBy
        hl_by = QW.QHBoxLayout()
        hl_by.setContentsMargins(5, 5, 5, 5)
        hl_by.setSpacing(5)
        mw.label_TestedBy = _make_label(_("Tested By"))
        mw.label_TestedBy.setObjectName("label_TestedBy")
        hl_by.addWidget(mw.label_TestedBy)
        hl_by.addSpacerItem(QW.QSpacerItem(10, 0, QW.QSizePolicy.Policy.Minimum))
        mw.comboBox_TestedBy = _make_combobox(editable=True)
        mw.comboBox_TestedBy.setObjectName("comboBox_TestedBy")
        sp2 = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.comboBox_TestedBy.setSizePolicy(sp2)
        hl_by.addWidget(mw.comboBox_TestedBy)
        row1.addLayout(hl_by)

        outer.addLayout(row1)

        # 行 2：TestProfile
        row2 = QW.QHBoxLayout()
        row2.setContentsMargins(5, 5, 5, 5)
        row2.setSpacing(5)
        mw.label_TestProfile = _make_label(_("Test Profile"))
        mw.label_TestProfile.setObjectName("label_TestProfile")
        row2.addWidget(mw.label_TestProfile)
        row2.addSpacerItem(QW.QSpacerItem(33, 0, QW.QSizePolicy.Policy.Minimum))
        mw.lineEdit_TestProfile = _make_lineedit(readonly=True)
        mw.lineEdit_TestProfile.setObjectName("lineEdit_TestProfile")
        sp3 = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.lineEdit_TestProfile.setSizePolicy(sp3)
        row2.addWidget(mw.lineEdit_TestProfile)
        mw.pushButton_TestProfile = _make_button(_("Open"))
        mw.pushButton_TestProfile.setObjectName("pushButton_TestProfile")
        sp4 = QW.QSizePolicy(QW.QSizePolicy.Policy.Fixed, QW.QSizePolicy.Policy.Fixed)
        mw.pushButton_TestProfile.setSizePolicy(sp4)
        row2.addWidget(mw.pushButton_TestProfile)
        outer.addLayout(row2)

        parent_layout.addWidget(groupBox)
        mw.groupBox_TestConfig = groupBox

    # ─────────────────────────────────────────────────────
    #  Path（InputPath + OutputPath）
    # ─────────────────────────────────────────────────────
    def _build_path(self, parent, parent_layout) -> None:
        mw = self.main_window
        groupBox = QW.QGroupBox(_("Path"), parent)
        groupBox.setObjectName("groupBox_Path")
        groupBox.setFont(QG.QFont("Microsoft YaHei UI", 9))
        groupBox.setMinimumHeight(60)
        groupBox.setSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)

        outer = QW.QHBoxLayout(groupBox)
        outer.setContentsMargins(5, 15, 5, 5)
        outer.setSpacing(5)

        # Input Path（左半边）
        hl_in = QW.QHBoxLayout()
        hl_in.setSpacing(5)
        mw.label_InputPath = _make_label(_("Input Path "))
        mw.label_InputPath.setObjectName("label_InputPath")
        hl_in.addWidget(mw.label_InputPath)
        mw.lineEdit_InputPath = _make_lineedit(readonly=True)
        mw.lineEdit_InputPath.setObjectName("lineEdit_InputPath")
        sp = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.lineEdit_InputPath.setSizePolicy(sp)
        hl_in.addWidget(mw.lineEdit_InputPath)
        mw.pushButton_InputPath = _make_button(_("Open"))
        mw.pushButton_InputPath.setObjectName("pushButton_InputPath")
        hl_in.addWidget(mw.pushButton_InputPath)
        outer.addLayout(hl_in, 1)  # stretch=1，各占一半

        # 分隔线
        sep = QW.QFrame()
        sep.setFrameShape(QW.QFrame.Shape.VLine)
        sep.setFrameShadow(QW.QFrame.Shadow.Sunken)
        sep.setStyleSheet("color: #c0b8a8;")
        outer.addWidget(sep)

        # Output Path（右半边）
        hl_out = QW.QHBoxLayout()
        hl_out.setSpacing(5)
        mw.label_OutputPath = _make_label(_("Output Path"))
        mw.label_OutputPath.setObjectName("label_OutputPath")
        hl_out.addWidget(mw.label_OutputPath)
        mw.lineEdit_OutputPath = _make_lineedit(readonly=True)
        mw.lineEdit_OutputPath.setObjectName("lineEdit_OutputPath")
        sp3 = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.lineEdit_OutputPath.setSizePolicy(sp3)
        hl_out.addWidget(mw.lineEdit_OutputPath)
        mw.pushButton_OutputPath = _make_button(_("Open"))
        mw.pushButton_OutputPath.setObjectName("pushButton_OutputPath")
        hl_out.addWidget(mw.pushButton_OutputPath)
        outer.addLayout(hl_out, 1)  # stretch=1，各占一半

        parent_layout.addWidget(groupBox)
        mw.groupBox_Path = groupBox

    # ─────────────────────────────────────────────────────
    #  Battery Config（4 个嵌套 Frame，2×2 网格）
    # ─────────────────────────────────────────────────────
    def _build_battery_config(self, parent, parent_layout) -> None:
        mw = self.main_window
        groupBox = QW.QGroupBox(_("Battery Config"), parent)
        groupBox.setObjectName("groupBox_BatteryConfig")
        groupBox.setFont(QG.QFont("Microsoft YaHei UI", 9))
        groupBox.setMinimumHeight(400)
        groupBox.setSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Expanding)

        # 2×2 网格布局，让左右两列等宽撑满
        grid = QW.QGridLayout(groupBox)
        grid.setContentsMargins(5, 15, 5, 5)
        grid.setSpacing(5)

        # ── Frame 3：左上（BatteryType + ConstructionMethod + Specification）──
        frame_3 = QW.QFrame()
        frame_3.setFrameShape(QW.QFrame.Shape.Box)
        frame_3.setFrameShadow(QW.QFrame.Shadow.Sunken)
        sp_f3 = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Expanding)
        frame_3.setSizePolicy(sp_f3)

        vl_3 = QW.QVBoxLayout(frame_3)
        vl_3.setContentsMargins(5, 5, 5, 5)
        vl_3.setSpacing(5)

        # BatteryType
        hl_bt = QW.QHBoxLayout()
        hl_bt.setContentsMargins(5, 5, 5, 5)
        mw.label_BatteryType = _make_label(_("Battery Type"))
        mw.label_BatteryType.setObjectName("label_BatteryType")
        hl_bt.addWidget(mw.label_BatteryType)
        hl_bt.addSpacerItem(QW.QSpacerItem(62, 0, QW.QSizePolicy.Policy.Minimum))
        mw.comboBox_BatteryType = _make_combobox()
        mw.comboBox_BatteryType.setObjectName("comboBox_BatteryType")
        sp_cb = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.comboBox_BatteryType.setSizePolicy(sp_cb)
        hl_bt.addWidget(mw.comboBox_BatteryType)
        vl_3.addLayout(hl_bt)

        # ConstructionMethod
        hl_cm = QW.QHBoxLayout()
        hl_cm.setContentsMargins(5, 5, 5, 5)
        mw.label_ConstructionMethod = _make_label(_("Construction Method"))
        mw.label_ConstructionMethod.setObjectName("label_ConstructionMethod")
        hl_cm.addWidget(mw.label_ConstructionMethod)
        hl_cm.addSpacerItem(QW.QSpacerItem(12, 0, QW.QSizePolicy.Policy.Minimum))
        mw.comboBox_ConstructionMethod = _make_combobox()
        mw.comboBox_ConstructionMethod.setObjectName("comboBox_ConstructionMethod")
        sp_cb2 = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.comboBox_ConstructionMethod.setSizePolicy(sp_cb2)
        hl_cm.addWidget(mw.comboBox_ConstructionMethod)
        vl_3.addLayout(hl_cm)

        # Specification（两个下拉框垂直排列）
        hl_spec = QW.QHBoxLayout()
        hl_spec.setContentsMargins(5, 5, 5, 5)
        hl_spec.setSpacing(5)
        mw.label_Specification = _make_label(_("Specification"))
        mw.label_Specification.setObjectName("label_Specification")
        sp_lbl = QW.QSizePolicy(QW.QSizePolicy.Policy.Minimum, QW.QSizePolicy.Policy.Expanding)
        mw.label_Specification.setSizePolicy(sp_lbl)
        hl_spec.addWidget(mw.label_Specification)
        hl_spec.addSpacerItem(QW.QSpacerItem(55, 0, QW.QSizePolicy.Policy.Minimum))

        vl_spec = QW.QVBoxLayout()
        vl_spec.setContentsMargins(0, 0, 0, 0)
        vl_spec.setSpacing(6)
        mw.comboBox_Specification_Method = _make_combobox()
        mw.comboBox_Specification_Method.setObjectName("comboBox_Specification_Method")
        sp_cb3 = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.comboBox_Specification_Method.setSizePolicy(sp_cb3)
        vl_spec.addWidget(mw.comboBox_Specification_Method)
        mw.comboBox_Specification_Type = _make_combobox()
        mw.comboBox_Specification_Type.setObjectName("comboBox_Specification_Type")
        sp_cb4 = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.comboBox_Specification_Type.setSizePolicy(sp_cb4)
        vl_spec.addWidget(mw.comboBox_Specification_Type)
        hl_spec.addLayout(vl_spec)
        vl_3.addLayout(hl_spec)
        grid.addWidget(frame_3, 0, 0)

        # ── Frame 2：右上（Manufacturer + BatchDateCode + SamplesQty）──
        frame_2 = QW.QFrame()
        frame_2.setFrameShape(QW.QFrame.Shape.Box)
        frame_2.setFrameShadow(QW.QFrame.Shadow.Sunken)

        vl_2 = QW.QVBoxLayout(frame_2)
        vl_2.setContentsMargins(5, 5, 5, 5)
        vl_2.setSpacing(5)

        # Manufacturer
        hl_mfr = QW.QHBoxLayout()
        hl_mfr.setSizeConstraint(QW.QLayout.SizeConstraint.SetMinimumSize)
        hl_mfr.setContentsMargins(5, 5, 5, 5)
        mw.label_Manufacturer = _make_label(_("Manufacturer"))
        mw.label_Manufacturer.setObjectName("label_Manufacturer")
        hl_mfr.addWidget(mw.label_Manufacturer)
        hl_mfr.addSpacerItem(QW.QSpacerItem(25, 0, QW.QSizePolicy.Policy.Minimum))
        mw.comboBox_Manufacturer = _make_combobox()
        mw.comboBox_Manufacturer.setObjectName("comboBox_Manufacturer")
        sp_cb5 = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.comboBox_Manufacturer.setSizePolicy(sp_cb5)
        hl_mfr.addWidget(mw.comboBox_Manufacturer)
        vl_2.addLayout(hl_mfr)

        # BatchDateCode
        hl_bdc = QW.QHBoxLayout()
        hl_bdc.setContentsMargins(5, 5, 5, 5)
        mw.label_BatchDateCode = _make_label(_("Batch/Date Code"))
        mw.label_BatchDateCode.setObjectName("label_BatchDateCode")
        hl_bdc.addWidget(mw.label_BatchDateCode)
        hl_bdc.addSpacerItem(QW.QSpacerItem(5, 0, QW.QSizePolicy.Policy.Minimum))
        mw.lineEdit_BatchDateCode = _make_lineedit()
        mw.lineEdit_BatchDateCode.setObjectName("lineEdit_BatchDateCode")
        hl_bdc.addWidget(mw.lineEdit_BatchDateCode)
        vl_2.addLayout(hl_bdc)

        # SamplesQty
        hl_sq = QW.QHBoxLayout()
        hl_sq.setContentsMargins(5, 5, 5, 5)
        mw.label_SamplesQty = _make_label(_("Samples Qty"))
        mw.label_SamplesQty.setObjectName("label_SamplesQty")
        hl_sq.addWidget(mw.label_SamplesQty)
        hl_sq.addSpacerItem(QW.QSpacerItem(30, 0, QW.QSizePolicy.Policy.Minimum))
        mw.lineEdit_SamplesQty = _make_lineedit()
        mw.lineEdit_SamplesQty.setObjectName("lineEdit_SamplesQty")
        hl_sq.addWidget(mw.lineEdit_SamplesQty)
        vl_2.addLayout(hl_sq)
        grid.addWidget(frame_2, 0, 1)

        # ── Frame 4：左下（RequiredUseableCapacity + CalculationNominalCapacity + DatasheetNominalCapacity）──
        frame_4 = QW.QFrame()
        frame_4.setFrameShape(QW.QFrame.Shape.Box)
        frame_4.setFrameShadow(QW.QFrame.Shadow.Sunken)

        vl_4 = QW.QVBoxLayout(frame_4)
        vl_4.setContentsMargins(5, 5, 5, 5)
        vl_4.setSpacing(5)

        # RequiredUseableCapacity
        hl_ruc = QW.QHBoxLayout()
        hl_ruc.setContentsMargins(5, 5, 5, 5)
        mw.label_RequiredUseableCapacity = _make_label(_("Required Useable Capacity(mAh)"))
        mw.label_RequiredUseableCapacity.setObjectName("label_RequiredUseableCapacity")
        hl_ruc.addWidget(mw.label_RequiredUseableCapacity)
        hl_ruc.addSpacerItem(QW.QSpacerItem(25, 0, QW.QSizePolicy.Policy.Minimum))
        mw.lineEdit_RequiredUseableCapacity = _make_lineedit()
        mw.lineEdit_RequiredUseableCapacity.setObjectName("lineEdit_RequiredUseableCapacity")
        hl_ruc.addWidget(mw.lineEdit_RequiredUseableCapacity)
        vl_4.addLayout(hl_ruc)

        # CalculationNominalCapacity
        hl_cnc = QW.QHBoxLayout()
        hl_cnc.setContentsMargins(5, 5, 5, 5)
        mw.label_CalculationNominalCapacity = _make_label(_("Calculation Nominal Capacity(mAh)"))
        mw.label_CalculationNominalCapacity.setObjectName("label_CalculationNominalCapacity")
        hl_cnc.addWidget(mw.label_CalculationNominalCapacity)
        hl_cnc.addSpacerItem(QW.QSpacerItem(10, 0, QW.QSizePolicy.Policy.Minimum))
        mw.lineEdit_CalculationNominalCapacity = _make_lineedit()
        mw.lineEdit_CalculationNominalCapacity.setObjectName("lineEdit_CalculationNominalCapacity")
        hl_cnc.addWidget(mw.lineEdit_CalculationNominalCapacity)
        vl_4.addLayout(hl_cnc)

        # DatasheetNominalCapacity
        hl_dnc = QW.QHBoxLayout()
        hl_dnc.setContentsMargins(5, 5, 5, 5)
        mw.label_DatasheetNominalCapacity = _make_label(_("Datasheet Nominal Capacity(mAh)"))
        mw.label_DatasheetNominalCapacity.setObjectName("label_DatasheetNominalCapacity")
        hl_dnc.addWidget(mw.label_DatasheetNominalCapacity)
        hl_dnc.addSpacerItem(QW.QSpacerItem(15, 0, QW.QSizePolicy.Policy.Minimum))
        mw.lineEdit_DatasheetNominalCapacity = _make_lineedit()
        mw.lineEdit_DatasheetNominalCapacity.setObjectName("lineEdit_DatasheetNominalCapacity")
        hl_dnc.addWidget(mw.lineEdit_DatasheetNominalCapacity)
        vl_4.addLayout(hl_dnc)
        grid.addWidget(frame_4, 1, 0)

        # ── Frame 1：右下（TemperatureType + Temperature + AcceleratedAging）──
        frame_1 = QW.QFrame()
        frame_1.setLayoutDirection(QC.Qt.LayoutDirection.LeftToRight)
        frame_1.setFrameShape(QW.QFrame.Shape.Box)
        frame_1.setFrameShadow(QW.QFrame.Shadow.Sunken)

        vl_1 = QW.QVBoxLayout(frame_1)
        vl_1.setContentsMargins(5, 5, 5, 5)
        vl_1.setSpacing(5)

        # TemperatureType + comboBox
        hl_tt = QW.QHBoxLayout()
        hl_tt.setContentsMargins(5, 5, 5, 5)
        mw.label_TemperatureType = _make_label(_("Temp. Type"))
        mw.label_TemperatureType.setObjectName("label_TemperatureType")
        hl_tt.addWidget(mw.label_TemperatureType)
        hl_tt.addSpacerItem(QW.QSpacerItem(5, 0, QW.QSizePolicy.Policy.Minimum))
        mw.comboBox_Temperature = _make_combobox()
        mw.comboBox_Temperature.setObjectName("comboBox_Temperature")
        sp_cb6 = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.comboBox_Temperature.setSizePolicy(sp_cb6)
        hl_tt.addWidget(mw.comboBox_Temperature)
        vl_1.addLayout(hl_tt)

        # Temperature spinbox
        hl_temp = QW.QHBoxLayout()
        hl_temp.setContentsMargins(5, 5, 5, 5)
        mw.label_Temperature = _make_label(_("Temperature(℃)"))
        mw.label_Temperature.setObjectName("label_Temperature")
        hl_temp.addWidget(mw.label_Temperature)
        hl_temp.addSpacerItem(QW.QSpacerItem(50, 0, QW.QSizePolicy.Policy.Minimum))
        mw.spinBox_Temperature = QW.QSpinBox()
        mw.spinBox_Temperature.setObjectName("spinBox_Temperature")
        mw.spinBox_Temperature.setFont(_FONT)
        mw.spinBox_Temperature.setMinimum(-60)
        mw.spinBox_Temperature.setMaximum(120)
        sp_sb = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.spinBox_Temperature.setSizePolicy(sp_sb)
        hl_temp.addWidget(mw.spinBox_Temperature)
        vl_1.addLayout(hl_temp)

        # AcceleratedAging
        hl_aa = QW.QHBoxLayout()
        hl_aa.setContentsMargins(5, 5, 5, 5)
        hl_aa.setSpacing(5)
        mw.label_AcceleratedAging = _make_label(_("Accelerated Aging(Years)"))
        mw.label_AcceleratedAging.setObjectName("label_AcceleratedAging")
        hl_aa.addWidget(mw.label_AcceleratedAging)
        hl_aa.addSpacerItem(QW.QSpacerItem(5, 0, QW.QSizePolicy.Policy.Minimum))
        mw.spinBox_AcceleratedAging = QW.QSpinBox()
        mw.spinBox_AcceleratedAging.setObjectName("spinBox_AcceleratedAging")
        mw.spinBox_AcceleratedAging.setFont(_FONT)
        mw.spinBox_AcceleratedAging.setFocusPolicy(QC.Qt.FocusPolicy.ClickFocus)
        mw.spinBox_AcceleratedAging.setAlignment(
            QC.Qt.AlignmentFlag.AlignLeading | QC.Qt.AlignmentFlag.AlignLeft | QC.Qt.AlignmentFlag.AlignVCenter
        )
        mw.spinBox_AcceleratedAging.setMinimum(0)
        mw.spinBox_AcceleratedAging.setMaximum(10)
        mw.spinBox_AcceleratedAging.setProperty("value", 0)
        sp_sb2 = QW.QSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)
        mw.spinBox_AcceleratedAging.setSizePolicy(sp_sb2)
        hl_aa.addWidget(mw.spinBox_AcceleratedAging)
        vl_1.addLayout(hl_aa)
        grid.addWidget(frame_1, 1, 1)

        parent_layout.addWidget(groupBox)
        mw.groupBox_BatteryConfig = groupBox

    # ─────────────────────────────────────────────────────
    #  Test Information（ScrollArea + Table）
    # ─────────────────────────────────────────────────────
    def _build_test_information(self, parent, parent_layout) -> None:
        mw = self.main_window
        groupBox = QW.QGroupBox(_("Test Information"), parent)
        groupBox.setObjectName("groupBox_TestInformation")
        groupBox.setFont(QG.QFont("Microsoft YaHei UI", 9))
        groupBox.setMinimumHeight(131)
        groupBox.setSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Expanding)

        info_lo = QW.QVBoxLayout(groupBox)
        info_lo.setContentsMargins(5, 15, 5, 5)
        info_lo.setSpacing(0)

        # ScrollArea
        mw.scrollArea = QW.QScrollArea()
        mw.scrollArea.setObjectName("scrollArea")
        mw.scrollArea.setWidgetResizable(True)
        info_lo.addWidget(mw.scrollArea)

        scroll_content = QW.QWidget()
        scroll_content.setObjectName("scrollAreaWidgetContents")
        scroll_layout = QW.QVBoxLayout(scroll_content)
        mw.scrollArea.setWidget(scroll_content)

        # Table
        mw.tableWidget_TestInformation = QW.QTableWidget()
        mw.tableWidget_TestInformation.setObjectName("tableWidget_TestInformation")
        mw.tableWidget_TestInformation.setColumnCount(3)
        mw.tableWidget_TestInformation.setRowCount(12)
        mw.tableWidget_TestInformation.setFont(QG.QFont("Microsoft JhengHei", 8))
        mw.tableWidget_TestInformation.horizontalHeader().setVisible(False)
        mw.tableWidget_TestInformation.horizontalHeader().setMinimumSectionSize(30)
        mw.tableWidget_TestInformation.horizontalHeader().setStretchLastSection(False)
        mw.tableWidget_TestInformation.verticalHeader().setVisible(False)
        mw.tableWidget_TestInformation.verticalHeader().setDefaultSectionSize(30)
        mw.tableWidget_TestInformation.setFocusPolicy(QC.Qt.FocusPolicy.ClickFocus)
        mw.tableWidget_TestInformation.setTabKeyNavigation(False)
        scroll_layout.addWidget(mw.tableWidget_TestInformation)

        parent_layout.addWidget(groupBox)
        mw.groupBox_TestInformation = groupBox

    # ─────────────────────────────────────────────────────
    #  顶部操作栏（Run + Version + ReportedBy + 进度条）
    # ─────────────────────────────────────────────────────
    def _build_top_bar(self, parent_layout) -> None:
        mw = self.main_window

        # Run 按钮
        mw.pushButton_Run = QW.QPushButton(_("Run"))
        mw.pushButton_Run.setObjectName("pushButton_Run")
        mw.pushButton_Run.setMinimumSize(200, 36)
        run_font = QG.QFont("Consolas", 16)
        run_font.setBold(False)
        run_font.setKerning(True)
        run_font.setStyleStrategy(QG.QFont.StyleStrategy.PreferAntialias)
        mw.pushButton_Run.setFont(run_font)
        mw.pushButton_Run.setCursor(QG.QCursor(QC.Qt.CursorShape.PointingHandCursor))
        mw.pushButton_Run.setFocusPolicy(QC.Qt.FocusPolicy.ClickFocus)

        # Version
        mw.label_Version = _make_label(_("Report Ver."))
        mw.label_Version.setObjectName("label_Version")
        mw.lineEdit_Version = _make_lineedit()
        mw.lineEdit_Version.setObjectName("lineEdit_Version")
        mw.lineEdit_Version.setMaximumWidth(100)
        mw.lineEdit_Version.setAlignment(
            QC.Qt.AlignmentFlag.AlignRight | QC.Qt.AlignmentFlag.AlignTrailing | QC.Qt.AlignmentFlag.AlignVCenter
        )

        # ReportedBy
        mw.label_ReportedBy = _make_label(_("Reported By"))
        mw.label_ReportedBy.setObjectName("label_ReportedBy")
        mw.comboBox_ReportedBy = _make_combobox(editable=True)
        mw.comboBox_ReportedBy.setObjectName("comboBox_ReportedBy")
        mw.comboBox_ReportedBy.setMinimumWidth(200)
        mw.comboBox_ReportedBy.setMaximumWidth(500)
        mw.comboBox_ReportedBy.setSizePolicy(QW.QSizePolicy.Policy.Expanding, QW.QSizePolicy.Policy.Fixed)

        # 进度条
        mw.progressBar = QW.QProgressBar()
        mw.progressBar.setObjectName("progressBar")
        mw.progressBar.setMaximumHeight(24)
        mw.progressBar.setProperty("value", 0)
        mw.progressBar.setAlignment(QC.Qt.AlignmentFlag.AlignCenter)

        # 进度条（独占一行，满宽）
        parent_layout.addWidget(mw.progressBar)

        # 水平布局：[Version 组] [ReportedBy 组] [Run]
        top_bar = QW.QHBoxLayout()
        top_bar.setSpacing(10)

        # Version 组：label + field 紧凑排列
        ver_group = QW.QHBoxLayout()
        ver_group.setSpacing(4)
        ver_group.addWidget(mw.label_Version)
        ver_group.addWidget(mw.lineEdit_Version)
        top_bar.addLayout(ver_group)

        top_bar.addSpacing(20)

        # ReportedBy 组：label + combobox 紧贴，整组优先占剩余空间
        rb_group = QW.QHBoxLayout()
        rb_group.setSpacing(4)
        rb_group.addWidget(mw.label_ReportedBy)
        rb_group.addWidget(mw.comboBox_ReportedBy, 1)  # combobox 优先膨胀
        top_bar.addLayout(rb_group, 1)  # 整组给 stretch 优先级

        top_bar.addWidget(mw.pushButton_Run)

        parent_layout.addLayout(top_bar)

        # 兼容旧代码：保留 frame_RunButton 引用（某些外部代码可能访问）
        mw.frame_RunButton = QW.QFrame()
        mw.frame_RunButton.setVisible(False)

    # ─────────────────────────────────────────────────────
    #  图表区域（默认隐藏）
    # ─────────────────────────────────────────────────────
    def _build_chart_area(self) -> None:
        mw = self.main_window

        mw.chart_area_widget = QW.QWidget()
        mw.chart_area_widget.setObjectName("chart_area_widget")
        mw.chart_area_widget.setMinimumSize(600, 400)
        mw.chart_area_widget.setVisible(False)

        chart_layout = QW.QHBoxLayout(mw.chart_area_widget)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(5)

        mw.chart_control_panel = QW.QWidget()
        mw.chart_control_panel.setObjectName("chart_control_panel")
        mw.chart_control_panel.setMinimumWidth(150)
        mw.chart_control_panel.setMaximumWidth(200)
        mw.chart_control_panel.setVisible(False)
        chart_layout.addWidget(mw.chart_control_panel)

        mw.chart_container = QW.QWidget()
        mw.chart_container.setObjectName("chart_container")
        mw.chart_container.setMinimumSize(600, 400)
        mw.chart_container.setVisible(False)
        chart_layout.addWidget(mw.chart_container)

        chart_layout.setStretch(0, 1)
        chart_layout.setStretch(1, 4)

    # ─────────────────────────────────────────────────────
    #  状态栏
    # ─────────────────────────────────────────────────────
    def _build_status_bar(self) -> None:
        mw = self.main_window
        mw.statusBar_BatteryAnalysis = QW.QStatusBar()
        mw.statusBar_BatteryAnalysis.setObjectName("statusBar_BatteryAnalysis")
        mw.setStatusBar(mw.statusBar_BatteryAnalysis)

    # ─────────────────────────────────────────────────────
    #  窗口居中
    # ─────────────────────────────────────────────────────
    def _adjust_window_size(self) -> None:
        """调整窗口：最小完整显示，不超出屏幕，自动居中"""
        screen = QW.QApplication.primaryScreen().availableGeometry()
        ref_w, ref_h = 920, 750
        w = max(min(ref_w, screen.width()), 800)
        h = max(min(ref_h, screen.height()), 600)
        self.main_window.resize(w, h)

        frame = self.main_window.frameGeometry()
        frame.moveCenter(screen.center())
        if frame.top() < screen.top():
            frame.moveTop(screen.top())
        if frame.left() < screen.left():
            frame.moveLeft(screen.left())
        self.main_window.move(frame.topLeft())

    # ─────────────────────────────────────────────────────
    #  菜单 / 工具栏 / Actions
    # ─────────────────────────────────────────────────────
    def create_actions(self) -> None:
        mw = self.main_window

        # 文件菜单动作
        mw.actionNew = QG.QAction(_("New"), mw)
        mw.actionNew.setObjectName("actionNew")
        mw.actionNew.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.New))

        mw.actionOpen = QG.QAction(_("Open"), mw)
        mw.actionOpen.setObjectName("actionOpen")
        mw.actionOpen.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Open))

        mw.actionSave = QG.QAction(_("Save"), mw)
        mw.actionSave.setObjectName("actionSave")
        mw.actionSave.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Save))

        mw.actionSave_As = QG.QAction(_("Save As"), mw)
        mw.actionSave_As.setObjectName("actionSave_As")
        mw.actionSave_As.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.SaveAs))

        mw.actionExport_Report = QG.QAction(_("Export Report"), mw)
        mw.actionExport_Report.setObjectName("actionExport_Report")

        mw.actionExit = QG.QAction(_("Exit"), mw)
        mw.actionExit.setObjectName("actionExit")
        mw.actionExit.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Quit))

        # 编辑菜单动作
        mw.actionUndo = QG.QAction(_("Undo"), mw)
        mw.actionUndo.setObjectName("actionUndo")
        mw.actionUndo.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Undo))

        mw.actionRedo = QG.QAction(_("Redo"), mw)
        mw.actionRedo.setObjectName("actionRedo")
        mw.actionRedo.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Redo))

        mw.actionCut = QG.QAction(_("Cut"), mw)
        mw.actionCut.setObjectName("actionCut")
        mw.actionCut.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Cut))

        mw.actionCopy = QG.QAction(_("Copy"), mw)
        mw.actionCopy.setObjectName("actionCopy")
        mw.actionCopy.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Copy))

        mw.actionPaste = QG.QAction(_("Paste"), mw)
        mw.actionPaste.setObjectName("actionPaste")
        mw.actionPaste.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.Paste))

        mw.actionPreferences = QG.QAction(_("Preferences"), mw)
        mw.actionPreferences.setObjectName("actionPreferences")

        # 视图菜单动作
        mw.actionShow_Statusbar = QG.QAction(_("Show Statusbar"), mw)
        mw.actionShow_Statusbar.setObjectName("actionShow_Statusbar")
        mw.actionShow_Statusbar.setCheckable(True)
        mw.actionShow_Statusbar.setChecked(True)

        mw.actionZoom_In = QG.QAction(_("Zoom In"), mw)
        mw.actionZoom_In.setObjectName("actionZoom_In")
        mw.actionZoom_In.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.ZoomIn))

        mw.actionZoom_Out = QG.QAction(_("Zoom Out"), mw)
        mw.actionZoom_Out.setObjectName("actionZoom_Out")
        mw.actionZoom_Out.setShortcut(QG.QKeySequence(QG.QKeySequence.StandardKey.ZoomOut))

        mw.actionReset_Zoom = QG.QAction(_("Reset Zoom"), mw)
        mw.actionReset_Zoom.setObjectName("actionReset_Zoom")

        # 工具菜单动作
        mw.actionBatteryChartViewer = QG.QAction(_("BatteryChartViewer"), mw)
        mw.actionBatteryChartViewer.setObjectName("actionBatteryChartViewer")

        mw.actionCalculate_Battery = QG.QAction(_("Calculate Battery"), mw)
        mw.actionCalculate_Battery.setObjectName("actionCalculate_Battery")

        mw.actionAnalyze_Data = QG.QAction(_("Analyze Data"), mw)
        mw.actionAnalyze_Data.setObjectName("actionAnalyze_Data")

        mw.actionGenerate_Report = QG.QAction(_("Generate Report"), mw)
        mw.actionGenerate_Report.setObjectName("actionGenerate_Report")

        mw.actionBatch_Processing = QG.QAction(_("Batch Processing"), mw)
        mw.actionBatch_Processing.setObjectName("actionBatch_Processing")

        mw.actionConfiguration = QG.QAction(_("Configuration"), mw)
        mw.actionConfiguration.setObjectName("actionConfiguration")

        # 帮助菜单动作
        mw.actionUser_Mannual = QG.QAction(_("User Manual"), mw)
        mw.actionUser_Mannual.setObjectName("actionUser_Mannual")

        mw.actionOnline_Help = QG.QAction(_("Online Help"), mw)
        mw.actionOnline_Help.setObjectName("actionOnline_Help")

        mw.actionAbout = QG.QAction(_("About"), mw)
        mw.actionAbout.setObjectName("actionAbout")

        # 主题菜单动作
        mw.actionLight_Theme = QG.QAction(_("Light Theme"), mw)
        mw.actionLight_Theme.setObjectName("actionLight_Theme")

        mw.actionDark_Theme = QG.QAction(_("Dark Theme"), mw)
        mw.actionDark_Theme.setObjectName("actionDark_Theme")

    def create_menus(self) -> None:
        mw = self.main_window
        menubar = mw.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu(_("File"))
        file_menu.addAction(mw.actionNew)
        file_menu.addAction(mw.actionOpen)
        file_menu.addAction(mw.actionSave)
        file_menu.addAction(mw.actionSave_As)
        file_menu.addSeparator()
        file_menu.addAction(mw.actionExport_Report)
        file_menu.addSeparator()
        file_menu.addAction(mw.actionExit)

        # 编辑菜单
        edit_menu = menubar.addMenu(_("Edit"))
        edit_menu.addAction(mw.actionUndo)
        edit_menu.addAction(mw.actionRedo)
        edit_menu.addSeparator()
        edit_menu.addAction(mw.actionCut)
        edit_menu.addAction(mw.actionCopy)
        edit_menu.addAction(mw.actionPaste)
        edit_menu.addSeparator()
        edit_menu.addAction(mw.actionPreferences)

        # 视图菜单
        view_menu = menubar.addMenu(_("View"))
        view_menu.addAction(mw.actionShow_Statusbar)
        view_menu.addSeparator()
        view_menu.addAction(mw.actionZoom_In)
        view_menu.addAction(mw.actionZoom_Out)
        view_menu.addAction(mw.actionReset_Zoom)
        view_menu.addSeparator()
        view_menu.addAction(mw.actionLight_Theme)
        view_menu.addAction(mw.actionDark_Theme)

        # 工具菜单
        tools_menu = menubar.addMenu(_("Tools"))
        tools_menu.addAction(mw.actionBatteryChartViewer)
        tools_menu.addSeparator()
        tools_menu.addAction(mw.actionCalculate_Battery)
        tools_menu.addAction(mw.actionAnalyze_Data)
        tools_menu.addAction(mw.actionGenerate_Report)
        tools_menu.addAction(mw.actionBatch_Processing)
        tools_menu.addSeparator()
        tools_menu.addAction(mw.actionConfiguration)

        # 帮助菜单
        help_menu = menubar.addMenu(_("Help"))
        help_menu.addAction(mw.actionUser_Mannual)
        help_menu.addAction(mw.actionOnline_Help)
        help_menu.addSeparator()
        help_menu.addAction(mw.actionAbout)

