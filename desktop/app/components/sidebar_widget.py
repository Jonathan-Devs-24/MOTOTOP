# desktop/app/components/sidebar_widget.py
import random
from PyQt6.QtWidgets import QWidget, QStyle, QStyleOption
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor

class SidebarWidget(QWidget):
    """Contenedor personalizado para el sidebar con renderizado de partículas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        
        self.particles = []
        self.max_particles = 15
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(16)

    def init_particles(self):
        w = self.width() if self.width() > 0 else 200
        h = self.height() if self.height() > 0 else 700
        
        self.particles = []
        for _ in range(self.max_particles):
            size = random.randint(15, 45)
            self.particles.append({
                'x': random.uniform(0, w),
                'y': random.uniform(0, h),
                'size': size,
                'speed_y': random.uniform(-0.6, -0.1),
                'speed_x': random.uniform(-0.1, 0.1),
                'alpha': random.randint(15, 40),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-0.5, 0.5)
            })

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.init_particles()  # Reinicia la dispersión para cubrir el nuevo alto/ancho real

    def update_particles(self):
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        for p in self.particles:
            p['y'] += p['speed_y']
            p['x'] += p['speed_x']
            p['rotation'] += p['rot_speed']
            
            if p['y'] + p['size'] < 0:
                p['y'] = h + p['size']
                p['x'] = random.uniform(0, w)
                p['alpha'] = random.randint(15, 40)
            if p['x'] < -p['size']:
                p['x'] = w
            elif p['x'] > w:
                p['x'] = -p['size']
                
        self.update()

    def paintEvent(self, event):
        # SOLUCIÓN OBLIGATORIA PARA WIDGETS PERSONALIZADOS EN PYQT
        # Esto procesa correctamente el 'background-color' del QSS en el componente
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
        # RENDERIZADO DE PARTÍCULAS (Detrás de los botones, delante del fondo oscuro)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for p in self.particles:
            painter.save()
            center_x = p['x'] + p['size'] / 2
            center_y = p['y'] + p['size'] / 2
            painter.translate(center_x, center_y)
            painter.rotate(p['rotation'])
            
            color = QColor(255, 255, 255, p['alpha'])
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            
            half_s = p['size'] / 2
            painter.drawRect(QRectF(-half_s, -half_s, p['size'], p['size']))
            
            painter.restore()
            
        painter.end()