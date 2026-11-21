from functools import partial
from pathlib import Path

from PyQt6.QtWidgets import QTabWidget, QLabel, QWidget, QGridLayout, QPushButton, QCheckBox, QDialog, QHBoxLayout, \
    QVBoxLayout, QFileDialog, QTextEdit

from src.contyper.gui.util import CTWindow, CTWidget
from src.contyper.core.config import config as cf

def change_list_size(L, size):
    """
    Changes the size of a list based on the length given. If the correct length is too large, False values are placed.
    """
    L.extend([False] * max(0, size - len(L)))
    return L[:size]

class Settings(CTWindow):
    def __init__(self):
        super().__init__()

    def init_ui(self):
        widget = QTabWidget(self)

        file_tab = FileWidget(self)
        widget.addTab(file_tab, "Files")

        keybind_tab = KeybindWidget(self)
        widget.addTab(keybind_tab, "Keybinds")

        self.setCentralWidget(widget)

class KeybindWidget(CTWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent_ = parent
        self.button_grid: list[list[QPushButton]] = []

        # pulls the False,True,False... strings from the .ini file from each layer
        per_layer_keybind_booleans = [cf.get("Shortcuts", str(i)) for i in range(cf.ruleset.num_layers)]
        self.keybind_booleans = [[item == "True" for item in layer.split(",")] for layer in per_layer_keybind_booleans]
        self.keycodes = cf.get("Shortcuts", "keycodes").split(",")
        self.keynames = cf.get("Shortcuts", "keynames").split(",")
        self.init_ui()

    def init_ui(self):
        grid = self.layout()
        if grid is None:
            grid = QGridLayout()
            self.setLayout(grid)
        else:
            # remove and delete all old widgets
            while grid.count():
                item = grid.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.deleteLater()
        self.button_grid = []
        self.keybind_booleans = [change_list_size(layer, len(self.keycodes)) for layer in self.keybind_booleans]
        grid.addWidget(QLabel("Layer 0:   Alt"), 0, 0)
        for layer in range(1, cf.ruleset.num_layers):
            grid.addWidget(QLabel(f"Layer {layer}:   Alt"), layer + 1, 0)
            self.button_grid.append([])
            for index, (keycode, keyname) in enumerate(zip(self.keycodes, self.keynames)):
                button = QPushButton(f"+ {keyname}")
                button.setCheckable(True)
                button.setChecked(self.keybind_booleans[layer][index])
                self.button_grid[-1].append(button)
                grid.addWidget(button, layer + 1, index + 1)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save)
        grid.addWidget(save_button, cf.ruleset.num_layers + 1, 0)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.parent_.close)
        grid.addWidget(cancel_button, cf.ruleset.num_layers + 1, 1)
        edit_keys_button = QPushButton("Edit Keys...")
        edit_keys_button.clicked.connect(self.edit_keys)
        grid.addWidget(edit_keys_button, cf.ruleset.num_layers + 1, 2)

    def edit_keys(self):
        dialog = ModifierKeysWindow(self.keycodes)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_keys = dialog.get_selected()
            self.keycodes = selected_keys[0]
            self.keynames = selected_keys[1]
            self.init_ui()

    def save(self):
        # yeah right it's so pretty :)
        self.keybind_booleans = [[False for _ in enumerate(self.keycodes)]] + [[button.isChecked() if type(button) == QPushButton else button for button in layer] for
                                layer in self.button_grid]
        if len(self.keybind_booleans) != len(set(tuple(layer) for layer in self.keybind_booleans)):
            return
        cf.set("Shortcuts", "keycodes", ",".join(self.keycodes))
        cf.set("Shortcuts", "keynames", ",".join(self.keynames))
        for index, layer in enumerate(self.keybind_booleans):
            cf.set("Shortcuts", str(index), ",".join([str(i) for i in layer]))
        cf.write_()

