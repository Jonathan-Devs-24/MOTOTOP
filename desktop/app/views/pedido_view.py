import traceback
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QScrollArea,
    QMessageBox
)

from views.pedido_card import PedidoCard
from views.pedido_form import PedidoForm


class PedidoView(QWidget):

    def __init__(self, pedido_service, cliente_service, vendedor_service, producto_service):
        super().__init__()

        self.service = pedido_service
        self.cliente_service = cliente_service
        self.vendedor_service = vendedor_service
        self.producto_service = producto_service

        layout = QVBoxLayout()

        self.btn_new = QPushButton("Nuevo pedido")
        self.btn_new.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.btn_new.clicked.connect(self.open_form)

        layout.addWidget(self.btn_new)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(0)
        self.container.setLayout(self.list_layout)
        self.scroll.setWidget(self.container)

        layout.addWidget(self.scroll)

        self.setLayout(layout)

        self.load_data()

    def load_data(self):

        try:
            while self.list_layout.count():
                item = self.list_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            pedidos = self.service.listar()
            pedidos_data = pedidos.get("results", pedidos)

            for pedido in pedidos_data:
                card = PedidoCard(
                    pedido,
                    self.service,
                    self.load_data
                )
                self.list_layout.addWidget(card)

            self.list_layout.addStretch()

        except Exception as e:
            error_msg = str(e)
            print(f"Error cargando pedidos: {error_msg}")
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los pedidos: {error_msg}")

    def open_form(self):
        self.form = PedidoForm(
            self.service,
            self.cliente_service,
            self.vendedor_service,
            self.producto_service,
            self.load_data
        )
        self.form.show()
