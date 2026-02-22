import requests
from bs4 import BeautifulSoup

def rastreador_dinamico(producto_busqueda):
    busqueda_fmt = producto_busqueda.replace(' ', '-')
    url = f"https://listado.mercadolibre.com.ar/{busqueda_fmt}_NoIndex_True"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        resultados = []
        items = soup.find_all('li', {'class': 'ui-search-layout__item'})
        for item in items[:10]:
            titulo_tag = (
                item.select_one('.poly-component__title') or
                item.select_one('.ui-search-item__title') or
                item.find('h2'))
            titulo = titulo_tag.text.strip() if titulo_tag else 'Sin nombre'
            precio_tag = item.find('span', {'class': 'andes-money-amount__fraction'})
            precio = int(precio_tag.text.replace('.', '')) if precio_tag else 0
            link_tag = item.find('a', href=True)
            link = link_tag['href'] if link_tag else '#'

            resultados.append({'nombre': titulo, 'precio': precio, 'url': link})
        return resultados
    except Exception:
        return[]