class ModifierKeysWindow(QDialog):
    def __init__(self, codes):
        super().__init__()
        self.layout = None
        self.widget = None
        self.layout = QGridLayout(self)

        self.keys = {
            "<+": "LShift",
            ">+": "RShift",
            "<^": "LCtrl",
            ">^": "RCtrl"
        }
        self.total_codes = list(self.keys.keys())
        self.codes = codes
        self.total_human = list(self.keys.values())
        self.checkbox_list: list[QCheckBox] = []

        for key_code, key_readable in zip(self.total_codes, self.total_human):
            checkbox = QCheckBox(f"{key_readable} ({key_code})")
            checkbox.setChecked(key_code in self.codes)
            self.checkbox_list.append(checkbox)
            self.layout.addWidget(checkbox)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        self.layout.addWidget(save_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(cancel_button)
        self.show()

    def get_selected(self) -> tuple[list, list]:
        codes = []
        human = []
        for code, readable, checkbox in zip(self.total_codes, self.total_human, self.checkbox_list):
            if checkbox.isChecked():
                codes.append(code)
                human.append(readable)
        return codes, human

class FileWidget(CTWidget):
    def __init__(self, parent):
        super().__init__()
        self.current_tab = 0
        self.parent_ = parent
        self.selected_path = Path(cf.get("Files", "selectedfile"))
        self.ruleset_directory = Path(cf.get("Files", "rulesetdir"))
        self.init_ui()

    def init_ui(self):
        grid = self.layout()
        if grid is None:
            grid = QGridLayout()
            self.setLayout(grid)
        else:
            while grid.count():
                item = grid.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.deleteLater()
        ruleset_selection_widget = QTabWidget()
        grid.addWidget(ruleset_selection_widget, 0, 0, 1, 1)
        preset_menu = QWidget()
        ruleset_selection_widget.addTab(preset_menu, "Presets")
        preset_layout = QVBoxLayout(preset_menu)
        for file in cf.joinpath("presets").rglob("*"):
            if file.is_file() and file.suffix.lower() in {".yml", ".yaml"}:
                preset_layout.addWidget(self.create_button(file))
        custom_menu = QWidget()
        ruleset_selection_widget.addTab(custom_menu, "Custom Rulesets")
        custom_layout = QVBoxLayout(custom_menu)
        change_dir = QPushButton("Change Directory...")
        change_dir.clicked.connect(self.change_dir)
        custom_layout.addWidget(change_dir)
        try:
            for file in self.ruleset_directory.rglob("*"):
                if file.is_file() and file.suffix.lower() in {".yml", ".yaml"}:
                    custom_layout.addWidget(self.create_button(file))
        except OSError:
            pass
        ruleset_selection_widget.setCurrentIndex(self.current_tab)
        ruleset_selection_widget.currentChanged.connect(self.on_tab_switch)

        with open(self.selected_path, encoding="utf-8") as rs:
            textbox = QTextEdit(rs.read().replace("\n", "<br>"))
        textbox.setReadOnly(True)
        grid.addWidget(textbox, 0, 1, 1, 2)
        set_ruleset_button = QPushButton("Save")
        set_ruleset_button.clicked.connect(self.save_rs)
        grid.addWidget(set_ruleset_button, 1, 1)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.parent_.close)
        grid.addWidget(cancel_button, 1, 2)

    def save_rs(self):
        cf.set("Files", "rulesetdir", str(self.ruleset_directory))
        cf.set("Files", "selectedfile", str(self.selected_path))
        cf.write_()

    def create_button(self, path):
        button_string = "✓   " if path == self.selected_path else ""
        button_string += cf.get_title(path)
        button = QPushButton(button_string)
        button.clicked.connect(partial(lambda x: self.set_rs(x), path))
        return button

    def set_rs(self, path):
        self.selected_path = path
        self.init_ui()

    def change_dir(self):
        file_path = QFileDialog.getExistingDirectory(
            None,
            "Select a Ruleset Directory",
            ""
        )

        if file_path:
            self.ruleset_directory = Path(file_path)
            self.init_ui()

    def on_tab_switch(self, index):
        self.current_tab = index