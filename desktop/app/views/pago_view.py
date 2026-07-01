# desktop/app/views/pago_view.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QLabel,
    QAbstractItemView,
    QHeaderView,
    QScrollArea,
    QFrame
)
from views.pago_form import PagoForm

# Paleta de diseño unificada para fondos claros: Blanco, Gris Claro, detalles en Negro y acentos en Rojo
QSS_STYLE_CLARO = """
    QWidget {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        color: #212529;
    }
    
    /* Indicador del Panel Principal */
    QLabel#infoLabel {
        background-color: #ffffff;
        border-left: 4px solid #dc3545;
        padding: 14px;
        font-size: 15px;
        font-weight: bold;
        border-radius: 4px;
        color: #212529;
        border: 1px solid #e9ecef;
    }
    
    /* Contenedor con scroll para las tarjetas */
    QScrollArea {
        border: none;
        background-color: #f8f9fa;
    }
    
    /* Diseño de la Tarjeta de cada Factura */
    QFrame#cardFactura {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    
    QLabel#cardTitle {
        font-size: 14px;
        font-weight: bold;
        color: #1a1a1a;
    }
    
    QLabel#cardBadgePendiente {
        background-color: #fff3cd;
        color: #856404;
        padding: 3px 8px;
        font-weight: bold;
        border-radius: 4px;
        font-size: 11px;
    }
    
    QLabel#cardBadgePagada {
        background-color: #d4edda;
        color: #155724;
        padding: 3px 8px;
        font-weight: bold;
        border-radius: 4px;
        font-size: 11px;
    }
    
    QLabel#cardSummaryText {
        font-size: 12px;
        color: #495057;
        font-weight: 500;
    }
    
    /* Botones de acción dentro de la tarjeta */
    QPushButton {
        background-color: #212529;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
        min-width: 70px;
    }
    QPushButton:hover {
        background-color: #dc3545;
    }
    QPushButton:pressed {
        background-color: #b02a37;
    }
    QPushButton#btn_recargar_global {
        background-color: #ffffff;
        color: #212529;
        border: 1px solid #ced4da;
        padding: 8px 16px;
    }
    QPushButton#btn_recargar_global:hover {
        background-color: #e2e6ea;
        color: #212529;
    }
    
    /* Grilla de pagos interna de la tarjeta */
    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        gridline-color: #f1f3f5;
        border-radius: 4px;
    }
    QTableWidget::item {
        padding: 5px;
        color: #495057;
    }
    QTableWidget::item:selected {
        background-color: #f1f3f5;
        color: #dc3545;
        font-weight: bold;
    }
    QHeaderView::section {
        background-color: #f1f3f5;
        color: #495057;
        padding: 6px;
        border: 1px solid #e9ecef;
        font-weight: bold;
        font-size: 11px;
    }
    
    QScrollBar:vertical {
        border: none;
        background: #f8f9fa;
        width: 8px;
    }
    QScrollBar::handle:vertical {
        background: #ced4da;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #adb5bd;
    }
"""

