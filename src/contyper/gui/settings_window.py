from PyQt6.QtWidgets import QTabWidget, QLabel, QWidget, QGridLayout, QPushButton, QCheckBox, QDialog

from src.contyper.gui.main_window import CTMainWindow
from src.contyper.core.config import config as cf
def split_shortcut_toggle_string(shortcut_string, num_keys):
    """
    reads a layer of True,False,True from ini file and appends Falses to the end
    so that it matches length with the number of keys activated
    """
    split_string = shortcut_string.split(",")
    shortcut_toggles = [False for _ in range(num_keys)]
    for index, key in enumerate(split_string[:num_keys-1]):
        shortcut_toggles[index] = key.strip() == "True"
    return shortcut_toggles



class Settings(CTMainWindow):
    def __init__(self):
        super().__init__()
        self.widget = None
        self.keybinds = None

    def init_ui(self):
        self.widget = QTabWidget(self)
        self.keybinds = KeybindWidget(self)

        self.widget.addTab(self.keybinds, "Keybinds")
        self.setCentralWidget(self.widget)

class KeybindWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent_ = parent
        self.keybind_toggles = None
        self.human = []
        self.codes = []
        self.layout_ = None
        self.button_grid = None
        self.codes = cf.get("Shortcuts", "codes").split(",")
        self.human = cf.get("Shortcuts", "human").split(",")
        self.init_ui()

    def init_ui(self):
        shortcut_toggle_strings = [cf.get("Shortcuts", str(i)) for i in range(cf.ruleset.num_layers)]
        self.keybind_toggles = [split_shortcut_toggle_string(layer, len(self.codes)) for layer in shortcut_toggle_strings]
        print(self.keybind_toggles)
        self.button_grid: list[list] = []
        self.layout_ = QGridLayout(self)
        self.layout_.addWidget(QLabel("Modifier Key:"))
        self.layout_.addWidget(QLabel("Layer 0:   Alt"), 1, 0)
        self.button_grid.append([False for _ in self.codes])
        for layer in range(1, cf.ruleset.num_layers):
            self.layout_.addWidget(QLabel(f"Layer {layer}:   Alt"), layer + 1, 0)
            self.button_grid.append([])
            for index, modifier in enumerate(self.human):
                button = QPushButton(f"+ {modifier}")
                button.setCheckable(True)
                try:
                    button.setChecked(self.keybind_toggles[layer][index])
                except:
                    print(self.keybind_toggles[layer], index)
                self.button_grid[-1].append(button)
                self.layout_.addWidget(button, layer + 1, 1 + index)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save)
        self.layout_.addWidget(save_button, cf.ruleset.num_layers + 1, 0)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.parent_.close)
        self.layout_.addWidget(cancel_button, cf.ruleset.num_layers + 1, 1)
        edit_keys = QPushButton("Edit Modifier Keys...")
        edit_keys.clicked.connect(self.edit_keys)
        self.layout_.addWidget(edit_keys, cf.ruleset.num_layers + 1, 2, 1, 2)


    def edit_keys(self):
        dialog = ModifierKeysWindow(self.codes)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_keys = dialog.get_selected()
            print("edit_keys dialog saved")
            self.codes = selected_keys[0]
            self.human = selected_keys[1]
            self.init_ui()

    def save(self):
        print("saving")
        self.keybind_toggles = [[button.isChecked() if type(button) == QPushButton else button for button in layer] for layer in self.button_grid]
        if len(self.keybind_toggles) != len(set(tuple(layer) for layer in self.keybind_toggles)):
            print("stopping.")
            return
        cf.set("Shortcuts", "codes", ",".join(self.codes))
        for index, layer in enumerate(self.keybind_toggles):
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