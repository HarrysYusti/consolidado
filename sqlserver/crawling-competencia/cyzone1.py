# Nombre del archivo: cyzone1.py
# Ubicación: /home/rpauser/airflow/notebooks/cyzone1.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import os
import urllib3

# Librerías para el nuevo método de inserción
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# --- Lógica original para el Certificado Zscaler ---
cert_path = None
try:
    base_script_path = os.path.dirname(__file__) if '__file__' in globals() else os.getcwd()
    cert_path_candidate = os.path.join(base_script_path, "zscaler_root.pem")
    if os.path.isfile(cert_path_candidate):
        cert_path = cert_path_candidate
        print(f"✅ Certificado Zscaler encontrado en: {cert_path}")
    else:
        print(f"⚠️ ADVERTENCIA: No se encontró 'zscaler_root.pem' en {base_script_path}.")
except Exception as e_cert:
    print(f"⚠️ ADVERTENCIA: Error al localizar el certificado Zscaler: {e_cert}")


# --- INICIO: FUNCIONES DE CRAWLING COMPLETAS Y RESTAURADAS ---

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

def obtener_categoria_pagina_listado_cyzone(soup):
    category_span_tag = soup.select_one("a.link.belcorp-breadcrumb-custom-0-x-breadcrumbLink span.belcorp-breadcrumb-custom-0-x-lastBreadcrumb")
    if category_span_tag:
        return category_span_tag.get_text(strip=True).capitalize()
    return None

def extraer_productos_cyzone(soup, url_actual, categoria_heredada):
    # Esta es la versión corregida que sí extrae precios
    productos = []
    nombre_producto_tag = soup.select_one("span.vtex-store-components-3-x-productBrand--product-name-pdp-product-name")
    if not nombre_producto_tag: 
        return []
    
    nombre_producto = nombre_producto_tag.get_text(strip=True)

    precio_actual_str = "No encontrado"
    precio_normal_str = "No encontrado"
    search_area = soup

    def _construir_precio_desde_contenedor(contenedor):
        if not contenedor: return "No encontrado"
        currency_code_tag = contenedor.select_one("span.belcorp-belcorp-product-price-0-x-currencyCode--pdp")
        currency_integer_tags = contenedor.select("span.belcorp-belcorp-product-price-0-x-currencyInteger--pdp")
        if currency_code_tag and currency_integer_tags:
            partes_enteras = "".join([tag.get_text(strip=True) for tag in currency_integer_tags])
            precio_construido = f"{currency_code_tag.get_text(strip=True)}{partes_enteras}"
            return precio_construido.strip()
        raw_text = contenedor.get_text(strip=True, separator=' ')
        return raw_text if raw_text and any(char.isdigit() for char in raw_text) else "No encontrado"

    selling_price_wrapper = search_area.select_one("span.belcorp-belcorp-product-price-0-x-sellingPriceValue--pdp")
    list_price_wrapper = search_area.select_one("span.belcorp-belcorp-product-price-0-x-listPriceValue--pdp")
    
    if selling_price_wrapper:
        precio_actual_str = _construir_precio_desde_contenedor(selling_price_wrapper)
    
    if list_price_wrapper:
        precio_normal_str = _construir_precio_desde_contenedor(list_price_wrapper)
    
    if precio_actual_str == "No encontrado" and precio_normal_str != "No encontrado":
        precio_actual_str = precio_normal_str
    elif precio_actual_str != "No encontrado" and precio_normal_str == "No encontrado":
        precio_normal_str = precio_actual_str

    descripcion_producto_texto = "No disponible"
    desc_overall_container = soup.select_one("div.vtex-store-components-3-x-productDescriptionContainer") or soup.select_one("div.vtex-store-components-3-x-productDescriptionText")
    if desc_overall_container:
        content_div = desc_overall_container.select_one("div.vtex-store-components-3-x-content")
        if content_div:
            text_candidate = ' '.join(content_div.get_text(separator=' ', strip=True).split())
            if text_candidate:
                descripcion_producto_texto = text_candidate
    
    productos.append({
        "brand": nombre_producto, 
        "price": precio_actual_str, 
        "precio_normal": precio_normal_str, 
        "categoria": categoria_heredada, 
        "descripcion_producto": descripcion_producto_texto, 
        "url": url_actual
    })
    return productos

