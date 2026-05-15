# desktop/app/views/factura_dialog.py

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout
)


class FacturaDialog(QDialog):

    def __init__(self, factura, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Factura #{factura['id']}")
        self.resize(520, 420)

        layout = QVBoxLayout()

        title = QLabel(f"Factura #{factura['id']} - Pedido #{factura['pedido']}")
        title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        layout.addWidget(title)

        status_text = "Pagada" if factura.get('pagada') else "Pendiente"
        status_label = QLabel(f"Estado: {status_text}")
        layout.addWidget(status_label)

        date_label = QLabel(f"Fecha: {factura.get('fecha_emision', '-')}")
        layout.addWidget(date_label)

        total_label = QLabel(f"Total: ${factura.get('total', 0)}")
        total_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(total_label)

        details_label = QLabel("Detalles:")
        details_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(details_label)

        text = ""
        for detalle in factura.get('detalles', []):
            producto = detalle.get('producto', {})
            nombre = producto.get('nombre', 'Producto')
            cantidad = detalle.get('cantidad', 0)
            precio_unitario = detalle.get('precio_unitario', 0)
            subtotal = detalle.get('subtotal', 0)
            text += f"{nombre} x{cantidad} @ ${precio_unitario} = ${subtotal}\n"

        detalles = QTextEdit()
        detalles.setReadOnly(True)
        detalles.setPlainText(text if text else "Sin detalles disponibles.")
        detalles.setMinimumHeight(180)
        layout.addWidget(detalles)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
