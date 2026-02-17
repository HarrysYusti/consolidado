# Nombre del archivo: dbs1.py
# Ubicación: /home/rpauser/airflow/notebooks/dbs1.py

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

def obtener_categoria_pagina_listado_dbs(soup):
    category_title_tag = soup.select_one("h1.category-title")
    if category_title_tag:
        return category_title_tag.get_text(strip=True)
    return None

def extraer_productos_dbs(soup, url_actual, categoria_heredada):
    productos = []
    nombre_producto_tag = soup.select_one("h1.page-title span.base")
    if not nombre_producto_tag:
        return []
    
    nombre_producto = nombre_producto_tag.get_text(strip=True)

    precio_actual_str = "No encontrado"
    precio_normal_str = "No encontrado"
    selling_price_container = soup.select_one("span[data-price-type='finalPrice']")
    list_price_container = soup.select_one("span[data-price-type='oldPrice']")

    if selling_price_container:
        precio_actual_str = selling_price_container.select_one("span.price").get_text(strip=True) if selling_price_container.select_one("span.price") else "No encontrado"
    
    if list_price_container:
        precio_normal_str = list_price_container.select_one("span.price").get_text(strip=True) if list_price_container.select_one("span.price") else "No encontrado"

    if precio_actual_str != "No encontrado" and precio_normal_str == "No encontrado":
        precio_normal_str = precio_actual_str

    descripcion_producto_texto = "No disponible"
    description_element = soup.select_one("div.product.attribute.description .value")
    
    if not description_element:
        description_element = soup.select_one("div#description")

    if description_element:
        descripcion_producto_texto = ' '.join(description_element.get_text(separator=' ', strip=True).split())

    productos.append({
        "brand": nombre_producto, 
        "price": precio_actual_str,
        "precio_normal": precio_normal_str, 
        "categoria": categoria_heredada,
        "descripcion_producto": descripcion_producto_texto, 
        "url": url_actual
    })
    return productos

