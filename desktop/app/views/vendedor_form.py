#views/vendedor_form.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
    QLabel,
    QMessageBox,
    QInputDialog,
    QGroupBox,
)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt


class VendedorForm(QWidget):

    def __init__(
        self,
        vendedor_service,
        zona_service,
        user_service,
        on_success,
        vendedor=None,
    ):
        super().__init__()

        self.vendedor_service = vendedor_service
        self.zona_service = zona_service
        self.user_service = user_service
        self.on_success = on_success
        self.vendedor = vendedor

        self.setWindowTitle("Editar Vendedor" if vendedor else "Nuevo Vendedor")
        self.resize(480, 650)
        
        self.zonas = []
        self.init_ui()

    def init_ui(self):
        # Estilos generales del formulario y componentes
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                font-size: 13px;
                color: #333333;
            }
            QGroupBox {
                background-color: #FFFFFF;
                border: 1px solid #D8D8D8;
                border-radius: 6px;
                margin-top: 15px;
                font-weight: bold;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 0 5px;
                color: #2196F3;
            }
            QLineEdit, QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #2196F3;
            }
            QPushButton#btn_save {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 4px;
                padding: 10px;
                min-height: 25px;
            }
            QPushButton#btn_save:hover {
                background-color: #43A047;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 10, 20, 20)
        main_layout.setSpacing(15)

        # =========================
        # DATOS PERSONALES
        # =========================
        group_personal = QGroupBox("Datos Personales")
        form_personal = QFormLayout()
        form_personal.setSpacing(10)
        form_personal.setContentsMargins(15, 15, 15, 15)

        self.nombre = QLineEdit()
        self.apellido = QLineEdit()
        self.telefono = QLineEdit()
        
        self.comision = QLineEdit()
        self.comision.setPlaceholderText("0.00")
        # Validador numérico estricto para la comisión (2 decimales)
        validador_comision = QDoubleValidator(0.00, 100.00, 2, self)
        validador_comision.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.comision.setValidator(validador_comision)

        self.estado = QComboBox()
        self.estado.addItem("Activo", "activo")
        self.estado.addItem("Inactivo", "inactivo")

        form_personal.addRow("Nombre:", self.nombre)
        form_personal.addRow("Apellido:", self.apellido)
        form_personal.addRow("Teléfono:", self.telefono)
        form_personal.addRow("Comisión (%):", self.comision)
        form_personal.addRow("Estado:", self.estado)
        group_personal.setLayout(form_personal)
        main_layout.addWidget(group_personal)

        # =========================
        # ASIGNACIÓN DE ZONA
        # =========================
        group_zona = QGroupBox("Ubicación y Zona")
        form_zona = QFormLayout()
        form_zona.setContentsMargins(15, 15, 15, 15)

        zona_container = QHBoxLayout()
        self.zona = QComboBox()
        self.zona.setSizePolicy(self.zona.sizePolicy().Policy.Expanding, self.zona.sizePolicy().Policy.Fixed)
        
        self.btn_add_zona = QPushButton("+")
        self.btn_add_zona.setFixedWidth(36)
        self.btn_add_zona.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.btn_add_zona.clicked.connect(self.add_new_zona)
        
        zona_container.addWidget(self.zona)
        zona_container.addWidget(self.btn_add_zona)

        form_zona.addRow("Zona Asignada:", zona_container)
        group_zona.setLayout(form_zona)
        main_layout.addWidget(group_zona)

        # =========================
        # CREDENCIALES DE ACCESO
        # =========================
        self.group_credentials = QGroupBox("Credenciales de Acceso")
        form_credentials = QFormLayout()
        form_credentials.setSpacing(10)
        form_credentials.setContentsMargins(15, 15, 15, 15)

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        form_credentials.addRow("Usuario:", self.username)
        form_credentials.addRow("Contraseña:", self.password)
        self.group_credentials.setLayout(form_credentials)
        main_layout.addWidget(self.group_credentials)

        # =========================
        # ACCIONES
        # =========================
        self.btn_save = QPushButton("Guardar")
        self.btn_save.setObjectName("btn_save")
        self.btn_save.clicked.connect(self.save)
        
        main_layout.addStretch()
        main_layout.addWidget(self.btn_save)

        self.setLayout(main_layout)

        # Cargas iniciales obligatorias
        self.load_zonas()

        if self.vendedor:
            self.load_vendedor()

    def load_zonas(self):
        try:
            self.zona.clear()
            data = self.zona_service.listar()
            zonas = data.get("results", data)
            self.zonas = zonas

            for z in zonas:
                self.zona.addItem(z["nombre"], z["id"])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar zonas: {str(e)}")

    def load_vendedor(self):
        v = self.vendedor

        self.nombre.setText(v.get("nombre", ""))
        self.apellido.setText(v.get("apellido", ""))
        self.telefono.setText(v.get("telefono", ""))
        self.comision.setText(str(v.get("comision", "")))

        index_estado = self.estado.findData(v.get("estado", "activo"))
        if index_estado >= 0:
            self.estado.setCurrentIndex(index_estado)

        index_zona = self.zona.findData(v.get("zona"))
        if index_zona >= 0:
            self.zona.setCurrentIndex(index_zona)

        usuario_id = v.get("usuario")
        if usuario_id:
            try:
                usuario_data = self.user_service.obtener(usuario_id)
                self.username.setText(usuario_data.get("username", ""))
                self.password.setText("••••••••")
            except Exception:
                self.username.setText("[No disponible]")
                self.password.setText("[No disponible]")

        # Configuración de modo lectura para edición
        self.username.setReadOnly(True)
        self.password.setReadOnly(True)
        self.password.setEchoMode(QLineEdit.EchoMode.Normal)
        self.btn_add_zona.setDisabled(True)
        self.group_credentials.setTitle("Credenciales de Acceso (Modo Lectura)")

    def add_new_zona(self):
        text, ok = QInputDialog.getText(
            self, "Nueva Zona", "Ingrese el nombre de la nueva zona comercial:"
        )

        if ok and text.strip():
            try:
                nueva_zona = self.zona_service.crear({
                    "nombre": text.strip(),
                    "descripcion": ""
                })
                self.load_zonas()
                
                index = self.zona.findData(nueva_zona["id"])
                if index >= 0:
                    self.zona.setCurrentIndex(index)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear la zona: {str(e)}")

    def validate_data(self):
        if not self.nombre.text().strip():
            raise ValueError("El campo 'Nombre' es obligatorio.")

        if self.zona.currentData() is None:
            raise ValueError("Debe seleccionar o registrar una zona válida.")

        if not self.vendedor:
            if not self.username.text().strip():
                raise ValueError("El 'Nombre de usuario' es obligatorio para nuevos vendedores.")
            if not self.password.text().strip():
                raise ValueError("La 'Contraseña' es obligatoria para nuevos vendedores.")

    def build_vendedor_data(self, user_id=None):
        # Normalización del separador decimal para evitar fallos de persistencia
        comision_val = self.comision.text().strip().replace(",", ".")
        
        data = {
            "nombre": self.nombre.text().strip(),
            "apellido": self.apellido.text().strip(),
            "telefono": self.telefono.text().strip(),
            "comision": comision_val if comision_val else "0.00",
            "estado": self.estado.currentData(),
            "zona": self.zona.currentData(),
        }

        if user_id is not None:
            data["usuario"] = user_id

        return data

    def save(self):
        try:
            self.validate_data()

            if self.vendedor:
                data = self.build_vendedor_data()
                self.vendedor_service.actualizar(self.vendedor["id"], data)
                QMessageBox.information(self, "Éxito", "Registro de vendedor actualizado.")
            else:
                user = self.user_service.crear({
                    "username": self.username.text().strip(),
                    "password": self.password.text().strip(),
                })

                vendedor_data = self.build_vendedor_data(user_id=user["id"])
                self.vendedor_service.crear(vendedor_data)
                QMessageBox.information(self, "Éxito", "Nuevo vendedor registrado correctamente.")

            self.on_success()
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Validación de Datos", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error de Persistencia", str(e))