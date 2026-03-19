from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import sys
import os

class Header(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        self.setStyleSheet("""
            background-color: white;
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 5)

        self.logo = QLabel()
        logo_path = resource_path("assets/logo.jpg")
        pixmap = QPixmap(logo_path)
        self.logo.setPixmap(pixmap.scaled(
            180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        self.logo.setAlignment(Qt.AlignCenter)

        titulo = QLabel("Sistema de Inventario")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            background-color: white;
        """)
        titulo.setStyleSheet("""
            font-size: 17px;
            font-weight: 500;
            color: #333333;
            text-transform: uppercase;
        """)

        layout.addWidget(titulo)
        layout.addWidget(self.logo)

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

