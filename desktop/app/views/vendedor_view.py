# desktop/app/views/vendedor_view.py 
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
from PyQt6.QtGui import QColor

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

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # =========================
        # TOP BAR
        # =========================
        top_bar = QHBoxLayout()

        self.btn_new = QPushButton("Nuevo Vendedor")
        self.btn_refresh = QPushButton("Recargar")

        # Hoja de estilos unificada para componentes de la barra superior
        self.btn_new.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
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
        self.btn_new.clicked.connect(self.open_form)
        
        # =========================
        # MENSAJE INFORMATIVO (NUEVO)
        # =========================
        self.lbl_mensaje = QLabel(
            "Al presionar \"Cambiar\" en la sección \"Acción\" se confirma la inactividad o actividad de un vendedor. "
            "Al indicar que un vendedor está inactivo, este no podrá iniciar sesión en la app."
        )
        self.lbl_mensaje.setWordWrap(True)  # Permite que el texto quiebre línea si la ventana es chica
        self.lbl_mensaje.setStyleSheet("""
            QLabel {
                color: #555555;
                font-size: 12px;
                font-style: italic;
                padding: 5px 2px;
            }
        """)
        main_layout.addWidget(self.lbl_mensaje)

        # =========================
        # TABLA DE VENDEDORES
        # =========================
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "Teléfono", "Comisión", "Usuario", "Contraseña", "Estado", "Acción"
        ])

        # Comportamiento de la tabla
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        
        # Estilo visual de la tabla y sus encabezados
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F9F9F9;
                gridline-color: #E0E0E0;
                border: 1px solid #D8D8D8;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                color: #333333;
                padding: 6px;
                font-weight: bold;
                border: 1px solid #E0E0E0;
            }
        """)

        # Configuración de anchos de columna (Responsivo)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.table.setColumnWidth(0, 40)   # ID
        self.table.setColumnWidth(1, 120)  # Nombre
        self.table.setColumnWidth(2, 120)  # Apellido
        self.table.setColumnWidth(3, 110)  # Teléfono
        self.table.setColumnWidth(4, 80)   # Comisión
        self.table.setColumnWidth(5, 110)  # Usuario
        self.table.setColumnWidth(6, 140)  # Contraseña
        self.table.setColumnWidth(7, 90)   # Estado
        self.table.setColumnWidth(8, 100)  # Acción
        
        # Permitir que las columnas principales se expandan si hay espacio libre
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        # Carga inicial
        self.load_data()

    def load_data(self):
        try:
            data = self.vendedor_service.listar()
            vendedores = data.get("results", data)

            self.table.setRowCount(len(vendedores))

            for row, vendedor in enumerate(vendedores):
                # Generación de ítems de celda estándar
                id_item = QTableWidgetItem(str(vendedor.get("id", "")))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                comision_item = QTableWidgetItem(f"{vendedor.get('comision', '')}%")
                comision_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                self.table.setItem(row, 0, id_item)
                self.table.setItem(row, 1, QTableWidgetItem(vendedor.get("nombre", "")))
                self.table.setItem(row, 2, QTableWidgetItem(vendedor.get("apellido", "")))
                self.table.setItem(row, 3, QTableWidgetItem(vendedor.get("telefono", "")))
                self.table.setItem(row, 4, comision_item)

                # Resolución de datos de usuario de forma asíncrona simulada
                usuario_id = vendedor.get("usuario")
                username = "[No asignado]"
                password = "[No asignado]"

                if usuario_id:
                    try:
                        usuario_data = self.user_service.obtener(usuario_id)
                        username = usuario_data.get("username", "[Error]")
                        password = "••••••••"
                    except Exception:
                        username = "[Error al cargar]"
                        password = "[Error al cargar]"

                self.table.setItem(row, 5, QTableWidgetItem(username))
                self.table.setItem(row, 6, QTableWidgetItem(password))

                # Manejo visual del Estado
                estado = str(vendedor.get("estado", "")).upper()
                estado_item = QTableWidgetItem(estado)
                estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Resaltado condicional por color de texto según estado
                if estado in ["ACTIVO", "HABIILITADO"]:
                    estado_item.setForeground(QColor("#2E7D32"))  # Verde oscuro
                else:
                    estado_item.setForeground(QColor("#C62828"))  # Rojo oscuro
                
                self.table.setItem(row, 7, estado_item)

                # Celda contenedora del botón de acción para mantener consistencia de padding
                btn_container = QWidget()
                btn_layout = QHBoxLayout(btn_container)
                btn_layout.setContentsMargins(4, 2, 4, 2)
                
                btn_estado = QPushButton("Cambiar")
                btn_estado.setStyleSheet("""
                    QPushButton {
                        background-color: #FF9800;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e68900;
                    }
                """)
                
                # Referencia local para el callback de la señal
                vendedor_id = vendedor.get("id")
                btn_estado.clicked.connect(
                    lambda checked, vid=vendedor_id, r=row: self.cambiar_estado(vid, r)
                )
                
                btn_layout.addWidget(btn_estado)
                self.table.setCellWidget(row, 8, btn_container)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")

    def cambiar_estado(self, vendedor_id, row):
        try:
            resultado = self.vendedor_service.cambiar_estado(vendedor_id)
            nuevo_estado = str(resultado.get("estado", "")).upper()
            mensaje = resultado.get("mensaje", "Estado cambiado con éxito.")

            # Corrección de índice de columna: el estado se almacena en la columna 7
            estado_item = QTableWidgetItem(nuevo_estado)
            estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if nuevo_estado in ["ACTIVO", "HABILITADO"]:
                estado_item.setForeground(QColor("#2E7D32"))
            else:
                estado_item.setForeground(QColor("#C62828"))
                
            self.table.setItem(row, 7, estado_item)

            QMessageBox.information(self, "Operación Exitosa", mensaje)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar estado: {str(e)}")

    def open_form(self):
        self.form = VendedorForm(
            self.vendedor_service,
            self.zona_service,
            self.user_service,
            self.load_data,
        )
        self.form.show()