import hashlib
from django.shortcuts import render
from django.core.cache import cache
from .scraper import rastreador_dinamico

def inicio(request):
    query = request.GET.get("q", "").strip()
    resultados = []

    if query:
        # Optimización: Hashing de la clave para garantizar seguridad y longitud fija
        query_hash = hashlib.md5(query.lower().encode('utf-8')).hexdigest()
        cache_key = f"busqueda_{query_hash}"

        resultados = cache.get(cache_key)
        
        if not resultados:
            resultados = rastreador_dinamico(query)
            if resultados: 
                cache.set(cache_key, resultados, timeout=900)

    return render(request, "index.html", {"ofertas": resultados, "query": query})