class PagoView(QWidget):

    def __init__(self, factura=None, pago_service=None):
        super().__init__()

        self.factura = factura
        self.service = pago_service

        # Definición del alcance de la ventana
        if self.factura:
            self.setWindowTitle(f"Pagos - Factura #{self.factura['id']}")
            self.resize(750, 480)
        else:
            self.setWindowTitle("Cobranzas - Panel General")
            self.resize(900, 650)
            
        self.setStyleSheet(QSS_STYLE_CLARO)

        # Layout Principal de la Sección
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Indicador Superior
        self.info = QLabel("")
        self.info.setObjectName("infoLabel")
        self.main_layout.addWidget(self.info)

        if self.factura:
            # === VISTA INDIVIDUAL DESDE UNA FACTURA ESPECÍFICA ===
            buttons_layout = QHBoxLayout()
            self.btn_crear = QPushButton("Crear")
            self.btn_editar = QPushButton("Editar")
            self.btn_eliminar = QPushButton("Eliminar")
            self.btn_recargar = QPushButton("Recargar")

            self.btn_crear.clicked.connect(self.crear_pago)
            self.btn_editar.clicked.connect(self.editar_pago)
            self.btn_eliminar.clicked.connect(self.eliminar_pago)
            self.btn_recargar.clicked.connect(self.cargar_pagos)

            buttons_layout.addWidget(self.btn_crear)
            buttons_layout.addWidget(self.btn_editar)
            buttons_layout.addWidget(self.btn_eliminar)
            buttons_layout.addStretch()  
            buttons_layout.addWidget(self.btn_recargar)
            self.main_layout.addLayout(buttons_layout)

            self.table = QTableWidget()
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["ID", "Monto", "Método", "Estado", "Referencia"])
            self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.main_layout.addWidget(self.table)
        else:
            # === VISTA GENERAL DE COBRANZAS (DISEÑO POR TARJETAS CLARAS) ===
            top_actions = QHBoxLayout()
            self.btn_recargar_global = QPushButton("Recargar Panel")
            self.btn_recargar_global.setObjectName("btn_recargar_global")
            self.btn_recargar_global.clicked.connect(self.cargar_pagos)
            top_actions.addStretch()
            top_actions.addWidget(self.btn_recargar_global)
            self.main_layout.addLayout(top_actions)

            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_widget = QWidget()
            self.scroll_layout = QVBoxLayout(self.scroll_widget)
            self.scroll_layout.setSpacing(15)
            self.scroll_layout.setContentsMargins(0, 0, 0, 0)
            self.scroll_area.setWidget(self.scroll_widget)
            self.main_layout.addWidget(self.scroll_area)

        self.setLayout(self.main_layout)
        self.cargar_pagos()

    def cargar_pagos(self):
        try:
            if self.factura:
                # 1. Solicitar los datos al servicio
                response = self.service.listar_por_factura(self.factura["id"])
                
                # FILTRO DE SEGURIDAD LOCAL: Asegura aislar solo los pagos que corresponden a ESTA factura
                pagos = [p for p in response["results"] if int(p["factura"]) == int(self.factura["id"])]
                
                total_f = float(self.factura["total"])
                total_p = sum(float(p["monto"]) for p in pagos if p["estado"].lower() == "completado")
                pendiente = total_f - total_p

                self.info.setText(
                    f"Factura #{self.factura['id']}  |  Total: ${total_f:.2f}  |  "
                    f"Pagado: ${total_p:.2f}  |  Pendiente: ${pendiente:.2f}"
                )

                # 2. Limpiar filas residuales e inicializar la grilla con el tamaño correcto
                self.table.setRowCount(0)
                self.table.setRowCount(len(pagos))
                
                for row, p in enumerate(pagos):
                    self.table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
                    self.table.setItem(row, 1, QTableWidgetItem(f"$ {p['monto']}"))
                    self.table.setItem(row, 2, QTableWidgetItem(p["metodo_pago"].upper()))
                    self.table.setItem(row, 3, QTableWidgetItem(p["estado"].upper()))
                    self.table.setItem(row, 4, QTableWidgetItem(str(p["referencia"]) if p["referencia"] else "-"))
            else:
                # === EL BLOQUE ELSE SE CONSERVA EXACTAMENTE IGUAL ===
                self.info.setText("Listado General de Cobranzas — Control de Comprobantes")
                
                while self.scroll_layout.count():
                    item = self.scroll_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                response = self.service.listar()
                todos_los_pagos = response["results"]

                pagos_por_factura = {}
                for p in todos_los_pagos:
                    f_id = p["factura"]
                    if f_id not in pagos_por_factura:
                        pagos_por_factura[f_id] = []
                    pagos_por_factura[f_id].append(p)

                for f_id, lista_pagos in pagos_por_factura.items():
                    card = QFrame()
                    card.setObjectName("cardFactura")
                    card_layout = QVBoxLayout(card)
                    card_layout.setContentsMargins(15, 15, 15, 15)
                    card_layout.setSpacing(12)

                    header_layout = QHBoxLayout()
                    lbl_titulo = QLabel(f"Factura #{f_id}")
                    lbl_titulo.setObjectName("cardTitle")
                    header_layout.addWidget(lbl_titulo)

                    total_pagado = sum(float(p["monto"]) for p in lista_pagos if p["estado"].lower() == "completado")
                    
                    lbl_resumen = QLabel(f"Total Cobrado: ${total_pagado:.2f}  |  Transacciones: {len(lista_pagos)}")
                    lbl_resumen.setObjectName("cardSummaryText")
                    header_layout.addWidget(lbl_resumen)
                    header_layout.addStretch()

                    card_buttons = QHBoxLayout()
                    btn_edit = QPushButton("Editar")
                    btn_delete = QPushButton("Eliminar")
                    
                    btn_edit.clicked.connect(lambda checked, fid=f_id: self.editar_pago_general(fid))
                    btn_delete.clicked.connect(lambda checked, fid=f_id: self.eliminar_pago_general(fid))
                    
                    card_buttons.addWidget(btn_edit)
                    card_buttons.addWidget(btn_delete)
                    header_layout.addLayout(card_buttons)
                    card_layout.addLayout(header_layout)

                    sub_table = QTableWidget()
                    sub_table.setObjectName(f"table_factura_{f_id}")
                    sub_table.setColumnCount(5)
                    sub_table.setHorizontalHeaderLabels(["ID Pago", "Monto", "Método", "Estado", "Referencia"])
                    sub_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
                    sub_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
                    sub_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                    sub_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                    sub_table.setFixedHeight(110)
                    
                    sub_table.setRowCount(len(lista_pagos))
                    for row, p in enumerate(lista_pagos):
                        sub_table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
                        sub_table.setItem(row, 1, QTableWidgetItem(f"$ {p['monto']}"))
                        sub_table.setItem(row, 2, QTableWidgetItem(p["metodo_pago"].upper()))
                        sub_table.setItem(row, 3, QTableWidgetItem(p["estado"].upper()))
                        sub_table.setItem(row, 4, QTableWidgetItem(str(p["referencia"]) if p["referencia"] else "-"))
                    
                    card_layout.addWidget(sub_table)
                    self.scroll_layout.addWidget(card)
                
                self.scroll_layout.addStretch()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # === CONTROLES DE EDICIÓN PARA LA ENTRADA GENERAL ===
    def obtener_id_desde_subtabla(self, factura_id):
        tabla = self.findChild(QTableWidget, f"table_factura_{factura_id}")
        if tabla:
            fila = tabla.currentRow()
            if fila >= 0:
                return int(tabla.item(fila, 0).text())
        return None

    def editar_pago_general(self, factura_id):
        pago_id = self.obtener_id_desde_subtabla(factura_id)
        if not pago_id:
            QMessageBox.warning(self, "Atención", "Seleccione una fila en la tabla de la factura correspondiente.")
            return
        try:
            pago = self.service.obtener(pago_id)
            dialog = PagoForm(self, factura_id=factura_id, pago=pago)
            if dialog.exec():
                self.service.actualizar(pago_id, dialog.obtener_datos())
                self.cargar_pagos()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def eliminar_pago_general(self, factura_id):
        pago_id = self.obtener_id_desde_subtabla(factura_id)
        if not pago_id:
            QMessageBox.warning(self, "Atención", "Seleccione una fila en la tabla de la factura correspondiente.")
            return
        if QMessageBox.question(self, "Confirmar", "¿Desea eliminar el pago seleccionado?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                self.service.eliminar(pago_id)
                self.cargar_pagos()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # === CONTROLES DE EDICIÓN PARA VISTA INDIVIDUAL (DESDE FACTURAS) ===
    def obtener_id_seleccionado(self):
        if not self.table:
            return None
        fila = self.table.currentRow()
        return int(self.table.item(fila, 0).text()) if fila >= 0 else None

    def crear_pago(self):
        if not self.factura: return
        dialog = PagoForm(self, factura_id=self.factura["id"])
        if dialog.exec():
            try:
                self.service.crear(dialog.obtener_datos())
                self.cargar_pagos()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def editar_pago(self):
        pago_id = self.obtener_id_seleccionado()
        if not pago_id: return
        try:
            pago = self.service.obtener(pago_id)
            dialog = PagoForm(self, factura_id=self.factura["id"], pago=pago)
            if dialog.exec():
                self.service.actualizar(pago_id, dialog.obtener_datos())
                self.cargar_pagos()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def eliminar_pago(self):
        pago_id = self.obtener_id_seleccionado()
        if not pago_id or QMessageBox.question(self, "Confirmar", "¿Eliminar pago?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.eliminar(pago_id)
            self.cargar_pagos()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
            