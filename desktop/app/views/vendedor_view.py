from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)

from services.vendedor_service import VendedorService
from services.zona_service import ZonaService
from services.user_service import UserService
from views.vendedor_form import VendedorForm


class VendedorView(QWidget):

    def __init__(self, http_client):
        super().__init__()

        self.http = http_client
        self.vendedor_service = VendedorService(self.http)
        self.zona_service = ZonaService(self.http)
        self.user_service = UserService(self.http)

        layout = QVBoxLayout()

        # =========================
        # TOP BAR
        # =========================

        top_bar = QHBoxLayout()

        self.btn_refresh = QPushButton("Recargar")
        self.btn_new = QPushButton("Nuevo Vendedor")

        self.btn_new.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)

        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)

        top_bar.addWidget(self.btn_new)
        top_bar.addWidget(self.btn_refresh)
        top_bar.addStretch()

        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_new.clicked.connect(self.open_form)

        # =========================
        # TABLA DE VENDEDORES
        # =========================

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Apellido", "Teléfono", "Comisión", "Usuario", "Contraseña", "Estado", "Acción"]
        )
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 120)
        self.table.setColumnWidth(7, 80)
        self.table.setColumnWidth(8, 100)

        layout.addLayout(top_bar)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # cargar inicial
        self.load_data()

    # =========================

    def load_data(self):
        try:
            data = self.vendedor_service.listar()
            vendedores = data.get("results", data)

            self.table.setRowCount(len(vendedores))

            for row, vendedor in enumerate(vendedores):
                self.table.setItem(
                    row, 0, QTableWidgetItem(str(vendedor.get("id", "")))
                )
                self.table.setItem(
                    row, 1, QTableWidgetItem(vendedor.get("nombre", ""))
                )
                self.table.setItem(
                    row, 2, QTableWidgetItem(vendedor.get("apellido", ""))
                )
                self.table.setItem(
                    row, 3, QTableWidgetItem(vendedor.get("telefono", ""))
                )
                self.table.setItem(
                    row, 4, QTableWidgetItem(str(vendedor.get("comision", "")))
                )
                
                # Obtener datos del usuario
                usuario_id = vendedor.get("usuario")
                username = "[No asignado]"
                password = "[No asignado]"
                
                if usuario_id:
                    try:
                        usuario_data = self.user_service.obtener(usuario_id)
                        username = usuario_data.get("username", "[Error]")
                        password = "[Protegida en servidor]"
                    except Exception as e:
                        username = "[Error al cargar]"
                        password = "[Error al cargar]"
                
                self.table.setItem(
                    row, 5, QTableWidgetItem(username)
                )
                self.table.setItem(
                    row, 6, QTableWidgetItem(password)
                )
                
                estado = vendedor.get("estado", "")
                self.table.setItem(
                    row, 7, QTableWidgetItem(estado)
                )
                
                # Botón para cambiar estado
                btn_estado = QPushButton("Cambiar")
                btn_estado.setStyleSheet("""
                    QPushButton {
                        background-color: #FF9800;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e68900;
                    }
                """)
                btn_estado.clicked.connect(
                    lambda checked, vid=vendedor.get("id"), row_num=row: self.cambiar_estado(vid, row_num)
                )
                self.table.setCellWidget(row, 8, btn_estado)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # =========================

    def cambiar_estado(self, vendedor_id, row):
        try:
            resultado = self.vendedor_service.cambiar_estado(vendedor_id)
            
            nuevo_estado = resultado.get("estado", "")
            mensaje = resultado.get("mensaje", "Estado cambiado")
            
            # Actualizar la tabla
            self.table.setItem(row, 5, QTableWidgetItem(nuevo_estado))
            
            QMessageBox.information(
                self,
                "OK",
                mensaje,
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # =========================

    def open_form(self):
        self.form = VendedorForm(
            self.vendedor_service,
            self.zona_service,
            self.user_service,
            self.load_data,
        )
        self.form.show()
