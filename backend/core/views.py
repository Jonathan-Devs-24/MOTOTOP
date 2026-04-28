# backend/core/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
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


class RubroViewSet(viewsets.ModelViewSet):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer       

     
# ProductoViewSet
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.prefetch_related('proveedorproducto_set__proveedor')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductoReadSerializer
        return ProductoWriteSerializer
    

# ClienteViewSet
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    

# VendedorViewSet
class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer

# ZonaViewSet
class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer

# CompraViewSet
class CompraViewSet(viewsets.ModelViewSet):
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
    


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserWriteSerializer