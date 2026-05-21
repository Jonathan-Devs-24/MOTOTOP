# desktop/app/views/pago_form.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
)


class PagoForm(QWidget):

    def __init__(self, factura, pago_service, on_success, pago=None):
        super().__init__()

        self.factura = factura
        self.pago_service = pago_service
        self.on_success = on_success
        self.pago = pago

        self.setWindowTitle(
            "Editar Pago"
            if pago
            else f"Nuevo Pago - Factura #{factura['id']}"
        )

        self.resize(400, 300)

        layout = QVBoxLayout()

        layout.addWidget(
            QLabel(f"Factura #{factura['id']}")
        )

        layout.addWidget(
            QLabel(
                f"Total: ${factura.get('total', 0)}"
            )
        )

        layout.addWidget(QLabel("Monto"))

        self.monto = QLineEdit()
        layout.addWidget(self.monto)

        layout.addWidget(
            QLabel("Método de pago")
        )

        self.metodo_pago = QComboBox()

        self.metodo_pago.addItem(
            "Efectivo",
            "efectivo"
        )

        self.metodo_pago.addItem(
            "Transferencia",
            "transferencia"
        )

        self.metodo_pago.addItem(
            "Tarjeta",
            "tarjeta"
        )

        layout.addWidget(self.metodo_pago)

        # Estado fijo en completado
        layout.addWidget(
            QLabel("Estado")
        )

        self.estado = QComboBox()

        self.estado.addItem(
            "Completado",
            "completado"
        )

        self.estado.setEnabled(False)

        layout.addWidget(self.estado)

        layout.addWidget(QLabel("Referencia"))

        self.referencia = QLineEdit()
        layout.addWidget(self.referencia)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.save)

        layout.addWidget(self.btn_guardar)

        layout.addStretch()

        self.setLayout(layout)

        if self.pago:
            self.load_pago()

    def load_pago(self):

        self.monto.setText(
            str(
                self.pago.get("monto", "")
            )
        )

        self.referencia.setText(
            self.pago.get("referencia") or ""
        )

        metodo = self.pago.get(
            "metodo_pago"
        )

        index = self.metodo_pago.findData(
            metodo
        )

        if index >= 0:
            self.metodo_pago.setCurrentIndex(
                index
            )

    def validate_data(self):

        monto_text = self.monto.text().strip()

        if not monto_text:
            raise ValueError(
                "Debe ingresar el monto"
            )

        try:
            monto = float(monto_text)

        except ValueError:
            raise ValueError(
                "El monto debe ser numérico"
            )

        if monto <= 0:
            raise ValueError(
                "El monto debe ser mayor a cero"
            )

    def build_data(self):

        return {
            "factura": self.factura["id"],
            "monto": float(
                self.monto.text().strip()
            ),
            "metodo_pago": self.metodo_pago.currentData(),
            "estado": "completado",
            "referencia": self.referencia.text().strip() or None,
        }

    def save(self):

        try:
            self.validate_data()

            data = self.build_data()

            if self.pago:

                self.pago_service.actualizar(
                    self.pago["id"],
                    data
                )

                QMessageBox.information(
                    self,
                    "OK",
                    "Pago actualizado correctamente"
                )

            else:

                self.pago_service.crear(data)

                QMessageBox.information(
                    self,
                    "OK",
                    "Pago registrado correctamente"
                )

            # Refrescar vista principal
            self.on_success()

            # Forzar repaint
            parent = self.parent()

            if parent:
                parent.update()
                parent.repaint()

            self.close()

        except ValueError as e:

            QMessageBox.warning(
                self,
                "Validación",
                str(e)
            )

        except Exception as e:

            error_text = str(e)

            if hasattr(e, "response") and e.response is not None:

                try:
                    error_text = str(
                        e.response.json()
                    )
                except:
                    error_text = e.response.text

            QMessageBox.critical(
                self,
                "Error",
                error_text
            )