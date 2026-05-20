# desktop/app/views/envio_form.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
    QDateTimeEdit,
)

from PyQt6.QtCore import QDateTime


class EnvioForm(QWidget):

    def __init__(self, pedido, envio_service, on_success, envio=None):
        super().__init__()

        self.pedido = pedido
        self.envio_service = envio_service
        self.on_success = on_success
        self.envio = envio

        self.setWindowTitle(
            "Editar Envío" if envio else f"Nuevo Envío - Pedido #{pedido['id']}"
        )
        self.resize(500, 500)

        layout = QVBoxLayout()

        # ==========================================
        # PEDIDO
        # ==========================================
        layout.addWidget(QLabel(f"Pedido #{pedido['id']}"))

        # ==========================================
        # EMPRESA DE TRANSPORTE
        # ==========================================
        layout.addWidget(QLabel("Empresa de transporte"))
        self.empresa_transporte = QComboBox()
        self.empresa_transporte.setEditable(True)
        layout.addWidget(self.empresa_transporte)

        self.cargar_empresas_transporte()

        # ==========================================
        # TRACKING
        # ==========================================
        layout.addWidget(QLabel("Código de seguimiento"))
        self.tracking_code = QLineEdit()
        layout.addWidget(self.tracking_code)

        # ==========================================
        # ESTADO
        # ==========================================
        layout.addWidget(QLabel("Estado del envío"))

        self.estado_envio = QComboBox()
        self.estado_envio.addItem("Recibido", "recibido")
        self.estado_envio.addItem("En preparación", "preparacion")
        self.estado_envio.addItem("Enviado", "enviado")
        self.estado_envio.addItem("Entregado", "entregado")
        self.estado_envio.addItem("Cancelado", "cancelado")
        layout.addWidget(self.estado_envio)

        # ==========================================
        # FECHA ENVÍO
        # ==========================================
        layout.addWidget(QLabel("Fecha de envío"))

        self.fecha_envio = QDateTimeEdit()
        self.fecha_envio.setCalendarPopup(True)
        self.fecha_envio.setDateTime(QDateTime.currentDateTime())
        self.fecha_envio.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        layout.addWidget(self.fecha_envio)

        # ==========================================
        # FECHA ESTIMADA
        # ==========================================
        layout.addWidget(QLabel("Fecha estimada"))

        self.fecha_estimada = QDateTimeEdit()
        self.fecha_estimada.setCalendarPopup(True)
        self.fecha_estimada.setDateTime(QDateTime.currentDateTime())
        self.fecha_estimada.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        layout.addWidget(self.fecha_estimada)

        # ==========================================
        # FECHA ENTREGA
        # ==========================================
        layout.addWidget(QLabel("Fecha de entrega"))

        self.fecha_entrega = QDateTimeEdit()
        self.fecha_entrega.setCalendarPopup(True)
        self.fecha_entrega.setDateTime(QDateTime.currentDateTime())
        self.fecha_entrega.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        layout.addWidget(self.fecha_entrega)

        # ==========================================
        # BOTÓN GUARDAR
        # ==========================================
        self.btn_save = QPushButton("Guardar")
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)

        layout.addStretch()
        self.setLayout(layout)

        if self.envio:
            self.load_envio()

    # ==========================================
    # CARGAR DATOS EN EDICIÓN
    # ==========================================

    def load_envio(self):
        self.empresa_transporte.setCurrentText(
            self.envio.get("empresa_transporte", "")
        )

        self.tracking_code.setText(
            self.envio.get("tracking_code", "")
        )

        estado = self.envio.get("estado_envio", "recibido")
        index = self.estado_envio.findData(estado)
        if index >= 0:
            self.estado_envio.setCurrentIndex(index)

    # ==========================================
    # VALIDACIÓN
    # ==========================================

    def validate_data(self):
        if self.pedido.get("estado") != "confirmado":
            raise ValueError(
                "Solo se pueden crear envíos para pedidos confirmados"
            )

    # ==========================================
    # CONSTRUCCIÓN DE DATOS
    # ==========================================

    def build_data(self):
        return {
            "pedido": self.pedido["id"],
            "empresa_transporte": self.empresa_transporte.currentText().strip(),
            "tracking_code": self.tracking_code.text().strip() or None,
            "estado_envio": self.estado_envio.currentData(),
            "fecha_envio": self.fecha_envio.dateTime().toString(
                "yyyy-MM-dd HH:mm:ss"
            ),
            "fecha_estimada": self.fecha_estimada.dateTime().toString(
                "yyyy-MM-dd HH:mm:ss"
            ),
            "fecha_entrega": self.fecha_entrega.dateTime().toString(
                "yyyy-MM-dd HH:mm:ss"
            ),
        }

    # ==========================================
    # GUARDAR
    # ==========================================

    def save(self):
        try:
            self.validate_data()

            data = self.build_data()

            if self.envio:
                self.envio_service.actualizar(
                    self.envio["id"],
                    data,
                )

                QMessageBox.information(
                    self,
                    "OK",
                    "Envío actualizado correctamente",
                )
            else:
                self.envio_service.crear(data)

                QMessageBox.information(
                    self,
                    "OK",
                    "Envío creado correctamente",
                )

            self.on_success()
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
            
            
    def cargar_empresas_transporte(self):
        try:
            envios = self.envio_service.listar()

            if isinstance(envios, dict) and "results" in envios:
                envios = envios["results"]

            empresas = sorted({
                envio.get("empresa_transporte", "").strip()
                for envio in envios
                if envio.get("empresa_transporte")
            })

            self.empresa_transporte.addItems(empresas)

        except Exception:
            pass