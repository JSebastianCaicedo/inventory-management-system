from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal

class LoginView(QWidget):
    login_ok = Signal()

    def __init__(self, parent = None):
        super().__init__(parent)

        btn = QPushButton("Entrar")
        btn.clicked.connect(self.login_ok.emit)

        layout = QVBoxLayout(self)
        layout.addWidget(btn)