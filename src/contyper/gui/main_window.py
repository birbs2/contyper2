from PyQt6.QtWidgets import QMainWindow


class CTMainWindow(QMainWindow):
    def closeEvent(self, a0):
        a0.ignore()
        self.hide()

    def show(self):
        self.init_ui()
        super().show()

    def init_ui(self):
        pass