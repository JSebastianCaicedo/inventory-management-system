from PySide6.QtWidgets import (
    QWidget, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Signal

class LoginWindow(QWidget):
    login_success = Signal(object)

    def __init__(self, api_client):
        super().__init__()
        self.setWindowTitle("Login - Inventario")
        self.api_client = api_client
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.addStretch(1)

        self.setLayout(layout)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        layout.addWidget(self.user_input)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_input)

        self.login_btn = QPushButton("Iniciar Sesión")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        layout.addStretch(2)

        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
                font-family: 'Helvetica Neue';
            }

            QLineEdit {
                border: 1px solid #cfcfcf;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }

            QPushButton {
                background-color: #0d6efd;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-weight: 500;
            }

            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)


    def login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        ok = self.api_client.login(username, password)
        if ok:
            self.login_success.emit(self.api_client)
        else:
            QMessageBox.warning(self, "Error", "Credenciales inválidas")
