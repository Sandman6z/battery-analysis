"""One-time introduction to selecting original NDAX data directly."""

from PyQt6 import QtCore as QC
from PyQt6 import QtGui as QG
from PyQt6 import QtWidgets as QW

from battery_analysis.i18n import _
from battery_analysis.ui.styles.style_manager import get_theme_engine

# Track this workflow change, not every application patch version.
GUIDE_SETTING_KEY = "onboarding/ndax_direct_folder_v1"


class NdaxPathGuide(QW.QWidget):
    """Spotlight the real Open button without replacing its normal action."""

    def __init__(self, parent: QW.QWidget, target: QW.QPushButton, settings: QC.QSettings):
        super().__init__(parent)
        self.target = target
        self.settings = settings
        self.setObjectName("ndaxPathGuide")
        self.setFocusPolicy(QC.Qt.FocusPolicy.StrongFocus)

        self.card = QW.QFrame(self)
        self.card.setObjectName("ndaxGuideCard")
        self.card.setAutoFillBackground(True)
        layout = QW.QVBoxLayout(self.card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        title = QW.QLabel(_("Open your NDAX folder directly"))
        font = title.font()
        font.setBold(True)
        title.setFont(font)
        title.setWordWrap(True)
        layout.addWidget(title)
        self.description = QW.QLabel(
            _(
                "No Excel folder is needed anymore. Click Open next to the NDAX path "
                "and select the original folder containing your NDAX files."
            )
        )
        self.description.setWordWrap(True)
        self.description.setTextFormat(QC.Qt.TextFormat.PlainText)
        layout.addWidget(self.description)
        self.done_button = QW.QPushButton(_("Got it"))
        self.done_button.setMinimumHeight(32)
        self.done_button.clicked.connect(self.finish)
        layout.addWidget(self.done_button, alignment=QC.Qt.AlignmentFlag.AlignRight)
        self.setAccessibleName(title.text())
        self.setAccessibleDescription(self.description.text())
        self.escape = QG.QShortcut(QG.QKeySequence("Escape"), self)
        self.escape.setContext(QC.Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.escape.activated.connect(self.finish)
        self._apply_theme()
        get_theme_engine().theme_changed.connect(self._apply_theme)

        # Watch the whole ancestor chain: scroll areas can move the target too.
        self._watched = []
        widget = target
        while widget is not None:
            self._watched.append(widget)
            widget.installEventFilter(self)
            if widget is parent:
                break
            widget = widget.parentWidget()
        self._position()

    def _apply_theme(self) -> None:
        engine = get_theme_engine()
        self.accent = engine.get_token("accent_blue")
        self.card.setStyleSheet(
            f"QFrame#ndaxGuideCard {{ background: {engine.get_token('bg_card')}; "
            f"border: 2px solid {self.accent}; border-radius: 8px; }}"
            f"QFrame#ndaxGuideCard QLabel {{ color: {engine.get_token('text_primary')}; "
            "background: transparent; }"
            f"QFrame#ndaxGuideCard QPushButton {{ color: {engine.get_token('text_primary')}; }}"
        )
        self.update()

    def _position(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        self.setGeometry(parent.rect())
        self.spotlight = QC.QRect(self.target.mapTo(parent, QC.QPoint()), self.target.size())
        # Let clicks reach the actual button; all other clicks stay on the guide.
        self.setMask(QG.QRegion(self.rect()) - QG.QRegion(self.spotlight))
        self.card.setFixedWidth(min(380, max(1, self.width() - 24)))
        self.card.adjustSize()
        x = max(
            12,
            min(self.spotlight.right() - self.card.width(), self.width() - self.card.width() - 12),
        )
        y = self.spotlight.bottom() + 16
        if y + self.card.height() > self.height() - 12:
            y = self.spotlight.top() - self.card.height() - 16
        self.card.move(x, max(12, y))
        self.update()

    def eventFilter(self, watched, event):
        if watched is self.target and event.type() == QC.QEvent.Type.MouseButtonPress:
            if event.button() == QC.Qt.MouseButton.LeftButton:
                self.finish()
        elif event.type() in (QC.QEvent.Type.Move, QC.QEvent.Type.Resize):
            self._position()
        return super().eventFilter(watched, event)

    def paintEvent(self, event):
        painter = QG.QPainter(self)
        painter.setRenderHint(QG.QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QG.QColor(0, 0, 0, 140))
        painter.setPen(QG.QPen(QG.QColor(self.accent), 3))
        painter.drawRoundedRect(self.spotlight.adjusted(-3, -3, 3, 3), 5, 5)
        # A short pointer connects the explanation to the highlighted control.
        x = self.spotlight.center().x()
        edge = (
            self.card.y()
            if self.card.y() > self.spotlight.bottom()
            else self.card.geometry().bottom()
        )
        anchor = self.spotlight.bottom() + 4 if edge == self.card.y() else self.spotlight.top() - 4
        painter.drawLine(x, anchor, min(x, self.card.geometry().right() - 12), edge)

    def finish(self) -> None:
        self.settings.setValue(GUIDE_SETTING_KEY, True)
        for widget in self._watched:
            widget.removeEventFilter(self)
        self.hide()
        self.target.setFocus(QC.Qt.FocusReason.OtherFocusReason)
        self.deleteLater()


def show_ndax_path_guide(
    parent: QW.QWidget, target: QW.QPushButton, settings: QC.QSettings | None = None
) -> NdaxPathGuide | None:
    """Show once per local user; closing the app without dismissing does not count."""
    if settings is None:
        settings = QC.QSettings()
    if settings.value(GUIDE_SETTING_KEY, False, type=bool) or not parent.isVisible():
        return None
    ancestor = target.parentWidget()
    while ancestor is not None and ancestor is not parent:
        if isinstance(ancestor, QW.QScrollArea):
            ancestor.ensureWidgetVisible(target)
            break
        ancestor = ancestor.parentWidget()
    guide = NdaxPathGuide(parent, target, settings)
    guide.show()
    guide.raise_()
    guide.done_button.setFocus(QC.Qt.FocusReason.OtherFocusReason)
    return guide
