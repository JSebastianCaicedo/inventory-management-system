import sys
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget,
    QLineEdit, QLabel, QPushButton,
    QRadioButton, QButtonGroup,
    QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt

from PySide6.QtCore import Signal

from api_client import ApiClient
from queue_store import init_queue
from sync_manager import SyncManager
from movement_service import procesar_movimiento

class InventariosWindow(QWidget):
    logout_requested = Signal()

    def __init__(self, api_client: ApiClient, maquina_id: str, queue_db_path: str = "cola_local.db"):
        super().__init__()
        self.primaryTextStyle = """
            font-size: 17px;
            font-weight: 500;
            color: #333333;
            """
        #self.setWindowTitle("Programa de inventario - La Cava")

        self.api_client = api_client
        self.maquina_id = maquina_id
        self.queue_db_path = queue_db_path

        init_queue(self.queue_db_path) #Crea la tabla si no existe

        self.lote = []
        self._build_ui()

        self.sync_manager = SyncManager(self.api_client, self.queue_db_path)
        self.sync_manager.start()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Creación de widgets
        self.usuario_input = QLabel("Usuario: -")
        self.usuario_input.setStyleSheet(self.primaryTextStyle)

        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código de barras")
        self.codigo_input.returnPressed.connect(self.buscar_producto)

        self.producto_label = QLabel("Producto: -")
        self.producto_label.setStyleSheet(self.primaryTextStyle)

        self.cantidad_input = QLineEdit()
        self.cantidad_input.setPlaceholderText("Cantidad")
        self.cantidad_input.returnPressed.connect(self.agregar_a_lote)

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
                border-radius: 6px;
                padding: 6px;
                font-size: 12px;
                font-weight: 500;
            }

            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)


        #Radio buttons
        self.entrada_radio = QRadioButton("ENTRADA")
        self.entrada_radio.setStyleSheet(self.primaryTextStyle)
        self.salida_radio = QRadioButton("SALIDA")
        self.salida_radio.setStyleSheet(self.primaryTextStyle)
        self.entrada_radio.setChecked(True)

        tipo_group = QButtonGroup()
        tipo_group.addButton(self.entrada_radio)
        tipo_group.addButton(self.salida_radio)

        self.agregar_btn = QPushButton("Agregar a lote")
        self.agregar_btn.clicked.connect(self.agregar_a_lote)

        self.lote_table = QTableWidget(0, 4)
        self.lote_table.setHorizontalHeaderLabels(
            ["Código", "Producto", "Tipo", "Cantidad"]
        )
        self.lote_table.horizontalHeader().setStretchLastSection(True)

        self.cargar_btn = QPushButton("CARGAR A BASE DE DATOS Y GENERAR REPORTE")
        self.cargar_btn.clicked.connect(self.cargar_lote)

        #Botón de cerrar sesión
        self.logout_btn = QPushButton("Cerrar Sesión")
        self.logout_btn.clicked.connect(self.logout)

        #Usuario
        layout.addWidget(self.usuario_input)

        #Código y producto
        layout.addWidget(self.codigo_input)
        layout.addWidget(self.producto_label)

        #Cantidad
        layout.addWidget(self.cantidad_input)

        #Tipo de movimiento
        tipo_layout = QHBoxLayout()
        tipo_layout.addWidget(self.entrada_radio)
        tipo_layout.addWidget(self.salida_radio)
        layout.addLayout(tipo_layout)

        layout.addWidget(self.agregar_btn)
        layout.addWidget(self.lote_table)
        layout.addWidget(self.cargar_btn)

        #Cerrar sesión
        layout.addWidget(self.logout_btn)

    #Funciones de acción

    def buscar_producto(self):
        codigo = self.codigo_input.text().strip()
        try:
            producto = self.api_client.get_producto(codigo)
        except Exception:
            QMessageBox.warning(self, "Error", "No se pudo consultar el servidor")
            return 
        
        if not producto:
            QMessageBox.warning(self, "Error", "Producto no encontrado")
            return 
        
        self.producto_actual = producto
        self.producto_label.setText(f"Producto: {producto['nombre']}")

    def agregar_a_lote(self):
        if not hasattr(self, "producto_actual"):
            QMessageBox.warning(self, "Error", "No hay producto seleccionado")
            return
        
        try:
            cantidad = float(self.cantidad_input.text().strip())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Cantidad inválida")
            return
        
        tipo = "ENTRADA" if self.entrada_radio.isChecked() else "SALIDA"

        movimiento = {
            "sku": self.producto_actual["sku"],
            "producto": self.producto_actual["nombre"],
            "tipo": tipo,
            "cantidad": cantidad
        }

        self.lote.append(movimiento)

        row = self.lote_table.rowCount()
        self.lote_table.insertRow(row)
        self.lote_table.setItem(row, 0, QTableWidgetItem(movimiento["sku"]))
        self.lote_table.setItem(row, 1, QTableWidgetItem(movimiento["producto"]))
        self.lote_table.setItem(row, 2, QTableWidgetItem(movimiento["tipo"]))
        self.lote_table.setItem(row, 3, QTableWidgetItem(str(movimiento["cantidad"])))

        #limpiar campos
        self.codigo_input.clear()
        self.cantidad_input.clear()
        self.producto_label.setText("Producto: -")
        self.codigo_input.setFocus()

    def cargar_lote(self):
        if not self.lote:
            QMessageBox.information(self, "Aviso", "No hay movimientos para cargar")
            return
            
        #usuario = self.usuario_input.text().strip() or "desconocido"
        usuario = self.api_client.usuario or "desconocido"
        now = datetime.now()

        enviados = 0
        encolados = 0

        for mov in self.lote:
            # sku es el código de barras
            sku = mov["sku"]
            cantidad = int(mov["cantidad"])
            tipo = mov["tipo"] #ENTRADA O SALIDA

            delta = cantidad if tipo == 'ENTRADA' else -cantidad

            ok, error_msg = procesar_movimiento(
                api = self.api_client,
                queue_db = self.queue_db_path,
                sku = sku,
                delta = delta,
                tipo = tipo,
                usuario = usuario,
                maquina_id = self.maquina_id
            )

            if ok:
                enviados += 1
            else:
                if error_msg:
                    QMessageBox.warning(self, "Error", error_msg)
                else:
                    encolados += 1

        r = self.api_client.generar_reporte()

        if r.status_code == 200:
            data = r.json()
            nombre_archivo = data["archivo"]

        QMessageBox.information(self, "Éxito", f"Reporte generado: {nombre_archivo}")
        QMessageBox.information(
            self, "Resultado",
            f"Movimientos: {len(self.lote)}\nEnviados: {enviados}\nGuardados para sincronizar: {encolados}"
        )

        #limpiar lote
        self.lote.clear()
        self.lote_table.setRowCount(0)
        self.codigo_input.setFocus()

    def logout(self):
        self.logout_requested.emit()
