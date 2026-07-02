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
    QFormLayout
)

from PyQt6.QtCore import QDateTime

QSS_STYLE = """
    QWidget#EnvioForm {
        background-color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        color: #1a1a1a;
    }
    QLabel {
        font-weight: bold;
        color: #495057;
    }
    QLabel#lbl_pedido_header {
        font-size: 15px;
        font-weight: bold;
        color: #ffffff;
        background-color: #212529;
        padding: 10px;
        border-left: 4px solid #dc3545;
        border-radius: 4px;
        margin-bottom: 5px;
    }
    QLineEdit, QComboBox, QDateTimeEdit {
        background-color: #f8f9fa;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 6px;
        color: #212529;
        min-height: 22px;
    }
    QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus {
        border: 1px solid #dc3545;
        background-color: #ffffff;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #212529;
        selection-background-color: #dc3545;
        selection-color: white;
    }
    QPushButton#btn_save {
        background-color: #dc3545;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 12px;
        font-size: 14px;
        font-weight: bold;
        margin-top: 15px;
    }
    QPushButton#btn_save:hover {
        background-color: #bd2130;
    }
    QPushButton#btn_save:pressed {
        background-color: #b02a37;
    }
"""

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
        self.resize(500, 520)

        self.setObjectName("EnvioForm")
        self.setStyleSheet(QSS_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Header del Pedido Destacado
        self.lbl_pedido = QLabel(f"📦 Seguimiento de Pedido #{pedido['id']}")
        self.lbl_pedido.setObjectName("lbl_pedido_header")
        main_layout.addWidget(self.lbl_pedido)

        # Formulario Estructurado
        form_layout = QFormLayout()
        form_layout.setSpacing(14)

        # Empresa Transporte
        self.empresa_transporte = QComboBox()
        self.empresa_transporte.setEditable(True)
        form_layout.addRow("Empresa de Transporte:", self.empresa_transporte)

        self.cargar_empresas_transporte()

        # Tracking
        self.tracking_code = QLineEdit()
        self.tracking_code.setPlaceholderText("Ej: TRK123456789")
        form_layout.addRow("Código de Seguimiento:", self.tracking_code)

        # Estado del Envío
        self.estado_envio = QComboBox()
        self.estado_envio.addItem("Recibido", "recibido")
        self.estado_envio.addItem("En preparación", "preparacion")
        self.estado_envio.addItem("Enviado", "enviado")
        self.estado_envio.addItem("Entregado", "entregado")
        self.estado_envio.addItem("Cancelado", "cancelado")
        form_layout.addRow("Estado del Envío:", self.estado_envio)

        # Configuración común para selectores de fecha
        formato_fecha = "yyyy-MM-dd HH:mm:ss"
        ahora = QDateTime.currentDateTime()

        # Fecha Envío
        self.fecha_envio = QDateTimeEdit()
        self.fecha_envio.setCalendarPopup(True)
        self.fecha_envio.setDateTime(ahora)
        self.fecha_envio.setDisplayFormat(formato_fecha)
        form_layout.addRow("Fecha de Envío:", self.fecha_envio)

        # Fecha Estimada
        self.fecha_estimada = QDateTimeEdit()
        self.fecha_estimada.setCalendarPopup(True)
        self.fecha_estimada.setDateTime(ahora)
        self.fecha_estimada.setDisplayFormat(formato_fecha)
        form_layout.addRow("Fecha Estimada:", self.fecha_estimada)

        # Fecha Entrega
        self.fecha_entrega = QDateTimeEdit()
        self.fecha_entrega.setCalendarPopup(True)
        self.fecha_entrega.setDateTime(ahora)
        self.fecha_entrega.setDisplayFormat(formato_fecha)
        form_layout.addRow("Fecha de Entrega:", self.fecha_entrega)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        # Botón Guardar
        self.btn_save = QPushButton("Guardar")
        self.btn_save.setObjectName("btn_save")
        self.btn_save.clicked.connect(self.save)
        main_layout.addWidget(self.btn_save)

        self.setLayout(main_layout)

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
        
        