from django.contrib import admin
from django.urls import path
from buscador.views import inicio, producto_detalle, seguimiento, configuracion

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='home'),
    path('producto/<int:producto_id>/', producto_detalle, name='producto_detalle'),
    path('seguimiento/', seguimiento, name='seguimiento'),
    path('configuracion/', configuracion, name='configuracion'),
]