def crawl_cyzone(url_inicio, max_profundidad=7, retardo=2, ssl_verify_option=False, initial_category_name="General", product_limit_per_category=300):
    visitados = set()
    a_visitar = [(url_inicio, 0, initial_category_name)]
    productos_de_esta_categoria_crawl = []
    urls_procesadas_count = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    while a_visitar:
        if len(productos_de_esta_categoria_crawl) >= product_limit_per_category:
            print(f"    Límite de {product_limit_per_category} productos alcanzado para '{initial_category_name}'.")
            break
        
        url_actual, profundidad_actual, categoria_heredada_actual = a_visitar.pop(0)
        if url_actual in visitados or profundidad_actual > max_profundidad:
            continue
            
        visitados.add(url_actual)
        urls_procesadas_count += 1
        if urls_procesadas_count % 5 == 0 or profundidad_actual == 0:
            print(f"Procesando ({urls_procesadas_count}): {url_actual}")
            
        try:
            respuesta = requests.get(url_actual, timeout=20, headers=headers, verify=ssl_verify_option)
            respuesta.raise_for_status()
        except requests.RequestException as e:
            print(f"Error de red al acceder a {url_actual}: {e}")
            continue
            
        html = respuesta.text
        soup = BeautifulSoup(html, 'html.parser')
        categoria_para_descendientes = obtener_categoria_pagina_listado_cyzone(soup) or categoria_heredada_actual
        
        if soup.select_one("span.vtex-store-components-3-x-productBrand--product-name-pdp-product-name"):
            productos_de_esta_categoria_crawl.extend(extraer_productos_cyzone(soup, url_actual, categoria_para_descendientes))
            
        if profundidad_actual < max_profundidad:
            for link_tag in soup.select("a.vtex-product-summary-2-x-clearLink"):
                href = link_tag.get("href")
                if href:
                    enlace_completo = urljoin(url_actual, href)
                    if es_url_valida(enlace_completo) and urlparse(enlace_completo).netloc == urlparse(url_inicio).netloc and enlace_completo not in visitados:
                        a_visitar.append((enlace_completo, profundidad_actual + 1, categoria_para_descendientes))

            next_page_tag = None
            label_div = soup.find("div", class_="vtex-button__label", string=re.compile(r"Mostrar más", re.I))
            if label_div:
                next_page_tag = label_div.find_parent('a') or label_div.find_parent('button')
            
            if not next_page_tag:
                next_page_tag = soup.select_one('a.vtex-button[rel="next"]')
            
            if next_page_tag and next_page_tag.get("href"):
                enlace_completo = urljoin(url_actual, next_page_tag.get("href"))
                if es_url_valida(enlace_completo) and urlparse(enlace_completo).netloc == urlparse(url_inicio).netloc and enlace_completo not in visitados:
                    print(f"Paginación encontrada. Añadiendo a la cola: {enlace_completo}")
                    a_visitar.append((enlace_completo, profundidad_actual, categoria_para_descendientes))
            
        time.sleep(retardo)
        
    print(f"Crawl para '{initial_category_name}' finalizado. Extraídos {len(productos_de_esta_categoria_crawl)} productos.")
    return productos_de_esta_categoria_crawl

# --- FIN: FUNCIONES DE CRAWLING ---

# --- INICIO: NUEVA SECCIÓN DE CÓDIGO PARA CREDENCIALES ---

# Función para extraer credenciales desde un archivo de texto
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
        # Lanza un error si las credenciales no se encuentran, para detener la ejecución.
        raise ValueError("No se encontraron el usuario o la contraseña en el archivo de credenciales.")

# --- FIN: NUEVA SECCIÓN DE CÓDIGO ---


