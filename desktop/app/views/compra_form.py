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

QSS_STYLE = """
    QWidget#CompraForm {
        background-color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        color: #1a1a1a;
    }
    QLabel {
        font-weight: bold;
        color: #495057;
    }
    QComboBox, QSpinBox {
        background-color: #f8f9fa;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 6px;
        color: #212529;
        min-height: 20px;
    }
    QComboBox:focus, QSpinBox:focus {
        border: 1px solid #dc3545;
        background-color: #ffffff;
    }
    QPushButton#btn_add_producto {
        background-color: #6c757d;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }
    QPushButton#btn_add_producto:hover {
        background-color: #5c636a;
    }
    QPushButton#btn_delete {
        background-color: #f8d7da;
        color: #b02a37;
        border: 1px solid #f5c2c7;
        border-radius: 4px;
        font-weight: bold;
        min-width: 28px;
        max-width: 28px;
        min-height: 28px;
    }
    QPushButton#btn_delete:hover {
        background-color: #dc3545;
        color: white;
    }
    QPushButton#btn_save {
        background-color: #dc3545;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
        margin-top: 15px;
    }
    QPushButton#btn_save:hover {
        background-color: #bd2130;
    }
"""

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

        self.setWindowTitle("Nueva Compra — MOTO-TOP")
        self.resize(450, 480)
        
        self.setObjectName("CompraForm")
        self.setStyleSheet(QSS_STYLE)

        self.productos = []

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # =========================
        # PROVEEDOR
        # =========================

        layout.addWidget(QLabel("Proveedor:"))

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
        
        layout.addWidget(QLabel("Items de la Compra:"))

        self.detalles_layout = QVBoxLayout()
        self.detalles_layout.setSpacing(8)

        layout.addLayout(self.detalles_layout)

        self.btn_add_producto = QPushButton("＋ Agregar producto")
        self.btn_add_producto.setObjectName("btn_add_producto")

        self.btn_add_producto.clicked.connect(
            self.add_producto_row
        )

        layout.addWidget(self.btn_add_producto)
        layout.addStretch()

        # =========================
        # GUARDAR
        # =========================

        self.btn_save = QPushButton("Guardar Compra")
        self.btn_save.setObjectName("btn_save")
        self.btn_save.clicked.connect(self.save)

        layout.addWidget(self.btn_save)

        self.setLayout(layout)

        self.add_producto_row()

    # =========================

    def add_producto_row(self):

        row = QHBoxLayout()
        row.setSpacing(6)

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

        btn_delete = QPushButton("✕")
        btn_delete.setObjectName("btn_delete")

        row.addWidget(combo, stretch=3)
        row.addWidget(cantidad, stretch=1)
        row.addWidget(btn_delete, stretch=0)

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
        if len(self.productos) <= 1:
            return  # Mantiene al menos una fila en el formulario

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
            
            