# C:\Users\jonat\MotoTop\desktop\app\views\pedido_card.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from views.factura_dialog import FacturaDialog


ESTILO_CARD_PEDIDO = """
QWidget#contenedor_card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
}

QLabel {
    color: #1e1e24;
    font-size: 13px;
}

QLabel#id_pedido {
    color: #1e1e24;
    font-size: 14px;
    font-weight: bold;
}

QLabel#cliente_pedido {
    color: #2d3748;
    font-weight: 600;
}

QLabel#meta_info {
    color: #718096;
    font-size: 12px;
}

QLabel#total_pedido {
    color: #1e1e24;
    font-size: 14px;
    font-weight: bold;
}

/* Badges de Estado */
QLabel#badge_pendiente {
    background-color: #fef3c7;
    color: #d97706;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 11px;
}

QLabel#badge_confirmado {
    background-color: #dcfce7;
    color: #15803d;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 11px;
}

QLabel#badge_cancelado {
    background-color: #fee2e2;
    color: #b91c1c;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 11px;
}

/* Botones de acción dentro de la card (Aislados del QMessageBox) */
QWidget#contenedor_card QPushButton {
    font-weight: bold;
    font-size: 12px;
    border-radius: 4px;
    padding: 6px 14px;
    color: white;
}

QWidget#contenedor_card QPushButton#btn_confirmar {
    background-color: #15803d;
}
QWidget#contenedor_card QPushButton#btn_confirmar:hover {
    background-color: #166534;
}

QWidget#contenedor_card QPushButton#btn_cancelar {
    background-color: #e53935;  /* Rojo Admin */
}
QWidget#contenedor_card QPushButton#btn_cancelar:hover {
    background-color: #b71c1c;
}

QWidget#contenedor_card QPushButton#btn_factura {
    background-color: #1e1e24;  /* Negro corporativo */
}
QWidget#contenedor_card QPushButton#btn_factura:hover {
    background-color: #2d2d35;
}
"""

class PedidoCard(QWidget):

    def __init__(self, pedido, service, refresh_callback):
        super().__init__()

        self.pedido = pedido
        self.service = service
        self.refresh = refresh_callback

        # 1. Aplicamos la hoja de estilos unificada
        self.setStyleSheet(ESTILO_CARD_PEDIDO)

        # 2. Layout Raíz (Único layout asignado al componente base de la tarjeta)
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 4, 0, 4) # Margen sutil entre tarjetas
        self.setLayout(root_layout)

        # 3. Marco físico contenedor de la tarjeta
        self.card_frame = QWidget()
        self.card_frame.setObjectName("contenedor_card")
        
        # El layout interno donde se meten todos los datos reales
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)

        # --- PRIMERA LÍNEA: ID, CLIENTE, ESTADO ---
        header_layout = QHBoxLayout()
        
        id_label = QLabel(f"Pedido #{pedido['id']}")
        id_label.setObjectName("id_pedido")
        
        # CONTROL DE SEGURIDAD: Validar si 'cliente' viene como diccionario o como ID entero
        cliente = pedido.get('cliente')
        if isinstance(cliente, dict):
            nombre_cliente = f"{cliente.get('nombre', '')} {cliente.get('apellido','')}".strip()
        elif isinstance(cliente, int) or (isinstance(cliente, str) and cliente.isdigit()):
            nombre_cliente = f"Cliente ID: {cliente} (Refrescar para ver)"
        else:
            nombre_cliente = "Cliente no especificado"

        cliente_label = QLabel(nombre_cliente)
        cliente_label.setObjectName("cliente_pedido")
        
        # CONTROL DE SEGURIDAD: Evitar KeyError si 'estado' no viene en la respuesta del POST
        estado_raw = pedido.get('estado', 'pendiente')
        estado = estado_raw.lower() if estado_raw else 'pendiente'
        
        estado_label = QLabel(f" {estado.capitalize()} ")
        estado_label.setObjectName(f"badge_{estado}")
        estado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(id_label)
        header_layout.addWidget(cliente_label)
        header_layout.addWidget(estado_label)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        
        # --- SEGUNDA LÍNEA: VENDEDOR, ORIGEN, FECHA, TOTAL ---
        details_layout = QHBoxLayout()
        
        # CONTROL DE SEGURIDAD: Vendedor defensivo
        vendedor = pedido.get('vendedor')
        if isinstance(vendedor, dict):
            vendedor_text = f"{vendedor.get('nombre', '')} {vendedor.get('apellido','')}".strip()
        elif vendedor is not None:
            vendedor_text = f"Vendedor ID: {vendedor}"
        else:
            vendedor_text = "Sin vendedor"

        vendedor_label = QLabel(f"Vend: {vendedor_text}")
        vendedor_label.setObjectName("meta_info")

        origen_label = QLabel(f"Origen: {pedido.get('origen', 'N/A')}")
        origen_label.setObjectName("meta_info")
        
        fecha_label = QLabel(f"{pedido.get('fecha_pedido', '')}")
        fecha_label.setObjectName("meta_info")
        
        total_label = QLabel(f"Total: ${pedido.get('total', '0.00')}")
        total_label.setObjectName("total_pedido")

        details_layout.addWidget(vendedor_label)
        details_layout.addWidget(origen_label)
        details_layout.addWidget(fecha_label)
        details_layout.addStretch()
        details_layout.addWidget(total_label)
        card_layout.addLayout(details_layout)

        # --- TERCERA LÍNEA: DETALLE DE PRODUCTOS ---
        if pedido.get('detalles'):
            productos_layout = QHBoxLayout()
            productos_text = []
            for d in pedido['detalles']:
                producto = d.get('producto')
                if isinstance(producto, dict):
                    productos_text.append(f"{producto.get('nombre', 'Producto')} x{d.get('cantidad', 1)}")
                else:
                    productos_text.append(f"Prod ID: {producto} x{d.get('cantidad', 1)}")
            
            productos_label = QLabel(" • ".join(productos_text))
            productos_label.setObjectName("meta_info")
            productos_label.setWordWrap(True)
            productos_layout.addWidget(productos_label)
            card_layout.addLayout(productos_layout)

        # --- CUARTA LÍNEA: ACCIONES DISPONIBLES ---
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        if estado == 'pendiente':
            btn_confirmar = QPushButton("Confirmar")
            btn_confirmar.setObjectName("btn_confirmar")
            btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_confirmar.clicked.connect(self.confirmar_pedido)

            btn_cancelar = QPushButton("Cancelar")
            btn_cancelar.setObjectName("btn_cancelar")
            btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_cancelar.clicked.connect(self.cancelar_pedido)

            actions_layout.addWidget(btn_confirmar)
            actions_layout.addWidget(btn_cancelar)
            actions_layout.addStretch()
            card_layout.addLayout(actions_layout)

        elif estado == 'confirmado':
            if not pedido.get('facturada', False):
                btn_factura = QPushButton("Generar factura")
                btn_factura.setObjectName("btn_factura")
                btn_factura.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_factura.clicked.connect(self.generar_factura)
                actions_layout.addWidget(btn_factura)
            else:
                btn_ver_factura = QPushButton("Ver factura")
                btn_ver_factura.setObjectName("btn_factura")
                btn_ver_factura.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_ver_factura.clicked.connect(self.ver_factura)
                actions_layout.addWidget(btn_ver_factura)
            
            actions_layout.addStretch()
            card_layout.addLayout(actions_layout)

        # 4. Inyección final: Metemos la tarjeta física dentro del layout raíz
        root_layout.addWidget(self.card_frame)
    
    # --- MÉTODOS OPERATIVOS ---
    # --- REEMPLAZAR MÉTODO COMPLETADO EN pedido_card.py ---
    def confirmar_pedido(self):
        # 1. Preguntar primero (Bloquea la ejecución hasta que el usuario elija)
        generar = QMessageBox.question(
            self,
            "Confirmar pedido",
            "¿Está seguro de que desea confirmar este pedido?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        # 2. Si la respuesta NO es "Yes", frenamos la ejecución inmediatamente
        if generar != QMessageBox.StandardButton.Yes:
            return

        # 3. Solo si aceptó, procedemos con la petición al servidor Django
        try:
            self.service.confirmar(self.pedido['id'])

            # Ofrecer la factura tras el éxito de la confirmación
            facturar = QMessageBox.question(
                self,
                "Generar factura",
                "Pedido confirmado de forma segura. ¿Desea generar la factura ahora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if facturar == QMessageBox.StandardButton.Yes:
                self.generar_factura()
            else:
                QMessageBox.information(
                    self,
                    "Pedido confirmado",
                    "El pedido se confirmó sin generar factura."
                )

            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo confirmar el pedido: {e}")
            
            
    def cancelar_pedido(self):
        confirm = QMessageBox.question(
            self,
            "Cancelar pedido",
            "¿Está seguro de que desea cancelar este pedido?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            self.service.cancelar(self.pedido['id'])
            QMessageBox.information(
                self,
                "Pedido cancelado",
                "El pedido fue cancelado correctamente."
            )
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cancelar el pedido: {e}")

    def generar_factura(self):
        try:
            self.service.generar_factura(self.pedido['id'])
            QMessageBox.information(
                self,
                "Factura creada",
                "La factura se generó correctamente."
            )
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar la factura: {e}")

    def ver_factura(self):
        try:
            factura = self.service.obtener_factura(self.pedido['id'])
            dialog = FacturaDialog(factura, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la factura: {e}")
            