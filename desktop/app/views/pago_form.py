# desktop/app/views/pago_form.py

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox
)


class PagoForm(QDialog):

    def __init__(
        self,
        parent=None,
        factura_id=None,
        pago=None
    ):

        super().__init__(parent)

        self.pago = pago
        self.factura_id = factura_id

        self.setWindowTitle("Pago")

        layout = QVBoxLayout()

        # FACTURA

        layout.addWidget(
            QLabel(
                f"Factura ID: {self.factura_id}"
            )
        )

        # MONTO

        layout.addWidget(QLabel("Monto"))

        self.monto_input = QLineEdit()

        layout.addWidget(self.monto_input)

        # METODO

        layout.addWidget(QLabel("Método"))

        self.metodo_combo = QComboBox()

        self.metodo_combo.addItems([
            "efectivo",
            "transferencia",
            "tarjeta"
        ])

        layout.addWidget(self.metodo_combo)

        # ESTADO

        layout.addWidget(QLabel("Estado"))

        self.estado_combo = QComboBox()

        self.estado_combo.addItems([
            "pendiente",
            "completado",
            "fallido"
        ])

        layout.addWidget(self.estado_combo)

        # REFERENCIA

        layout.addWidget(QLabel("Referencia"))

        self.referencia_input = QLineEdit()

        layout.addWidget(self.referencia_input)

        # BOTON

        self.btn_guardar = QPushButton(
            "Guardar"
        )

        self.btn_guardar.clicked.connect(
            self.accept
        )

        layout.addWidget(self.btn_guardar)

        self.setLayout(layout)

        # EDICION

        if self.pago:

            self.monto_input.setText(
                str(self.pago["monto"])
            )

            self.metodo_combo.setCurrentText(
                self.pago["metodo_pago"]
            )

            self.estado_combo.setCurrentText(
                self.pago["estado"]
            )

            self.referencia_input.setText(
                str(
                    self.pago["referencia"] or ""
                )
            )

    def obtener_datos(self):

        return {
            "factura": self.factura_id,
            "monto": float(
                self.monto_input.text()
            ),
            "metodo_pago": self.metodo_combo.currentText(),
            "estado": self.estado_combo.currentText(),
            "referencia": self.referencia_input.text()
        }