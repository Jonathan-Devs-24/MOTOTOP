# backend/core/serializers.py
from rest_framework import serializers
from .models import *
from django.db import transaction


# Producto Serializer
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
        

# Cliente Serializer     
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
    
# DetallePedido (escritura) Serializer sin información del producto  
class DetallePedidoWriteSerializer(serializers.ModelSerializer):
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cantidad inválida")
        return value

    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad']
      
#  DetallePedido (lectura) Serializer con información del producto 
class DetallePedidoReadSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()

    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
   
     
# Pedido Serializer para escritura, que incluye detalles sin información del producto
class PedidoWriteSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoWriteSerializer(many=True, write_only=True)

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        pedido = Pedido.objects.create(**validated_data)

        for detalle in detalles_data:
            detalle_obj = DetallePedido(
                pedido=pedido,
                **detalle
            )
            detalle_obj.save()

        return pedido
    
    class Meta:
        model = Pedido
        fields = ['cliente', 'vendedor', 'origen', 'detalles']

# Vendedor Serializer
class VendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = ['id', 'nombre', 'apellido']

# Pedido Serializer para lectura, que incluye detalles con información del producto y cliente con información completa
class PedidoReadSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    vendedor = VendedorSerializer()
    detalles = DetallePedidoReadSerializer(many=True)

    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'vendedor', 'fecha', 'estado', 'total', 'detalles']
     
        
# FACTURA ____________________________________________________________    
class DetalleFacturaReadSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()

    class Meta:
        model = DetalleFactura
        fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
        
class FacturaReadSerializer(serializers.ModelSerializer):
    detalles = DetalleFacturaReadSerializer(many=True)

    class Meta:
        model = Factura
        fields = ['id', 'pedido', 'fecha', 'total', 'detalles']
        

        
        
# Pago
class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['factura', 'fecha', 'monto', 'estado']
     
# Envio   
class EnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envio
        fields = ['pedido', 'estado', 'fecha_envio', 'fecha_entrega']
        

# COMPRA

# Detalle compra read
class DetalleCompraReadSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()

    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']

# Detalle compra Write
class DetalleCompraWriteSerializer(serializers.ModelSerializer):
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cantidad inválida")
        return value

    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad']
        

# Compra Write
class CompraWriteSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Compra
        fields = ['proveedor', 'detalles']

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        compra = Compra.objects.create(**validated_data)

        for detalle in detalles_data:
            detalle_obj = DetalleCompra(
                compra=compra,
                **detalle
            )
            detalle_obj.save()

        return compra

# Compra Read
class CompraReadSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraReadSerializer(many=True)

    class Meta:
        model = Compra
        fields = ['id', 'proveedor', 'fecha', 'estado', 'total', 'detalles']