def crawl_dbs(url_inicio, max_profundidad=5, retardo=1, ssl_verify_option=False, initial_category_name="General", product_limit_per_category=300):
    visitados = set()
    a_visitar = [(url_inicio, 0, initial_category_name)]
    productos_de_esta_categoria_crawl = []
    urls_procesadas_count = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    while a_visitar:
        if len(productos_de_esta_categoria_crawl) >= product_limit_per_category: break
        url_actual, profundidad_actual, categoria_heredada_actual = a_visitar.pop(0)
        if url_actual in visitados or profundidad_actual > max_profundidad: continue
        visitados.add(url_actual)
        urls_procesadas_count += 1
        if urls_procesadas_count % 5 == 0: print(f"Procesando ({urls_procesadas_count}): {url_actual}")
        try:
            respuesta = requests.get(url_actual, timeout=60, headers=headers, verify=ssl_verify_option)
            respuesta.raise_for_status()
        except requests.RequestException as e:
            print(f"Error de red al acceder a {url_actual}: {e}")
            continue
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        categoria_para_descendientes = obtener_categoria_pagina_listado_dbs(soup) or categoria_heredada_actual
        if soup.select_one("h1.page-title span.base"):
            productos_de_esta_categoria_crawl.extend(extraer_productos_dbs(soup, url_actual, categoria_para_descendientes))
        if profundidad_actual < max_profundidad:
            for link_tag in soup.select("a.product.photo.product-item-photo"):
                href = link_tag.get("href")
                if href:
                    enlace_completo = urljoin(url_actual, href)
                    if es_url_valida(enlace_completo) and urlparse(enlace_completo).netloc == urlparse(url_inicio).netloc and enlace_completo not in visitados:
                        a_visitar.append((enlace_completo, profundidad_actual + 1, categoria_para_descendientes))
            next_page_tag = soup.select_one("li.pages-item-next a.action.next")
            if next_page_tag and next_page_tag.get("href"):
                enlace_completo = urljoin(url_actual, next_page_tag.get("href"))
                if es_url_valida(enlace_completo) and urlparse(enlace_completo).netloc == urlparse(url_inicio).netloc and enlace_completo not in visitados:
                    a_visitar.append((enlace_completo, profundidad_actual, categoria_para_descendientes))
        time.sleep(retardo)
    print(f"Crawl para '{initial_category_name}' finalizado. Extraídos {len(productos_de_esta_categoria_crawl)} productos.")
    return productos_de_esta_categoria_crawl

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
    print("--- INICIANDO INSERCIÓN DE DBS CON SQLAlchemy y Pandas ---")
    try:
        df_productos = pd.DataFrame(productos)
        
        df_productos.rename(columns={
            'descripcion_producto': 'descripcion',   
            'brand': 'producto',   
            'price': 'precio_actual_str'
        }, inplace=True)
        
        df_productos['precio_actual'] = df_productos['precio_actual_str'].apply(convertir_precio)
        df_productos['precio_normal'] = df_productos['precio_normal'].apply(convertir_precio)

        print(f"Productos antes del filtro de precio: {len(df_productos)}")
        df_filtrado = df_productos[df_productos['precio_actual'] > 0].copy()
        print(f"Productos después del filtro (precio > 0): {len(df_filtrado)}")

        if df_filtrado.empty:
            print("No quedaron productos válidos después del filtro. No se realizará la inserción.")
            return

        df_filtrado['marca_id'] = 9 # ID correcto para DBS
        df_filtrado['fecha_extraccion'] = pd.to_datetime('now', utc=True).tz_convert('America/Santiago').strftime("%Y-%m-%d %H:%M:%S")
        if 'url' not in df_filtrado.columns: df_filtrado['url'] = ''

        columnas_finales = [
            'marca_id', 'producto', 'categoria', 'precio_actual', 'descripcion', 'url',
            'fecha_extraccion', 'precio_normal'
        ]
        # Añadimos columnas faltantes con None si no existen en el df
        for col in columnas_finales:
            if col not in df_filtrado.columns:
                df_filtrado[col] = None
        
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
            username=username_sql,     # <-- Reemplazado
            password=password_sql,     # <-- Reemplazado
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
                chunksize=200,
                method=None
            )
            end_time = time.time()
            print(f"Inserción de {len(df_final)} productos de DBS completada en {end_time - start_time:.2f} segundos.")
            
    except Exception as e:
        print(f"ERROR durante el proceso de inserción con SQLAlchemy para DBS: {e}")
        raise

# --- FUNCIÓN PRINCIPAL QUE ORQUESTA TODO ---
def ejecutar_proceso_dbs():
    print("Iniciando el proceso completo de crawling y carga de datos para DBS.")
    
    target_categories_config = {
        "Maquillaje": "https://dbs.cl/maquillaje",
        "Skincare": "https://dbs.cl/skincare",
        "Capilar": "https://dbs.cl/capilar",
        "Corporal": "https://dbs.cl/corporal",
        "Perfumes": "https://dbs.cl/perfumes"
    }
    
    all_products_from_focused_categories = []
    ssl_verification = False
    if not ssl_verification:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("¡ATENCIÓN! La verificación SSL está DESHABILITADA.")

    for category_name_key, category_url_start in target_categories_config.items():
        print(f"\n--- Iniciando crawling para DBS categoría: {category_name_key} ---")
        productos_de_esta_categoria = crawl_dbs(
            url_inicio=category_url_start,
            max_profundidad=5,
            retardo=1,
            ssl_verify_option=ssl_verification,
            initial_category_name=category_name_key,
            product_limit_per_category=250
        )
        all_products_from_focused_categories.extend(productos_de_esta_categoria)

    print(f"\nTotal de productos únicos extraídos de DBS: {len(all_products_from_focused_categories)}")

    if all_products_from_focused_categories:
        insertar_productos_db(all_products_from_focused_categories)
    else:
        print("No se extrajeron productos de DBS.")
        
    print("Proceso completo de crawling y carga para DBS finalizado exitosamente.")

if __name__ == "__main__":
    ejecutar_proceso_dbs()