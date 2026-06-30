from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView,
)
from PyQt6.QtCore import Qt

from services.cliente_service import ClienteService
from services.zona_service import ZonaService
from services.user_service import UserService
from views.cliente_form import ClienteForm


class ClienteView(QWidget):

    def __init__(self, http_client):
        super().__init__()

        self.http = http_client
        self.cliente_service = ClienteService(self.http)
        self.zona_service = ZonaService(self.http)
        self.user_service = UserService(self.http)
        self.zonas_map = {}

        self.init_ui()

    def init_ui(self):
        # Corrección: Nombre unificado del layout principal con márgenes limpios
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # =========================
        # TOP BAR
        # =========================
        top_bar = QHBoxLayout()
        self.btn_new = QPushButton("Nuevo Cliente")
        self.btn_refresh = QPushButton("Recargar")

        self.btn_new.setStyleSheet("""
            QPushButton {
                background-color: #673AB7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5E35B1;
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
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)

        top_bar.addWidget(self.btn_new)
        top_bar.addWidget(self.btn_refresh)
        top_bar.addStretch()

        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_new.clicked.connect(self.open_form)  # Corrección: Conexión directa sin lambda innecesario

        # =========================
        # TABLA DE CLIENTES
        # =========================
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "Documento", "Teléfono",
            "Email", "Dirección", "CP", "Localidad", "Provincia",
            "Zona", "Usuario", "Acciones"
        ])

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F9F9F9;
                gridline-color: #E0E0E0;
                border: 1px solid #D8D8D8;
                border-radius: 4px;
                selection-background-color: #EDE7F6;
                selection-color: #311B92;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                color: #333333;
                padding: 6px;
                font-weight: bold;
                border: 1px solid #E0E0E0;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.table.setColumnWidth(0, 40)    # ID
        self.table.setColumnWidth(1, 110)   # Nombre
        self.table.setColumnWidth(2, 110)   # Apellido
        self.table.setColumnWidth(3, 90)    # Documento
        self.table.setColumnWidth(4, 100)   # Teléfono
        self.table.setColumnWidth(5, 140)   # Email
        self.table.setColumnWidth(6, 140)   # Dirección
        self.table.setColumnWidth(7, 60)    # CP
        self.table.setColumnWidth(8, 100)   # Localidad
        self.table.setColumnWidth(9, 100)   # Provincia
        self.table.setColumnWidth(10, 110)  # Zona
        self.table.setColumnWidth(11, 110)  # Usuario
        self.table.setColumnWidth(12, 150)  # Acciones

        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        self.load_data()

    def load_zonas_map(self):
        try:
            data = self.zona_service.listar()
            zonas = data.get("results", data)
            self.zonas_map = {z["id"]: z["nombre"] for z in zonas}
        except Exception as e:
            self.zonas_map = {}
            QMessageBox.warning(self, "Advertencia", f"No se pudieron cargar zonas: {e}")

    def load_data(self):
        try:
            self.load_zonas_map()

            data = self.cliente_service.listar()
            clientes = data.get("results", data)

            self.table.setRowCount(len(clientes))

            for row, cliente in enumerate(clientes):
                id_item = QTableWidgetItem(str(cliente.get("id", "")))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 0, id_item)

                self.table.setItem(row, 1, QTableWidgetItem(cliente.get("nombre", "")))
                self.table.setItem(row, 2, QTableWidgetItem(cliente.get("apellido", "")))
                self.table.setItem(row, 3, QTableWidgetItem(cliente.get("nro_documento", "")))
                self.table.setItem(row, 4, QTableWidgetItem(cliente.get("telefono", "")))
                self.table.setItem(row, 5, QTableWidgetItem(cliente.get("email", "")))
                self.table.setItem(row, 6, QTableWidgetItem(cliente.get("direccion", "")))
                
                cp_item = QTableWidgetItem(cliente.get("codigo_postal", ""))
                cp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 7, cp_item)
                
                self.table.setItem(row, 8, QTableWidgetItem(cliente.get("localidad", "")))
                self.table.setItem(row, 9, QTableWidgetItem(cliente.get("provincia", "")))

                zona_id = cliente.get("zona")
                zona_nombre = self.zonas_map.get(zona_id, str(zona_id) if zona_id else "")
                self.table.setItem(row, 10, QTableWidgetItem(zona_nombre))

                usuario_id = cliente.get("usuario")
                username = "[No asignado]"
                if usuario_id:
                    try:
                        usuario_data = self.user_service.obtener(usuario_id)
                        username = usuario_data.get("username", "[Sin nombre]")
                    except Exception:
                        username = "[Error al cargar]"

                self.table.setItem(row, 11, QTableWidgetItem(username))

                # Contenedor de acciones
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 2, 4, 2)
                actions_layout.setSpacing(6)

                btn_edit = QPushButton("Editar")
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #673AB7;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #5E35B1;
                    }
                """)
                btn_edit.clicked.connect(
                    lambda checked, c=cliente: self.open_form(c)
                )

                btn_delete = QPushButton("Eliminar")
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #E53935;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #D32F2F;
                    }
                """)
                btn_delete.clicked.connect(
                    lambda checked, cid=cliente.get("id"), r=row: self.delete_cliente(cid, r)
                )

                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_delete)

                self.table.setCellWidget(row, 12, actions_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al recuperar datos: {str(e)}")

    def open_form(self, cliente=None):
        self.form = ClienteForm(
            self.cliente_service,
            self.zona_service,
            self.user_service,
            self.load_data,
            cliente=cliente,
        )
        self.form.show()

    def delete_cliente(self, cliente_id, row):
        if not cliente_id:
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar permanentemente este cliente?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            self.cliente_service.eliminar(cliente_id)
            QMessageBox.information(self, "Operación Exitosa", "Cliente eliminado correctamente.")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el registro: {str(e)}")