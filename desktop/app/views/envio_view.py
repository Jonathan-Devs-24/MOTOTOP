# desktop/app/views/envio_view.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)

from services.pedido_service import PedidoService


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
        layout = QVBoxLayout()

        # Botones
        botones_layout = QHBoxLayout()

        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_crear = QPushButton("Crear envío")

        botones_layout.addWidget(self.btn_actualizar)
        botones_layout.addWidget(self.btn_crear)
        botones_layout.addStretch()

        # Tabla
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

        # Layout
        layout.addLayout(botones_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Eventos
        self.btn_actualizar.clicked.connect(self.cargar_datos)
        self.btn_crear.clicked.connect(self.crear_envio)

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
            pedidos = self.pedido_service.listar()

            if isinstance(pedidos, dict) and "results" in pedidos:
                pedidos = pedidos["results"]

            pedidos_confirmados = [
                p for p in pedidos
                if p["estado"] == "confirmado"
            ]

            pedidos_con_envio = {
                envio["pedido"]
                for envio in self.envio_service.listar().get("results", [])
                if isinstance(self.envio_service.listar(), dict)
            }

            pedido_disponible = None

            for pedido in pedidos_confirmados:
                if pedido["id"] not in pedidos_con_envio:
                    pedido_disponible = pedido
                    break

            if not pedido_disponible:
                QMessageBox.information(
                    self,
                    "Información",
                    "No hay pedidos confirmados disponibles para generar envíos."
                )
                return

            data = {
                "pedido": pedido_disponible["id"],
                "empresa_transporte": "Correo Argentino",
                "tracking_code": "",
                "estado_envio": "recibido"
            }

            self.envio_service.crear(data)

            QMessageBox.information(
                self,
                "Éxito",
                "Envío creado correctamente."
            )

            self.cargar_datos()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
            
            