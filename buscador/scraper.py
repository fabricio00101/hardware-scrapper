import requests
from bs4 import BeautifulSoup

def rastreador_dinamico(producto_busqueda):
    busqueda_fmt = producto_busqueda.replace(' ', '-')
    url = f"https://listado.mercadolibre.com.ar/{busqueda_fmt}_NoIndex_True"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    try:
        # Añadir un timeout es una excelente práctica para evitar que el proceso se quede colgado
        response = requests.get(url, headers=headers, timeout=5) 
        response.raise_for_status() # Verifica si hubo un error HTTP (ej. 404, 403)
        
        # Cambiamos a 'lxml' para máxima velocidad
        soup = BeautifulSoup(response.text, 'lxml') 
        resultados = []
        
        # Limitamos la búsqueda inicial a los primeros 10 elementos directamente en el DOM
        items = soup.select('li.ui-search-layout__item', limit=10)
        
        for item in items:
            titulo_tag = item.select_one('.poly-component__title, .ui-search-item__title, h2')
            titulo = titulo_tag.text.strip() if titulo_tag else 'Sin nombre'
            
            precio_tag = item.select_one('span.andes-money-amount__fraction')
            precio = int(precio_tag.text.replace('.', '')) if precio_tag else 0
            
            link_tag = item.select_one('a[href]')
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