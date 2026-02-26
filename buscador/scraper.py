import requests
import random
import logging
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

CONFIG_MERCADO_LIBRE = {
    'item_container': 'li.ui-search-layout__item',
    'title': '.poly-component__title, .ui-search-item__title, h2',
    'price': 'span.andes-money-amount__fraction',
    'link': 'a[href]'
}

# Optimización: Pool de conexiones TCP y reintentos automáticos
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def obtener_headers_aleatorios():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    return {'User-Agent': random.choice(user_agents)}

def rastreador_dinamico(producto_busqueda):
    if not producto_busqueda:
        return []

    busqueda_fmt = producto_busqueda.replace(' ', '-')
    url = f"https://listado.mercadolibre.com.ar/{busqueda_fmt}_NoIndex_True"
    
    try:
        # Uso de la sesión global en lugar de requests.get aislado
        response = session.get(url, headers=obtener_headers_aleatorios(), timeout=5) 
        response.raise_for_status()
        
        # response.content es marginalmente más rápido que .text al pasarlo a lxml
        soup = BeautifulSoup(response.content, 'lxml') 
        resultados = []
        
        items = soup.select(CONFIG_MERCADO_LIBRE['item_container'], limit=10)
        
        for item in items:
            titulo_tag = item.select_one(CONFIG_MERCADO_LIBRE['title'])
            precio_tag = item.select_one(CONFIG_MERCADO_LIBRE['price'])
            link_tag = item.select_one(CONFIG_MERCADO_LIBRE['link'])
            
            titulo = titulo_tag.text.strip() if titulo_tag else 'Sin nombre'
            
            # Sanitización de precio más robusta (evita errores si el precio tiene texto)
            precio_str = precio_tag.text.replace('.', '') if precio_tag else '0'
            precio = int(precio_str) if precio_str.isdigit() else 0
            
            link = link_tag['href'] if link_tag else '#'

            resultados.append({'nombre': titulo, 'precio': precio, 'url': link})
            
        return resultados
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red durante scraping de Meli ({url}): {e}")
        return []
    except Exception as e:
        logger.error(f"ERROR FATAL EN SCRAPER ({url}): {e}", exc_info=True)
        return []