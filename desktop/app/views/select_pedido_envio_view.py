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


class SelectPedidoEnvioView(QWidget):
    """
    Ventana para seleccionar un pedido confirmado
    que todavía no tenga envío asociado.
    """

    def __init__(self, pedidos, on_select):
        super().__init__()

        self.pedidos = pedidos
        self.on_select = on_select

        self.setWindowTitle("Seleccionar Pedido")
        self.resize(800, 400)

        self.init_ui()
        self.cargar_datos()

    # ==================================================
    # INTERFAZ
    # ==================================================

    def init_ui(self):
        layout = QVBoxLayout()

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

        # Ajustar columnas
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Botón seleccionar
        self.btn_seleccionar = QPushButton("Seleccionar Pedido")
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