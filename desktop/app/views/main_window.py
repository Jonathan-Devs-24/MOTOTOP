# desktop/app/views/main_window.py
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Componente personalizado
from components.sidebar_widget import SidebarWidget

# =========================
# PRODUCTOS
# =========================
from services.producto_service import ProductoService
from views.producto_view import ProductoView
from services.cliente_service import ClienteService
from services.pedido_service import PedidoService

# =========================
# VENDEDORES
# =========================
from services.vendedor_service import VendedorService
from services.zona_service import ZonaService
from services.user_service import UserService
from views.vendedor_view import VendedorView

# =========================
# CLIENTES
# =========================
from views.cliente_view import ClienteView

# =========================
# PEDIDOS
# =========================
from views.pedido_view import PedidoView

# =========================
# COMPRAS
# =========================
from services.compra_service import CompraService
from services.factura_service import FacturaService
from services.informe_service import InformeService
from views.compra_view import CompraView
from views.factura_view import FacturaView
from views.informe_view import InformeView

# =========================
# ENVIOS
# =========================
from services.envio_service import EnvioService
from views.envio_view import EnvioView

# =========================
# PAGOS / COBRANZAS
# =========================
from services.pago_service import PagoService
from views.pago_view import PagoView


class MainWindow(QWidget):

    def __init__(self, http_client):
        super().__init__()

        self.http = http_client

        # =========================
        # SERVICES
        # =========================
        self.producto_service = ProductoService(self.http)
        self.cliente_service = ClienteService(self.http)
        self.vendedor_service = VendedorService(self.http)
        self.pedido_service = PedidoService(self.http)
        self.compra_service = CompraService(self.http)
        self.factura_service = FacturaService(self.http)
        self.informe_service = InformeService(self.http)
        self.envio_service = EnvioService(self.http)
        self.pago_service = PagoService(self.http)

        # =========================
        # WINDOW
        # =========================
        self.setWindowTitle("MotoTop Desktop")
        self.resize(1200, 700)

        # =========================
        # MAIN LAYOUT
        # =========================
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # =========================
        # SIDEBAR (Instanciación del componente externo)
        # =========================
        self.sidebar_widget = SidebarWidget()
        
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(15, 25, 15, 25)
        sidebar_layout.setSpacing(8)
        
        #=============================
        # LOGO DE EMPRESA
        # ============================
        logo_label = QLabel()
        # Cambia "ruta/de/tu/logo.png" por la dirección real de tu imagen (ej. "assets/logo.png")
        pixmap = QPixmap("img\moto-top-sinfondo.png") 
        
        # Redimensionar la imagen para que se ajuste al ancho del menú (ej. 150px de ancho)
        # manteniendo la relación de aspecto y con escalado suave
        scaled_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Centrar el logo
        
        # Espaciado inferior opcional para que no quede pegado al primer botón
        logo_label.setStyleSheet("margin-bottom: 15px;") 
        
        sidebar_layout.addWidget(logo_label)
        # ---------------------------------------------------------
        

        btn_productos = QPushButton("Productos")
        btn_vendedores = QPushButton("Vendedores")
        btn_clientes = QPushButton("Clientes")
        btn_pedidos = QPushButton("Pedidos")
        btn_facturas = QPushButton("Facturas")
        btn_compras = QPushButton("Compras")
        btn_pagos = QPushButton("Cobranzas")
        btn_envios = QPushButton("Envíos")
        btn_informes = QPushButton("Informes")

        sidebar_layout.addWidget(btn_productos)
        sidebar_layout.addWidget(btn_vendedores)
        sidebar_layout.addWidget(btn_clientes)
        sidebar_layout.addWidget(btn_pedidos)
        sidebar_layout.addWidget(btn_facturas)
        sidebar_layout.addWidget(btn_compras)
        sidebar_layout.addWidget(btn_pagos)
        sidebar_layout.addWidget(btn_envios)
        sidebar_layout.addWidget(btn_informes)

        sidebar_layout.addStretch()

        # =========================
        # CONTENEDOR CENTRAL
        # =========================
        self.center_container = QWidget()
        self.center_container.setObjectName("main_container")
        
        center_layout = QVBoxLayout(self.center_container)
        center_layout.setContentsMargins(20, 20, 20, 20)

        self.stack = QStackedWidget()
        center_layout.addWidget(self.stack)

        # =========================
        # VISTAS
        # =========================
        self.view_productos = ProductoView(self.producto_service)
        self.view_vendedores = VendedorView(self.http)
        self.view_clientes = ClienteView(self.http)
        self.view_pedidos = PedidoView(
            self.pedido_service,
            self.cliente_service,
            self.vendedor_service,
            self.producto_service
        )
        self.view_facturas = FacturaView(self.factura_service)
        self.view_compras = CompraView(self.compra_service)
        self.view_pagos = PagoView(factura=None, pago_service=self.pago_service)
        self.view_envios = EnvioView(self.envio_service)
        self.view_informes = InformeView(self.informe_service)

        # =========================
        # AGREGAR AL STACK
        # =========================
        self.stack.addWidget(self.view_productos)
        self.stack.addWidget(self.view_vendedores)
        self.stack.addWidget(self.view_clientes)
        self.stack.addWidget(self.view_pedidos)
        self.stack.addWidget(self.view_facturas)
        self.stack.addWidget(self.view_compras)
        self.stack.addWidget(self.view_pagos)
        self.stack.addWidget(self.view_envios)
        self.stack.addWidget(self.view_informes)

        # =========================
        # CONEXIONES
        # =========================
        btn_productos.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_productos))
        btn_vendedores.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_vendedores))
        btn_clientes.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_clientes))
        btn_pedidos.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_pedidos))
        btn_facturas.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_facturas))
        btn_compras.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_compras))
        btn_pagos.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_pagos))
        btn_envios.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_envios))
        btn_informes.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_informes))

        # =========================
        # LAYOUT FINAL
        # =========================
        main_layout.addWidget(self.sidebar_widget, 1)
        main_layout.addWidget(self.center_container, 4)

        self.setLayout(main_layout)
        self.apply_styles()
        
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#main_container {
                background-color: #c8cbd0;
            }

            QWidget#sidebar {
                background-color: #1e1e24;
                border-right: 1px solid #3a3a4a;
            }

            QWidget#sidebar QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 12px 15px;
                text-align: left;
                font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
            }

            QWidget#sidebar QPushButton:hover {
                background-color: #2a2a35;
                color: #e53935;
            }

            QWidget#sidebar QPushButton:pressed {
                background-color: #e53935;
                color: #ffffff;
            }
        """)