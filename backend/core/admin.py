# backend/core/admin.py
from django.contrib import admin
from .models import  *

# Intermedias 
class RubroProductoInline(admin.TabularInline):
    model = RubroProducto
    extra = 1

class ProveedorProductoInline(admin.TabularInline):
    model = ProveedorProducto
    extra = 1

class ProductoAdmin(admin.ModelAdmin):
    inlines = [RubroProductoInline, ProveedorProductoInline]

# Registro de modelos en el admin
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Rubro)
admin.site.register(Proveedor)
admin.site.register(Zona)
admin.site.register(Cliente)
admin.site.register(Vendedor)

