# desktop/app/views/pago_view.py

from collections import defaultdict

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

from services.factura_service import FacturaService


class PagoView(QWidget):

    def __init__(self, factura=None, pago_service=None):
        super().__init__()

        self.factura = factura
        self.pago_service = pago_service

        self.factura_service = FacturaService(
            self.pago_service.http
        )

        if self.factura:
            self.setWindowTitle(
                f"Pagos - Factura #{self.factura['id']}"
            )
        else:
            self.setWindowTitle("Cobranzas")

        self.resize(1300, 550)

        self.init_ui()
        self.cargar_datos()

    def init_ui(self):

        layout = QVBoxLayout()

        # ====================================
        # Resumen
        # ====================================

        self.label_total = QLabel()
        self.label_pagado = QLabel()
        self.label_saldo = QLabel()
        self.label_estado = QLabel()

        layout.addWidget(self.label_total)
        layout.addWidget(self.label_pagado)
        layout.addWidget(self.label_saldo)
        layout.addWidget(self.label_estado)

        # ====================================
        # Botones
        # ====================================

        botones_layout = QHBoxLayout()

        self.btn_actualizar = QPushButton(
            "Actualizar"
        )

        self.btn_nuevo = QPushButton(
            "Nuevo pago"
        )

        self.btn_editar = QPushButton(
            "Editar"
        )

        self.btn_eliminar = QPushButton(
            "Eliminar"
        )

        botones_layout.addWidget(
            self.btn_actualizar
        )

        botones_layout.addWidget(
            self.btn_nuevo
        )

        botones_layout.addWidget(
            self.btn_editar
        )

        botones_layout.addWidget(
            self.btn_eliminar
        )

        botones_layout.addStretch()

        layout.addLayout(botones_layout)

        # ====================================
        # Tabla
        # ====================================

        self.table = QTableWidget()

        self.table.setColumnCount(10)

        self.table.setHorizontalHeaderLabels([
            "Pago ID",
            "Factura",
            "Pedido",
            "Total Factura",
            "Total Pagado",
            "Saldo",
            "Estado Factura",
            "Monto Pago",
            "Método",
            "Fecha",
        ])

        layout.addWidget(self.table)

        self.setLayout(layout)

        # ====================================
        # Configuración
        # ====================================

        if not self.factura:

            self.btn_nuevo.setEnabled(False)
            self.btn_editar.setEnabled(False)
            self.btn_eliminar.setEnabled(False)

            self.label_total.hide()
            self.label_pagado.hide()
            self.label_saldo.hide()
            self.label_estado.hide()

        # ====================================
        # Eventos
        # ====================================

        self.btn_actualizar.clicked.connect(
            self.cargar_datos
        )

        self.btn_nuevo.clicked.connect(
            self.nuevo_pago
        )

        self.btn_editar.clicked.connect(
            self.editar_pago
        )

        self.btn_eliminar.clicked.connect(
            self.eliminar_pago
        )

    def calcular_total_pagado(self, pagos):

        total = 0

        for pago in pagos:

            if pago.get("estado") == "completado":

                total += float(
                    pago.get("monto", 0)
                )

        return total

    def cargar_resumen_factura(self, pagos):

        total_factura = float(
            self.factura.get("total", 0)
        )

        total_pagado = self.calcular_total_pagado(
            pagos
        )

        saldo = total_factura - total_pagado

        estado = (
            "SALDADA"
            if saldo <= 0
            else "PENDIENTE"
        )

        self.label_total.setText(
            f"Total factura: ${total_factura:.2f}"
        )

        self.label_pagado.setText(
            f"Total pagado: ${total_pagado:.2f}"
        )

        self.label_saldo.setText(
            f"Saldo pendiente: ${saldo:.2f}"
        )

        self.label_estado.setText(
            f"Estado: {estado}"
        )

        if saldo <= 0:

            self.label_estado.setStyleSheet(
                """
                color: green;
                font-weight: bold;
                font-size: 14px;
                """
            )

            self.label_saldo.setStyleSheet(
                """
                color: green;
                font-weight: bold;
                """
            )

        else:

            self.label_estado.setStyleSheet(
                """
                color: red;
                font-weight: bold;
                font-size: 14px;
                """
            )

            self.label_saldo.setStyleSheet(
                """
                color: red;
                font-weight: bold;
                """
            )

    def cargar_datos(self):

        try:

            if self.factura:

                pagos = self.pago_service.listar_por_factura(
                    self.factura["id"]
                )

            else:

                pagos = self.pago_service.listar()

                if isinstance(pagos, dict):
                    pagos = pagos.get("results", [])

            # ====================================
            # Resumen
            # ====================================

            if self.factura:

                self.cargar_resumen_factura(
                    pagos
                )

            # ====================================
            # Cache pagos
            # ====================================

            pagos_por_factura = defaultdict(list)

            for pago in pagos:

                factura_id = pago.get("factura")

                pagos_por_factura[
                    factura_id
                ].append(pago)

            # ====================================
            # Tabla
            # ====================================

            self.table.setRowCount(len(pagos))

            for row, pago in enumerate(pagos):

                pago_id = pago.get("id")

                factura_id = pago.get("factura")

                factura = self.factura_service.obtener(
                    factura_id
                )

                total_factura = float(
                    factura.get("total", 0)
                )

                pagos_factura = pagos_por_factura[
                    factura_id
                ]

                total_pagado = (
                    self.calcular_total_pagado(
                        pagos_factura
                    )
                )

                saldo = (
                    total_factura
                    - total_pagado
                )

                estado_factura = (
                    "Saldada"
                    if saldo <= 0
                    else "Pendiente"
                )

                # ====================================
                # Pago ID
                # ====================================

                self.table.setItem(
                    row,
                    0,
                    QTableWidgetItem(
                        str(pago_id)
                    )
                )

                # ====================================
                # Factura
                # ====================================

                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        str(factura_id)
                    )
                )

                # ====================================
                # Pedido
                # ====================================

                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        str(
                            factura.get(
                                "pedido",
                                ""
                            )
                        )
                    )
                )

                # ====================================
                # Total Factura
                # ====================================

                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        f"${total_factura:.2f}"
                    )
                )

                # ====================================
                # Total Pagado
                # ====================================

                self.table.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        f"${total_pagado:.2f}"
                    )
                )

                # ====================================
                # Saldo
                # ====================================

                self.table.setItem(
                    row,
                    5,
                    QTableWidgetItem(
                        f"${saldo:.2f}"
                    )
                )

                # ====================================
                # Estado Factura
                # ====================================

                self.table.setItem(
                    row,
                    6,
                    QTableWidgetItem(
                        estado_factura
                    )
                )

                # ====================================
                # Monto Pago
                # ====================================

                self.table.setItem(
                    row,
                    7,
                    QTableWidgetItem(
                        str(
                            pago.get(
                                "monto",
                                ""
                            )
                        )
                    )
                )

                # ====================================
                # Método
                # ====================================

                self.table.setItem(
                    row,
                    8,
                    QTableWidgetItem(
                        str(
                            pago.get(
                                "metodo_pago",
                                ""
                            )
                        )
                    )
                )

                # ====================================
                # Fecha
                # ====================================

                self.table.setItem(
                    row,
                    9,
                    QTableWidgetItem(
                        str(
                            pago.get(
                                "fecha_pago",
                                ""
                            )
                        )
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

        pago_id = int(
            self.table.item(row, 0).text()
        )

        try:

            pago = self.pago_service.obtener(
                pago_id
            )

            from views.pago_form import PagoForm

            self.form = PagoForm(
                factura=self.factura,
                pago_service=self.pago_service,
                on_success=self.cargar_datos,
                pago=pago
            )

            self.form.show()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    def eliminar_pago(self):

        row = self.table.currentRow()

        if row < 0:

            QMessageBox.warning(
                self,
                "Selección requerida",
                "Debe seleccionar un pago."
            )

            return

        pago_id = int(
            self.table.item(row, 0).text()
        )

        confirm = QMessageBox.question(
            self,
            "Confirmar",
            "¿Eliminar el pago seleccionado?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:

            self.pago_service.eliminar(
                pago_id
            )

            QMessageBox.information(
                self,
                "OK",
                "Pago eliminado correctamente"
            )

            self.cargar_datos()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
            