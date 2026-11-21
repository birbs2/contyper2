import unicodedata

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from unicodedata import combining

from src.contyper.core.config import config as cf
from src.contyper.gui.column_layout import FlowLayout
from src.contyper.gui.util import CTWindow

def is_diacrtic(char):
    return (
            len(char) > 1
            or unicodedata.combining(char) > 0
    )

class Reference(CTWindow):
    def __init__(self):
        self.widget = QWidget()
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.widget)
        self.setCentralWidget(self.widget)
        for section_title, section in cf.ruleset.sections.items():
            layout.addWidget(QLabel(section_title))
            section_layout = FlowLayout()
            layout.addLayout(section_layout)
            for loop_data in section:
                loop_widget = QWidget()
                loop_layout = QHBoxLayout(loop_widget)
                (entry, loop), = loop_data.items()
                entry_label = QLabel(entry)
                entry_label.setStyleSheet("border: 1px solid black; padding: 5px;")
                loop_string = "→ " + ", ".join([f"<b>{"◌" if is_diacrtic(item) else ""}{item}</b>" for item in loop])
                loop_label = QLabel(loop_string)
                loop_layout.addWidget(entry_label)
                loop_layout.addWidget(loop_label)
                section_layout.addWidget(loop_widget)
