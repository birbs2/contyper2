import sys
import traceback

from PyQt6.QtWidgets import QApplication

from src.contyper.gui.tray_icon import TrayIcon

def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)

sys.excepthook = excepthook

def main():
    app = QApplication(sys.argv)
    ti = TrayIcon(app)
    app.exec()

if __name__ == '__main__':
    main()



