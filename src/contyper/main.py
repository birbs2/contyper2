import sys
import traceback

from PyQt6.QtWidgets import QApplication

from src.contyper.gui.tray_icon import TrayIcon
from src.contyper.core.config import config as cf

def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)

sys.excepthook = excepthook

def main():
    app = QApplication(sys.argv)
    with open(cf.joinpath("gui", "style.qss")) as style:
        app.setStyleSheet(style.read())
    ti = TrayIcon(app)
    app.exec()

if __name__ == '__main__':
    main()



