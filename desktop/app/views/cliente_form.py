from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
    QLabel,
    QMessageBox,
    QInputDialog,
    QFormLayout,
    QTabWidget
)

# --- NUEVO: Estilo visual moderno (QSS) ---
ESTILO_MODERNO = """
    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        background-color: #f8f9fa;
        color: #333333;
    }
    QLineEdit, QComboBox {
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 6px 12px;
        background-color: #ffffff;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #0d6efd;
        background-color: #fff;
    }
    QPushButton {
        background-color: #0d6efd;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0b5ed7;
    }
    QPushButton:disabled {
        background-color: #6c757d;
    }
    QPushButton#btn_add_zona {
        background-color: #198754;
    }
    QPushButton#btn_add_zona:hover {
        background-color: #157347;
    }
    QTabWidget::pane {
        border: 1px solid #dee2e6;
        background: #ffffff;
        border-radius: 4px;
    }
    QTabBar::tab {
        background: #e9ecef;
        padding: 8px 16px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background: #ffffff;
        border-bottom: 2px solid #0d6efd;
        font-weight: bold;
    }
    QPushButton#btn_guardar {
    background-color: #6f42c1;  /* Morado principal */
    color: white;
    }

    QPushButton#btn_guardar:hover {
        background-color: #59359a;  /* Morado más oscuro al pasar el mouse */
    }

    QPushButton#btn_guardar:pressed {
        background-color: #492a80;  /* Morado aún más oscuro al hacer clic */
    }
"""


