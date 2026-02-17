# Nombre del archivo: esika1.py
# Ubicación: /home/rpauser/airflow/notebooks/esika1.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import urllib3

# Librerías para el nuevo método de inserción
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# --- INICIO: FUNCIONES DE CRAWLING ---

def es_url_valida(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def convertir_precio(precio_str):
    if not precio_str or precio_str.lower() == "no encontrado": return 0.0
    s = precio_str.replace("$", "").replace("\xa0", "").strip(); s = re.sub(r"[^\d\.,]", "", s)
    ld = s.rfind('.'); lc = s.rfind(',')
    if lc > ld : s = s.replace(".", ""); s = s.replace(",", ".")
    elif ld > lc: s = s.replace(",", "")
    else: s = s.replace(",", "")
    ono = precio_str.replace("$", "").replace("\xa0", "").strip()
    if '.' in ono and ',' not in ono and not re.search(r'\.\d{2}$', ono): s = s.replace(".", "")
    try: return float(s)
    except ValueError:
        sno = re.sub(r"[^\d]", "", precio_str.replace("$", "").replace("\xa0", "").strip())
        if sno:
            try: return float(sno)
            except ValueError: return 0.0
        return 0.0

def obtener_categoria_pagina_listado_esika(soup):
    breadcrumb_items_vtex = soup.select("ul.vtex-breadcrumb-1-x-list li.vtex-breadcrumb-1-x-listItem")
    if breadcrumb_items_vtex and len(breadcrumb_items_vtex) >= 1:
        cat_tag = breadcrumb_items_vtex[-1].select_one("a span")
        if cat_tag:
            return cat_tag.get_text(strip=True).capitalize()
        else:
            a_tag = breadcrumb_items_vtex[-1].select_one("a")
            if a_tag: return a_tag.get_text(strip=True).capitalize()
    return None

def extraer_productos_esika(soup, url_actual, categoria_heredada):
    productos = []
    nombre_producto_tag = soup.select_one("span.vtex-store-components-3-x-productBrand--product-name-pdp-product-name")
    if not nombre_producto_tag: return []
    nombre_producto = nombre_producto_tag.get_text(strip=True)
    precio_actual_str = "No encontrado"; precio_normal_str = "No encontrado"
    search_area = soup
    def _construir_precio_desde_contenedor_esika(contenedor):
        if not contenedor: return "No encontrado"
        currency_code_tag = contenedor.select_one("span.belcorp-belcorp-product-price-0-x-currencyCode--pdp")
        currency_integer_tags = contenedor.select("span.belcorp-belcorp-product-price-0-x-currencyInteger--pdp")
        if currency_code_tag and currency_integer_tags:
            price_val_constructed = currency_code_tag.get_text(strip=True) + "".join([tag.get_text(strip=True) for tag in currency_integer_tags])
            return price_val_constructed.strip()
        raw_text = contenedor.get_text(strip=True, separator=' ')
        return raw_text if raw_text and any(char.isdigit() for char in raw_text) else "No encontrado"
    selling_price_wrapper = search_area.select_one("span.belcorp-belcorp-product-price-0-x-sellingPriceValue--pdp")
    list_price_wrapper = search_area.select_one("span.belcorp-belcorp-product-price-0-x-listPriceValue--pdp")
    if selling_price_wrapper: precio_actual_str = _construir_precio_desde_contenedor_esika(selling_price_wrapper)
    if list_price_wrapper: precio_normal_str = _construir_precio_desde_contenedor_esika(list_price_wrapper)
    if precio_actual_str != "No encontrado" and precio_normal_str == "No encontrado": precio_normal_str = precio_actual_str
    elif precio_actual_str == "No encontrado" and precio_normal_str != "No encontrado": precio_actual_str = precio_normal_str
    
    descripcion_producto_texto = "No disponible"
    description_button = None
    for btn in soup.find_all("button", class_="belcorp-belcorp-accordion-pdp-0-x-accordions"):
        if btn.get_text(strip=True).lower() == "descripción":
            description_button = btn; break
    if description_button:
        panel_id = description_button.get('aria-controls')
        description_panel = soup.find("div", id=panel_id) if panel_id else description_button.find_next_sibling("div")
        if description_panel:
            descripcion_producto_texto = ' '.join(description_panel.get_text(separator=' ', strip=True).split())
    if descripcion_producto_texto == "No disponible":
        direct_desc_div = soup.select_one("div.vtex-store-components-3-x-content.h-auto div[style='display:contents']")
        if direct_desc_div:
            descripcion_producto_texto = ' '.join(direct_desc_div.get_text(separator=' ', strip=True).split())

    productos.append({"brand": nombre_producto, "price": precio_actual_str, "precio_normal": precio_normal_str, "categoria": categoria_heredada, "descripcion_detalle": descripcion_producto_texto, "url": url_actual})
    return productos

def crawl_esika(url_inicio, max_profundidad=8, retardo=1, ssl_verify_option=False, initial_category_name="General", product_limit_per_category=300):
    visitados = set()
    a_visitar = [(url_inicio, 0, initial_category_name)]
    productos_totales = []
    urls_procesadas_count = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    while a_visitar:
        if len(productos_totales) >= product_limit_per_category: break
        url_actual, profundidad_actual, categoria_heredada_actual = a_visitar.pop(0)
        if url_actual in visitados or profundidad_actual > max_profundidad: continue
        visitados.add(url_actual)
        urls_procesadas_count += 1
        if urls_procesadas_count % 5 == 0: print(f"Procesando URL #{urls_procesadas_count}: {url_actual}")
        try:
            respuesta = requests.get(url_actual, timeout=20, headers=headers, verify=ssl_verify_option)
            respuesta.raise_for_status()
        except requests.RequestException as e:
            print(f"Error de red al acceder a {url_actual}: {e}")
            continue
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        categoria_para_descendientes = obtener_categoria_pagina_listado_esika(soup) or categoria_heredada_actual
        if soup.select_one("span.vtex-store-components-3-x-productBrand--product-name-pdp-product-name"):
            productos_totales.extend(extraer_productos_esika(soup, url_actual, categoria_para_descendientes))
        
        for link_tag in soup.select("a.vtex-product-summary-2-x-clearLink"):
            href = link_tag.get("href")
            if href:
                enlace_completo = urljoin(url_actual, href)
                if es_url_valida(enlace_completo) and urlparse(enlace_completo).netloc == urlparse(url_inicio).netloc and enlace_completo not in visitados:
                    a_visitar.append((enlace_completo, profundidad_actual + 1, categoria_para_descendientes))
        next_page_tag = soup.select_one('a.vtex-button[rel="next"]') or soup.find("a", class_=lambda x: x and "vtex-button" in x, string=re.compile(r"Mostrar más|Siguiente", re.I))
        if next_page_tag and next_page_tag.get("href"):
            enlace_completo = urljoin(url_actual, next_page_tag.get("href"))
            if es_url_valida(enlace_completo) and urlparse(enlace_completo).netloc == urlparse(url_inicio).netloc and enlace_completo not in visitados:
                a_visitar.append((enlace_completo, profundidad_actual, categoria_para_descendientes))
        time.sleep(retardo)
    return productos_totales

# --- FIN: FUNCIONES DE CRAWLING ---

# --- INICIO: NUEVA SECCIÓN DE CÓDIGO PARA CREDENCIALES ---

def extract_credentials(file_path):
    """
    Lee un archivo de texto y extrae el nombre de usuario y la contraseña
    usando expresiones regulares.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    
    username_match = re.search(r'username="([^"]+)"', content)
    password_match = re.search(r'password="([^"]+)"', content)
    
    if username_match and password_match:
        username = username_match.group(1)
        password = password_match.group(1)
        return username , password
    else:
        raise ValueError("No se encontraron el usuario o la contraseña en el archivo de credenciales.")

# --- FIN: NUEVA SECCIÓN DE CÓDIGO ---


# --- FUNCIÓN DE INSERCIÓN MODIFICADA ---
def insertar_productos_db(productos):
    if not productos:
        print("No hay productos para insertar en la base de datos.")
        return

    print("--- INICIANDO INSERCIÓN DE ÉSIKA CON SQLAlchemy y Pandas ---")
    
    try:
        df_productos = pd.DataFrame(productos)
        print(f"Se ha creado un DataFrame con {len(df_productos)} productos para procesar.")
        
        df_productos.rename(columns={'descripcion_detalle': 'descripcion', 'brand': 'producto', 'price': 'precio_actual_str'}, inplace=True)
        df_productos['precio_actual'] = pd.to_numeric(df_productos['precio_actual_str'].apply(convertir_precio), errors='coerce').fillna(0)
        df_productos['precio_normal'] = pd.to_numeric(df_productos['precio_normal'].apply(convertir_precio), errors='coerce').fillna(0)
        
        print(f"Productos antes del filtro: {len(df_productos)}")
        df_filtrado = df_productos[df_productos['precio_actual'] > 0].copy()
        print(f"Productos después del filtro (solo con precio > 0): {len(df_filtrado)}")
        
        if df_filtrado.empty:
            print("No quedaron productos válidos después de aplicar el filtro de precio. No se realizará la inserción.")
            return

        df_filtrado['marca_id'] = 2 # ID para Ésika
        df_filtrado['fecha_extraccion'] = pd.to_datetime('now', utc=True).tz_convert('America/Santiago').strftime("%Y-%m-%d %H:%M:%S")
        if 'url' not in df_filtrado.columns: df_filtrado['url'] = ''

        columnas_finales = ['marca_id', 'producto', 'categoria', 'precio_actual', 'descripcion', 'url', 'fecha_extraccion', 'precio_normal']
        df_final = df_filtrado.reindex(columns=columnas_finales)

        # --- INICIO: BLOQUE DE CÓDIGO MODIFICADO ---
        try:
            file_path = '/home/rpauser/airflow/notebooks/SQL2022.txt'
            username_sql, password_sql = extract_credentials(file_path)
            print("Credenciales de SQL Server obtenidas desde el archivo.")
        except Exception as e:
            print(f"Error al leer el archivo de credenciales: {e}")
            raise
            
        connection_url = URL.create(
            "mssql+pyodbc", 
            username=username_sql,    # <-- Reemplazado
            password=password_sql,    # <-- Reemplazado
            host="10.156.16.46\\SQL2022", 
            database="GAIA", 
            query={"driver": "ODBC Driver 17 for SQL Server"}
        )
        # --- FIN: BLOQUE DE CÓDIGO MODIFICADO ---

        engine = create_engine(connection_url)

        with engine.begin() as connection:
            start_time = time.time()
            df_final.to_sql(
                name='competencia_productos',
                schema='dbo',
                con=connection,
                if_exists='append',
                index=False,
                chunksize=500,
                method='multi'
            )
            end_time = time.time()
            print(f"Inserción de {len(df_final)} productos de Ésika completada en {end_time - start_time:.2f} segundos.")
            
    except Exception as e:
        print(f"ERROR durante el proceso de inserción con SQLAlchemy para Ésika: {e}")
        raise


# --- FUNCIÓN PRINCIPAL QUE ORQUESTA TODO ---
def ejecutar_proceso_esika():
    print("Iniciando el proceso completo de crawling y carga de datos para Ésika.")
    target_categories_config_esika = {
        "Maquillaje": "https://esika.tiendabelcorp.cl/maquillaje",
        "Perfumes": "https://esika.tiendabelcorp.cl/perfumes",
        "Skincare": "https://esika.tiendabelcorp.cl/skincare",
        "Cuidado personal": "https://esika.tiendabelcorp.cl/cuidado-personal",
    }
    all_products_esika = []
    ssl_verification_choice = False 
    if not ssl_verification_choice:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("¡ATENCIÓN! La verificación SSL está DESHABILITADA para Ésika.")
    
    for category_name_key, category_url in target_categories_config_esika.items():
        print(f"\n--- Iniciando crawling para Ésika categoría: {category_name_key} desde {category_url} ---")
        productos_de_cat = crawl_esika(
            url_inicio=category_url,
            max_profundidad=8,
            retardo=1,
            ssl_verify_option=ssl_verification_choice,
            initial_category_name=category_name_key,
            product_limit_per_category=300
        )
        all_products_esika.extend(productos_de_cat)

    print(f"\nTotal de productos extraídos de Ésika (bruto): {len(all_products_esika)}")
    
    final_filtered_products_esika = []
    seen_product_urls_esika = set()
    for prod in all_products_esika:
        prod_url = prod.get("url")
        if prod_url and prod_url not in seen_product_urls_esika:
            final_filtered_products_esika.append(prod)
            seen_product_urls_esika.add(prod_url)
    
    print(f"Total de productos únicos filtrados de Ésika para inserción: {len(final_filtered_products_esika)}")
    
    if final_filtered_products_esika:
        insertar_productos_db(final_filtered_products_esika)
    else:
        print("No se extrajeron productos de Ésika, no se realizará inserción en la base de datos.")
        
    print("Proceso completo de crawling y carga para Ésika finalizado exitosamente.")

if __name__ == "__main__":
    ejecutar_proceso_esika()