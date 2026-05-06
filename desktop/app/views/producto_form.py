# desktop/app/views/producto_form.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QListWidget, QLabel, QMessageBox, QListWidgetItem, QFileDialog
)


class ProductoForm(QWidget):

    def __init__(self, producto_service, rubro_service, proveedor_service, on_success):
        super().__init__()

        self.producto_service = producto_service
        self.rubro_service = rubro_service
        self.proveedor_service = proveedor_service
        self.on_success = on_success

        self.image_path = None

        self.setWindowTitle("Nuevo Producto")

        layout = QVBoxLayout()

        # =========================
        # CAMPOS
        # =========================

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre")

        self.precio = QLineEdit()
        self.precio.setPlaceholderText("Precio")

        self.stock = QLineEdit()
        self.stock.setPlaceholderText("Stock")

        layout.addWidget(self.nombre)
        layout.addWidget(self.precio)
        layout.addWidget(self.stock)

        # =========================
        # IMAGEN
        # =========================

        self.btn_img = QPushButton("Seleccionar imagen")
        self.btn_img.clicked.connect(self.select_image)

        self.lbl_img = QLabel("Sin imagen")

        layout.addWidget(self.btn_img)
        layout.addWidget(self.lbl_img)

        # =========================
        # RUBROS
        # =========================

        layout.addWidget(QLabel("Rubros"))

        self.rubros_list = QListWidget()
        self.rubros_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.rubros_list)

        self.rubro_input = QLineEdit()
        self.rubro_input.setPlaceholderText("Nuevo rubro")

        self.btn_add_rubro = QPushButton("Agregar rubro")
        self.btn_add_rubro.clicked.connect(self.create_rubro)

        self.btn_delete_rubro = QPushButton("Eliminar rubro seleccionado")
        self.btn_delete_rubro.clicked.connect(self.delete_rubro)

        layout.addWidget(self.rubro_input)
        layout.addWidget(self.btn_add_rubro)
        layout.addWidget(self.btn_delete_rubro)

        # =========================
        # PROVEEDORES
        # =========================

        layout.addWidget(QLabel("Proveedores"))

        self.prov_list = QListWidget()
        self.prov_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.prov_list)

        self.prov_nombre = QLineEdit()
        self.prov_nombre.setPlaceholderText("Nombre")

        self.prov_apellido = QLineEdit()
        self.prov_apellido.setPlaceholderText("Apellido")

        self.prov_tel = QLineEdit()
        self.prov_tel.setPlaceholderText("Teléfono")

        self.prov_email = QLineEdit()
        self.prov_email.setPlaceholderText("Email")

        self.btn_add_prov = QPushButton("Agregar proveedor")
        self.btn_add_prov.clicked.connect(self.create_proveedor)

        self.btn_delete_prov = QPushButton("Eliminar proveedor seleccionado")
        self.btn_delete_prov.clicked.connect(self.delete_proveedor)

        layout.addWidget(self.prov_nombre)
        layout.addWidget(self.prov_apellido)
        layout.addWidget(self.prov_tel)
        layout.addWidget(self.prov_email)
        layout.addWidget(self.btn_add_prov)
        layout.addWidget(self.btn_delete_prov)

        # =========================
        # GUARDAR
        # =========================

        self.btn_save = QPushButton("Guardar")
        self.btn_save.clicked.connect(self.save)

        layout.addWidget(self.btn_save)

        self.setLayout(layout)

        self.load_options()

    # =========================
    # CARGA DE DATOS
    # =========================

    def load_options(self):
        try:
            self.rubros_list.clear()
            self.prov_list.clear()

            rubros = self.rubro_service.listar()
            proveedores = self.proveedor_service.listar()

            rubros_data = rubros.get("results", rubros)
            proveedores_data = proveedores.get("results", proveedores)

            for r in rubros_data:
                item = QListWidgetItem(r["nombre"])
                item.setData(1, r["id"])
                self.rubros_list.addItem(item)

            for p in proveedores_data:
                item = QListWidgetItem(p["nombre"])
                item.setData(1, p["id"])
                self.prov_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def get_selected_ids(self, list_widget):
        return [item.data(1) for item in list_widget.selectedItems()]

    # =========================
    # RUBROS
    # =========================

    def create_rubro(self):
        try:
            nombre = self.rubro_input.text().strip()
            if not nombre:
                raise ValueError("Nombre obligatorio")

            self.rubro_service.crear({"nombre": nombre})
            self.rubro_input.clear()
            self.load_options()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_rubro(self):
        try:
            for item in self.rubros_list.selectedItems():
                self.rubro_service.eliminar(item.data(1))

            self.load_options()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # =========================
    # PROVEEDORES
    # =========================

    def create_proveedor(self):
        try:
            data = {
                "nombre": self.prov_nombre.text().strip(),
                "apellido": self.prov_apellido.text().strip(),
                "telefono": self.prov_tel.text().strip(),
                "email": self.prov_email.text().strip(),
            }

            if not data["nombre"]:
                raise ValueError("Nombre obligatorio")

            self.proveedor_service.crear(data)

            self.prov_nombre.clear()
            self.prov_apellido.clear()
            self.prov_tel.clear()
            self.prov_email.clear()

            self.load_options()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_proveedor(self):
        try:
            for item in self.prov_list.selectedItems():
                self.proveedor_service.eliminar(item.data(1))

            self.load_options()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # =========================
    # IMAGEN
    # =========================

    def select_image(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file:
            self.image_path = file
            self.lbl_img.setText(file)

    # =========================
    # SAVE
    # =========================

    def save(self):
        try:
            nombre = self.nombre.text().strip()
            precio = float(self.precio.text())
            stock = int(self.stock.text())

            if not nombre:
                raise ValueError("Nombre obligatorio")

            data = {
                "nombre": nombre,
                "precio_base": precio,
                "stock": stock,
                "rubros": self.get_selected_ids(self.rubros_list),
                "proveedores": self.get_selected_ids(self.prov_list),
            }

            files = None
            if self.image_path:
                files = {"img": open(self.image_path, "rb")}

            self.producto_service.crear(data, files)

            QMessageBox.information(self, "OK", "Producto creado")

            self.on_success()
            self.close()

        except ValueError as ve:
            QMessageBox.warning(self, "Validación", str(ve))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
