from typing import override

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QIcon, QAction, QCursor
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu

from src.contyper.core.config import config as cf
from src.contyper.gui.appearance import AppearanceWindow
from src.contyper.gui.file_manager import FileManager
from src.contyper.gui.reference import ReferenceWindow
from src.contyper.gui.settings_window import Settings


class TrayIcon(QSystemTrayIcon):
    def __init__(self, app):
        super().__init__(QIcon(str(cf.joinpath("assets", "logo.png"))))
        self.menu = QMenu()
        self.setToolTip("Contyper 2")
        self.app = app

        self.reference = ReferenceWindow()
        self.file_manager = FileManager()
        self.appearance = AppearanceWindow()
        self.settings = Settings()

        self.activated.connect(self.on_activated)
        self.init_menu()
        self.show()

    def add_action(self, name, callback):
        a = QAction(name, self)
        a.triggered.connect(callback)
        self.menu.addAction(a)

    def init_menu(self):
        self.add_action("Open Reference...", self.reference.show)
        self.add_action("Open File Manager...", self.file_manager.show)
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


