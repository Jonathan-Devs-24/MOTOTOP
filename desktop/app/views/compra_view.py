# desktop/app/views/compra_view.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QScrollArea,
    QGridLayout,
    QMessageBox
)

from views.compra_card import CompraCard
from views.compra_form import CompraForm

from services.proveedor_service import ProveedorService
from services.producto_service import ProductoService


class CompraView(QWidget):

    def __init__(self, compra_service):
        super().__init__()

        self.service = compra_service

        self.proveedor_service = ProveedorService(
            self.service.http
        )

        self.producto_service = ProductoService(
            self.service.http
        )

        layout = QVBoxLayout()

        self.btn_new = QPushButton("Nueva compra")

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

        self.btn_new.clicked.connect(
            self.open_form
        )

        layout.addWidget(self.btn_new)

        # =========================
        # SCROLL
        # =========================

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()

        self.grid = QGridLayout()

        self.container.setLayout(self.grid)

        self.scroll.setWidget(self.container)

        layout.addWidget(self.scroll)

        self.setLayout(layout)

        self.load_data()

    # =========================

    def load_data(self):

        try:

            while self.grid.count():
                item = self.grid.takeAt(0)

                widget = item.widget()

                if widget:
                    widget.deleteLater()

            compras = self.service.listar()

            compras_data = compras.get(
                "results",
                compras
            )

            row = 0
            col = 0

            for compra in compras_data:

                card = CompraCard(
                    compra,
                    self.service,
                    self.load_data
                )

                self.grid.addWidget(card, row, col)

                col += 1

                if col > 2:
                    col = 0
                    row += 1

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las compras: {str(e)}")

    # =========================

    def open_form(self):

        self.form = CompraForm(
            self.service,
            self.proveedor_service,
            self.producto_service,
            self.load_data
        )

        self.form.show()
        
