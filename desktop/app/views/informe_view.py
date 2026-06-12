from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QGroupBox
)
from PyQt6.QtCore import QDate, Qt


class InformeView(QWidget):

    def __init__(self, informe_service):
        super().__init__()

        self.service = informe_service

        self.setWindowTitle("Informes")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDate(QDate.currentDate().addDays(-30))
        self.fecha_inicio.setDisplayFormat("yyyy-MM-dd")

        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDate(QDate.currentDate())
        self.fecha_fin.setDisplayFormat("yyyy-MM-dd")

        self.btn_refresh = QPushButton("Actualizar")
        self.btn_refresh.setStyleSheet(
            "background-color: #1976D2; color: white; border: none; padding: 8px 16px; border-radius: 4px;"
        )
        self.btn_refresh.clicked.connect(self.load_data)

        controls_layout.addWidget(QLabel("Desde:"))
        controls_layout.addWidget(self.fecha_inicio)
        controls_layout.addWidget(QLabel("Hasta:"))
        controls_layout.addWidget(self.fecha_fin)
        controls_layout.addWidget(self.btn_refresh)
        controls_layout.addStretch()

        main_layout.addLayout(controls_layout)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)

        self.card_total_ventas = self.build_card("Total ventas", "$0")
        self.card_pedidos_pendientes = self.build_card("Pedidos pendientes de envío", "0")
        self.card_facturas_pendientes = self.build_card("Facturas pendientes", "0")
        self.card_clientes_saldo = self.build_card("Clientes con saldo", "0")

        cards_layout.addWidget(self.card_total_ventas)
        cards_layout.addWidget(self.card_pedidos_pendientes)
        cards_layout.addWidget(self.card_facturas_pendientes)
        cards_layout.addWidget(self.card_clientes_saldo)

        main_layout.addLayout(cards_layout)

        self.table_ventas_vendedor = QTableWidget(0, 2)
        self.table_ventas_vendedor.setHorizontalHeaderLabels(["Vendedor", "Total ventas"])
        self.table_ventas_vendedor.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_ventas_vendedor.verticalHeader().setVisible(False)
        self.table_ventas_vendedor.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_ventas_vendedor.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.table_clientes_saldo = QTableWidget(0, 4)
        self.table_clientes_saldo.setHorizontalHeaderLabels(["Cliente", "Facturado", "Pagado", "Saldo"])
        self.table_clientes_saldo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_clientes_saldo.verticalHeader().setVisible(False)
        self.table_clientes_saldo.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_clientes_saldo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        main_layout.addWidget(QLabel("Ventas por vendedor"))
        main_layout.addWidget(self.table_ventas_vendedor)
        main_layout.addWidget(QLabel("Top clientes con saldo"))
        main_layout.addWidget(self.table_clientes_saldo)

        self.setLayout(main_layout)

        self.load_data()

    def build_card(self, title, value):
        card = QGroupBox()
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #555; font-weight: bold;")

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        card.setLayout(layout)
        card.setStyleSheet(
            "QGroupBox { background-color: white; border: 1px solid #ddd; border-radius: 10px; }"
        )

        card.value_label = value_label
        return card

    def load_data(self):
        try:
            fecha_inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")

            ventas_data = self.service.ventas(fecha_inicio, fecha_fin)
            pedidos_data = self.service.pedidos_pendientes_envio()
            facturas_data = self.service.facturas_pendientes_cobro()
            clientes_data = self.service.saldo_clientes()
            vendedores_data = self.service.venta_por_vendedor(fecha_inicio, fecha_fin)

            total_ventas = ventas_data.get("total_ventas", 0)
            self.card_total_ventas.value_label.setText(f"${total_ventas}")
            self.card_pedidos_pendientes.value_label.setText(str(len(pedidos_data)))
            self.card_facturas_pendientes.value_label.setText(str(len(facturas_data)))
            clientes_con_saldo = sum(1 for cliente in clientes_data if float(cliente.get("saldo", 0)) > 0)
            self.card_clientes_saldo.value_label.setText(str(clientes_con_saldo))

            self.populate_table(
                self.table_ventas_vendedor,
                vendedores_data,
                ["vendedor_nombre", "total_ventas"]
            )

            self.populate_table(
                self.table_clientes_saldo,
                sorted(clientes_data, key=lambda c: float(c.get("saldo", 0)), reverse=True)[:8],
                ["cliente_nombre", "total_facturado", "total_pagado", "saldo"]
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los informes: {e}")

    def populate_table(self, table, items, fields):
        table.setRowCount(0)
        for item in items:
            row = table.rowCount()
            table.insertRow(row)
            for col, field in enumerate(fields):
                value = item.get(field, "-")
                table.setItem(row, col, QTableWidgetItem(str(value)))
