# desktop/app/views/pago_form.py
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QDoubleSpinBox
)

QSS_STYLE = """
    QDialog {
        background-color: #1a1a1a;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        color: #ffffff;
    }
    QLabel {
        font-weight: bold;
        color: #cccccc;
    }
    QLabel#lbl_factura {
        font-size: 14px;
        color: #ffffff;
        background-color: #262626;
        padding: 8px;
        border-left: 3px solid #dc3545;
        border-radius: 2px;
        margin-bottom: 5px;
    }
    QLineEdit, QComboBox, QDoubleSpinBox {
        background-color: #262626;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 6px;
        color: #ffffff;
        min-height: 20px;
    }
    QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
        border: 1px solid #dc3545;
    }
    QComboBox QAbstractItemView {
        background-color: #262626;
        color: #ffffff;
        selection-background-color: #dc3545;
    }
    QPushButton {
        background-color: #dc3545;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
        margin-top: 10px;
    }
    QPushButton:hover {
        background-color: #bd2130;
    }
    QPushButton:pressed {
        background-color: #b02a37;
    }
"""

class PagoForm(QDialog):

    def __init__(self, parent=None, factura_id=None, pago=None):
        super().__init__(parent)

        self.pago = pago
        self.factura_id = factura_id

        self.setWindowTitle("Formulario de Pago")
        self.resize(400, 320)
        self.setStyleSheet(QSS_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_factura = QLabel(f"Factura ID: {self.factura_id}")
        self.lbl_factura.setObjectName("lbl_factura")
        main_layout.addWidget(self.lbl_factura)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # Monto
        self.monto_input = QDoubleSpinBox()
        self.monto_input.setMaximum(9999999.99)
        self.monto_input.setDecimals(2)
        self.monto_input.setPrefix("$ ")
        form_layout.addRow("Monto:", self.monto_input)

        # Método de Pago (Consistente con METODO_CHOICES)
        self.metodo_combo = QComboBox()
        self.metodo_combo.addItems(["efectivo", "transferencia", "tarjeta"])
        form_layout.addRow("Método:", self.metodo_combo)

        # Estado del Pago (CORREGIDO: 'procesando' en lugar de 'pendiente')
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["procesando", "completado", "fallido"])
        form_layout.addRow("Estado:", self.estado_combo)

        # Referencia
        self.referencia_input = QLineEdit()
        self.referencia_input.setPlaceholderText("Ej. Nº de transacción o recibo")
        form_layout.addRow("Referencia:", self.referencia_input)

        main_layout.addLayout(form_layout)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.accept)
        main_layout.addWidget(self.btn_guardar)

        self.setLayout(main_layout)

        if self.pago:
            self.monto_input.setValue(float(self.pago["monto"]))
            self.metodo_combo.setCurrentText(self.pago["metodo_pago"])
            self.estado_combo.setCurrentText(self.pago["estado"])
            self.referencia_input.setText(str(self.pago["referencia"] or ""))

    def obtener_datos(self):
        # Mapeo limpio para asegurar que no viajen strings vacías o nulos problemáticos
        ref_text = self.referencia_input.text().strip()
        
        datos = {
            "factura": self.factura_id,
            "monto": self.monto_input.value(),
            "metodo_pago": self.metodo_combo.currentText(),
            "estado": self.estado_combo.currentText(),
        }
        
        # Si hay texto en referencia se agrega, si no, se omite o manda vacío según soporte el Modelo
        if ref_text:
            datos["referencia"] = ref_text
        else:
            datos["referencia"] = ""
            
        return datos
    
    