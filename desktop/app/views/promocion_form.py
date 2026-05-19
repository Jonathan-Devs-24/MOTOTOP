# desktop/app/views/promocion_form.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox
)

from PyQt6.QtCore import QDate


class PromocionForm(QWidget):

    def __init__(
        self,
        producto,
        promocion_service,
        producto_promocion_service,
        on_success
    ):
        super().__init__()

        self.producto = producto
        self.promocion_service = promocion_service
        self.producto_promocion_service = producto_promocion_service
        self.on_success = on_success

        self.setWindowTitle(
            f"Promoción - {producto['nombre']}"
        )

        layout = QVBoxLayout()

        # =========================
        # NOMBRE
        # =========================

        layout.addWidget(QLabel("Nombre promoción"))

        self.nombre = QLineEdit()
        layout.addWidget(self.nombre)

        # =========================
        # TIPO
        # =========================

        layout.addWidget(QLabel("Tipo"))

        self.tipo = QComboBox()
        self.tipo.addItems([
            "descuento",
            "2x1",
            "temporada"
        ])

        layout.addWidget(self.tipo)

        # =========================
        # FECHAS
        # =========================

        layout.addWidget(QLabel("Fecha inicio"))

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDate(QDate.currentDate())

        layout.addWidget(self.fecha_inicio)

        layout.addWidget(QLabel("Fecha fin"))

        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDate(QDate.currentDate())

        layout.addWidget(self.fecha_fin)

        # =========================
        # DESCUENTO
        # =========================

        layout.addWidget(QLabel("Valor descuento"))

        self.valor_descuento = QDoubleSpinBox()
        self.valor_descuento.setMaximum(999999)
        self.valor_descuento.setDecimals(2)

        layout.addWidget(self.valor_descuento)

        # =========================
        # BOTON
        # =========================

        self.btn_save = QPushButton("Guardar promoción")
        self.btn_save.clicked.connect(self.save)

        layout.addWidget(self.btn_save)

        self.setLayout(layout)

    # =========================

    def save(self):
        try:

            promo_data = {
                "nombre": self.nombre.text(),
                "tipo": self.tipo.currentText(),
                "fecha_inicio": self.fecha_inicio.date().toString("yyyy-MM-dd"),
                "fecha_fin": self.fecha_fin.date().toString("yyyy-MM-dd"),
            }

            promocion = self.promocion_service.crear(
                promo_data
            )

            producto_promocion_data = {
                "producto": self.producto["id"],
                "promocion": promocion["id"],
                "tipo_descuento": "porcentaje",
                "valor_descuento": self.valor_descuento.value()
            }

            self.producto_promocion_service.crear(
                producto_promocion_data
            )

            QMessageBox.information(
                self,
                "OK",
                "Promoción creada"
            )

            self.on_success()

            self.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
            
            