from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QLabel,
    QComboBox,
    QHBoxLayout,
    QSpinBox,
    QTextEdit
)


class PedidoForm(QWidget):

    def __init__(
        self,
        pedido_service,
        cliente_service,
        vendedor_service,
        producto_service,
        on_success
    ):
        super().__init__()

        self.pedido_service = pedido_service
        self.cliente_service = cliente_service
        self.vendedor_service = vendedor_service
        self.producto_service = producto_service
        self.on_success = on_success

        self.setWindowTitle("Nuevo Pedido")

        self.productos = []

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Cliente"))

        self.cliente_combo = QComboBox()
        clientes = self.cliente_service.listar()
        clientes_data = clientes.get("results", clientes)

        for c in clientes_data:
            self.cliente_combo.addItem(
                f"{c['nombre']} {c.get('apellido','')}",
                c["id"]
            )

        layout.addWidget(self.cliente_combo)

        layout.addWidget(QLabel("Vendedor (opcional)"))

        self.vendedor_combo = QComboBox()
        self.vendedor_combo.addItem("Sin vendedor", None)

        vendedores = self.vendedor_service.listar()
        vendedores_data = vendedores.get("results", vendedores)

        for v in vendedores_data:
            self.vendedor_combo.addItem(
                f"{v['nombre']} {v.get('apellido','')}",
                v["id"]
            )

        layout.addWidget(self.vendedor_combo)

        layout.addWidget(QLabel("Origen"))
        self.origen_combo = QComboBox()
        self.origen_combo.addItem("Local", "local")
        self.origen_combo.addItem("Mobile", "mobile")
        self.origen_combo.addItem("Web", "web")
        layout.addWidget(self.origen_combo)

        layout.addWidget(QLabel("Observaciones"))
        self.observaciones = QTextEdit()
        self.observaciones.setFixedHeight(80)
        layout.addWidget(self.observaciones)

        self.detalles_layout = QVBoxLayout()
        layout.addLayout(self.detalles_layout)

        self.btn_add_producto = QPushButton("Agregar producto")
        self.btn_add_producto.clicked.connect(self.add_producto_row)
        layout.addWidget(self.btn_add_producto)

        self.btn_save = QPushButton("Guardar pedido")
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)

        self.setLayout(layout)

        self.add_producto_row()

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

    def remove_producto_row(self, detalle):

        for i in reversed(range(detalle["layout"].count())):
            widget = detalle["layout"].itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.productos.remove(detalle)

    def save(self):

        try:
            detalles = []

            for d in self.productos:
                detalles.append({
                    "producto": d["combo"].currentData(),
                    "cantidad": d["cantidad"].value()
                })

            if not detalles:
                raise ValueError("Debe ingresar al menos un producto")

            data = {
                "cliente": self.cliente_combo.currentData(),
                "origen": self.origen_combo.currentData(),
                "observaciones": self.observaciones.toPlainText(),
                "detalles": detalles
            }

            vendedor_id = self.vendedor_combo.currentData()
            if vendedor_id is not None:
                data["vendedor"] = vendedor_id

            self.pedido_service.crear(data)

            QMessageBox.information(
                self,
                "OK",
                "Pedido creado"
            )

            self.on_success()
            self.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
