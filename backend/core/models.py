# backend/core/models.py
from django.db import models
from django.contrib.auth.models import User

# Zona
class Zona(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    

# Cliente
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, null=True, blank=True)
    nro_documento = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=50)
    email = models.EmailField()
    direccion = models.CharField(max_length=150)
    codigo_postal = models.CharField(max_length=20)
    localidad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)

    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    zona = models.ForeignKey(Zona, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre
    

# Vendedor
class Vendedor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=50)
    comision = models.DecimalField(max_digits=5, decimal_places=2)
    estado = models.CharField(max_length=50)

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    zona = models.ForeignKey(Zona, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre
    
    
# Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    img = models.ImageField(upload_to='productos/', null=True, blank=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    rubros = models.ManyToManyField('Rubro', through='RubroProducto')
    proveedores = models.ManyToManyField('Proveedor', through='ProveedorProducto')

    def __str__(self):
        return self.nombre
    
# Rubro
class Rubro(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre
    

# Proveedor
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

# RubroProducto
class RubroProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto', 'rubro')

    def __str__(self):
        return f"{self.producto} - {self.rubro}"
    

# ProveedorProducto
class ProveedorProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto', 'proveedor')

    def __str__(self):
        return f"{self.producto} - {self.proveedor}"
    
# Pedido
class Pedido(models.Model):

    ORIGEN_CHOICES = [
        ('web', 'Web'),
        ('local', 'Local'),
        ('mobile', 'Mobile'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.SET_NULL, null=True, blank=True)

    origen = models.CharField(max_length=20, choices=ORIGEN_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente}"
    

# DetallePedido
class DetallePedido(models.Model):

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto} x{self.cantidad}"


# Compra
class Compra(models.Model):

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('recibida', 'Recibida'),
        ('cancelada', 'Cancelada'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    fecha_compra = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor}"
    

# DetalleCompra
class DetalleCompra(models.Model):

    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto} x{self.cantidad}"
    
# Factura
class Factura(models.Model):

    TIPO_CHOICES = [
        ('A', 'Factura A'),
        ('B', 'Factura B'),
        ('C', 'Factura C'),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)

    tipo_comprobante = models.CharField(max_length=1, choices=TIPO_CHOICES)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    fecha_emision = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Factura #{self.id} - Pedido {self.pedido.id}"
    
# Pago
class Pago(models.Model):

    METODO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
    ]

    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos')

    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)

    fecha_pago = models.DateTimeField(auto_now_add=True)
    referencia = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Pago #{self.id} - {self.factura}"
    
# Envio
class Envio(models.Model):

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)

    empresa_transporte = models.CharField(max_length=100)
    tracking_code = models.CharField(max_length=100, blank=True, null=True)

    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_estimada = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    estado_envio = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"Envio Pedido {self.pedido.id}"
    
