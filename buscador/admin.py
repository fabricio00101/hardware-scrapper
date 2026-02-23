from django.contrib import admin
from .models import Producto, HistorialPrecio

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tienda', 'creado_en')
    search_fields = ('nombre', 'url')
    list_filter = ('tienda',)

@admin.register(HistorialPrecio)
class HistorialPrecioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'precio', 'fecha_registro')
    list_filter = ('fecha_registro',)
    autocomplete_fields = ('producto',)
    search_fields = ('producto__nombre',)