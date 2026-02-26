import hashlib
import logging
from django.core.cache import cache
from django.db import transaction
from .scraper import rastreador_dinamico
from .models import Producto, HistorialPrecio

logger = logging.getLogger(__name__)

def obtener_resultados_busqueda(query):
    """
    Gestiona el ciclo completo de búsqueda: caché de base de datos intermedio,
    lanzamiento del web scraper y persistencia de precios actualizados.
    """
    if not query:
        return []

    # Se normaliza la query para el ID del caché
    query_hash = hashlib.md5(query.lower().encode('utf-8')).hexdigest()
    cache_key = f"busqueda_{query_hash}"

    resultados = cache.get(cache_key)
    
    if resultados:
        return resultados

    # Si no hay caché, iniciamos el scrapper
    resultados = rastreador_dinamico(query)
    
    if resultados: 
        try:
            with transaction.atomic():
                for item in resultados:
                    producto, _ = Producto.objects.get_or_create(
                        url=item['url'],
                        defaults={'nombre': item['nombre'], 'tienda': 'Mercado Libre'}
                    )
                    
                    ultimo_historial = producto.historial_precios.first()
                    if not ultimo_historial or float(ultimo_historial.precio) != float(item['precio']):
                        HistorialPrecio.objects.create(producto=producto, precio=item['precio'])
                        
                    item['id'] = producto.id 
        except Exception as e:
            logger.error(f"Error guardando productos en DB al buscar '{query}': {e}", exc_info=True)
        
        # Guardar en Cache por 15 minutos independientemente de si falló o no la DB
        cache.set(cache_key, resultados, timeout=900)

    return resultados
