import hashlib
from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.db import transaction
from .scraper import rastreador_dinamico
from .models import Producto, HistorialPrecio

def inicio(request):
    query = request.GET.get("q", "").strip()
    resultados = []

    if query:
        query_hash = hashlib.md5(query.lower().encode('utf-8')).hexdigest()
        cache_key = f"busqueda_{query_hash}"

        resultados = cache.get(cache_key)
        
        if not resultados:
            resultados = rastreador_dinamico(query)
            if resultados: 
                try:
                    with transaction.atomic():
                        for item in resultados:
                            producto, _ = Producto.objects.get_or_create(
                                url=item['url'],
                                defaults={'nombre': item['nombre'], 'tienda': 'Mercado Libre'}
                            )
                            HistorialPrecio.objects.create(producto=producto, precio=item['precio'])
                            # Inyectamos el ID relacional al diccionario para el frontend
                            item['id'] = producto.id 
                except Exception as e:
                    print(f"Error guardando en DB: {e}")
                
                cache.set(cache_key, resultados, timeout=900)

    return render(request, "index.html", {"ofertas": resultados, "query": query})

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
    resultados = []

    if query:
        query_hash = hashlib.md5(query.lower().encode('utf-8')).hexdigest()
        cache_key = f"busqueda_{query_hash}"

        resultados = cache.get(cache_key)
        
        if not resultados:
            resultados = rastreador_dinamico(query)
            if resultados: 
                try:
                    with transaction.atomic():
                        for item in resultados:
                            producto, _ = Producto.objects.get_or_create(
                                url=item['url'],
                                defaults={'nombre': item['nombre'], 'tienda': 'Mercado Libre'}
                            )
                            HistorialPrecio.objects.create(producto=producto, precio=item['precio'])
                            item['id'] = producto.id 
                except Exception as e:
                    print(f"Error guardando en DB: {e}")
                
                cache.set(cache_key, resultados, timeout=900)
        
        # Lógica de Ordenamiento en memoria (rápido, ya que son max 10-50 items)
        if resultados:
            reverse_sort = True if sort_order == "desc" else False
            resultados = sorted(resultados, key=lambda x: x['precio'], reverse=reverse_sort)

    return render(request, "index.html", {
        "ofertas": resultados, 
        "query": query, 
        "current_sort": sort_order
    })

# NUEVAS VISTAS
def seguimiento(request):
    # Optimización: prefetch_related para evitar el problema N+1 al consultar la DB
    productos = Producto.objects.all().prefetch_related('historial_precios').order_by('-creado_en')
    return render(request, "seguimiento.html", {"productos": productos})

def configuracion(request):
    return render(request, "configuracion.html")