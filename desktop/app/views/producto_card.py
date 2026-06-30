# desktop/app/views/producto_card.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QStyle,      
    QStyleOption
)

from PyQt6.QtGui import QPixmap, QPainter
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

        self.rubro_service = RubroService(self.service.http)
        self.proveedor_service = ProveedorService(self.service.http)
        self.promocion_service = PromocionService(self.service.http)
        self.producto_promocion_service = ProductoPromocionService(self.service.http)

        self.tiene_promocion = False
        self.promocion_rel_id = None

        self.check_promocion()

        # Layout principal de la tarjeta
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # =========================
        # IMAGEN (Contenedor limpio)
        # =========================
        self.img_label = QLabel()
        self.img_label.setObjectName("product_image")
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setMinimumSize(150, 150)

        if producto.get("img"):
            try:
                response = requests.get(producto["img"], timeout=5)
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.img_label.setPixmap(
                    pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )
            except:
                self.img_label.setText("Error al cargar imagen")
        else:
            self.img_label.setText("Sin imagen")

        layout.addWidget(self.img_label)

        # =========================
        # ETIQUETA DE PROMOCIÓN
        # =========================
        if self.tiene_promocion:
            promo_label = QLabel("🔥 EN PROMOCIÓN")
            promo_label.setObjectName("promo_tag")
            promo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(promo_label)

        # =========================
        # INFORMACIÓN DEL PRODUCTO
        # =========================
        nombre = QLabel(producto["nombre"])
        nombre.setObjectName("product_title")
        nombre.setWordWrap(True)
        layout.addWidget(nombre)

        # Detalle secundario (ID)
        lbl_id = QLabel(f"ID: {producto['id']}")
        lbl_id.setObjectName("product_id")
        layout.addWidget(lbl_id)

        # Contenedor horizontal para precio y stock
        meta_layout = QHBoxLayout()
        
        lbl_precio = QLabel(f"${float(producto['precio_base']):.2f}")
        lbl_precio.setObjectName("product_price")
        
        lbl_stock = QLabel(f"Stock: {producto['stock']}")
        lbl_stock.setObjectName("product_stock")
        
        meta_layout.addWidget(lbl_precio)
        meta_layout.addStretch()
        meta_layout.addWidget(lbl_stock)
        layout.addLayout(meta_layout)

        layout.addStretch()

        # =========================
        # BOTONES DE ACCIÓN
        # =========================
        self.btn_edit = QPushButton("Editar")
        self.btn_delete = QPushButton("Eliminar")
        self.btn_promo = QPushButton("+ Promo")
        self.btn_remove_promo = QPushButton("- Promo")

        self.btn_edit.setObjectName("btn_edit")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_promo.setObjectName("btn_promo")
        self.btn_remove_promo.setObjectName("btn_remove")

        # Conexiones
        self.btn_edit.clicked.connect(self.open_edit_form)
        self.btn_delete.clicked.connect(self.delete)
        self.btn_promo.clicked.connect(self.open_promocion_form)
        self.btn_remove_promo.clicked.connect(self.remove_promocion)

        # Layout de acciones en filas organizadas
        actions_layout_top = QHBoxLayout()
        actions_layout_top.addWidget(self.btn_edit)
        
        if self.tiene_promocion:
            actions_layout_top.addWidget(self.btn_remove_promo)
        else:
            actions_layout_top.addWidget(self.btn_promo)
            
        layout.addLayout(actions_layout_top)
        layout.addWidget(self.btn_delete)

        # =========================
        # HOJA DE ESTILOS DE LA TARJETA
        # =========================
        self.apply_card_styles()
        self.setLayout(layout)

    def apply_card_styles(self):
        # Determinamos el identificador del objeto según el estado
        if self.tiene_promocion:
            self.setObjectName("active_promo_card")
            border_style = "2px solid #e53935;"  # Borde rojo grueso
        else:
            self.setObjectName("standard_card")
            border_style = "2px solid #3a3a4a;"  # Borde gris oscuro definido

        self.setStyleSheet(f"""
            /* Forzar el contenedor externo de la tarjeta */
            QWidget#{self.objectName()} {{
                background-color: #ffffff;
                border: {border_style}
                border-radius: 8px;
            }}
            
            /* Evitar que los elementos internos hereden el borde de la tarjeta */
            QLabel {{
                border: none;
                background-color: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QLabel#product_title {{
                font-size: 15px;
                font-weight: bold;
                color: #1e1e24;
                padding-top: 5px;
            }}
            
            QLabel#product_id {{
                font-size: 11px;
                color: #7f8c8d;
                font-weight: bold;
            }}
            
            QLabel#product_price {{
                font-size: 17px;
                font-weight: bold;
                color: #e53935;
            }}
            
            QLabel#product_stock {{
                font-size: 12px;
                color: #475569;
                font-weight: 600;
            }}
            
            QLabel#promo_tag {{
                background-color: #e53935;
                color: #ffffff;
                font-size: 10px;
                font-weight: bold;
                padding: 4px;
                border-radius: 4px;
            }}
            
            QPushButton {{
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: bold;
                color: #ffffff;
            }}
            
            QPushButton#btn_edit {{ background-color: #2ecc71; }}
            QPushButton#btn_edit:hover {{ background-color: #27ae60; }}
            
            QPushButton#btn_promo {{ background-color: #ff9800; }}
            QPushButton#btn_promo:hover {{ background-color: #e68a00; }}
            
            QPushButton#btn_remove {{ background-color: #9c27b0; }}
            QPushButton#btn_remove:hover {{ background-color: #8e24aa; }}
            
            QPushButton#btn_delete {{ background-color: #e74c3c; }}
            QPushButton#btn_delete:hover {{ background-color: #c0392b; }}
        """)

    def paintEvent(self, event):
        """Obliga a Qt a renderizar las propiedades de fondo y borde del QSS"""
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
        painter.end()

    # =========================
    # LOGICA OPERATIVA RESGUARDADA
    # =========================
    def check_promocion(self):
        try:
            promociones = self.producto_promocion_service.listar()
            data = promociones.get("results", promociones)
            for rel in data:
                if rel["producto"] == self.producto["id"]:
                    self.tiene_promocion = True
                    self.promocion_rel_id = rel["id"]
                    break
        except:
            pass

    def open_edit_form(self):
        self.form = ProductoForm(
            self.service,
            self.rubro_service,
            self.proveedor_service,
            self.refresh,
            self.producto
        )
        self.form.show()

    def open_promocion_form(self):
        self.form = PromocionForm(
            self.producto,
            self.promocion_service,
            self.producto_promocion_service,
            self.refresh
        )
        self.form.show()

    def remove_promocion(self):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle("Confirmar")
        box.setText("¿Quitar promoción?")
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.setStyleSheet("""
            QMessageBox { background-color: #f5f6f8; }
            QLabel { color: #1e1e24; }
            QPushButton { background-color: #e2e8f0; color: #1e1e24; border: 1px solid #cbd5e1; padding: 6px 15px; }
            QPushButton:hover { background-color: #cbd5e1; }
        """)
        
        confirm = box.exec()
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self.producto_promocion_service.eliminar(self.promocion_rel_id)
            QMessageBox.information(self, "OK", "Promoción eliminada")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete(self):
        # Crear la caja de mensaje
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle("Confirmar")
        box.setText(f"¿Eliminar {self.producto['nombre']}?")
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        # Forzar estilos específicos para limpiar la herencia y ver los botones oscuros
        box.setStyleSheet("""
            QMessageBox {
                background-color: #f5f6f8;
            }
            QLabel {
                color: #1e1e24;
                font-size: 13px;
            }
            QPushButton {
                background-color: #e2e8f0;
                color: #1e1e24;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 6px 15px;
                font-weight: bold;
                min-width: 65px;
            }
            QPushButton:hover {
                background-color: #cbd5e1;
            }
        """)

        # Ejecutar y evaluar la respuesta
        confirm = box.exec()

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.eliminar(self.producto["id"])
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))