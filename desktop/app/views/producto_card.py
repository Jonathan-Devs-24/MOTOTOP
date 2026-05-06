# desktop/app/views/producto_card.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox
)

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import requests

from views.producto_form import ProductoForm
from views.promocion_form import PromocionForm

from services.rubro_service import RubroService
from services.proveedor_service import ProveedorService
from services.promocion_service import PromocionService
from services.producto_promocion_service import ProductoPromocionService


class ProductoCard(QWidget):

    def __init__(self, producto, service, refresh_callback):
        super().__init__()

        self.producto = producto
        self.service = service
        self.refresh = refresh_callback

        self.rubro_service = RubroService(
            self.service.http
        )

        self.proveedor_service = ProveedorService(
            self.service.http
        )

        self.promocion_service = PromocionService(
            self.service.http
        )

        self.producto_promocion_service = ProductoPromocionService(
            self.service.http
        )

        self.tiene_promocion = False
        self.promocion_rel_id = None

        self.check_promocion()

        # =========================
        # LAYOUT
        # =========================

        layout = QVBoxLayout()

        # =========================
        # IMAGEN
        # =========================

        self.img_label = QLabel()
        self.img_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        if producto.get("img"):

            try:
                response = requests.get(
                    producto["img"]
                )

                pixmap = QPixmap()
                pixmap.loadFromData(
                    response.content
                )

                self.img_label.setPixmap(
                    pixmap.scaled(
                        150,
                        150,
                        Qt.AspectRatioMode.KeepAspectRatio
                    )
                )

            except:
                self.img_label.setText(
                    "Error cargando imagen"
                )

        else:
            self.img_label.setText("Sin imagen")

        layout.addWidget(self.img_label)

        # =========================
        # PROMOCIÓN
        # =========================

        if self.tiene_promocion:

            promo_label = QLabel(
                "🔥 EN PROMOCIÓN"
            )

            promo_label.setStyleSheet("""
                background-color: #ff4444;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 6px;
            """)

            promo_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            layout.addWidget(promo_label)

        # =========================
        # INFO
        # =========================

        nombre = QLabel(producto["nombre"])
        nombre.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        layout.addWidget(nombre)

        layout.addWidget(
            QLabel(f"ID: {producto['id']}")
        )

        layout.addWidget(
            QLabel(
                f"Precio: ${producto['precio_base']}"
            )
        )

        layout.addWidget(
            QLabel(
                f"Stock: {producto['stock']}"
            )
        )

        # =========================
        # BOTONES
        # =========================

        self.btn_edit = QPushButton(
            "Editar"
        )

        self.btn_delete = QPushButton(
            "Eliminar"
        )

        self.btn_promo = QPushButton(
            "Agregar promoción"
        )

        self.btn_remove_promo = QPushButton(
            "Quitar promoción"
        )

        # =========================
        # CONEXIONES
        # =========================

        self.btn_edit.clicked.connect(
            self.open_edit_form
        )

        self.btn_delete.clicked.connect(
            self.delete
        )

        self.btn_promo.clicked.connect(
            self.open_promocion_form
        )

        self.btn_remove_promo.clicked.connect(
            self.remove_promocion
        )

        # =========================
        # LAYOUT BOTONES
        # =========================

        layout.addWidget(self.btn_edit)

        layout.addWidget(self.btn_promo)

        if self.tiene_promocion:
            layout.addWidget(
                self.btn_remove_promo
            )

        layout.addWidget(self.btn_delete)

        # =========================
        # ESTILO CARD
        # =========================

        if self.tiene_promocion:

            self.setStyleSheet("""
                QWidget {
                    border: 2px solid #ff4444;
                    border-radius: 10px;
                    padding: 8px;
                }
            """)

        else:

            self.setStyleSheet("""
                QWidget {
                    border: 1px solid #999;
                    border-radius: 10px;
                    padding: 8px;
                }
            """)

        self.setLayout(layout)

    # =========================
    # PROMOCIONES
    # =========================

    def check_promocion(self):

        try:

            promociones = (
                self.producto_promocion_service
                .listar()
            )

            data = promociones.get(
                "results",
                promociones
            )

            for rel in data:

                if (
                    rel["producto"]
                    == self.producto["id"]
                ):

                    self.tiene_promocion = True
                    self.promocion_rel_id = rel["id"]

                    break

        except:
            pass

    # =========================
    # EDITAR
    # =========================

    def open_edit_form(self):

        self.form = ProductoForm(
            self.service,
            self.rubro_service,
            self.proveedor_service,
            self.refresh,
            self.producto
        )

        self.form.show()

    # =========================
    # PROMOCIÓN
    # =========================

    def open_promocion_form(self):

        self.form = PromocionForm(
            self.producto,
            self.promocion_service,
            self.producto_promocion_service,
            self.refresh
        )

        self.form.show()

    # =========================
    # QUITAR PROMO
    # =========================

    def remove_promocion(self):

        confirm = QMessageBox.question(
            self,
            "Confirmar",
            "Quitar promoción?"
        )

        if (
            confirm
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:

            self.producto_promocion_service.eliminar(
                self.promocion_rel_id
            )

            QMessageBox.information(
                self,
                "OK",
                "Promoción eliminada"
            )

            self.refresh()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

    # =========================
    # ELIMINAR
    # =========================

    def delete(self):

        confirm = QMessageBox.question(
            self,
            "Confirmar",
            f"Eliminar {self.producto['nombre']}?"
        )

        if (
            confirm
            == QMessageBox.StandardButton.Yes
        ):

            try:

                self.service.eliminar(
                    self.producto["id"]
                )

                self.refresh()

            except Exception as e:

                QMessageBox.critical(
                    self,
                    "Error",
                    str(e)
                )