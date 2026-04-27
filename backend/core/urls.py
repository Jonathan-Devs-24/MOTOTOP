# backend/core/urls.py
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'vendedores', VendedorViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'rubros', RubroViewSet)
router.register(r'zonas', ZonaViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'compras', CompraViewSet)
router.register(r'facturas', FacturaViewSet)
router.register(r'pagos', PagoViewSet)
router.register(r'envios', EnvioViewSet)
router.register(r'promociones', PromocionViewSet)

urlpatterns = router.urls