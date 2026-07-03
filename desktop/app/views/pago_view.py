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
        """
        Constructor de la vista de pagos.
        Puede recibir una factura específica (diccionario/objeto) o None (Vista General).
        """
        super().__init__()

        self.factura = factura
        self.service = pago_service
        # Extrae el ID limpio de la factura si fue provista
        self.factura_id = self._obtener_id_factura(self.factura)

        # Configura el título y tamaño de la ventana según el modo de apertura
        if self.factura_id is not None:
            self.setWindowTitle(f"Pagos - Factura #{self.factura_id}")
            self.resize(750, 480)
        else:
            self.setWindowTitle("Cobranzas - Panel General")
            self.resize(900, 650)
            
        self.setStyleSheet(QSS_STYLE_CLARO)

        # Inicializa el layout vertical principal
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Etiqueta informativa superior para saldos y títulos
        self.info = QLabel("")
        self.info.setObjectName("infoLabel")
        self.main_layout.addWidget(self.info)

        if self.factura:
            # === VISTA INDIVIDUAL DESDE UNA FACTURA ESPECÍFICA ===
            # Layout horizontal para las acciones de la vista individual
            buttons_layout = QHBoxLayout()
            self.btn_crear = QPushButton("Crear")
            self.btn_editar = QPushButton("Editar")
            self.btn_eliminar = QPushButton("Eliminar")
            self.btn_recargar = QPushButton("Recargar")

            # Conexión de señales de clicks a sus respectivos métodos
            self.btn_crear.clicked.connect(self.crear_pago)
            self.btn_editar.clicked.connect(self.editar_pago)
            self.btn_eliminar.clicked.connect(self.eliminar_pago)
            self.btn_recargar.clicked.connect(self.cargar_pagos)

            buttons_layout.addWidget(self.btn_crear)
            buttons_layout.addWidget(self.btn_editar)
            buttons_layout.addWidget(self.btn_eliminar)
            buttons_layout.addStretch()  # Empuja el botón recargar hacia la derecha
            buttons_layout.addWidget(self.btn_recargar)
            self.main_layout.addLayout(buttons_layout)

            # Configuración de la tabla única de pagos para la factura seleccionada
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
            # Layout superior para botón de actualización del panel completo
            top_actions = QHBoxLayout()
            self.btn_recargar_global = QPushButton("Recargar Panel")
            self.btn_recargar_global.setObjectName("btn_recargar_global")
            self.btn_recargar_global.clicked.connect(self.cargar_pagos)
            top_actions.addStretch()
            top_actions.addWidget(self.btn_recargar_global)
            self.main_layout.addLayout(top_actions)

            # Área de scroll para contener múltiples tarjetas dinámicamente sin desbordar la ventana
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_widget = QWidget()
            self.scroll_layout = QVBoxLayout(self.scroll_widget)
            self.scroll_layout.setSpacing(15)
            self.scroll_layout.setContentsMargins(0, 0, 0, 0)
            self.scroll_area.setWidget(self.scroll_widget)
            self.main_layout.addWidget(self.scroll_area)

        self.setLayout(self.main_layout)
        # Dispara la primera carga de datos al inicializar la vista
        self.cargar_pagos()

    def _obtener_id_factura(self, factura):
        """Helper para extraer el ID de factura de forma segura si viene como dict o modelo."""
        if isinstance(factura, dict):
            return factura.get("id")
        return getattr(factura, "id", None)

    def _obtener_total_factura(self):
        """Helper para extraer el importe total de la factura actual."""
        if isinstance(self.factura, dict):
            return self.factura.get("total")
        return getattr(self.factura, "total", None)

    def cargar_pagos(self):
        """
        === AQUÍ COMIENZA LO QUE ESTAMOS TRATANDO DE SOLUCIONAR ===
        Método central que recupera los datos desde la API y repobla la interfaz gráfica.
        """
        try:
            if self.factura_id is not None:
                # 1. Asegurar el ID de la factura actual como un entero limpio
                id_factura_actual = int(self.factura_id)

                # 2. SOLICITAR LOS DATOS AL SERVICIO (AQUÍ INTERVENIMOS PARA PASAR EL QUERY PARAMETER '?factura=')
                response = self.service.listar_por_factura(id_factura_actual)
                
                # Desempaquetar si la API devuelve un diccionario paginado con 'results' o una lista directa
                pagos_filtrados = response.get("results", response) if isinstance(response, dict) else response
                
                # 3. Cálculos basados ÚNICAMENTE en la lista devuelta por la API para esta factura
                total_f = float(self._obtener_total_factura() or 0)
                total_p = sum(float(p["monto"]) for p in pagos_filtrados if str(p["estado"]).lower() == "completado")
                pendiente = total_f - total_p

                # Actualiza la etiqueta informativa con los importes financieros procesados
                self.info.setText(
                    f"Factura #{id_factura_actual}  |  Total: ${total_f:.2f}  |  "
                    f"Pagado: ${total_p:.2f}  |  Pendiente: ${pendiente:.2f}"
                )

                # 4. LIMPIEZA ABSOLUTA DE LA TABLA ANTES DE REPOBLAR
                self.table.clearContents()
                self.table.setRowCount(0)
                
                # Establecemos el tamaño exacto de filas según los pagos validados por el backend
                self.table.setRowCount(len(pagos_filtrados))
                
                # 5. Llenar la tabla con los datos directamente
                for row, p in enumerate(pagos_filtrados):
                    self.table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
                    self.table.setItem(row, 1, QTableWidgetItem(f"$ {float(p['monto']):.2f}"))
                    self.table.setItem(row, 2, QTableWidgetItem(str(p["metodo_pago"]).upper()))
                    self.table.setItem(row, 3, QTableWidgetItem(str(p["estado"]).upper()))
                    self.table.setItem(row, 4, QTableWidgetItem(str(p["referencia"]) if p["referencia"] else "-"))
            else:
                # === VISTA GENERAL DE COBRANZAS ===
                # Configura el encabezado del panel general
                self.info.setText("Listado General de Cobranzas — Control de Comprobantes")
                
                # Limpia todos los widgets previos dentro del scroll layout para evitar duplicados visuales
                while self.scroll_layout.count():
                    item = self.scroll_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                # Petición general al servicio sin filtros locales
                response = self.service.listar()
                todos_los_pagos = response["results"] if isinstance(response, dict) else response

                # Agrupa la respuesta plana en un mapa indexado por ID de factura
                pagos_por_factura = {}
                for p in todos_los_pagos:
                    factura_campo = p.get("factura")
                    f_id = factura_campo.get("id") if isinstance(factura_campo, dict) else factura_campo
                    
                    if f_id not in pagos_por_factura:
                        pagos_por_factura[f_id] = []
                    pagos_por_factura[f_id].append(p)

                # Itera el mapa de agrupaciones para construir una tarjeta por cada factura
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

                    # Sumariza los montos cobrados cuyo estado sea estrictamente completado
                    total_pagado = sum(float(p["monto"]) for p in lista_pagos if str(p["estado"]).lower() == "completado")
                    
                    lbl_resumen = QLabel(f"Total Cobrado: ${total_pagado:.2f}  |  Transacciones: {len(lista_pagos)}")
                    lbl_resumen.setObjectName("cardSummaryText")
                    header_layout.addWidget(lbl_resumen)
                    header_layout.addStretch()

                    # Bloque de botones operativos para cada tarjeta individualizada
                    card_buttons = QHBoxLayout()
                    btn_edit = QPushButton("Editar")
                    btn_delete = QPushButton("Eliminar")
                    
                    # Conexiones con clausuras lambda para inyectar de forma segura el f_id iterado
                    btn_edit.clicked.connect(lambda checked, fid=f_id: self.editar_pago_general(fid))
                    btn_delete.clicked.connect(lambda checked, fid=f_id: self.eliminar_pago_general(fid))
                    
                    card_buttons.addWidget(btn_edit)
                    card_buttons.addWidget(btn_delete)
                    header_layout.addLayout(card_buttons)
                    card_layout.addLayout(header_layout)

                    # Inicializa la tabla embebida secundaria para listar los pagos de esta tarjeta
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
                        sub_table.setItem(row, 1, QTableWidgetItem(f"$ {float(p['monto']):.2f}"))
                        sub_table.setItem(row, 2, QTableWidgetItem(str(p["metodo_pago"]).upper()))
                        sub_table.setItem(row, 3, QTableWidgetItem(str(p["estado"]).upper()))
                        sub_table.setItem(row, 4, QTableWidgetItem(str(p["referencia"]) if p["referencia"] else "-"))
                    
                    card_layout.addWidget(sub_table)
                    self.scroll_layout.addWidget(card)
                
                # Mantiene las tarjetas alineadas al tope superior del área con scroll
                self.scroll_layout.addStretch()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error crítico al cargar pagos: {str(e)}")

    # === CONTROLES DE EDICIÓN PARA LA ENTRADA GENERAL ===
    def obtener_id_desde_subtabla(self, factura_id):
        """Busca dinámicamente una subtabla de tarjeta por nombre y retorna el ID del pago seleccionado."""
        tabla = self.findChild(QTableWidget, f"table_factura_{factura_id}")
        if tabla:
            fila = tabla.currentRow()
            if fila >= 0:
                return int(tabla.item(fila, 0).text())
        return None

    def editar_pago_general(self, factura_id):
        """Abre el formulario para editar un pago seleccionado desde el panel de tarjetas."""
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
        """Elimina un pago seleccionado desde el panel de tarjetas previa confirmación."""
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
        """Retorna el ID del pago seleccionado de la tabla en modo vista individual."""
        if not self.table:
            return None
        fila = self.table.currentRow()
        return int(self.table.item(fila, 0).text()) if fila >= 0 else None

    def crear_pago(self):
        """Instancia el formulario para registrar un nuevo cobro asignado a la factura actual."""
        if self.factura_id is None:
            return
        dialog = PagoForm(self, factura_id=self.factura_id)
        if dialog.exec():
            try:
                self.service.crear(dialog.obtener_datos())
                self.cargar_pagos()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def editar_pago(self):
        """Recupera los datos del pago seleccionado y abre el modal de edición."""
        pago_id = self.obtener_id_seleccionado()
        if not pago_id: return
        try:
            pago = self.service.obtener(pago_id)
            dialog = PagoForm(self, factura_id=self.factura_id, pago=pago)
            if dialog.exec():
                self.service.actualizar(pago_id, dialog.obtener_datos())
                self.cargar_pagos()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def eliminar_pago(self):
        """Remueve el pago seleccionado de la tabla única en modo vista individual."""
        pago_id = self.obtener_id_seleccionado()
        if not pago_id or QMessageBox.question(self, "Confirmar", "¿Eliminar pago?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.eliminar(pago_id)
            self.cargar_pagos()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))