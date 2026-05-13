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
)


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

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nombre"))
        self.nombre = QLineEdit()
        layout.addWidget(self.nombre)

        layout.addWidget(QLabel("Apellido"))
        self.apellido = QLineEdit()
        layout.addWidget(self.apellido)

        layout.addWidget(QLabel("Nro. documento"))
        self.nro_documento = QLineEdit()
        layout.addWidget(self.nro_documento)

        layout.addWidget(QLabel("Teléfono"))
        self.telefono = QLineEdit()
        layout.addWidget(self.telefono)

        layout.addWidget(QLabel("Email"))
        self.email = QLineEdit()
        layout.addWidget(self.email)

        layout.addWidget(QLabel("Dirección"))
        self.direccion = QLineEdit()
        layout.addWidget(self.direccion)

        layout.addWidget(QLabel("Código Postal"))
        self.codigo_postal = QLineEdit()
        layout.addWidget(self.codigo_postal)

        layout.addWidget(QLabel("Localidad"))
        self.localidad = QLineEdit()
        layout.addWidget(self.localidad)

        layout.addWidget(QLabel("Provincia"))
        self.provincia = QLineEdit()
        layout.addWidget(self.provincia)

        zona_layout = QHBoxLayout()
        zona_layout.addWidget(QLabel("Zona"))
        self.zona = QComboBox()
        zona_layout.addWidget(self.zona)

        self.btn_add_zona = QPushButton("+")
        self.btn_add_zona.setMaximumWidth(40)
        self.btn_add_zona.clicked.connect(self.add_new_zona)
        zona_layout.addWidget(self.btn_add_zona)
        layout.addLayout(zona_layout)

        layout.addWidget(QLabel("Nombre de usuario (opcional)"))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Contraseña (opcional)"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        self.btn_save = QPushButton("Guardar")
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)

        layout.addStretch()

        self.setLayout(layout)

        self.load_zonas()

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
