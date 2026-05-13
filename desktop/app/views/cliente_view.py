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

        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        self.btn_refresh = QPushButton("Recargar")
        self.btn_new = QPushButton("Nuevo Cliente")
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

        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "Documento", "Teléfono",
            "Email", "Dirección", "CP", "Localidad", "Provincia",
            "Zona", "Usuario", "Acciones"
        ])

        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 140)
        self.table.setColumnWidth(6, 150)
        self.table.setColumnWidth(7, 80)
        self.table.setColumnWidth(8, 100)
        self.table.setColumnWidth(9, 100)
        self.table.setColumnWidth(10, 120)
        self.table.setColumnWidth(11, 120)
        self.table.setColumnWidth(12, 160)

        layout.addLayout(top_bar)
        layout.addWidget(self.table)

        self.setLayout(layout)

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
                self.table.setItem(row, 0, QTableWidgetItem(str(cliente.get("id", ""))))
                self.table.setItem(row, 1, QTableWidgetItem(cliente.get("nombre", "")))
                self.table.setItem(row, 2, QTableWidgetItem(cliente.get("apellido", "")))
                self.table.setItem(row, 3, QTableWidgetItem(cliente.get("nro_documento", "")))
                self.table.setItem(row, 4, QTableWidgetItem(cliente.get("telefono", "")))
                self.table.setItem(row, 5, QTableWidgetItem(cliente.get("email", "")))
                self.table.setItem(row, 6, QTableWidgetItem(cliente.get("direccion", "")))
                self.table.setItem(row, 7, QTableWidgetItem(cliente.get("codigo_postal", "")))
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

                btn_edit = QPushButton("Editar")
                btn_edit.setStyleSheet("background-color: #2196F3; color: white;")
                btn_edit.clicked.connect(
                    lambda checked, c=cliente: self.open_form(c)
                )

                btn_delete = QPushButton("Eliminar")
                btn_delete.setStyleSheet("background-color: #F44336; color: white;")
                btn_delete.clicked.connect(
                    lambda checked, cid=cliente.get("id"), row=row: self.delete_cliente(cid, row)
                )

                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(4)
                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_delete)
                actions_widget.setLayout(actions_layout)

                self.table.setCellWidget(row, 12, actions_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

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
            "Eliminar cliente",
            "¿Estás seguro de eliminar este cliente?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            self.cliente_service.eliminar(cliente_id)
            QMessageBox.information(self, "OK", "Cliente eliminado correctamente")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
