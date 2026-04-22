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
    
    