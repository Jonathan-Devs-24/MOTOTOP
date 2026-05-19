# desktop/app/views/compra_card.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox
)


class CompraCard(QWidget):

    def __init__(self, compra, service, refresh_callback):
        super().__init__()

        self.compra = compra
        self.service = service
        self.refresh = refresh_callback

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Compra #{compra['id']}"))

        proveedor = compra.get("proveedor")
        layout.addWidget(QLabel(f"Proveedor: {proveedor}"))

        layout.addWidget(QLabel(f"Estado: {compra['estado']}"))
        layout.addWidget(QLabel(f"Total: ${compra['total']}"))
        layout.addWidget(QLabel(f"Fecha: {compra['fecha_compra']}"))

        layout.addWidget(QLabel("Productos:"))

        for detalle in compra["detalles"]:
            producto = detalle["producto"]["nombre"]
            cantidad = detalle["cantidad"]

            layout.addWidget(
                QLabel(f"- {producto} x{cantidad}")
            )

        self.btn_recibir = QPushButton("Marcar recibida")

        if compra["estado"] == "recibida":
            self.btn_recibir.setEnabled(False)

        self.btn_recibir.clicked.connect(self.recibir)

        layout.addWidget(self.btn_recibir)

        self.setLayout(layout)

    def recibir(self):
        try:
            self.service.recibir(self.compra["id"])

            QMessageBox.information(
                self,
                "OK",
                "Compra recibida"
            )

            self.refresh()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
            
            