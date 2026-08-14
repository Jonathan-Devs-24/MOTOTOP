# C:\Users\jonat\MotoTop\desktop\app\views\pedido_view.py
import traceback
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QMessageBox
)
from PyQt6.QtCore import Qt
from views.pedido_card import PedidoCard
from views.pedido_form import PedidoForm


ESTILO_ADMIN_PEDIDOS = """
    QWidget#main_view {
        background-color: #f5f6f8;                 /* Gris claro moderno de fondo general */
        font-family: 'Segoe UI', Arial, sans-serif;
    }

    /* Área de Scroll donde viven las tarjetas */
    QScrollArea {
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        background-color: #ffffff;
    }

    QWidget#scroll_container {
        background-color: #ffffff;                 /* Blanco limpio para el contenedor interno */
    }

    /* Botón Nuevo Pedido (Rojo Administrativo) */
    QPushButton#btn_nuevo_pedido {
        background-color: #e53935;                 /* Rojo destacado */
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 13px;
    }

    QPushButton#btn_nuevo_pedido:hover {
        background-color: #d32f2f;                 /* Rojo más oscuro al pasar el mouse */
    }

    QPushButton#btn_nuevo_pedido:pressed {
        background-color: #b71c1c;                 /* Rojo profundo al hacer clic */
    }

    /* Botón Refrescar (Azul para contrastar) */
    QPushButton#btn_refrescar {
        background-color: #1976d2;                 /* Azul profesional */
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 13px;
    }

    QPushButton#btn_refrescar:hover {
        background-color: #1565c0;                 /* Azul más oscuro al pasar el mouse */
    }

    QPushButton#btn_refrescar:pressed {
        background-color: #0d47a1;                 /* Azul profundo al hacer clic */
    }

    /* Botón Limpiar (Naranja para advertencia) */
    QPushButton#btn_limpiar {
        background-color: #f57c00;                 /* Naranja profesional */
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 13px;
    }

    QPushButton#btn_limpiar:hover {
        background-color: #e65100;                 /* Naranja más oscuro al pasar el mouse */
    }

    QPushButton#btn_limpiar:pressed {
        background-color: #bf360c;                 /* Naranja profundo al hacer clic */
    }

    /* Contenedor de botones horizontales */
    QWidget#botones_container {
        background-color: #f5f6f8;
    }
"""


class PedidoView(QWidget):

    def __init__(self, pedido_service, cliente_service, vendedor_service, producto_service):
        super().__init__()

        self.service = pedido_service
        self.cliente_service = cliente_service
        self.vendedor_service = vendedor_service
        self.producto_service = producto_service

        # ID para controlar el fondo general desde el QSS
        self.setObjectName("main_view")
        self.setStyleSheet(ESTILO_ADMIN_PEDIDOS)

        # Layout principal con mejor espaciado (padding)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Contenedor de botones horizontales
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)
        
        # Botón Nuevo Pedido configurado con su ID de estilo
        self.btn_new = QPushButton("Nuevo pedido")
        self.btn_new.setObjectName("btn_nuevo_pedido")
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.clicked.connect(self.open_form)
        botones_layout.addWidget(self.btn_new)

        # Botón Refrescar
        self.btn_refrescar = QPushButton("Refrescar")
        self.btn_refrescar.setObjectName("btn_refrescar")
        self.btn_refrescar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refrescar.clicked.connect(self.refresh_pedidos)
        botones_layout.addWidget(self.btn_refrescar)

        # Botón Limpiar Pantalla
        self.btn_limpiar = QPushButton("Limpiar pantalla")
        self.btn_limpiar.setObjectName("btn_limpiar")
        self.btn_limpiar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_limpiar.clicked.connect(self.limpiar_pantalla)
        botones_layout.addWidget(self.btn_limpiar)
        
        # Agregar stretch para que los botones se alineen a la izquierda
        botones_layout.addStretch()
        
        layout.addLayout(botones_layout)

        # Configuración del área de Scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        # Contenedor interno del scroll
        self.container = QWidget()
        self.container.setObjectName("scroll_container")
        
        # Layout de la lista (Separación sutil de 10px entre cada tarjeta de pedido)
        self.list_layout = QVBoxLayout()
        self.list_layout.setContentsMargins(10, 10, 10, 10)
        self.list_layout.setSpacing(10) 
        
        self.container.setLayout(self.list_layout)
        self.scroll.setWidget(self.container)

        layout.addWidget(self.scroll)
        self.setLayout(layout)


        self.load_data()
        
    def load_data(self, nuevo_pedido=None):
        try:
            # 1. Limpieza segura de la UI existente
            while self.list_layout.count():
                item = self.list_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    del item 

            # 2. Consumo del servicio
            pedidos = self.service.listar()
            
            # Si el servicio devuelve un entero (ej: código de error) o None, abortamos preventivamente
            if isinstance(pedidos, int) or pedidos is None:
                raise TypeError("La API no devolvió una respuesta válida.")

            pedidos_data = pedidos.get("results", pedidos)

            # Si el resultado no es una lista o es un diccionario vacío, normalizamos
            if not isinstance(pedidos_data, list):
                pedidos_data = []

            # 3. Validación de seguridad para nuevo_pedido
            # Si nuevo_pedido es un entero (ID), evitamos que rompa la validación .get()
            if nuevo_pedido is not None and isinstance(nuevo_pedido, dict):
                pedido_id = nuevo_pedido.get("id")
                if pedido_id is not None and not any(isinstance(p, dict) and p.get("id") == pedido_id for p in pedidos_data):
                    pedidos_data.insert(0, nuevo_pedido)

            # 4. Renderizado de Tarjetas con control de tipo
            for pedido in pedidos_data:
                # Nos aseguramos de que cada pedido sea efectivamente un diccionario antes de crear la Card
                if isinstance(pedido, dict):
                    card = PedidoCard(
                        pedido,
                        self.service,
                        self.load_data
                    )
                    self.list_layout.addWidget(card)

            self.list_layout.addStretch()

        except Exception as e:
            error_msg = str(e)
            print(f"Error cargando pedidos: {error_msg}")
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los pedidos: {error_msg}")
     
     
    def open_form(self):
        self.form = PedidoForm(
            self.service,
            self.cliente_service,
            self.vendedor_service,
            self.producto_service,
            self.load_data
        )
        self.form.show()

    def refresh_pedidos(self):
        """Recarga la lista de pedidos desde el servidor"""
        self.load_data()

    def limpiar_pantalla(self):
        """Limpia todos los pedidos de la pantalla"""
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                del item
        self.list_layout.addStretch()

