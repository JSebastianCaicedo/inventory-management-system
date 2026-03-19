from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class InventarioView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Inventario"))
