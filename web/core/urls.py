# web/core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('crear-pedido/', views.crear_pedido_view, name='crear_pedido'),
    path('mis-pedidos/', views.mis_pedidos_view, name='mis_pedidos'),
    path('mis-pedidos/<int:pedido_id>/factura/', views.ver_factura_view, name='ver_factura'),
    path('empresa/', views.empresa_view, name='empresa'),
]

