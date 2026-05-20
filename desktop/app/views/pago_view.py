# desktop/app/views/pago_view.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QLabel,
)


class PagoView(QWidget):

    def __init__(self, factura=None, pago_service=None):
        super().__init__()

        self.factura = factura
        self.pago_service = pago_service

        if self.factura:
            self.setWindowTitle(
                f"Pagos - Factura #{self.factura['id']}"
            )
        else:
            self.setWindowTitle("Cobranzas")

        self.resize(800, 400)

        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()

        # ==================================================
        # MODO GENERAL (SIN FACTURA)
        # ==================================================
        # Si se abre desde el menú lateral "Cobranzas",
        # no hay una factura específica.
        # Mostramos un mensaje y no permitimos CRUD.
        # ==================================================

        if not self.factura:
            mensaje = QLabel(
                "Seleccione una factura desde el módulo Facturas "
                "y luego presione el botón 'Pagos'."
            )
            layout.addWidget(mensaje)
            self.setLayout(layout)
            return

        # ==================================================
        # MODO DETALLE (CON FACTURA)
        # ==================================================

        botones_layout = QHBoxLayout()

        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_nuevo = QPushButton("Nuevo pago")
        self.btn_editar = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")

        botones_layout.addWidget(self.btn_actualizar)
        botones_layout.addWidget(self.btn_nuevo)
        botones_layout.addWidget(self.btn_editar)
        botones_layout.addWidget(self.btn_eliminar)
        botones_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Monto",
            "Método",
            "Estado",
            "Fecha",
            "Referencia",
        ])

        layout.addLayout(botones_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.btn_actualizar.clicked.connect(self.cargar_datos)
        self.btn_nuevo.clicked.connect(self.nuevo_pago)
        self.btn_editar.clicked.connect(self.editar_pago)
        self.btn_eliminar.clicked.connect(self.eliminar_pago)

    def cargar_datos(self):
        try:
            # Si la vista se abrió desde Facturas, filtramos por factura.
            # Si se abrió desde el menú "Cobranzas", mostramos todos.
            if self.factura:
                pagos = self.pago_service.listar_por_factura(
                    self.factura["id"]
                )
            else:
                pagos = self.pago_service.listar()

            # Si la API devuelve paginación DRF:
            # {
            #   "count": ...,
            #   "results": [...]
            # }
            if isinstance(pagos, dict):
                pagos = pagos.get("results", [])

            self.table.setRowCount(len(pagos))

            for row, pago in enumerate(pagos):
                # La API no devuelve "id" en PagoSerializer,
                # por eso no debemos intentar leer pago["id"].
                self.table.setItem(
                    row,
                    0,
                    QTableWidgetItem("-")
                )

                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(str(pago.get("monto", 0)))
                )

                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        pago.get("metodo_pago", "")
                    )
                )

                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        pago.get("estado", "")
                    )
                )

                self.table.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        pago.get("fecha_pago", "")
                    )
                )

                self.table.setItem(
                    row,
                    5,
                    QTableWidgetItem(
                        str(pago.get("referencia", "") or "")
                    )
                )

            self.table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    def nuevo_pago(self):
        from views.pago_form import PagoForm

        self.form = PagoForm(
            factura=self.factura,
            pago_service=self.pago_service,
            on_success=self.cargar_datos,
        )
        self.form.show()

    def editar_pago(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Debe seleccionar un pago."
            )
            return

        pago_id = int(self.table.item(row, 0).text())
        pago = self.pago_service.obtener(pago_id)

        from views.pago_form import PagoForm

        self.form = PagoForm(
            factura=self.factura,
            pago_service=self.pago_service,
            on_success=self.cargar_datos,
            pago=pago
        )
        self.form.show()

    def eliminar_pago(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Debe seleccionar un pago."
            )
            return

        pago_id = int(self.table.item(row, 0).text())

        confirm = QMessageBox.question(
            self,
            "Confirmar",
            "¿Eliminar el pago seleccionado?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            self.pago_service.eliminar(pago_id)

            QMessageBox.information(
                self,
                "OK",
                "Pago eliminado correctamente"
            )

            self.cargar_datos()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))