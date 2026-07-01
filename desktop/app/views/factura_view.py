from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QMessageBox,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# --- CONFIGURACIÓN DE ESTILOS VISUALES PARA FACTURAS ---
ESTILO_VIEW_FACTURA = """
QWidget#main_factura_view {
    background-color: #f5f6f8;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QScrollArea {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background-color: #ffffff;
}

QWidget#scroll_container {
    background-color: #ffffff;
}

/* Botón superior de Recargar (Negro Corporativo) */
QPushButton#btn_recargar {
    background-color: #1e1e24;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton#btn_recargar:hover {
    background-color: #2d2d35;
}

/* Tarjeta contenedora física de la Factura */
QWidget#contenedor_factura_card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
}

QLabel {
    color: #1e1e24;
    font-size: 13px;
}

QLabel#title_factura {
    font-size: 14px;
    font-weight: bold;
    color: #1e1e24;
}

QLabel#total_factura {
    font-size: 14px;
    font-weight: bold;
    color: #1e1e24;
}

QLabel#meta_info_factura {
    color: #718096;
    font-size: 12px;
}

/* Badges Condicionales de Pago */
QLabel#badge_pagada {
    background-color: #dcfce7;
    color: #15803d;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 11px;
}

QLabel#badge_pendiente {
    background-color: #fee2e2;
    color: #b91c1c;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 11px;
}

/* Botón interno de la Tarjeta (Rojo Administrativo) */
QWidget#contenedor_factura_card QPushButton {
    background-color: #e53935;
    color: white;
    font-weight: bold;
    font-size: 12px;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
}
QWidget#contenedor_factura_card QPushButton:hover {
    background-color: #d32f2f;
}
"""


class FacturaView(QWidget):

    def __init__(self, factura_service):
        super().__init__()

        self.service = factura_service
        self.setWindowTitle("Facturas")
        self.resize(550, 700)
        
        # Enlace de estilos base
        self.setObjectName("main_factura_view")
        self.setStyleSheet(ESTILO_VIEW_FACTURA)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        top_bar = QHBoxLayout()
        self.btn_refresh = QPushButton("Recargar")
        self.btn_refresh.setObjectName("btn_recargar")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.load_data)
        
        top_bar.addWidget(self.btn_refresh)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.container.setObjectName("scroll_container")
        
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(12) 
        self.list_layout.setContentsMargins(10, 10, 10, 10)
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
                else:
                    del item 

            facturas = self.service.listar()
            facturas_data = facturas.get("results", facturas)

            if not facturas_data:
                empty_label = QLabel("No hay facturas generadas.")
                empty_label.setObjectName("meta_info_factura")
                empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.list_layout.addWidget(empty_label)
            else:
                for factura in facturas_data:
                    self.list_layout.addWidget(self.build_card(factura))

            self.list_layout.addStretch()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las facturas: {e}")

    def build_card(self, factura):
        card = QWidget()
        card.setObjectName("contenedor_factura_card")
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)

        # Línea Superior: Título y Estado Badge
        header_layout = QHBoxLayout()
        title = QLabel(f"Factura #{factura['id']} — Pedido #{factura['pedido']}")
        title.setObjectName("title_factura")
        
        is_pagada = factura.get("pagada", False)
        status_label = QLabel(" Pagada " if is_pagada else " Pendiente ")
        status_label.setObjectName("badge_pagada" if is_pagada else "badge_pendiente")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(status_label)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)

        # Línea Central: Metadatos y Total
        info_layout = QHBoxLayout()
        date_label = QLabel(f"Fecha de emisión: {factura.get('fecha_emision', '-')}")
        date_label.setObjectName("meta_info_factura")
        
        total_label = QLabel(f"Total: ${factura.get('total', 0)}")
        total_label.setObjectName("total_factura")
        
        info_layout.addWidget(date_label)
        info_layout.addStretch()
        info_layout.addWidget(total_label)
        card_layout.addLayout(info_layout)

        # Desglose de Productos
        if factura.get('detalles'):
            prod_container = QWidget()
            prod_container.setStyleSheet("background-color: #f8f9fa; border-radius: 4px; padding: 5px;")
            prod_layout = QVBoxLayout(prod_container)
            prod_layout.setSpacing(4)
            prod_layout.setContentsMargins(8, 8, 8, 8)

            for detalle in factura['detalles']:
                product = detalle.get('producto', {})
                product_name = product.get('nombre', 'Producto')
                cantidad = detalle.get('cantidad', 0)
                subtotal = detalle.get('subtotal', 0)
                
                detail_line = QLabel(f"• {product_name} x{cantidad}  —  Subtotal: ${subtotal}")
                detail_line.setObjectName("meta_info_factura")
                prod_layout.addWidget(detail_line)
                
            card_layout.addWidget(prod_container)

        # Línea Inferior: Acciones de Caja
        actions_layout = QHBoxLayout()
        btn_pagos = QPushButton("Administrar Pagos")
        btn_pagos.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pagos.clicked.connect(lambda _, f=factura: self.abrir_pagos(f))
        
        actions_layout.addWidget(btn_pagos)
        actions_layout.addStretch()
        card_layout.addLayout(actions_layout)
        
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