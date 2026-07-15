# core/urls.py (Archivo de rutas principal de tu proyecto)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Conectamos las URLs de la app 'pagos'
    path('pagos/', include('pagos.urls')),
]