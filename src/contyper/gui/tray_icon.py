import subprocess
from typing import override

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QSystemTrayIcon

from src.contyper.core.config import config as cf
from src.contyper.gui.reference import Reference
from src.contyper.gui.settings import Settings
from src.contyper.gui.util import CTMenu

class RunAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        self.setText("Run AHK")
        self.setCheckable(True)
        self.toggled.connect(self.clicked)
        self.proc = None
        self.trigger()

    def clicked(self, state):
        if state:
            self.proc = subprocess.Popen(
                [cf.joinpath("ct2.exe")],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            self.setText("AHK is Running")
            self.parent().setIcon(QIcon(str(cf.joinpath("assets", "logo.png"))))
            self.parent().setToolTip("Contyper 2")
        elif self.proc is not None:
            self.proc.terminate()
            self.setText("Run AHK")
            self.parent().setIcon(QIcon(str(cf.joinpath("assets", "logo_disabled.png"))))
            self.parent().setToolTip("Contyper 2 (stopped)")

class TrayIcon(QSystemTrayIcon):
    def __init__(self, app):
        super().__init__()
        self.menu = CTMenu()
        self.app = app

        self.reference = Reference()
        self.settings = Settings()

        self.activated.connect(self.on_activated)
        self.init_menu()
        self.show()

    def add_action(self, name, callback):
        a = QAction(name, self)
        a.triggered.connect(callback)
        self.menu.addAction(a)

    def init_menu(self):
        self.menu.addAction(RunAction(self))
        self.add_action("Open Reference...", self.reference.show)
        self.add_action("Open Settings...", self.settings.show)
        self.menu.addSeparator()
        self.add_action("Quit", self.app.quit)
        self.setContextMenu(self.menu)

    def on_activated(self, reason):
        match reason:
            case QSystemTrayIcon.ActivationReason.Trigger | QSystemTrayIcon.ActivationReason.Context:
                icon_rect = self.geometry()
                menu_rect = self.menu.sizeHint()
                self.menu.popup(QPoint(
                    icon_rect.left(),
                    icon_rect.top() - menu_rect.height()
                ))
            case QSystemTrayIcon.ActivationReason.DoubleClick | QSystemTrayIcon.ActivationReason.MiddleClick:
                self.reference.show()