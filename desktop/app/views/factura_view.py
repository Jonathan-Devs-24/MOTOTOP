# desktop/app/views/factura_view.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QMessageBox,
    QHBoxLayout,
)
from PyQt6.QtGui import QFont


class FacturaView(QWidget):

    def __init__(self, factura_service):
        super().__init__()

        self.service = factura_service

        self.setWindowTitle("Facturas")

        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        self.btn_refresh = QPushButton("Recargar")
        self.btn_refresh.setStyleSheet("background-color: #757575; color: white; border: none; padding: 8px 16px; border-radius: 4px;")
        self.btn_refresh.clicked.connect(self.load_data)
        

        top_bar.addWidget(self.btn_refresh)
        top_bar.addStretch()

        layout.addLayout(top_bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(10)
        self.list_layout.setContentsMargins(5, 5, 5, 5)
        self.container.setLayout(self.list_layout)

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        try:
            while self.list_layout.count():
                item = self.list_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            facturas = self.service.listar()
            facturas_data = facturas.get("results", facturas)

            if not facturas_data:
                empty_label = QLabel("No hay facturas generadas.")
                empty_label.setStyleSheet("color: #666; font-size: 11pt;")
                self.list_layout.addWidget(empty_label)
            else:
                for factura in facturas_data:
                    self.list_layout.addWidget(self.build_card(factura))

            self.list_layout.addStretch()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las facturas: {e}")

    def build_card(self, factura):
        card = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(6)
        card.setLayout(card_layout)
        card.setStyleSheet(
            "background-color: white; border: 1px solid #ddd; border-radius: 8px;"
        )

        title = QLabel(f"Factura #{factura['id']} - Pedido #{factura['pedido']}")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        card_layout.addWidget(title)

        status_text = "Pagada" if factura.get("pagada") else "Pendiente"
        status_label = QLabel(f"Estado: {status_text}")
        status_label.setStyleSheet("color: #555;")
        card_layout.addWidget(status_label)

        date_label = QLabel(f"Fecha: {factura.get('fecha_emision', '-')}")
        date_label.setStyleSheet("color: #555;")
        card_layout.addWidget(date_label)

        total_label = QLabel(f"Total: ${factura.get('total', 0)}")
        total_label.setStyleSheet("color: #333; font-weight: bold;")
        card_layout.addWidget(total_label)

        if factura.get('detalles'):
            details_label = QLabel("Productos:")
            details_label.setStyleSheet("color: #444; font-weight: bold;")
            card_layout.addWidget(details_label)

            for detalle in factura['detalles']:
                product = detalle.get('producto', {})
                product_name = product.get('nombre', 'Producto')
                cantidad = detalle.get('cantidad', 0)
                subtotal = detalle.get('subtotal', 0)
                detail_line = QLabel(f"- {product_name} x{cantidad} / ${subtotal}")
                detail_line.setStyleSheet("color: #555; font-size: 9pt;")
                card_layout.addWidget(detail_line)
                
                
        btn_pagos = QPushButton("Pagos")
        btn_pagos.clicked.connect(
            lambda _, f=factura: self.abrir_pagos(f)
        )
        card_layout.addWidget(btn_pagos)
        
        
        return card
    
    
    
    def abrir_pagos(self, factura):
        from services.pago_service import PagoService
        from views.pago_view import PagoView

        pago_service = PagoService(self.service.http)

        self.pago_view = PagoView(
            factura=factura,
            pago_service=pago_service
        )
        self.pago_view.show()
