from functools import partial
from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget, \
    QFileDialog, QTextEdit

from src.contyper.gui.main_window import CTMainWindow
from src.contyper.core.config import config as cf

def clearLayout(layout):
  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()

class FileManager(CTMainWindow):
    def __init__(self):
        super().__init__()
        self.ruleset_widget = None
        self.layout = None
        self.widget = None
        self.selected_rs = Path(cf.get("Files", "selectedfile"))
        print(self.selected_rs)
        self.init_ui()

    def init_ui(self):
        self.widget = QWidget()
        self.layout = QHBoxLayout(self.widget)
        self.setCentralWidget(self.widget)
        self.load_buttons()
        self.load_text()

    def load_text(self):
        text_layout = QVBoxLayout()
        self.layout.addLayout(text_layout)
        with open(self.selected_rs, encoding="utf-8") as rs:
            file_text = QTextEdit(rs.read().replace("\n", "<br>"))
        file_text.setReadOnly(True)
        text_layout.addWidget(file_text)

        button_layout = QHBoxLayout()
        text_layout.addLayout(button_layout)
        set_active = QPushButton("Set as Active Ruleset")
        set_active.clicked.connect(self.save_rs)
        button_layout.addWidget(set_active)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.close)
        button_layout.addWidget(cancel)

    def set_rs(self, path: Path):
        self.selected_rs = path
        clearLayout(self.layout)
        self.load_buttons()
        self.load_text()

    def save_rs(self):
        cf.set("Files", "selectedfile", str(self.selected_rs))
        print("Hello")
        cf.write_()
        clearLayout(self.layout)
        self.load_buttons()
        self.load_text()

    def create_button(self, file):
        button = QPushButton(f"{"✓" if Path(cf.get("Files", "selectedfile")) == file else ""}   {cf.get_title(file)}")
        button.clicked.connect(partial(lambda x: self.set_rs(x), file))
        return button

    def load_buttons(self):
        current_tab = None
        if self.ruleset_widget is not None:
            current_tab = self.ruleset_widget.currentIndex()

        self.ruleset_widget = QTabWidget()
        self.layout.addWidget(self.ruleset_widget)

        preset_submenu = QWidget()
        self.ruleset_widget.addTab(preset_submenu, "Presets")
        preset_layout = QVBoxLayout(preset_submenu)
        for file in cf.joinpath("presets").rglob("*"):
            if file.is_file() and file.suffix.lower() in {".yml", ".yaml"}:
                preset_layout.addWidget(self.create_button(file))

        custom_submenu = QWidget()
        self.ruleset_widget.addTab(custom_submenu, "Custom Rulesets")
        custom_layout = QVBoxLayout(custom_submenu)
        change_dir = QPushButton("Change Custom Ruleset...")
        change_dir.clicked.connect(self.change_dir)
        custom_layout.addWidget(change_dir)
        try:
            for file in Path(cf.get("Files", "rulesetdir")).rglob("*"):
                if file.is_file() and file.suffix.lower() in {".yml", ".yaml"}:
                    custom_layout.addWidget(self.create_button(file))
        except Exception as e:
            print(e)
        if current_tab is not None:
            self.ruleset_widget.setCurrentIndex(current_tab)

    def change_dir(self):
        file_path = QFileDialog.getExistingDirectory(
            None,
            "Select a Ruleset Directory",
            ""
        )

        if file_path:
            cf.set("Files", "rulesetdir", file_path)
            cf.write_()
            self.init_ui()
            print("reseting")

