# desktop/app/views/main_window.py

# Una vez loguedo, esta es la ventana principal que se 
# muestra. Contiene un sidebar con botones para cada 
# módulo y un área central que cambia según el módulo 
# seleccionado.

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel
)

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
from views.compra_view import CompraView
from views.factura_view import FacturaView


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

        self.producto_service = ProductoService(
            self.http
        )

        self.cliente_service = ClienteService(
            self.http
        )

        self.vendedor_service = VendedorService(
            self.http
        )

        self.pedido_service = PedidoService(
            self.http
        )

        self.compra_service = CompraService(
            self.http
        )

        self.factura_service = FacturaService(
            self.http
        )
        
        self.envio_service = EnvioService(
            self.http
        )
        
        self.pago_service = PagoService(
            self.http
        )

        # =========================
        # WINDOW
        # =========================

        self.setWindowTitle("MotoTop Desktop")

        self.resize(1200, 700)

        # =========================
        # MAIN LAYOUT
        # =========================

        main_layout = QHBoxLayout()

        # =========================
        # SIDEBAR
        # =========================

        sidebar = QVBoxLayout()

        btn_productos = QPushButton("Productos")
        btn_vendedores = QPushButton("Vendedores")
        btn_clientes = QPushButton("Clientes")
        btn_pedidos = QPushButton("Pedidos")
        btn_facturas = QPushButton("Facturas")
        btn_compras = QPushButton("Compras")
        btn_pagos = QPushButton("Cobranzas")
        btn_envios = QPushButton("Envíos")
        btn_informes = QPushButton("Informes")

        sidebar.addWidget(btn_productos)
        sidebar.addWidget(btn_vendedores)
        sidebar.addWidget(btn_clientes)
        sidebar.addWidget(btn_pedidos)
        sidebar.addWidget(btn_facturas)
        sidebar.addWidget(btn_compras)
        sidebar.addWidget(btn_pagos)
        sidebar.addWidget(btn_envios)
        sidebar.addWidget(btn_informes)

        sidebar.addStretch()

        # =========================
        # STACK
        # =========================

        self.stack = QStackedWidget()

        # =========================
        # VISTAS
        # =========================

        self.view_productos = ProductoView(
            self.producto_service
        )

        self.view_vendedores = VendedorView(
            self.http
        )

        self.view_clientes = ClienteView(
            self.http
        )

        self.view_pedidos = PedidoView(
            self.pedido_service,
            self.cliente_service,
            self.vendedor_service,
            self.producto_service
        )

        self.view_facturas = FacturaView(
            self.factura_service
        )

        self.view_compras = CompraView(
            self.compra_service
        )

        self.view_pagos = PagoView(
            factura=None,
            pago_service=self.pago_service
        )

        self.view_envios = EnvioView(
            self.envio_service
        )

        self.view_informes = QLabel(
            "Módulo Informes"
        )

        # =========================
        # AGREGAR AL STACK
        # =========================

        self.stack.addWidget(
            self.view_productos
        )

        self.stack.addWidget(
            self.view_vendedores
        )

        self.stack.addWidget(
            self.view_clientes
        )

        self.stack.addWidget(
            self.view_pedidos
        )

        self.stack.addWidget(
            self.view_facturas
        )

        self.stack.addWidget(
            self.view_compras
        )

        self.stack.addWidget(
            self.view_pagos
        )

        self.stack.addWidget(
            self.view_envios
        )

        self.stack.addWidget(
            self.view_informes
        )

        
        # =========================
        # CONEXIONES
        # =========================

        btn_productos.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.view_productos
            )
        )

        btn_vendedores.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.view_vendedores
            )
        )

        btn_clientes.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.view_clientes
            )
        )

        btn_pedidos.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.view_pedidos
            )
        )

        btn_facturas.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.view_facturas
            )
        )

        btn_compras.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.view_compras
            )
        )

        btn_pagos.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.view_pagos
            )
        )

        btn_envios.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.view_envios
            )
        )

        btn_informes.clicked.connect(
            lambda: self.stack.setCurrentWidget(
                self.view_informes
            )
        )

        # =========================
        # LAYOUT FINAL
        # =========================

        main_layout.addLayout(sidebar, 1)

        main_layout.addWidget(self.stack, 4)

        self.setLayout(main_layout)
        
        