from PyQt6.QtWidgets import QMainWindow, QWidget, QMenu


class CTWindow(QMainWindow):
    def closeEvent(self, a0):
        a0.ignore()
        self.hide()

    def show(self):
        self.init_ui()
        super().show()

    def init_ui(self):
        """
        regenerates the ui of a window
        """
        pass

class CTWidget(QWidget):
    def __init__(self):
        """
        a CTWidget object should be the only thing reading from the .ini file,
        which should only occur in the __init__ method.
        """
        super().__init__()

    def init_ui(self):
        """
        regenerates the ui of a widget
        """
        pass

class CTMenu(QMenu):
    def mouseReleaseEvent(self, a0):
        action = self.activeAction()
        if action and action.isCheckable() and action.isEnabled():
            action.trigger()
            a0.accept()
        else:
            super().mouseReleaseEvent(a0)