# desktop/app/views/select_pedido_envio_view.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QHeaderView,
)

QSS_STYLE = """
    QWidget#SelectPedidoEnvioView {
        background-color: #ffffff;
    }
    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        gridline-color: #f1f3f5;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        color: #212529;
    }
    QHeaderView::section {
        background-color: #f8f9fa;
        color: #495057;
        padding: 8px;
        font-weight: bold;
        border: none;
        border-bottom: 2px solid #dee2e6;
    }
    QTableWidget::item {
        padding: 6px;
    }
    QTableWidget::item:selected {
        background-color: #f8d7da;
        color: #b02a37;
    }
    QPushButton#btn_seleccionar {
        background-color: #dc3545;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
        font-weight: bold;
        margin-top: 10px;
    }
    QPushButton#btn_seleccionar:hover {
        background-color: #bd2130;
    }
    QPushButton#btn_seleccionar:pressed {
        background-color: #b02a37;
    }
"""

class SelectPedidoEnvioView(QWidget):
    """
    Ventana para seleccionar un pedido confirmado
    que todavía no tenga envío asociado.
    """

    def __init__(self, pedidos, on_select):
        super().__init__()

        self.pedidos = pedidos
        self.on_select = on_select

        self.setWindowTitle("Seleccionar Pedido — MOTO-TOP")
        self.resize(800, 400)

        self.setObjectName("SelectPedidoEnvioView")
        self.setStyleSheet(QSS_STYLE)

        self.init_ui()
        self.cargar_datos()

    # ==================================================
    # INTERFAZ
    # ==================================================

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Tabla de pedidos
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Cliente",
            "Fecha",
            "Estado",
            "Total",
        ])

        # Comportamiento visual de la tabla
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)

        # Ajustar columnas
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Botón seleccionar
        self.btn_seleccionar = QPushButton("Seleccionar Pedido")
        self.btn_seleccionar.setObjectName("btn_seleccionar")
        self.btn_seleccionar.clicked.connect(self.seleccionar_pedido)

        # Doble clic en la fila
        self.table.doubleClicked.connect(self.seleccionar_pedido)

        # Layout
        layout.addWidget(self.table)
        layout.addWidget(self.btn_seleccionar)

        self.setLayout(layout)

    # ==================================================
    # CARGA DE DATOS
    # ==================================================

    def cargar_datos(self):
        self.table.setRowCount(len(self.pedidos))

        for row, pedido in enumerate(self.pedidos):
            cliente = pedido.get("cliente", {})

            if isinstance(cliente, dict):
                nombre = cliente.get("nombre", "")
                apellido = cliente.get("apellido", "")
                cliente_texto = f"{nombre} {apellido}".strip()
            else:
                cliente_texto = str(cliente)

            fecha = pedido.get("fecha", "")
            estado = pedido.get("estado", "")
            total = pedido.get("total", 0)

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(str(pedido["id"]))
            )
            self.table.setItem(
                row,
                1,
                QTableWidgetItem(cliente_texto)
            )
            self.table.setItem(
                row,
                2,
                QTableWidgetItem(str(fecha))
            )
            self.table.setItem(
                row,
                3,
                QTableWidgetItem(str(estado))
            )
            self.table.setItem(
                row,
                4,
                QTableWidgetItem(str(total))
            )

    # ==================================================
    # SELECCIÓN
    # ==================================================

    def seleccionar_pedido(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Debe seleccionar un pedido."
            )
            return

        pedido = self.pedidos[row]

        # Ejecutar callback recibido
        self.on_select(pedido)

        # Cerrar esta ventana
        self.close()