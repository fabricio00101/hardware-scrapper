import requests
import random
from bs4 import BeautifulSoup

CONFIG_MERCADO_LIBRE = {
    'item_container': 'li.ui-search-layout__item',
    'title': '.poly-component__title, .ui-search-item__title, h2',
    'price': 'span.andes-money-amount__fraction',
    'link': 'a[href]'
}
def obtener_headers_aleatorios():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    return {'User-Agent': random.choice(user_agents)}

def rastreador_dinamico(producto_busqueda):
    busqueda_fmt = producto_busqueda.replace(' ', '-')
    url = f"https://listado.mercadolibre.com.ar/{busqueda_fmt}_NoIndex_True"
    
    try:
        # Usamos los headers aleatorios
        response = requests.get(url, headers=obtener_headers_aleatorios(), timeout=5) 
        response.raise_for_status()
        
        # Cambiamos a 'lxml' para máxima velocidad
        soup = BeautifulSoup(response.text, 'lxml') 
        resultados = []
        
        # Limitamos la búsqueda inicial a los primeros 10 elementos directamente en el DOM
        items = soup.select('li.ui-search-layout__item', limit=10)
        
        for item in items:
            titulo_tag = item.select_one(CONFIG_MERCADO_LIBRE['title'])
            titulo = titulo_tag.text.strip() if titulo_tag else 'Sin nombre'
            
            precio_tag = item.select_one(CONFIG_MERCADO_LIBRE['price'])
            precio = int(precio_tag.text.replace('.', '')) if precio_tag else 0
            
            link_tag = item.select_one(CONFIG_MERCADO_LIBRE['link'])
            link = link_tag['href'] if link_tag else '#'

            resultados.append({'nombre': titulo, 'precio': precio, 'url': link})
            
        return resultados
        
    except requests.exceptions.RequestException as e:
        # Aquí puedes registrar (loguear) el error de red específicamente
        print(f"Error de red: {e}")
        return []
    except Exception as e:
        print(f"ERROR FATAL EN SCRAPER: {e}") # Mira tu terminal para ver este mensaje
        return []