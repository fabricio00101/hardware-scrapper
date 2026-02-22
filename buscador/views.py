from django.shortcuts import render
from django.core.cache import cache
from .scraper import rastreador_dinamico


def inicio(request):
    query = request.GET.get("q", "").strip()
    resultados = []

    if query:
        # Creamos una llave única para esta búsqueda
        cache_key = f"busqueda_{query.replace(' ', '_').lower()}"

        # Intentamos obtener los resultados de la memoria caché
        resultados = cache.get(cache_key)
        
        if not resultados:
            resultados = rastreador_dinamico(query)
            # ¡NUEVO!: Solo guardar en caché si se encontraron productos
            if resultados: 
                cache.set(cache_key, resultados, 900)

    return render(request, "index.html", {"ofertas": resultados, "query": query})
