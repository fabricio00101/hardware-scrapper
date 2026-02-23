from django.db import models
from django.utils import timezone

class Producto(models.Model):
    nombre = models.CharField(max_length=255, db_index=True)
    url = models.URLField(unique=True, max_length=500)
    tienda = models.CharField(max_length=50, default='Mercado Libre')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class HistorialPrecio(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='historial_precios')
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_registro = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name_plural = "Historiales de Precios"

    def __str__(self):
        return f"{self.producto.nombre} - ${self.precio} ({self.fecha_registro.strftime('%d/%m/%Y')})"