# desktop/app/views/pago_view.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QLabel
)

from views.pago_form import PagoForm


class PagoView(QWidget):

    def __init__(self, factura=None, pago_service=None):

        super().__init__()

        self.factura = factura
        self.service = pago_service

        # =========================
        # WINDOW TITLE
        # =========================

        if self.factura:

            self.setWindowTitle(
                f"Pagos - Factura #{self.factura['id']}"
            )

        else:

            self.setWindowTitle(
                "Pagos"
            )

        # =========================
        # LAYOUT
        # =========================

        layout = QVBoxLayout()

        # =========================
        # INFO FACTURA
        # =========================

        if self.factura:

            info = QLabel(
                f"Factura #{self.factura['id']} | "
                f"Total: ${self.factura['total']}"
            )

        else:

            info = QLabel(
                "Listado general de pagos"
            )

        layout.addWidget(info)

        # =========================
        # BOTONES
        # =========================

        buttons_layout = QHBoxLayout()

        self.btn_crear = QPushButton("Crear")
        self.btn_editar = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_recargar = QPushButton("Recargar")

        self.btn_crear.clicked.connect(
            self.crear_pago
        )

        self.btn_editar.clicked.connect(
            self.editar_pago
        )

        self.btn_eliminar.clicked.connect(
            self.eliminar_pago
        )

        self.btn_recargar.clicked.connect(
            self.cargar_pagos
        )

        buttons_layout.addWidget(self.btn_crear)
        buttons_layout.addWidget(self.btn_editar)
        buttons_layout.addWidget(self.btn_eliminar)
        buttons_layout.addWidget(self.btn_recargar)

        layout.addLayout(buttons_layout)

        # =========================
        # TABLA
        # =========================

        self.table = QTableWidget()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Factura",
            "Monto",
            "Método",
            "Estado",
            "Referencia"
        ])

        layout.addWidget(self.table)

        self.setLayout(layout)

        # =========================
        # LOAD
        # =========================

        self.cargar_pagos()

    # =========================================================
    # CARGAR PAGOS
    # =========================================================

    def cargar_pagos(self):

        try:

            if self.factura:

                response = self.service.listar_por_factura(
                    self.factura["id"]
                )

            else:

                response = self.service.listar()

            pagos = response["results"]

            if self.factura:

                pagos = [
                    p for p in pagos
                    if p["factura"] == self.factura["id"]
                ]

            self.table.setRowCount(
                len(pagos)
            )

            for row, pago in enumerate(pagos):

                self.table.setItem(
                    row,
                    0,
                    QTableWidgetItem(
                        str(pago["id"])
                    )
                )

                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        str(pago["factura"])
                    )
                )

                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        str(pago["monto"])
                    )
                )

                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        pago["metodo_pago"]
                    )
                )

                self.table.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        pago["estado"]
                    )
                )

                self.table.setItem(
                    row,
                    5,
                    QTableWidgetItem(
                        str(
                            pago["referencia"]
                        )
                    )
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    # =========================================================
    # OBTENER ID
    # =========================================================

    def obtener_id_seleccionado(self):

        fila = self.table.currentRow()

        if fila < 0:
            return None

        return int(
            self.table.item(fila, 0).text()
        )

    # =========================================================
    # CREAR
    # =========================================================

    def crear_pago(self):

        if not self.factura:

            QMessageBox.warning(
                self,
                "Error",
                "Debe abrir pagos desde una factura"
            )

            return

        dialog = PagoForm(
            self,
            factura_id=self.factura["id"]
        )

        if dialog.exec():

            try:

                data = dialog.obtener_datos()

                self.service.crear(data)

                self.cargar_pagos()

            except Exception as e:

                QMessageBox.critical(
                    self,
                    "Error",
                    str(e)
                )

    # =========================================================
    # EDITAR
    # =========================================================

    def editar_pago(self):

        if not self.factura:

            QMessageBox.warning(
                self,
                "Error",
                "Abra pagos desde una factura"
            )

            return

        pago_id = self.obtener_id_seleccionado()

        if not pago_id:

            QMessageBox.warning(
                self,
                "Error",
                "Seleccione un pago"
            )

            return

        try:

            pago = self.service.obtener(
                pago_id
            )

            dialog = PagoForm(
                self,
                factura_id=self.factura["id"],
                pago=pago
            )

            if dialog.exec():

                data = dialog.obtener_datos()

                self.service.actualizar(
                    pago_id,
                    data
                )

                self.cargar_pagos()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    # =========================================================
    # ELIMINAR
    # =========================================================

    def eliminar_pago(self):

        pago_id = self.obtener_id_seleccionado()

        if not pago_id:

            QMessageBox.warning(
                self,
                "Error",
                "Seleccione un pago"
            )

            return

        try:

            self.service.eliminar(
                pago_id
            )

            self.cargar_pagos()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )