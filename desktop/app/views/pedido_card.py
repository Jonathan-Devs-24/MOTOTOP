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


class PedidoCard(QWidget):

    def __init__(self, pedido, service, refresh_callback):
        super().__init__()

        self.pedido = pedido
        self.service = service
        self.refresh = refresh_callback

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Primera línea: ID, Cliente, Estado
        header_layout = QHBoxLayout()
        
        id_label = QLabel(f"Pedido #{pedido['id']}")
        id_font = QFont()
        id_font.setBold(True)
        id_label.setFont(id_font)
        id_label.setMinimumWidth(80)
        
        cliente = pedido['cliente']
        cliente_label = QLabel(f"{cliente['nombre']} {cliente.get('apellido','')}")
        cliente_label.setMinimumWidth(200)
        
        estado = pedido['estado'].capitalize()
        estado_label = QLabel(f"[{estado}]")
        estado_font = QFont()
        estado_font.setBold(True)
        estado_label.setFont(estado_font)
        estado_label.setMinimumWidth(100)
        
        header_layout.addWidget(id_label)
        header_layout.addWidget(cliente_label)
        header_layout.addWidget(estado_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)

        # Segunda línea: Vendedor, Origen, Total, Fecha
        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(20, 0, 0, 0)
        
        vendedor = pedido.get('vendedor')
        vendedor_text = f"{vendedor['nombre']} {vendedor.get('apellido','')}" if vendedor else "Sin vendedor"
        vendedor_label = QLabel(f"Vend: {vendedor_text}")
        vendedor_label.setMinimumWidth(150)
        vendedor_label.setStyleSheet("color: #666;")
        
        origen_label = QLabel(f"Origen: {pedido['origen']}")
        origen_label.setMinimumWidth(100)
        origen_label.setStyleSheet("color: #666;")
        
        total_label = QLabel(f"Total: ${pedido['total']}")
        total_font = QFont()
        total_font.setBold(True)
        total_label.setFont(total_font)
        total_label.setMinimumWidth(100)
        
        fecha_label = QLabel(f"{pedido['fecha_pedido']}")
        fecha_label.setStyleSheet("color: #999;")
        
        details_layout.addWidget(vendedor_label)
        details_layout.addWidget(origen_label)
        details_layout.addWidget(total_label)
        details_layout.addWidget(fecha_label)
        details_layout.addStretch()
        
        main_layout.addLayout(details_layout)

        # Productos (si existen)
        if pedido.get('detalles'):
            productos_layout = QHBoxLayout()
            productos_layout.setContentsMargins(20, 5, 0, 0)
            
            productos_text = []
            for d in pedido['detalles']:
                producto = d.get('producto')
                productos_text.append(f"{producto['nombre']} x{d['cantidad']}")
            
            productos_label = QLabel(" | ".join(productos_text))
            productos_label.setStyleSheet("color: #555; font-size: 9pt;")
            productos_label.setWordWrap(True)
            productos_layout.addWidget(productos_label)
            
            main_layout.addLayout(productos_layout)

        # Acciones de pedido
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(20, 5, 0, 0)

        if pedido['estado'] == 'pendiente':
            btn_confirmar = QPushButton("Confirmar")
            btn_confirmar.setStyleSheet(
                "background-color: #4CAF50; color: white; border: none; padding: 5px 12px;"
            )
            btn_confirmar.clicked.connect(self.confirmar_pedido)

            btn_cancelar = QPushButton("Cancelar")
            btn_cancelar.setStyleSheet(
                "background-color: #F44336; color: white; border: none; padding: 5px 12px;"
            )
            btn_cancelar.clicked.connect(self.cancelar_pedido)

            actions_layout.addWidget(btn_confirmar)
            actions_layout.addWidget(btn_cancelar)

        elif pedido['estado'] == 'confirmado':
            if not pedido.get('facturada', False):
                btn_factura = QPushButton("Generar factura")
                btn_factura.setStyleSheet(
                    "background-color: #FF9800; color: white; border: none; padding: 5px 12px;"
                )
                btn_factura.clicked.connect(self.generar_factura)
                actions_layout.addWidget(btn_factura)
            else:
                btn_ver_factura = QPushButton("Ver factura")
                btn_ver_factura.setStyleSheet(
                    "background-color: #607D8B; color: white; border: none; padding: 5px 12px;"
                )
                btn_ver_factura.clicked.connect(self.ver_factura)
                actions_layout.addWidget(btn_ver_factura)

        main_layout.addLayout(actions_layout)

        # Separador
        separator = QLabel("─" * 80)
        separator.setStyleSheet("color: #ddd;")
        main_layout.addWidget(separator)

        self.setLayout(main_layout)

    def confirmar_pedido(self):
        try:
            self.service.confirmar(self.pedido['id'])

            generar = QMessageBox.question(
                self,
                "Generar factura",
                "Pedido confirmado. ¿Desea generar la factura ahora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if generar == QMessageBox.StandardButton.Yes:
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
