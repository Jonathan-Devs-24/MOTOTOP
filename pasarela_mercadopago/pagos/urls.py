# pasarela_mercadopago/pagos/urls.py
from django.urls import path
from .views import feedback_view, iniciar_pago_view

urlpatterns = [
    # Ruta para iniciar el proceso de cobro (Ej: /pagos/iniciar/45/)
    path('iniciar/<int:factura_id>/', iniciar_pago_view, name='iniciar_pago'),
    
    # Ruta que procesa el retorno del cliente desde los servidores de MP
    path('feedback/', feedback_view, name='pago_feedback'),
]