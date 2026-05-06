# desktop/app/views/producto_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel
)

from services.rubro_service import RubroService
from services.proveedor_service import ProveedorService
from views.producto_form import ProductoForm


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

        # Top bar
        top_bar = QHBoxLayout()

        self.btn_prev = QPushButton("Anterior")
        self.btn_next = QPushButton("Siguiente")
        self.btn_refresh = QPushButton("Recargar")
        self.btn_new = QPushButton("Nuevo")

        self.lbl_page = QLabel("Página: 1")

        # Agregar botones
        top_bar.addWidget(self.btn_new)
        top_bar.addWidget(self.btn_prev)
        top_bar.addWidget(self.btn_next)
        top_bar.addWidget(self.btn_refresh)
        top_bar.addWidget(self.lbl_page)

        # Conexiones (DESPUÉS de crear botones)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_new.clicked.connect(self.open_form)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Precio", "Stock"
        ])

        layout.addLayout(top_bar)
        layout.addWidget(self.table)

        self.setLayout(layout)

    # =========================

    def load_data(self):
        try:
            data = self.service.listar(self.page)

            productos = data["results"]
            self.has_next = data["next"] is not None
            self.has_prev = data["previous"] is not None

            self.table.setRowCount(len(productos))

            for row, p in enumerate(productos):
                self.table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(p["nombre"]))
                self.table.setItem(row, 2, QTableWidgetItem(str(p["precio_base"])))
                self.table.setItem(row, 3, QTableWidgetItem(str(p["stock"])))

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