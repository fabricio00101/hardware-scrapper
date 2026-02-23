import time
import random
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.core.management.base import BaseCommand
from buscador.models import Producto, HistorialPrecio

class Command(BaseCommand):
    help = 'Escanea las URLs de los productos en seguimiento y actualiza sus precios automáticamente'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando motor de actualización de inventario...'))

        # Configuración de sesión robusta
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))

        productos = Producto.objects.all()
        actualizados = 0

        for producto in productos:
            try:
                # Evasión básica: User-Agent rotativo o fijo estándar
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0'}
                response = session.get(producto.url, headers=headers, timeout=8)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'lxml')
                
                # ¡NUEVO!: Selector CSS específico para la vista de PRODUCTO INDIVIDUAL en ML
                precio_tag = soup.select_one('div.ui-pdp-price__second-line span.andes-money-amount__fraction')

                if precio_tag:
                    precio_str = precio_tag.text.replace('.', '')
                    if precio_str.isdigit():
                        nuevo_precio = int(precio_str)

                        # Extraer el precio más reciente (gracias al ordering = ['-fecha_registro'] del modelo)
                        ultimo_historial = producto.historial_precios.first()
                        
                        # Guardar SOLO si el precio fluctuó, ahorra miles de filas en la DB
                        if not ultimo_historial or ultimo_historial.precio != nuevo_precio:
                            HistorialPrecio.objects.create(producto=producto, precio=nuevo_precio)
                            actualizados += 1
                            self.stdout.write(f"[FLUCTUACIÓN] {producto.nombre} -> ${nuevo_precio}")

                # Rate Limiting Defensivo: Dormir el hilo un tiempo aleatorio para evitar baneos de IP
                time.sleep(random.uniform(1.5, 3.5))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[ERROR] Timeout/Caída en {producto.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f'Ciclo finalizado. {actualizados} precios nuevos en la serie temporal.'))