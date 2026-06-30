# desktop/app/views/login_view.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPixmap, QColor, QPainter
import random

class LoginView(QWidget):

    login_success = pyqtSignal()

    def __init__(self, auth_service, auth_store, http_client):
        super().__init__()

        self.auth_service = auth_service
        self.auth_store = auth_store
        self.http = http_client

        self.setWindowTitle("Iniciar Sesión")

        # 1. Dimensiones fijas para que la ventana sea mas larga y estilizada
        self.setFixedSize(350, 500)

        # ---------- PARTICULAS AQUÍ --------------
        # 2. Inicialización de las partículas de fondo (Cuadrados)
        self.particles = []
        self.init_particles()

        # 3. Temporizador para controlar la animación (60 FPS aprox.)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(16)  # 16 milisegundos por ciclo

        # ------------------------------------------
        
        
        # 2. Configuracion del layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        # Espaciador superior para empujar el contenido hacia el centro
        top_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(top_spacer)

        # 3. Encabezado / Titulo
        self.title_label = QLabel("Iniciar Sesion")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Espacio sutil bajo el titulo
        layout.addSpacing(10)
        
        # --- IMAGEN INICIA AQUÍ ---
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Cargar la imagen 
        pixmap = QPixmap("img/moto-top.png")
        
        # Opcional, pero agregable: Redimensionar la imagen manteniendo la proporción (ej. ancho de 100px)
        scaled_pixmap = pixmap.scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(scaled_pixmap)
        
        layout.addWidget(self.logo_label)
        
        # Espacio sutil bajo la imagen antes de los campos de texto
        layout.addSpacing(15)
        # ----- IMAGEN TERMINA AQUÍ -----------------

        # 4. Campos de entrada
        self.username = QLineEdit()
        self.username.setPlaceholderText("Usuario")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        # 5. Boton de accion
        self.button = QPushButton("Login")
        self.button.clicked.connect(self.handle_login)

        # 6. Etiqueta de estado
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setObjectName("status_label")

        # Agregar componentes al layout
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.button)
        layout.addWidget(self.status)

        # Espaciador inferior para mantener la proporcion centrada
        bottom_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(bottom_spacer)

        self.setLayout(layout)

        # 7. Aplicacion de estilos visuales (QSS)
        self.apply_styles()

    def init_particles(self):
        """Crea la lista inicial de cuadrados con propiedades aleatorias."""
        num_particles = 15  # Cantidad de cuadrados en pantalla
        for _ in range(num_particles):
            self.particles.append({
                'x': random.uniform(0, 350),
                'y': random.uniform(0, 500),
                'size': random.uniform(20, 60),
                'speed': random.uniform(0.2, 0.8),
                'opacity': random.randint(5, 15)  # Opacidad baja (escala 0-255) para un efecto suave
            })
            
        self.update()  # Dispara automáticamente el método paintEvent de Qt


    def update_particles(self):
        """Actualiza la posición de cada cuadrado y solicita redibujar la pantalla."""
        for p in self.particles:
            p['y'] -= p['speed']
            
            if p['y'] < -p['size']:
                p['y'] = 500 + p['size']
                p['x'] = random.uniform(0, 350)
                p['size'] = random.uniform(20, 60)
                p['speed'] = random.uniform(0.2, 0.8)

        self.update()


    def paintEvent(self, event):
        """Dibuja el fondo y los elementos animados en cada fotograma."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dibujar el color base del fondo oscuro para limpiar la pantalla
        painter.fillRect(self.rect(), QColor("#c8cbd0"))

        # Configurar pincel sin bordes para los cuadrados flotantes
        painter.setPen(Qt.PenStyle.NoPen)

        # Dibujar cada uno de los cuadrados almacenados
        for p in self.particles:
            
            alpha = int(p['opacity'] * 6.5)  # Eleva el rango de visibilidad
            if alpha > 60: alpha = 60        # Límite para que no tape el texto
            
            
            # Color celeste/azul sutil con la opacidad asignada individualmente
            color = QColor(229, 57, 53, p['opacity'])
            painter.setBrush(color)
            
            # Dibuja el cuadrado en su posición actual convertida a entero
            painter.drawRect(int(p['x']), int(p['y']), int(p['size']), int(p['size']))

        painter.end()
        
        
    def apply_styles(self):
        # Defina aqui la hoja de estilos global para la vista del login
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
            }
            QLabel#title_label {
                color: #1a1a1a;
                font-size: 24px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #888888;
                border-radius: 6p;
                padding: 10px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #e53935;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #e53935;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
           
            QLabel#status_label {
                color: #ef4444;
                font-size: 12px;
            }
        """)
        # Asignar ID de objeto especifico para el titulo
        self.title_label.setObjectName("title_label")
        self.status.setObjectName("status_label")

    def handle_login(self):
        try:
            data = self.auth_service.login(
                self.username.text(),
                self.password.text()
            )

            self.auth_store.set_tokens(
                data["access"],
                data["refresh"]
            )

            self.http.set_token(self.auth_store.access)

            self.status.setText("Login OK")
            
            # Estilo exito temporal
            self.status.setStyleSheet("color: #2e7d32;")
            self.status.setText("Login OK")

            self.login_success.emit()

        except Exception as e:
            self.status.setText(str(e))
            
