# backend/core/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
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
from django.db.models import Sum, F, Q, Value, DecimalField, IntegerField
from django.db.models.functions import Coalesce
from datetime import datetime

from rest_framework.views import APIView
from .ai_service import GeminiAssistantService

# "#############################################"
from rest_framework.permissions import AllowAny
from .serializers import GeminiChatSerializer


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

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        pedido = self.get_object()

        if pedido.estado == 'confirmado':
            return Response(
                {"error": "No se puede cancelar un pedido ya confirmado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if pedido.estado == 'cancelado':
            return Response(
                {"mensaje": "El pedido ya está cancelado"},
                status=status.HTTP_200_OK
            )

        pedido.estado = 'cancelado'
        pedido.save()

        return Response(
            {"mensaje": "Pedido cancelado correctamente"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def factura(self, request, pk=None):
        pedido = self.get_object()
        try:
            factura = pedido.factura
            serializer = FacturaReadSerializer(factura)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Factura.DoesNotExist:
            return Response(
                {"error": "No existe factura para este pedido"},
                status=status.HTTP_404_NOT_FOUND
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
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Captura el parámetro ?factura= de la URL
        factura_id = self.request.query_params.get('factura')
        if factura_id is not None:
            queryset = queryset.filter(factura_id=factura_id)
        return queryset

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


class InformeViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def _parse_date(self, value, default=None):
        if not value:
            return default
        try:
            return datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValidationError('Formato de fecha inválido, use YYYY-MM-DD')

    def _get_date_range(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        inicio = self._parse_date(fecha_inicio)
        fin = self._parse_date(fecha_fin)
        if inicio and fin:
            fin = fin.replace(hour=23, minute=59, second=59)
        return inicio, fin

    def _filter_periodo(self, queryset, fecha_campo, inicio, fin):
        if inicio:
            queryset = queryset.filter(**{f'{fecha_campo}__gte': inicio})
        if fin:
            queryset = queryset.filter(**{f'{fecha_campo}__lte': fin})
        return queryset

    @action(detail=False, methods=['get'], url_path='venta-por-vendedor')
    def venta_por_vendedor(self, request):
        inicio, fin = self._get_date_range(request)
        pedidos = Pedido.objects.filter(estado='confirmado')
        pedidos = self._filter_periodo(pedidos, 'fecha_pedido', inicio, fin)
        valores = pedidos.values(
            'vendedor',
            'vendedor__nombre',
            'vendedor__apellido'
        ).annotate(total_ventas=Coalesce(Sum('total'), Value(0), output_field=DecimalField(max_digits=12, decimal_places=2))).order_by('-total_ventas')

        data = [
            {
                'vendedor_id': item['vendedor'],
                'vendedor_nombre': f"{item['vendedor__nombre']} {item['vendedor__apellido'] or ''}".strip(),
                'total_ventas': item['total_ventas']
            }
            for item in valores
        ]
        return Response(data)

    @action(detail=False, methods=['get'], url_path='ventas')
    def ventas(self, request):
        inicio, fin = self._get_date_range(request)
        pedidos = Pedido.objects.filter(estado='confirmado')
        pedidos = self._filter_periodo(pedidos, 'fecha_pedido', inicio, fin)
        total_ventas = pedidos.aggregate(total=Coalesce(Sum('total'), Value(0), output_field=DecimalField(max_digits=12, decimal_places=2)))['total']
        return Response({'total_ventas': total_ventas, 'fecha_inicio': request.query_params.get('fecha_inicio'), 'fecha_fin': request.query_params.get('fecha_fin')})

    @action(detail=False, methods=['get'], url_path='pedidos-pendientes-envio')
    def pedidos_pendientes_envio(self, request):
        pedidos = Pedido.objects.filter(estado='confirmado').exclude(envio__estado_envio='entregado')
        serializer = PedidoReadSerializer(pedidos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='saldo-clientes')
    def saldo_clientes(self, request):
        clientes = Cliente.objects.annotate(
            total_facturado=Coalesce(Sum('pedido__factura__total', distinct=True), Value(0), output_field=DecimalField(max_digits=12, decimal_places=2)),
            total_pagado=Coalesce(Sum('pedido__factura__pagos__monto', filter=Q(pedido__factura__pagos__estado='completado')), Value(0), output_field=DecimalField(max_digits=12, decimal_places=2))
        ).annotate(saldo=F('total_facturado') - F('total_pagado')).order_by('-saldo')

        data = [
            {
                'cliente_id': cliente.id,
                'cliente_nombre': str(cliente),
                'total_facturado': cliente.total_facturado,
                'total_pagado': cliente.total_pagado,
                'saldo': cliente.saldo
            }
            for cliente in clientes
        ]
        return Response(data)

    @action(detail=False, methods=['get'], url_path='facturas-pendientes-cobro')
    def facturas_pendientes_cobro(self, request):
        facturas = Factura.objects.annotate(
            total_pagado=Coalesce(Sum('pagos__monto', filter=Q(pagos__estado='completado')), Value(0), output_field=DecimalField(max_digits=12, decimal_places=2))
        ).filter(total_pagado__lt=F('total'))

        data = [
            {
                'factura_id': factura.id,
                'pedido_id': factura.pedido_id,
                'cliente_nombre': str(factura.pedido.cliente),
                'total': factura.total,
                'total_pagado': factura.total_pagado,
                'saldo': factura.total - factura.total_pagado
            }
            for factura in facturas
        ]
        return Response(data)

    @action(detail=False, methods=['get'], url_path='ventas-por-zona')
    def ventas_por_zona(self, request):
        inicio, fin = self._get_date_range(request)
        pedidos = Pedido.objects.filter(estado='confirmado')
        pedidos = self._filter_periodo(pedidos, 'fecha_pedido', inicio, fin)
        valores = pedidos.values(
            'vendedor__zona__id',
            'vendedor__zona__nombre'
        ).annotate(total_ventas=Coalesce(Sum('total'), 0)).order_by('-total_ventas')

        data = [
            {
                'zona_id': item['vendedor__zona__id'],
                'zona_nombre': item['vendedor__zona__nombre'],
                'total_ventas': item['total_ventas']
            }
            for item in valores
        ]
        return Response(data)

    @action(detail=False, methods=['get'], url_path='productos-mas-vendidos')
    def productos_mas_vendidos(self, request):
        top = request.query_params.get('top')
        try:
            top = int(top) if top else 10
        except ValueError:
            return Response({'error': 'El parámetro top debe ser un número'}, status=status.HTTP_400_BAD_REQUEST)

        detalles = DetallePedido.objects.filter(pedido__estado='confirmado')
        valores = detalles.values(
            'producto__id',
            'producto__nombre'
        ).annotate(
            cantidad_vendida=Coalesce(Sum('cantidad'), Value(0), output_field=IntegerField()),
            total_ventas=Coalesce(Sum(F('cantidad') * F('precio_unitario')), Value(0), output_field=DecimalField(max_digits=12, decimal_places=2))
        ).order_by('-cantidad_vendida')[:top]

        data = [
            {
                'producto_id': item['producto__id'],
                'producto_nombre': item['producto__nombre'],
                'cantidad_vendida': item['cantidad_vendida'],
                'total_ventas': item['total_ventas']
            }
            for item in valores
        ]
        return Response(data)
    


class GeminiChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GeminiChatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        prompt = serializer.validated_data.get('prompt')

        try:
            servicio = GeminiAssistantService()
            respuesta = servicio.responder(prompt)
            return Response({'respuesta': respuesta}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"\n[ERROR EN VISTA GEMINI]: {e}\n")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
            
            
            

           