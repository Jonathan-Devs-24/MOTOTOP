# desktop/app/views/producto_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QLabel, QScrollArea, QGridLayout
)

from services.rubro_service import RubroService
from services.proveedor_service import ProveedorService
from views.producto_form import ProductoForm
from views.producto_card import ProductoCard


class ProductoView(QWidget):

    def __init__(self, producto_service):
        super().__init__()

        self.service = producto_service
        self.rubro_service = RubroService(self.service.http)
        self.proveedor_service = ProveedorService(self.service.http)

        self.page = 1
        self.has_next = False
        self.has_prev = False

        layout = QVBoxLayout()

        # =========================
        # TOP BAR
        # =========================

        top_bar = QHBoxLayout()

        self.btn_prev = QPushButton("Anterior")
        self.btn_next = QPushButton("Siguiente")
        self.btn_refresh = QPushButton("Recargar")
        self.btn_new = QPushButton("Nuevo")

        self.lbl_page = QLabel("Página: 1")

        top_bar.addWidget(self.btn_new)
        top_bar.addWidget(self.btn_prev)
        top_bar.addWidget(self.btn_next)
        top_bar.addWidget(self.btn_refresh)
        top_bar.addWidget(self.lbl_page)

        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_new.clicked.connect(self.open_form)

        # =========================
        # GRID DE CARDS
        # =========================

        self.container = QWidget()
        self.grid = QGridLayout()
        self.container.setLayout(self.grid)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.container)

        layout.addLayout(top_bar)
        layout.addWidget(self.scroll)

        self.setLayout(layout)

        # cargar inicial
        self.load_data()

    # =========================

    def load_data(self):
        try:
            data = self.service.listar(self.page)

            productos = data["results"]
            self.has_next = data["next"] is not None
            self.has_prev = data["previous"] is not None

            # limpiar grid
            for i in reversed(range(self.grid.count())):
                widget = self.grid.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            # render cards
            cols = 3

            for i, p in enumerate(productos):
                card = ProductoCard(p, self.service, self.load_data)

                row = i // cols
                col = i % cols

                self.grid.addWidget(card, row, col)

            self.lbl_page.setText(f"Página: {self.page}")

        except Exception as e:
            print("ERROR:", e)

    # =========================

    def next_page(self):
        if self.has_next:
            self.page += 1
            self.load_data()

    def prev_page(self):
        if self.has_prev:
            self.page -= 1
            self.load_data()

    # =========================

    def open_form(self):
        self.form = ProductoForm(
            self.service,
            self.rubro_service,
            self.proveedor_service,
            self.load_data
        )
        self.form.show()
        
