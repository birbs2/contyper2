import unicodedata
from PyQt6.QtGui import QIcon, QAction

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QSizePolicy, QHBoxLayout, QFrame, QToolButton, \
    QMenu, QPushButton
from PyQt6.QtCore import Qt, QEvent

from src.contyper.core.config import config as cf
from src.contyper.gui.column_layout import ColumnLayout
from src.contyper.gui.util import CTWindow

def is_diacrtic(char):
    return (
            len(char) > 1
            or unicodedata.combining(char) > 0
    )

class ReferenceScrollArea(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.margin = 12
        self.menu_button = QToolButton(self.viewport())
        self.menu_button.setIcon(QIcon(str(cf.joinpath("assets", "hamburger.png"))))
        self.menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.menu = QMenu(self.menu_button)
        self.menu_button.setMenu(self.menu)

        coming_soon = QAction("coming soon", self)
        self.menu.addAction(coming_soon)

        self.viewport().installEventFilter(self)
        self.reposition()

    def eventFilter(self, a0, a1):
        if a0 is self.viewport() and a1.type() == QEvent.Type.Resize:
            self.reposition()
        return super().eventFilter(a0, a1)

    def reposition(self):
        viewport = self.viewport()
        button = self.menu_button
        button.adjustSize()
        button.move(
            viewport.width() - button.width() - self.margin,
            viewport.height() - button.height() - self.margin
        )
        button.raise_()

class Reference(CTWindow):
    def __init__(self):
        self.widget = QWidget()
        super().__init__("Ct Reference")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.widget)
        scroll_area = ReferenceScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.widget)
        self.setCentralWidget(scroll_area)
        for section_title, section in cf.ruleset.sections.items():
            section_title_layout = QHBoxLayout()
            section_title_widget = QLabel(section_title)
            section_title_layout.addWidget(section_title_widget)
            separator_line = QFrame()
            separator_line.setFrameShape(QFrame.Shape.HLine)
            separator_line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            section_title_layout.addWidget(separator_line)
            layout.addLayout(section_title_layout)
            section_layout = ColumnLayout()
            layout.addLayout(section_layout)
            for loop_data in section:
                loop_widget = QWidget()
                loop_layout = QVBoxLayout(loop_widget)
                (entry, loop), = loop_data.items()
                entry_label = QLabel(entry)
                entry_label.setObjectName("entryLabel")
                loop_string = "<br>".join([f"<b>{"◌" if is_diacrtic(item) else ""}{item}</b>" for item in loop])
                loop_label = QLabel(loop_string)
                loop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                loop_layout.addWidget(entry_label)
                loop_layout.addWidget(loop_label)
                section_layout.addWidget(loop_widget)
        layout.addStretch(1)
