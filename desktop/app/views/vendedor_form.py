#views/vendedor_form.py
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

        self.setWindowTitle(
            "Editar Vendedor" if vendedor else "Nuevo Vendedor"
        )
        self.resize(500, 700)

        self.zonas = []

        layout = QVBoxLayout()

        # =========================
        # DATOS PERSONALES
        # =========================

        layout.addWidget(QLabel("Nombre"))
        self.nombre = QLineEdit()
        layout.addWidget(self.nombre)

        layout.addWidget(QLabel("Apellido"))
        self.apellido = QLineEdit()
        layout.addWidget(self.apellido)

        layout.addWidget(QLabel("Teléfono"))
        self.telefono = QLineEdit()
        layout.addWidget(self.telefono)

        layout.addWidget(QLabel("Comisión"))
        self.comision = QLineEdit()
        self.comision.setPlaceholderText("Ejemplo: 10.50")
        layout.addWidget(self.comision)

        # =========================
        # ESTADO
        # =========================

        layout.addWidget(QLabel("Estado"))
        self.estado = QComboBox()
        self.estado.addItem("Activo", "activo")
        self.estado.addItem("Inactivo", "inactivo")
        layout.addWidget(self.estado)

        # =========================
        # ZONA
        # =========================

        zona_layout = QHBoxLayout()

        zona_layout.addWidget(QLabel("Zona"))
        self.zona = QComboBox()
        zona_layout.addWidget(self.zona)

        self.btn_add_zona = QPushButton("+")
        self.btn_add_zona.setMaximumWidth(40)
        self.btn_add_zona.clicked.connect(self.add_new_zona)
        zona_layout.addWidget(self.btn_add_zona)

        layout.addLayout(zona_layout)

        # =========================
        # CREDENCIALES
        # =========================

        layout.addWidget(QLabel("Nombre de usuario"))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Contraseña"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        # =========================
        # BOTÓN GUARDAR
        # =========================

        self.btn_save = QPushButton("Guardar")
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)

        layout.addStretch()

        self.setLayout(layout)

        # =========================
        # CARGA INICIAL
        # =========================

        self.load_zonas()

        if self.vendedor:
            self.load_vendedor()

    # ======================================================
    # CARGAR ZONAS
    # ======================================================

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

    # ======================================================
    # CARGAR DATOS PARA EDICIÓN
    # ======================================================

    def load_vendedor(self):
        v = self.vendedor

        self.nombre.setText(v.get("nombre", ""))
        self.apellido.setText(v.get("apellido", ""))
        self.telefono.setText(v.get("telefono", ""))
        self.comision.setText(str(v.get("comision", "")))

        # Estado
        estado_value = v.get("estado", "activo")
        index_estado = self.estado.findData(estado_value)
        if index_estado >= 0:
            self.estado.setCurrentIndex(index_estado)

        # Zona
        zona_id = v.get("zona")
        index_zona = self.zona.findData(zona_id)
        if index_zona >= 0:
            self.zona.setCurrentIndex(index_zona)

        # Cargar datos del usuario
        usuario_id = v.get("usuario")
        if usuario_id:
            try:
                usuario_data = self.user_service.obtener(usuario_id)
                self.username.setText(usuario_data.get("username", ""))
                # La contraseña está hasheada, mostrar un mensaje
                self.password.setText("[Contraseña hasheada en el servidor]")
            except Exception as e:
                self.username.setText("[No disponible]")
                self.password.setText("[No disponible]")

        # En edición mostrar credenciales en modo lectura
        self.username.setReadOnly(True)
        self.password.setReadOnly(True)
        # Mostrar contraseña en modo lectura (no oculta)
        self.password.setEchoMode(QLineEdit.EchoMode.Normal)
        # Desabilitar agregar zona nueva en edición
        self.btn_add_zona.setDisabled(True)

    # ======================================================
    # AGREGAR NUEVA ZONA
    # ======================================================

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

                # Recargar zonas
                self.load_zonas()

                # Seleccionar la zona recién creada
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

    # ======================================================
    # VALIDACIÓN
    # ======================================================

    def validate_data(self):
        nombre = self.nombre.text().strip()
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not nombre:
            raise ValueError("El nombre es obligatorio")

        if self.zona.currentData() is None:
            raise ValueError("Debe seleccionar una zona")

        if not self.vendedor:
            if not username:
                raise ValueError("El nombre de usuario es obligatorio")

            if not password:
                raise ValueError("La contraseña es obligatoria")

    # ======================================================
    # OBTENER DATOS DEL FORMULARIO
    # ======================================================

    def build_vendedor_data(self, user_id=None):
        data = {
            "nombre": self.nombre.text().strip(),
            "apellido": self.apellido.text().strip(),
            "telefono": self.telefono.text().strip(),
            "comision": self.comision.text().strip() or "0",
            "estado": self.estado.currentData(),
            "zona": self.zona.currentData(),
        }

        if user_id is not None:
            data["usuario"] = user_id

        return data

    # ======================================================
    # GUARDAR
    # ======================================================

    def save(self):
        try:
            self.validate_data()

            # ==========================================
            # EDICIÓN
            # ==========================================
            if self.vendedor:
                data = self.build_vendedor_data()

                self.vendedor_service.actualizar(
                    self.vendedor["id"],
                    data,
                )

                QMessageBox.information(
                    self,
                    "OK",
                    "Vendedor actualizado correctamente",
                )

            # ==========================================
            # CREACIÓN
            # ==========================================
            else:
                # 1. Crear usuario
                user = self.user_service.crear(
                    {
                        "username": self.username.text().strip(),
                        "password": self.password.text().strip(),
                    }
                )

                # 2. Crear vendedor
                vendedor_data = self.build_vendedor_data(
                    user_id=user["id"]
                )

                self.vendedor_service.crear(vendedor_data)

                QMessageBox.information(
                    self,
                    "OK",
                    "Vendedor creado correctamente",
                )

            # Refrescar lista y cerrar
            self.on_success()
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

