# desktop/app/views/main_window.py

# Una vez loguedo, esta es la ventana principal que se 
# muestra. Contiene un sidebar con botones para cada 
# módulo y un área central que cambia según el módulo 
# seleccionado.

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel
)

from services.producto_service import ProductoService
from views.producto_view import ProductoView


class MainWindow(QWidget):

    def __init__(self, http_client):
        super().__init__()

        self.http = http_client
        
        producto_service = ProductoService(self.http)

        self.setWindowTitle("MotoTop Desktop")
        self.resize(1000, 600)

        # Layout principal
        main_layout = QHBoxLayout()

        # Sidebar
        sidebar = QVBoxLayout()

        btn_productos = QPushButton("Productos")
        btn_clientes = QPushButton("Clientes")
        btn_pedidos = QPushButton("Pedidos")
        btn_compras = QPushButton("Compras")
        btn_pagos = QPushButton("Cobranzas")
        btn_envios = QPushButton("Envíos")
        btn_informes = QPushButton("Informes")

        sidebar.addWidget(btn_productos)
        sidebar.addWidget(btn_clientes)
        sidebar.addWidget(btn_pedidos)
        sidebar.addWidget(btn_compras)
        sidebar.addWidget(btn_pagos)
        sidebar.addWidget(btn_envios)
        sidebar.addWidget(btn_informes)

        # Área central
        self.stack = QStackedWidget()

        # Vistas placeholder (después se reemplazan)
        self.view_productos = ProductoView(producto_service)
        self.view_clientes = QLabel("Módulo Clientes")
        self.view_pedidos = QLabel("Módulo Pedidos")
        self.view_compras = QLabel("Módulo Compras")
        self.view_pagos = QLabel("Módulo Cobranzas")
        self.view_envios = QLabel("Módulo Envíos")
        self.view_informes = QLabel("Módulo Informes")

        self.stack.addWidget(self.view_productos)
        self.stack.addWidget(self.view_clientes)
        self.stack.addWidget(self.view_pedidos)
        self.stack.addWidget(self.view_compras)
        self.stack.addWidget(self.view_pagos)
        self.stack.addWidget(self.view_envios)
        self.stack.addWidget(self.view_informes)

        # Conexiones
        btn_productos.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_productos))
        btn_clientes.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_clientes))
        btn_pedidos.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_pedidos))
        btn_compras.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_compras))
        btn_pagos.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_pagos))
        btn_envios.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_envios))
        btn_informes.clicked.connect(lambda: self.stack.setCurrentWidget(self.view_informes))

        main_layout.addLayout(sidebar, 1)
        main_layout.addWidget(self.stack, 4)

        self.setLayout(main_layout)