# --- FUNCIÓN DE INSERCIÓN MODIFICADA ---
def insertar_productos_db(productos):
    if not productos:
        print("No hay productos para insertar en la base de datos.")
        return
    print("--- INICIANDO INSERCIÓN DE CYZONE CON SQLAlchemy y Pandas ---")
    try:
        df_productos = pd.DataFrame(productos)
        print(f"Se ha creado un DataFrame con {len(df_productos)} productos para procesar.")
        df_productos.rename(columns={'descripcion_producto': 'descripcion', 'brand': 'producto', 'price': 'precio_actual_str'}, inplace=True)
        df_productos['precio_actual'] = pd.to_numeric(df_productos['precio_actual_str'].apply(convertir_precio), errors='coerce').fillna(0)
        df_productos['precio_normal'] = pd.to_numeric(df_productos['precio_normal'].apply(convertir_precio), errors='coerce').fillna(0)
        print(f"Productos antes del filtro de precio: {len(df_productos)}")
        df_filtrado = df_productos[df_productos['precio_actual'] > 0].copy()
        print(f"Productos después del filtro (precio > 0): {len(df_filtrado)}")
        if df_filtrado.empty:
            print("No quedaron productos válidos después del filtro. No se realizará la inserción.")
            return
            
        df_filtrado['marca_id'] = 18
        df_filtrado['fecha_extraccion'] = pd.to_datetime('now', utc=True).tz_convert('America/Santiago').strftime("%Y-%m-%d %H:%M:%S")
        if 'url' not in df_filtrado.columns: df_filtrado['url'] = ''
        columnas_finales = ['marca_id', 'producto', 'categoria', 'precio_actual', 'descripcion', 'url', 'fecha_extraccion', 'precio_normal']
        df_final = df_filtrado.reindex(columns=columnas_finales)
        
        # --- INICIO: BLOQUE DE CÓDIGO MODIFICADO ---
        try:
            # Ruta al archivo de credenciales
            file_path = '/home/rpauser/airflow/notebooks/SQL2022.txt'
            # Llamar a la función para obtener usuario y contraseña
            username_sql, password_sql = extract_credentials(file_path)
            print("Credenciales de SQL Server obtenidas desde el archivo.")
        except Exception as e:
            print(f"Error al leer el archivo de credenciales: {e}")
            raise # Detener la ejecución si no se pueden leer las credenciales

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
            df_final.to_sql(name='competencia_productos', schema='dbo', con=connection, if_exists='append', index=False, chunksize=500, method='multi')
            end_time = time.time()
            print(f"Inserción de {len(df_final)} productos de Cyzone completada en {end_time - start_time:.2f} segundos.")
    except Exception as e:
        print(f"ERROR durante el proceso de inserción con SQLAlchemy para Cyzone: {e}")
        raise

# --- FUNCIÓN PRINCIPAL QUE ORQUESTA TODO ---
def ejecutar_proceso_cyzone():
    print("Iniciando el proceso completo de crawling y carga de datos para Cyzone.")
    target_categories_config_cyzone = {
        "Maquillaje": "https://cyzone.tiendabelcorp.cl/maquillaje/c",
        "Skincare": "https://cyzone.tiendabelcorp.cl/skincare/c",
        "Cuidado personal": "https://cyzone.tiendabelcorp.cl/cuidado-personal/c",
        "Perfumes": "https://cyzone.tiendabelcorp.cl/perfumes/c"
    }
    all_products_cyzone = []
    final_ssl_verify_for_crawl = cert_path if cert_path else False
    if not final_ssl_verify_for_crawl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("¡ATENCIÓN! La verificación SSL está DESHABILITADA.")
    for category_name_key, category_url in target_categories_config_cyzone.items():
        print(f"\n--- Iniciando crawling para Cyzone categoría: {category_name_key} ---")
        productos_de_cat = crawl_cyzone(
            url_inicio=category_url,
            max_profundidad=7,
            retardo=2,
            ssl_verify_option=final_ssl_verify_for_crawl,
            initial_category_name=category_name_key,
            product_limit_per_category=300
        )
        all_products_cyzone.extend(productos_de_cat)
    print(f"\nTotal de productos únicos extraídos de Cyzone: {len(all_products_cyzone)}")
    if all_products_cyzone:
        insertar_productos_db(all_products_cyzone)
    else:
        print("No se extrajeron productos de Cyzone.")
    print("Proceso completo de crawling y carga para Cyzone finalizado exitosamente.")

if __name__ == "__main__":
    ejecutar_proceso_cyzone()