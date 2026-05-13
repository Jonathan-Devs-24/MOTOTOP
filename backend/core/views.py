# backend/core/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import (
    Zona, Cliente, Vendedor, Producto, Rubro, Proveedor,
    RubroProducto, ProveedorProducto, Pedido, DetallePedido,
    Compra, DetalleCompra, Factura, DetalleFactura, Pago,
    Envio, Promocion, ProductoPromocion
)
from .serializers import *
from django.contrib.auth.models import User


class PedidoViewSet(viewsets.ModelViewSet):

    queryset = Pedido.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PedidoReadSerializer
        return PedidoWriteSerializer
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        pedido = self.get_object()

        try:
            pedido.confirmar()
            return Response(
                {"mensaje": "Pedido confirmado correctamente"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
       
class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [AllowAny]  # Sin autenticación para el desktop


class RubroViewSet(viewsets.ModelViewSet):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = [AllowAny]  # Sin autenticación para el desktop       

     
# ProductoViewSet

class ProductoViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Sin autenticación para el desktop

    queryset = Producto.objects.filter(activo=True).prefetch_related(
        'proveedorproducto_set__proveedor'
    )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductoReadSerializer
        return ProductoWriteSerializer
    
    
    def destroy(self, request, *args, **kwargs):
        producto = self.get_object()
        producto.activo = False
        producto.save()

        return Response(
            {"mensaje": "Producto desactivado"},
            status=status.HTTP_200_OK
        )
    

# ClienteViewSet
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    

# VendedorViewSet
class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    permission_classes = [AllowAny]  # Sin autenticación para el desktop

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        vendedor = self.get_object()
        
        try:
            # Cambiar entre activo e inactivo
            nuevo_estado = 'inactivo' if vendedor.estado == 'activo' else 'activo'
            vendedor.estado = nuevo_estado
            vendedor.save()
            
            return Response(
                {
                    "mensaje": f"Vendedor {nuevo_estado} correctamente",
                    "estado": nuevo_estado
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# ZonaViewSet
class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer
    permission_classes = [AllowAny]  # Sin autenticación para el desktop

# CompraViewSet
class CompraViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Sin autenticación para el desktop
    queryset = Compra.objects.all()
    serializer_class = CompraReadSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CompraReadSerializer
        return CompraWriteSerializer

    @action(detail=True, methods=['post'])
    def recibir(self, request, pk=None):
        compra = self.get_object()

        try:
            compra.marcar_recibida()
            return Response(
                {"mensaje": "Compra recibida correctamente"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# FacturaViewSet
class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FacturaReadSerializer
        return FacturaWriteSerializer
    

# PagoViewSet
class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

# EnvioViewSet
class EnvioViewSet(viewsets.ModelViewSet):
    queryset = Envio.objects.all()
    serializer_class = EnvioSerializer

# PromocionViewSet
class PromocionViewSet(viewsets.ModelViewSet):
    queryset = Promocion.objects.all()
    serializer_class = PromocionSerializer
    permission_classes = [AllowAny]  # Sin autenticación para el desktop


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserWriteSerializer
    permission_classes = [AllowAny]  # Sin autenticación para el desktop
    
class ProductoPromocionViewSet(viewsets.ModelViewSet):
    queryset = ProductoPromocion.objects.all()
    serializer_class = ProductoPromocionSerializer
    permission_classes = [AllowAny]  # Sin autenticación para el desktop
    
