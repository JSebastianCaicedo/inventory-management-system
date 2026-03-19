from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from ui.header import Header
from auth_gui import LoginWindow
from gui import InventariosWindow
from api_client import ApiClient
import uuid
import os
import json
import os
from pathlib import Path

appdata = Path(os.getenv("LOCALAPPDATA")) / "Inventario"
appdata.mkdir(exist_ok=True)

config_path = appdata / "config_local.json"
cola_path = appdata / "cola_local.db"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.setWindowTitle("Sistema de Inventario")

        self.api_client = ApiClient("http://0.0.0.0:8000")
        self.maquina_id = self._cargar_o_crear_maquina_id()

        self.root = QWidget()
        self.root.setStyleSheet("background-color: white;")

        self.layout_principal = QVBoxLayout(self.root)

        self.header = Header()
        self.layout_principal.addWidget(self.header)

        self.stack = QStackedWidget()
        self.layout_principal.addWidget(self.stack)

        self.setCentralWidget(self.root)

        self.mostrar_login()

    def _cargar_o_crear_maquina_id(self):
        config_file = config_path

        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                data = json.load(f)
                return data.get("maquina_id")
        
        maquina_id = str(uuid.uuid4())

        with open(config_file, "w") as f:
            json.dump({"maquina_id": maquina_id}, f)

        return maquina_id

    #Navegación de vistas
    def set_view(self, widget: QWidget):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.content_layout.addWidget(widget)

    def mostrar_login(self):
        login = LoginWindow(self.api_client)
        login.login_success.connect(self.on_login_success)
        self.stack.addWidget(login)
        self.stack.setCurrentWidget(login)

    def on_login_success(self, api_client):
        self.api_client = api_client
        self.mostrar_inventario()

    def _on_login_ok(self, username):
        self.usuario_actual = username

    def mostrar_inventario(self):
        inventario = InventariosWindow(
            api_client = self.api_client,
            maquina_id = self.maquina_id,
            queue_db_path = cola_path
        )
        inventario.usuario_input.setText(f"Usuario: {self.api_client.usuario}")
        inventario.logout_requested.connect(self.mostrar_login)
        self.stack.addWidget(inventario)
        self.stack.setCurrentWidget(inventario)