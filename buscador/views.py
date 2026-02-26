from django.shortcuts import render, get_object_or_404
from .models import Producto, HistorialPrecio
from .services import obtener_resultados_busqueda

def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Query optimizado: solo extrae columnas específicas sin instanciar objetos pesados
    historial = producto.historial_precios.order_by('fecha_registro').values('fecha_registro', 'precio')
    
    # Serialización de vectores para el gráfico en JS
    fechas = [h['fecha_registro'].strftime('%d/%m %H:%M') for h in historial]
    precios = [float(h['precio']) for h in historial]
    
    return render(request, "detalle.html", {
        "producto": producto,
        "fechas": fechas,
        "precios": precios
    })
def inicio(request):
    query = request.GET.get("q", "").strip()
    sort_order = request.GET.get("sort", "asc") # Parámetro de ordenamiento
    resultados = obtener_resultados_busqueda(query)

    # Lógica de Ordenamiento en memoria (rápido, ya que son max 10-50 items de caché/scraping por request)
    if resultados:
        reverse_sort = True if sort_order == "desc" else False
        resultados = sorted(resultados, key=lambda x: x['precio'], reverse=reverse_sort)

    return render(request, "index.html", {
        "ofertas": resultados, 
        "query": query, 
        "current_sort": sort_order
    })

from django.core.paginator import Paginator

# NUEVAS VISTAS
def seguimiento(request):
    # Optimización: prefetch_related para evitar el problema N+1 al consultar la DB
    productos_list = Producto.objects.all().prefetch_related('historial_precios').order_by('-creado_en')
    
    # Mostrar 10 productos por página.
    paginator = Paginator(productos_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "seguimiento.html", {"page_obj": page_obj})

def configuracion(request):
    return render(request, "configuracion.html")