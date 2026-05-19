# desktop/app/views/compra_form.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QLabel,
    QComboBox,
    QHBoxLayout,
    QSpinBox
)


class CompraForm(QWidget):

    def __init__(
        self,
        compra_service,
        proveedor_service,
        producto_service,
        on_success
    ):
        super().__init__()

        self.compra_service = compra_service
        self.proveedor_service = proveedor_service
        self.producto_service = producto_service
        self.on_success = on_success

        self.setWindowTitle("Nueva Compra")

        self.productos = []

        layout = QVBoxLayout()

        # =========================
        # PROVEEDOR
        # =========================

        layout.addWidget(QLabel("Proveedor"))

        self.proveedor_combo = QComboBox()

        proveedores = self.proveedor_service.listar()
        proveedores_data = proveedores.get("results", proveedores)

        for p in proveedores_data:
            self.proveedor_combo.addItem(
                f"{p['nombre']} {p['apellido']}",
                p["id"]
            )

        layout.addWidget(self.proveedor_combo)

        # =========================
        # DETALLES
        # =========================

        self.detalles_layout = QVBoxLayout()

        layout.addLayout(self.detalles_layout)

        self.btn_add_producto = QPushButton(
            "Agregar producto"
        )

        self.btn_add_producto.clicked.connect(
            self.add_producto_row
        )

        layout.addWidget(self.btn_add_producto)

        # =========================
        # GUARDAR
        # =========================

        self.btn_save = QPushButton("Guardar compra")

        self.btn_save.clicked.connect(self.save)

        layout.addWidget(self.btn_save)

        self.setLayout(layout)

        self.add_producto_row()

    # =========================

    def add_producto_row(self):

        row = QHBoxLayout()

        combo = QComboBox()

        productos = self.producto_service.listar()

        productos_data = productos.get("results", productos)

        for p in productos_data:
            combo.addItem(
                p["nombre"],
                p["id"]
            )

        cantidad = QSpinBox()
        cantidad.setMinimum(1)
        cantidad.setMaximum(9999)

        btn_delete = QPushButton("X")

        row.addWidget(combo)
        row.addWidget(cantidad)
        row.addWidget(btn_delete)

        self.detalles_layout.addLayout(row)

        detalle = {
            "combo": combo,
            "cantidad": cantidad,
            "layout": row
        }

        self.productos.append(detalle)

        btn_delete.clicked.connect(
            lambda: self.remove_producto_row(detalle)
        )

    # =========================

    def remove_producto_row(self, detalle):

        for i in reversed(range(detalle["layout"].count())):
            widget = detalle["layout"].itemAt(i).widget()

            if widget:
                widget.deleteLater()

        self.productos.remove(detalle)

    # =========================

    def save(self):

        try:

            detalles = []

            for d in self.productos:

                detalles.append({
                    "producto": d["combo"].currentData(),
                    "cantidad": d["cantidad"].value()
                })

            data = {
                "proveedor": self.proveedor_combo.currentData(),
                "detalles": detalles
            }

            self.compra_service.crear(data)

            QMessageBox.information(
                self,
                "OK",
                "Compra creada"
            )

            self.on_success()

            self.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
            
            