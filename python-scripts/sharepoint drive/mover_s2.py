import time
import os
import csv
from playwright.sync_api import sync_playwright

# --- CONFIGURACIÓN ---
RUTA_DESTINO_RAIZ = r"G:\Unidades compartidas\Finanzas Chile\07_ Old\2019"
ARCHIVO_AUTH = "auth_sharepoint.json"
ARCHIVO_FALTANTES = os.path.join(RUTA_DESTINO_RAIZ, "faltantes.csv")
SHAREPOINT_URL = "https://naturabr.sharepoint.com/teams/PLFinanciero/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fteams%2FPLFinanciero%2FDocumentos%20Compartilhados%2FGeneral%2F2019&viewid=c7229e51%2D388c%2D4691%2D8cdf%2D74e0a71c6756"

# Variable global para el límite (se pedirá al inicio)
MAX_MB_PERMITIDO = 0 # En MB

def inicializar_reporte():
    if not os.path.exists(ARCHIVO_FALTANTES):
        try:
            with open(ARCHIVO_FALTANTES, mode='w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f, delimiter=';').writerow(["Nombre", "Ruta", "Error", "Fecha"])
        except: pass

def registrar_error(nombre, ruta, error):
    try:
        with open(ARCHIVO_FALTANTES, mode='a', newline='', encoding='utf-8-sig') as f:
            csv.writer(f, delimiter=';').writerow([nombre, ruta, str(error), time.strftime("%Y-%m-%d %H:%M")])
    except: pass

def login_manual(p):
    print("\n🔐 LOGIN REQUERIDO.")
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(SHAREPOINT_URL)
    input("👉 Inicia sesión y presiona ENTER cuando veas los archivos...")
    context.storage_state(path=ARCHIVO_AUTH)
    browser.close()

def analizar_fila(fila):
    """Devuelve nombre y si es carpeta"""
    try:
        texto = fila.inner_text()
        nombre = texto.split('\n')[0].strip()
        texto_lower = texto.lower()
        
        # Detección de carpeta
        es_carpeta = "elemento" in texto_lower or fila.locator("i[data-icon-name*='Folder']").count() > 0
        
        # Excepciones visuales
        exts = [".xlsx", ".pdf", ".csv", ".docx", ".txt", ".pptx", ".zip", ".rar", ".msg", ".xlsm"]
        if any(ext in nombre.lower() for ext in exts):
            es_carpeta = False
            
        return nombre, es_carpeta
    except:
        return None, False

def procesar_carpeta_recursiva(page, ruta_local_actual, nivel=0):
    indent = "   " * nivel
    print(f"\n{indent}📂 RUTA: {ruta_local_actual}")
    
    # 1. Asegurar carpeta local
    os.makedirs(ruta_local_actual, exist_ok=True)

    # 2. Esperar carga de lista
    try:
        page.wait_for_selector("div[role='row']", timeout=10000)
        time.sleep(1) # Estabilizar
    except:
        print(f"{indent}   ⚠️ Carpeta vacía o error de carga.")
        return

    # 3. ESCANEO (INVENTARIO)
    items_carpeta = [] # Nombres de subcarpetas
    items_archivo = [] # Nombres de archivos
    
    filas = page.get_by_role("row").all()
    for fila in filas[1:]: # Saltar header
        if not fila.is_visible(): fila.scroll_into_view_if_needed()
        nombre, es_carpeta = analizar_fila(fila)
        if nombre:
            if es_carpeta:
                items_carpeta.append(nombre)
            else:
                items_archivo.append(nombre)

    # === PASO 1: CREAR ESTRUCTURA DE CARPETAS (ESPEJO) ===
    if items_carpeta:
        print(f"{indent}   🔨 Creando {len(items_carpeta)} carpetas vacías...")
        for nombre_folder in items_carpeta:
            ruta_subcarpeta = os.path.join(ruta_local_actual, nombre_folder)
            if not os.path.exists(ruta_subcarpeta):
                os.makedirs(ruta_subcarpeta, exist_ok=True)

    # === PASO 2: DESCARGAR ARCHIVOS (CON FILTRO MB) ===
    if items_archivo:
        print(f"{indent}   ⬇️  Procesando {len(items_archivo)} archivos...")
        
    for nombre_archivo in items_archivo:
        ruta_final = os.path.join(ruta_local_actual, nombre_archivo)
        
        if os.path.exists(ruta_final):
            continue 

        print(f"{indent}   ... {nombre_archivo}")
        
        try:
            # Re-localizar fila fresca (Vital para evitar error "Target closed")
            fila_viva = page.get_by_role("row").filter(has_text=nombre_archivo).first
            
            # Scroll y Clic Derecho
            fila_viva.scroll_into_view_if_needed()
            fila_viva.click(button="right")
            
            # Descargar
            with page.expect_download(timeout=30000) as download_info:
                # Intentamos selectores robustos para el menú
                if page.get_by_role("menuitem", name="Descargar").is_visible():
                    page.get_by_role("menuitem", name="Descargar").click()
                elif page.get_by_role("menuitem", name="Download").is_visible():
                    page.get_by_role("menuitem", name="Download").click()
                else:
                    # Fallback
                    page.locator("button[name='Descargar']").click()
            
            download = download_info.value
            temp_path = download.path() # Ruta temporal
            
            # --- VERIFICACIÓN DE PESO ---
            peso_bytes = os.path.getsize(temp_path)
            peso_mb = peso_bytes / (1024 * 1024)
            
            if peso_mb > MAX_MB_PERMITIDO:
                print(f"{indent}      🛑 SALTEADO: Pesa {peso_mb:.2f} MB (Máx: {MAX_MB_PERMITIDO} MB)")
                registrar_error(nombre_archivo, ruta_local_actual, f"Excede peso ({peso_mb:.2f} MB)")
                # No guardamos, dejamos que Playwright borre el temporal
            else:
                # Guardar
                download.save_as(ruta_final)
                print(f"{indent}      ✅ Guardado ({peso_mb:.2f} MB)")

        except Exception as e:
            print(f"{indent}      ❌ ERROR: {e}")
            registrar_error(nombre_archivo, ruta_local_actual, e)
            # Asegurar cerrar menú si quedó abierto
            page.locator("body").click()

    # === PASO 3: ENTRAR A SUBCARPETAS (RECURSIVIDAD) ===
    for nombre_folder in items_carpeta:
        ruta_subcarpeta = os.path.join(ruta_local_actual, nombre_folder)
        print(f"{indent}   👉 Entrando a: {nombre_folder}")
        
        try:
            # Re-localizar botón fresco
            # Usamos lógica de botón exacta + fallback de texto
            try:
                page.get_by_role("button", name=nombre_folder).first.click()
            except:
                page.get_by_text(nombre_folder, exact=True).first.click()

            page.wait_for_load_state("networkidle", timeout=10000)
            
            # --- RECURSIÓN ---
            procesar_carpeta_recursiva(page, ruta_subcarpeta, nivel + 1)
            
            # VOLVER
            print(f"{indent}   🔙 Regresando...")
            page.go_back()
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Espera vital para refrescar la lista padre
            page.wait_for_selector("div[role='row']", timeout=10000)
            time.sleep(1) 

        except Exception as e:
            print(f"{indent}   ❌ No pude navegar a {nombre_folder}: {e}")
            registrar_error(nombre_folder, ruta_local_actual, "Error navegación")
            # Si falla navegación, intentamos recuperar estado recargando
            page.reload()
            page.wait_for_load_state("networkidle")

def run():
    global MAX_MB_PERMITIDO
    
    if not os.path.exists(RUTA_DESTINO_RAIZ):
        print(f"❌ Error: No existe ruta G: {RUTA_DESTINO_RAIZ}")
        return

    # --- PEDIR DATOS AL USUARIO ---
    print("\n--- CONFIGURACIÓN ---")
    try:
        entrada = input("¿Cuál es el peso MÁXIMO por archivo en MB? (Ej: 50): ")
        MAX_MB_PERMITIDO = float(entrada)
    except:
        MAX_MB_PERMITIDO = 50.0
        print("⚠️ Entrada inválida. Usando 50 MB por defecto.")

    print(f"🎯 Límite establecido: {MAX_MB_PERMITIDO} MB")
    print("---------------------\n")

    inicializar_reporte()

    # Bucle de estabilidad
    while True:
        try:
            with sync_playwright() as p:
                if not os.path.exists(ARCHIVO_AUTH):
                    login_manual(p)

                print("🚀 INICIANDO V15...")
                browser = p.chromium.launch(headless=False, slow_mo=800) # Más lento para estabilidad
                context = browser.new_context(storage_state=ARCHIVO_AUTH, accept_downloads=True)
                page = context.new_page()
                
                # Ir a Inicio
                page.goto(SHAREPOINT_URL, timeout=60000)
                
                # Validar sesión
                try:
                    page.wait_for_selector("div[role='row']", timeout=20000)
                except:
                    print("🛑 Sesión caducada. Reiniciando...")
                    os.remove(ARCHIVO_AUTH)
                    browser.close()
                    continue

                # EJECUTAR RECORRIDO
                procesar_carpeta_recursiva(page, RUTA_DESTINO_RAIZ)
                
                print("\n🏁 PROCESO FINALIZADO.")
                browser.close()
                break # Romper bucle si termina bien

        except Exception as e:
            print(f"\n🔥 CRASH DEL NAVEGADOR: {e}")
            print("🔄 Reiniciando en 5 segundos...")
            time.sleep(5)

if __name__ == "__main__":
    run()