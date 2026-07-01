# desktop/app/views/promocion_form.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox
)
from PyQt6.QtCore import QDate

# Constante de diseño para mantener la consistencia visual de la app
QSS_STYLE = """
    QWidget {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        color: #333333;
    }
    QLabel {
        font-weight: bold;
        color: #495057;
    }
    QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
        background-color: #ffffff;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 6px;
        min-height: 20px;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
        border: 1px solid #0d6efd;
    }
    QPushButton {
        background-color: #0d6efd;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0b5ed7;
    }
    QPushButton:pressed {
        background-color: #0a58ca;
    }
"""

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

        self.setWindowTitle(f"Promoción - {producto['nombre']}")
        self.resize(450, 350)
        self.setStyleSheet(QSS_STYLE)

        # Layout Principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Layout de Formulario para alinear etiquetas e inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # Campo Nombre
        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Ej. Descuento de Invierno")
        form_layout.addRow("Nombre promoción:", self.nombre)

        # Campo Tipo
        self.tipo = QComboBox()
        self.tipo.addItems(["descuento", "2x1", "temporada"])
        form_layout.addRow("Tipo:", self.tipo)

        # Contenedor de Fechas (Horizontal)
        fechas_layout = QHBoxLayout()
        fechas_layout.setSpacing(10)

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDate(QDate.currentDate())
        
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDate(QDate.currentDate().addDays(7)) # Default 1 semana

        fechas_layout.addWidget(self.fecha_inicio)
        fechas_layout.addWidget(QLabel("hasta"))
        fechas_layout.addWidget(self.fecha_fin)
        
        form_layout.addRow("Vigencia:", fechas_layout)

        # Campo Valor Descuento
        self.valor_descuento = QDoubleSpinBox()
        self.valor_descuento.setMaximum(999999.99)
        self.valor_descuento.setDecimals(2)
        self.valor_descuento.setSuffix(" %") # O se puede cambiar según backend
        form_layout.addRow("Valor descuento:", self.valor_descuento)

        main_layout.addLayout(form_layout)

        # Botón Guardar
        self.btn_save = QPushButton("Guardar promoción")
        self.btn_save.clicked.connect(self.save)
        main_layout.addWidget(self.btn_save)

        self.setLayout(main_layout)

    def save(self):
        try:
            promo_data = {
                "nombre": self.nombre.text(),
                "tipo": self.tipo.currentText(),
                "fecha_inicio": self.fecha_inicio.date().toString("yyyy-MM-dd"),
                "fecha_fin": self.fecha_fin.date().toString("yyyy-MM-dd"),
            }

            promocion = self.promocion_service.crear(promo_data)

            producto_promocion_data = {
                "producto": self.producto["id"],
                "promocion": promocion["id"],
                "tipo_descuento": "porcentaje",
                "valor_descuento": self.valor_descuento.value()
            }

            self.producto_promocion_service.crear(producto_promocion_data)

            QMessageBox.information(self, "Éxito", "Promoción creada correctamente.")
            self.on_success()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))