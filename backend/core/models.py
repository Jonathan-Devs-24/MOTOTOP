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
    nro_documento = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=50)
    email = models.EmailField()
    direccion = models.CharField(max_length=150)
    localidad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)

    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    zona = models.ForeignKey(Zona, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre
    

# Vendedor
class Vendedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=50)
    comision = models.DecimalField(max_digits=5, decimal_places=2)
    estado = models.CharField(max_length=50)

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    zona = models.ForeignKey(Zona, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre