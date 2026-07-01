# desktop/app/views/factura_dialog.py
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout
)

# --- CONFIGURACIÓN DE ESTILOS VISUALES PARA DIÁLOGO FACTURA ---
ESTILO_DIALOG_FACTURA = """
QDialog {
    background-color: #f5f6f8;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QLabel {
    color: #1e1e24;
    font-size: 13px;
}

QLabel#title_dialog {
    font-size: 16px;
    font-weight: bold;
    color: #1e1e24;
    border-bottom: 2px solid #e53935; /* Subrayado Rojo Admin */
    padding-bottom: 4px;
}

QLabel#total_dialog {
    font-size: 14px;
    font-weight: bold;
    color: #1e1e24;
}

QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace; /* Tipografía limpia para tickets */
    font-size: 12px;
    color: #2d3748;
}

QPushButton#btn_cerrar_dialog {
    background-color: #1e1e24; /* Negro corporativo */
    color: white;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 4px;
    padding: 8px 20px;
}
QPushButton#btn_cerrar_dialog:hover {
    background-color: #2d2d35;
}
"""

class FacturaDialog(QDialog):

    def __init__(self, factura, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Factura #{factura['id']}")
        self.resize(520, 460)
        
        # Seteo de la hoja de estilos unificada
        self.setStyleSheet(ESTILO_DIALOG_FACTURA)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Cabecera de diálogo
        title = QLabel(f"Factura #{factura['id']}  —  Pedido #{factura['pedido']}")
        title.setObjectName("title_dialog")
        layout.addWidget(title)

        status_text = "🟢 Pagada" if factura.get('pagada') else "🔴 Pendiente de Pago"
        status_label = QLabel(f"Estado del documento: {status_text}")
        status_label.setStyleSheet("font-weight: 600; color: #4a5568;")
        layout.addWidget(status_label)

        date_label = QLabel(f"Fecha de emisión: {factura.get('fecha_emision', '-')}")
        date_label.setStyleSheet("color: #718096;")
        layout.addWidget(date_label)

        total_label = QLabel(f"Monto Total Recaudado: ${factura.get('total', 0)}")
        total_label.setObjectName("total_dialog")
        layout.addWidget(total_label)

        details_label = QLabel("Items / Conceptos facturados:")
        details_label.setStyleSheet("font-weight: bold; color: #1e1e24;")
        layout.addWidget(details_label)

        # Procesamiento del desglose de productos formato Ticket
        text = ""
        for detalle in factura.get('detalles', []):
            producto = detalle.get('producto', {})
            nombre = producto.get('nombre', 'Producto')
            cantidad = detalle.get('cantidad', 0)
            precio_unitario = detalle.get('precio_unitario', 0)
            subtotal = detalle.get('subtotal', 0)
            text += f"• {nombre:<25} x{cantidad:<4} @ ${precio_unitario:<8} = ${subtotal}\n"

        detalles = QTextEdit()
        detalles.setReadOnly(True)
        detalles.setPlainText(text if text else "Sin detalles disponibles de artículos.")
        layout.addWidget(detalles)

        # Layout inferior de cierre
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Cerrar Visor")
        close_button.setObjectName("btn_cerrar_dialog")
        from PyQt6.QtCore import Qt # Asegurar importación del cursor
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)