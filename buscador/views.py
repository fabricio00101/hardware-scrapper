import hashlib
from django.shortcuts import render
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

        # 1. Intentamos obtener de caché (Respuesta ultra rápida)
        resultados = cache.get(cache_key)
        
        if not resultados:
            # 2. Si no hay caché, ejecutamos el Scraper
            resultados = rastreador_dinamico(query)
            
            if resultados: 
                # 3. Persistencia Segura y Atómica en Base de Datos
                try:
                    with transaction.atomic():
                        for item in resultados:
                            # Buscar o crear el hardware por su URL única
                            producto, created = Producto.objects.get_or_create(
                                url=item['url'],
                                defaults={
                                    'nombre': item['nombre'], 
                                    'tienda': 'Mercado Libre'
                                }
                            )
                            # Registrar el precio actual en la línea de tiempo
                            HistorialPrecio.objects.create(
                                producto=producto,
                                precio=item['precio']
                            )
                except Exception as e:
                    print(f"Error guardando en DB: {e}")
                
                # 4. Guardar en caché para los próximos 15 minutos
                cache.set(cache_key, resultados, timeout=900)

    return render(request, "index.html", {"ofertas": resultados, "query": query})