class ClienteForm(QWidget):

    def __init__(
        self,
        cliente_service,
        zona_service,
        user_service,
        on_success,
        cliente=None,
    ):
        super().__init__()

        self.cliente_service = cliente_service
        self.zona_service = zona_service
        self.user_service = user_service
        self.on_success = on_success
        self.cliente = cliente

        self.setWindowTitle(
            "Editar Cliente" if cliente else "Nuevo Cliente"
        )
        self.resize(600, 800)

        self.zonas = []

        # --- REEMPLAZAR DENTRO DE __init__ ---
        self.setWindowTitle("Editar Cliente" if cliente else "Nuevo Cliente")
        self.resize(500, 450)  # Al usar pestañas, podemos reducir el tamaño vertical de 800 a 450
        self.setStyleSheet(ESTILO_MODERNO) # Aplicamos el diseño visual

        self.zonas = []

        # Layout Principal de la ventana
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Creamos el contenedor de pestañas
        tabs = QTabWidget()

        # ==========================================
        # PESTAÑA 1: DATOS PERSONALES
        # ==========================================
        tab_personales = QWidget()
        form_personales = QFormLayout(tab_personales)
        form_personales.setSpacing(10)

        self.nombre = QLineEdit()
        self.apellido = QLineEdit()
        self.nro_documento = QLineEdit()
        self.telefono = QLineEdit()
        self.email = QLineEdit()

        form_personales.addRow("Nombre:", self.nombre)
        form_personales.addRow("Apellido:", self.apellido)
        form_personales.addRow("Nro. Documento:", self.nro_documento)
        form_personales.addRow("Teléfono:", self.telefono)
        form_personales.addRow("Email:", self.email)
        
        tabs.addTab(tab_personales, "Datos Personales")

        # ==========================================
        # PESTAÑA 2: UBICACIÓN Y ZONA
        # ==========================================
        tab_ubicacion = QWidget()
        form_ubicacion = QFormLayout(tab_ubicacion)
        form_ubicacion.setSpacing(10)

        self.direccion = QLineEdit()
        self.codigo_postal = QLineEdit()
        self.localidad = QLineEdit()
        self.provincia = QLineEdit()

        # Sub-layout horizontal para la Zona y su botón "+"
        zona_layout = QHBoxLayout()
        self.zona = QComboBox()
        self.btn_add_zona = QPushButton("+")
        self.btn_add_zona.setObjectName("btn_add_zona") # ID para el estilo CSS
        self.btn_add_zona.setFixedWidth(35)
        self.btn_add_zona.clicked.connect(self.add_new_zona)
        zona_layout.addWidget(self.zona)
        zona_layout.addWidget(self.btn_add_zona)

        form_ubicacion.addRow("Dirección:", self.direccion)
        form_ubicacion.addRow("Código Postal:", self.codigo_postal)
        form_ubicacion.addRow("Localidad:", self.localidad)
        form_ubicacion.addRow("Provincia:", self.provincia)
        form_ubicacion.addRow("Zona:", zona_layout)

        tabs.addTab(tab_ubicacion, "Ubicación")

        # ==========================================
        # PESTAÑA 3: CUENTA DE USUARIO
        # ==========================================
        tab_cuenta = QWidget()
        form_cuenta = QFormLayout(tab_cuenta)
        form_cuenta.setSpacing(10)

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        form_cuenta.addRow("Usuario (opcional):", self.username)
        form_cuenta.addRow("Contraseña:", self.password)

        tabs.addTab(tab_cuenta, "Usuario y Acceso")

        # Agregar el contenedor de pestañas al layout principal
        main_layout.addWidget(tabs)

        # Botón de Guardar en la parte inferior (fuera de las pestañas)
        self.btn_save = QPushButton("Guardar Datos del Cliente")
        self.btn_save.setObjectName("btn_guardar")
        self.btn_save.setFixedHeight(40) # Más alto para denotar acción principal
        self.btn_save.clicked.connect(self.save)
        main_layout.addWidget(self.btn_save)

        self.setLayout(main_layout)

        self.load_zonas()
        # --- FIN  ---

        if self.cliente:
            self.load_cliente()

    def load_zonas(self):
        try:
            self.zona.clear()
            data = self.zona_service.listar()
            zonas = data.get("results", data)
            self.zonas = zonas

            for z in zonas:
                self.zona.addItem(z["nombre"], z["id"])
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_cliente(self):
        c = self.cliente

        self.nombre.setText(c.get("nombre", ""))
        self.apellido.setText(c.get("apellido", ""))
        self.nro_documento.setText(c.get("nro_documento", ""))
        self.telefono.setText(c.get("telefono", ""))
        self.email.setText(c.get("email", ""))
        self.direccion.setText(c.get("direccion", ""))
        self.codigo_postal.setText(c.get("codigo_postal", ""))
        self.localidad.setText(c.get("localidad", ""))
        self.provincia.setText(c.get("provincia", ""))

        zona_id = c.get("zona")
        index_zona = self.zona.findData(zona_id)
        if index_zona >= 0:
            self.zona.setCurrentIndex(index_zona)

        usuario_id = c.get("usuario")
        if usuario_id:
            try:
                usuario_data = self.user_service.obtener(usuario_id)
                self.username.setText(usuario_data.get("username", ""))
                self.password.setText("[Contraseña no disponible]")
                self.username.setReadOnly(True)
                self.password.setReadOnly(True)
                self.password.setEchoMode(QLineEdit.EchoMode.Normal)
            except Exception as e:
                self.username.setText("[Error al cargar]")
                self.password.setText("[Error al cargar]")
                self.username.setReadOnly(True)
                self.password.setReadOnly(True)
                self.password.setEchoMode(QLineEdit.EchoMode.Normal)
                QMessageBox.warning(self, "Advertencia", str(e))

        if self.cliente and usuario_id:
            self.btn_add_zona.setDisabled(True)

    def validate_data(self):
        if not self.nombre.text().strip():
            raise ValueError("El nombre es obligatorio")

        if not self.nro_documento.text().strip():
            raise ValueError("El número de documento es obligatorio")

        if not self.telefono.text().strip():
            raise ValueError("El teléfono es obligatorio")

        if not self.email.text().strip():
            raise ValueError("El email es obligatorio")

        if not self.direccion.text().strip():
            raise ValueError("La dirección es obligatoria")

        if not self.codigo_postal.text().strip():
            raise ValueError("El código postal es obligatorio")

        if not self.localidad.text().strip():
            raise ValueError("La localidad es obligatoria")

        if not self.provincia.text().strip():
            raise ValueError("La provincia es obligatoria")

        if self.zona.currentData() is None:
            raise ValueError("Debe seleccionar una zona")

        username = self.username.text().strip()
        password = self.password.text().strip()
        user_id = self.cliente.get("usuario") if self.cliente else None

        if username and not user_id:
            if not password:
                raise ValueError("La contraseña es obligatoria cuando se crea un usuario")

    def build_cliente_data(self, user_id=None):
        data = {
            "nombre": self.nombre.text().strip(),
            "apellido": self.apellido.text().strip(),
            "nro_documento": self.nro_documento.text().strip(),
            "telefono": self.telefono.text().strip(),
            "email": self.email.text().strip(),
            "direccion": self.direccion.text().strip(),
            "codigo_postal": self.codigo_postal.text().strip(),
            "localidad": self.localidad.text().strip(),
            "provincia": self.provincia.text().strip(),
            "zona": self.zona.currentData(),
        }

        if user_id is not None:
            data["usuario"] = user_id

        return data

    def add_new_zona(self):
        text, ok = QInputDialog.getText(
            self,
            "Agregar Zona",
            "Nombre de la zona:"
        )

        if ok and text.strip():
            try:
                nueva_zona = self.zona_service.crear(
                    {
                        "nombre": text.strip(),
                        "descripcion": ""
                    }
                )

                self.load_zonas()

                index = self.zona.findData(nueva_zona["id"])
                if index >= 0:
                    self.zona.setCurrentIndex(index)

                QMessageBox.information(
                    self,
                    "OK",
                    f"Zona '{text.strip()}' creada correctamente",
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def save(self):
        try:
            self.validate_data()

            if self.cliente:
                username = self.username.text().strip()
                user_id = self.cliente.get("usuario")

                if not user_id and username:
                    password = self.password.text().strip()
                    user = self.user_service.crear(
                        {
                            "username": username,
                            "password": password,
                        }
                    )
                    user_id = user["id"]

                data = self.build_cliente_data(user_id=user_id)
                self.cliente_service.actualizar(self.cliente["id"], data)

                QMessageBox.information(
                    self,
                    "OK",
                    "Cliente actualizado correctamente",
                )
            else:
                username = self.username.text().strip()
                password = self.password.text().strip()
                user_id = None

                if username:
                    user = self.user_service.crear(
                        {
                            "username": username,
                            "password": password,
                        }
                    )
                    user_id = user["id"]

                cliente_data = self.build_cliente_data(user_id=user_id)
                self.cliente_service.crear(cliente_data)

                QMessageBox.information(
                    self,
                    "OK",
                    "Cliente creado correctamente",
                )

            self.on_success()
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
