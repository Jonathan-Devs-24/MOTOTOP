# C:\Users\jonat\MotoTop\desktop\app\views\envio_view.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView
)

from services.pedido_service import PedidoService

QSS_STYLE = """
    QWidget#EnvioView {
        background-color: #ffffff;
    }
    QPushButton {
        background-color: #f8f9fa;
        color: #212529;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 8px 14px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
    }
    QPushButton#btn_crear {
        background-color: #dc3545;
        color: white;
        border: none;
    }
    QPushButton#btn_crear:hover {
        background-color: #bd2130;
    }
    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        gridline-color: #f1f3f5;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        color: #212529;
    }
    QHeaderView::section {
        background-color: #f8f9fa;
        color: #495057;
        padding: 8px;
        font-weight: bold;
        border: none;
        border-bottom: 2px solid #dee2e6;
    }
    QTableWidget::item {
        padding: 6px;
    }
    QTableWidget::item:selected {
        background-color: #f8d7da;
        color: #b02a37;
    }
"""

class EnvioView(QWidget):

    def __init__(self, envio_service):
        super().__init__()

        self.envio_service = envio_service

        # Usamos el mismo cliente HTTP del servicio de envíos
        self.pedido_service = PedidoService(
            envio_service.http
        )

        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        self.setObjectName("EnvioView")
        self.setStyleSheet(QSS_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(8)

        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_crear = QPushButton("＋ Crear envío")
        self.btn_crear.setObjectName("btn_crear")
        self.btn_editar = QPushButton("✏️ Editar envío")

        botones_layout.addWidget(self.btn_actualizar)
        botones_layout.addWidget(self.btn_crear)
        botones_layout.addWidget(self.btn_editar)
        botones_layout.addStretch()

        # Tabla Estilizada
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Pedido",
            "Cliente",
            "Empresa",
            "Tracking",
            "Estado",
        ])
        
        # Comportamiento visual moderno de la tabla
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        
        # CORRECCIÓN AQUÍ: Uso correcto de ResizeMode en PyQt6
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Layout
        layout.addLayout(botones_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Eventos
        self.btn_actualizar.clicked.connect(self.cargar_datos)
        self.btn_crear.clicked.connect(self.crear_envio)
        self.btn_editar.clicked.connect(self.editar_envio)

    def cargar_datos(self):
        try:
            envios = self.envio_service.listar()

            if isinstance(envios, dict) and "results" in envios:
                envios = envios["results"]

            self.table.setRowCount(len(envios))

            for row, envio in enumerate(envios):
                pedido = envio.get("pedido")
                empresa = envio.get("empresa_transporte", "")
                tracking = envio.get("tracking_code") or ""
                estado = envio.get("estado_envio", "")

                cliente = ""

                try:
                    pedido_data = self.pedido_service.obtener(pedido)
                    cliente_data = pedido_data.get("cliente", {})
                    nombre = cliente_data.get("nombre", "")
                    apellido = cliente_data.get("apellido", "")
                    cliente = f"{nombre} {apellido}".strip()
                except Exception:
                    cliente = ""

                self.table.setItem(row, 0, QTableWidgetItem(str(envio["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(pedido)))
                self.table.setItem(row, 2, QTableWidgetItem(cliente))
                self.table.setItem(row, 3, QTableWidgetItem(empresa))
                self.table.setItem(row, 4, QTableWidgetItem(tracking))
                self.table.setItem(row, 5, QTableWidgetItem(estado))

            self.table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    def crear_envio(self):
        try:
            # Obtener pedidos
            pedidos = self.pedido_service.listar()

            if isinstance(pedidos, dict) and "results" in pedidos:
                pedidos = pedidos["results"]

            # Filtrar solo pedidos confirmados
            pedidos_confirmados = [
                p for p in pedidos
                if p["estado"] == "confirmado"
            ]

            # Obtener envíos existentes
            envios = self.envio_service.listar()

            if isinstance(envios, dict) and "results" in envios:
                envios = envios["results"]

            # IDs de pedidos que ya tienen envío
            pedidos_con_envio = {
                envio["pedido"]
                for envio in envios
            }

            # Pedidos disponibles para crear envío
            pedidos_disponibles = [
                p for p in pedidos_confirmados
                if p["id"] not in pedidos_con_envio
            ]

            if not pedidos_disponibles:
                QMessageBox.information(
                    self,
                    "Información",
                    "No hay pedidos confirmados sin envío."
                )
                return

            # Abrir un formulario propio para seleccionar el pedido
            from views.select_pedido_envio_view import SelectPedidoEnvioView

            self.select_pedido_window = SelectPedidoEnvioView(
                pedidos=pedidos_disponibles,
                on_select=self.abrir_formulario_envio
            )
            self.select_pedido_window.show()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    def abrir_formulario_envio(self, pedido):
        from views.envio_form import EnvioForm

        self.envio_form = EnvioForm(
            pedido=pedido,
            envio_service=self.envio_service,
            on_success=self.cargar_datos
        )
        self.envio_form.show()

    def editar_envio(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Selección requerida",
                "Debe seleccionar un envío."
            )
            return

        envio_id = int(self.table.item(row, 0).text())
        envio = self.envio_service.obtener(envio_id)

        pedido_id = envio["pedido"]
        pedido = self.pedido_service.obtener(pedido_id)

        from views.envio_form import EnvioForm

        self.form = EnvioForm(
            pedido=pedido,
            envio_service=self.envio_service,
            on_success=self.cargar_datos,
            envio=envio
        )
        self.form.show()
        
        
