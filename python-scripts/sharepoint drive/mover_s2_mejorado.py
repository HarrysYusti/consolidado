import time
import os
import csv
import re
from playwright.sync_api import sync_playwright

# --- CONFIGURACIÓN ---
# RUTA_DESTINO_RAIZ = r"G:\Unidades compartidas\Finanzas Chile\07_ Old\2019"
RUTA_DESTINO_RAIZ = r"G:\Unidades compartidas\Finanzas Chile\07_ Old\2022"
ARCHIVO_AUTH = "auth_sharepoint.json"
ARCHIVO_FALTANTES = os.path.join(RUTA_DESTINO_RAIZ, "errores_descarga.csv")
ARCHIVO_COMPLETADAS = "carpetas_completadas.txt"
# SHAREPOINT_URL = "https://naturabr.sharepoint.com/teams/PLFinanciero/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fteams%2FPLFinanciero%2FDocumentos%20Compartilhados%2FGeneral%2F2019&viewid=c7229e51%2D388c%2D4691%2D8cdf%2D74e0a71c6756"
SHAREPOINT_URL = "https://naturabr.sharepoint.com/teams/PLFinanciero/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fteams%2FPLFinanciero%2FDocumentos%20Compartilhados%2FGeneral%2F2022&viewid=c7229e51%2D388c%2D4691%2D8cdf%2D74e0a71c6756"

# Límite global asignado en ejecución
MAX_MB_PERMITIDO = 0.0

def limpiar_nombre(nombre):
    """Limpia caracteres no válidos en nombres de archivos/carpetas en Windows"""
    return re.sub(r'[\\/*?:"<>|]', "", nombre).strip()

def ruta_segura(ruta):
    """Añade el prefijo \\?\ para permitir rutas largas en Windows"""
    ruta = os.path.abspath(ruta)
    if not ruta.startswith("\\\\?\\"):
        ruta = "\\\\?\\" + ruta
    return ruta

def inicializar_logs():
    if not os.path.exists(ruta_segura(RUTA_DESTINO_RAIZ)):
        os.makedirs(ruta_segura(RUTA_DESTINO_RAIZ), exist_ok=True)
    try:
        ruta_csv = ruta_segura(ARCHIVO_FALTANTES)
        if not os.path.exists(ruta_csv):
            with open(ruta_csv, mode='w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f, delimiter=';').writerow(["Nombre", "Ruta", "Error", "Fecha"])
    except: pass
    
    if not os.path.exists(ARCHIVO_COMPLETADAS):
        with open(ARCHIVO_COMPLETADAS, "w", encoding="utf-8") as f:
            pass

def generar_mapa_drive():
    """Genera un mapa completo actual del Drive local antes de empezar para referencia del usuario"""
    print("\n🔍 1. Generando Mapeo Completo Inicial de Google Drive local...")
    csv_file = "mapa_drive.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["tipo", "ruta_relativa"])
        
        ruta_raiz_abs = ruta_segura(RUTA_DESTINO_RAIZ)
        for root, dirs, files in os.walk(ruta_raiz_abs):
            for directory in dirs:
                full_dir = os.path.join(root, directory)
                rel_path = os.path.relpath(full_dir, ruta_raiz_abs)
                writer.writerow(["Carpeta", rel_path])
            for f in files:
                if f not in ["desktop.ini", "errores_descarga.csv", "carpetas_completadas.txt"]:
                    full_file = os.path.join(root, f)
                    rel_path = os.path.relpath(full_file, ruta_raiz_abs)
                    writer.writerow(["Archivo", rel_path])
    print(f"✅ Mapa local Drive guardado en '{csv_file}'.")

def contar_archivos_locales(ruta_relativa):
    """
    Cuenta todos los archivos (recursivamente) en la carpeta local correspondiente.
    Excluye archivos de sistema.
    """
    EXCLUIR = {"desktop.ini", "errores_descarga.csv", "carpetas_completadas.txt"}
    ruta_abs = ruta_segura(os.path.join(RUTA_DESTINO_RAIZ, ruta_relativa))
    if not os.path.exists(ruta_abs):
        return 0
    count = 0
    for _, _, files in os.walk(ruta_abs):
        for f in files:
            if f not in EXCLUIR:
                count += 1
    return count

def cargar_completadas():
    completadas = set()
    if os.path.exists(ARCHIVO_COMPLETADAS):
        with open(ARCHIVO_COMPLETADAS, "r", encoding="utf-8-sig") as f:
            for line in f:
                stripped = line.strip()  # strip completo: \n, \r, espacios
                if stripped:  # ignorar líneas vacías
                    completadas.add(stripped)
    return completadas

def marcar_completada(ruta_relativa):
    # La RAIZ (string vacío) se guarda con un marcador explícito para no confundirse con líneas vacías
    entrada = ruta_relativa if ruta_relativa else "__RAIZ_COMPLETA__"
    with open(ARCHIVO_COMPLETADAS, "a", encoding="utf-8") as f:
        f.write(entrada + "\n")

def registrar_error(nombre, ruta, error):
    try:
        ruta_csv = ruta_segura(ARCHIVO_FALTANTES)
        with open(ruta_csv, mode='a', newline='', encoding='utf-8-sig') as f:
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

def cerrar_popups(page):
    try:
        page.keyboard.press("Escape")
        time.sleep(0.5)

        # Fallback explícito del codegen: botones que tengan el nombre "dismiss"
        try:
            dismiss_btns = page.get_by_role("button", name=re.compile("dismiss", re.IGNORECASE)).all()
            for btn in dismiss_btns:
                if btn.is_visible():
                    btn.click()
                    time.sleep(0.5)
        except: pass

        bloqueadores = page.locator("button[aria-label='Cerrar'], button[aria-label='Close'], button[title='Cerrar'], i[data-icon-name='Cancel']").all()
        for btn in bloqueadores:
            if btn.is_visible():
                btn.click()
                time.sleep(0.5)
    except: pass

def analizar_fila(fila):
    try:
        texto = fila.inner_text()
        if not texto.strip(): return None, False, 0
        lineas = [l.strip() for l in texto.split('\n') if l.strip()]
        if not lineas: return None, False, 0
        
        nombre = limpiar_nombre(lineas[0])
        texto_low = texto.lower()
        
        es_carpeta = False
        num_elementos = 0
        
        match = re.search(r'(\d+)\s*elementos?', texto_low)
        if match:
            es_carpeta = True
            num_elementos = int(match.group(1))
        elif "elemento" in texto_low or fila.locator("i[data-icon-name*='Folder']").count() > 0:
            es_carpeta = True
            
        exts = [".xlsx", ".pdf", ".csv", ".docx", ".txt", ".pptx", ".zip", ".rar", ".msg", ".xlsm", ".xls"]
        if any(ext in nombre.lower() for ext in exts):
            es_carpeta = False
            
        return nombre, es_carpeta, num_elementos
    except: return None, False, 0

def procesar_carpeta(page, ruta_relativa_actual, completadas):
    """
    Lista elementos de la carpeta actual, descarga los archivos que falten y luego
    entra recursivamente en las subcarpetas. Al finalizar exitosamente, marca la carpeta.
    """
    indent = "   " * (ruta_relativa_actual.count(os.sep) + 1 if ruta_relativa_actual else 0)
    print(f"\n{indent}🗂️ [PROCESANDO] '{ruta_relativa_actual or 'RAIZ'}'")
    
    # Crear carpeta local si no existe
    ruta_local_abs = ruta_segura(os.path.join(RUTA_DESTINO_RAIZ, ruta_relativa_actual))
    os.makedirs(ruta_local_abs, exist_ok=True)

    try: 
        page.wait_for_selector("div[role='row']", timeout=15000)
    except Exception as e: 
        print(f"{indent}   ❌ No cargaron los elementos: {e}")
        return False

    cerrar_popups(page)
    time.sleep(1)

    items_carpeta = []
    items_archivo = []
    
    # Leer el DOM y clasificar
    filas = page.locator("div[role='row']").all()
    for fila in filas[1:]: 
        if not fila.is_visible(): 
            try: fila.scroll_into_view_if_needed()
            except: pass
        nombre, es_carpeta, num_elementos = analizar_fila(fila)
        if nombre:
            if es_carpeta: items_carpeta.append({"nombre": nombre, "num_elementos": num_elementos})
            else: items_archivo.append(nombre)

    # 1. Procesar Archivos (Descargar los que no existan localmente)
    # Si algún archivo es omitido por peso, la carpeta NO se marcará como completa.
    archivos_todos_ok = True
    for nombre_archivo in items_archivo:
        rel_path_file = os.path.join(ruta_relativa_actual, nombre_archivo) if ruta_relativa_actual else nombre_archivo
        p_abs_final = os.path.join(RUTA_DESTINO_RAIZ, rel_path_file)
        ruta_seg_final = ruta_segura(p_abs_final)

        if os.path.exists(ruta_seg_final):
            continue  # Ya existe, saltar
            
        print(f"{indent}   ... Descargando: {nombre_archivo}")
        try:
            fv = page.locator("div[role='row']").filter(has_text=nombre_archivo).first
            if not fv.is_visible():
                 fv = page.locator("div[role='row']").filter(has_text=re.compile(re.escape(nombre_archivo[:10]), re.IGNORECASE)).first
            
            try: fv.scroll_into_view_if_needed()
            except: pass
            
            fv.click(button="right")
            time.sleep(0.5)
            
            with page.expect_download(timeout=60000) as download_info:
                if page.get_by_role("menuitem", name="Descargar").is_visible():
                    page.get_by_role("menuitem", name="Descargar").click()
                elif page.get_by_role("menuitem", name="Download").is_visible():
                    page.get_by_role("menuitem", name="Download").click()
                elif page.locator("button[name='Descargar']").is_visible():
                    page.locator("button[name='Descargar']").click()
                else:
                    page.locator("button[name='Download']").click()
            
            download = download_info.value
            temp_path = download.path()
            peso_mb = os.path.getsize(temp_path) / (1024 * 1024)
            
            if peso_mb > MAX_MB_PERMITIDO:
                print(f"{indent}      🛑 SALTEADO: Pesa {peso_mb:.2f} MB (Máx: {MAX_MB_PERMITIDO} MB)")
                registrar_error(nombre_archivo, p_abs_final, f"Excede peso max ({peso_mb:.2f} MB)")
                archivos_todos_ok = False  # Archivo omitido → carpeta no se marcará completa
            else:
                intentos = 0
                while intentos < 3:
                    try:
                        download.save_as(ruta_seg_final)
                        break
                    except Exception as err:
                        intentos += 1
                        time.sleep(2)
                        if intentos == 3: raise err
                print(f"{indent}      ✅ Guardado ({peso_mb:.2f} MB)")

        except Exception as e:
            print(f"{indent}      ❌ ERROR Bajar: {e}")
            registrar_error(nombre_archivo, p_abs_final, str(e))
            try: page.keyboard.press("Escape")
            except: pass
            return False  # Error de descarga → no marcar como completada

    # 2. Procesar Subcarpetas
    subcarpetas_todas_ok = True
    for folder_info in items_carpeta:
        nombre_folder = folder_info["nombre"]
        rel_path_sub = os.path.join(ruta_relativa_actual, nombre_folder) if ruta_relativa_actual else nombre_folder

        # Omitir SOLO si está registrada en carpetas_completadas.txt
        if rel_path_sub in completadas:
            print(f"{indent}   ⏭️ OMITIENDO CARPETA (Ya procesada antes): {nombre_folder}")
            continue

        print(f"{indent}   👉 Acción: Entrando a {nombre_folder}")
        url_antes = page.url
        try:
            # Buscamos la fila exactamente como la catalogamos usando nuestra misma lógica de parser
            filas_candidatas = page.locator("div[role='row']").all()
            fila_viva = None
            for f in filas_candidatas[1:]: # Omitir header
                try:
                    nom_f, _, _ = analizar_fila(f)
                    if nom_f == nombre_folder:
                        fila_viva = f
                        break
                except: pass
            
            if not fila_viva:
                raise Exception(f"No se encontró la fila en el DOM exacto para: {nombre_folder}")
                
            try: fila_viva.scroll_into_view_if_needed()
            except: pass
            
            # Make sure we are clicking on the title itself, using the name FieldRenderer or similar
            link = fila_viva.locator("button[data-automationid='FieldRenderer-name'], a[data-automationid='FieldRenderer-name']").first
            if link.is_visible(): 
                link.click()
            else: 
                # Alternative locators
                alt_link = fila_viva.locator("a.ms-Link, button.ms-Link").first
                if alt_link.is_visible():
                    alt_link.click()
                else:
                    fila_viva.dblclick()
            
            # Wait for navigation
            time.sleep(3)
            
            if page.url == url_antes:
                print(f"{indent}   ⚠️ Aviso: Intentando doble clic de emergencia en la fila...")
                fila_viva.dblclick()
                time.sleep(3)
                if page.url == url_antes:
                    print(f"{indent}   ❌ BUCLE EVITADO: No pude entrar o navegar a la carpeta '{nombre_folder}'. Se omite para evitar infinitos.")
                    subcarpetas_todas_ok = False
                    continue
                    
            cerrar_popups(page)
            
            # Llamada recursiva
            sub_ok = procesar_carpeta(page, rel_path_sub, completadas)
            if not sub_ok:
                subcarpetas_todas_ok = False
            
            print(f"{indent}   🔙 Regresando a {ruta_relativa_actual or 'RAIZ'}...")
            page.go_back()
            time.sleep(2)
            page.wait_for_selector("div[role='row']", timeout=15000)
            cerrar_popups(page)
            time.sleep(1) 

        except Exception as e:
            print(f"{indent}   ❌ Error navegando a {nombre_folder}: {e}")
            subcarpetas_todas_ok = False
            try:
                page.go_back()
                time.sleep(2)
            except: pass

    if archivos_todos_ok and subcarpetas_todas_ok:
        marcar_completada(ruta_relativa_actual)
        completadas.add(ruta_relativa_actual)
        print(f"{indent}   ✅ CARPETA MARCADA COMO COMPLETA: '{ruta_relativa_actual or 'RAIZ'}'")
        return True
    
    return False


def run():
    global MAX_MB_PERMITIDO
    
    print("\n--- CONFIGURACIÓN ---")
    try:
        entrada = input("¿Cuál es el peso MÁXIMO por archivo en MB? (Ej: 50): ")
        MAX_MB_PERMITIDO = float(entrada)
    except:
        MAX_MB_PERMITIDO = 50.0
        print("⚠️ Entrada inválida. Usando 50 MB por defecto.")
    print(f"🎯 Límite: {MAX_MB_PERMITIDO} MB")

    inicializar_logs()
    generar_mapa_drive()
    
    completadas = cargar_completadas()
    print(f"📝 Se detectaron {len(completadas)} carpetas completadas de ejecuciones anteriores.")

    intentos_globales = 0
    while intentos_globales < 3:
        try:
            with sync_playwright() as p:
                if not os.path.exists(ARCHIVO_AUTH):
                    login_manual(p)

                print("\n🚀 INICIANDO BOT DE SINCRONIZACIÓN ITERATIVO...")
                browser = p.chromium.launch(headless=False, slow_mo=500)
                context = browser.new_context(storage_state=ARCHIVO_AUTH, accept_downloads=True)
                page = context.new_page()
                
                page.goto(SHAREPOINT_URL, timeout=60000)
                
                try: page.wait_for_selector("div[role='row']", timeout=20000)
                except:
                    print("🛑 Sesión caducada o fallo al iniciar. Reiniciando...")
                    try: os.remove(ARCHIVO_AUTH) 
                    except: pass
                    browser.close()
                    continue

                # Verificar si la RAIZ ya fue marcada como completada en ejecución anterior
                if "__RAIZ_COMPLETA__" in completadas:
                    print("\n🎉 ¡EXCELENTE! La RAIZ ya fue marcada como 100% completa en una ejección anterior.")
                    browser.close()
                    break

                exito = procesar_carpeta(page, "", completadas)
                
                if exito:
                    print("\n🏁 PROCESO DE SINCRONIZACIÓN FINALIZADO COMPLETAMENTE.")
                    browser.close()
                    break
                else:
                    raise Exception("La ejecución no finalizó en un estado 100% perfecto. Reiniciando para retomar...")

        except Exception as e:
            intentos_globales += 1
            print(f"\n🔥 CRASH / REINICIO: {e}")
            print(f"🔄 Retomando desde donde quedó en 5 segundos... (Intento {intentos_globales}/3)")
            time.sleep(5)
            # Recargar las completadas porque pudo marcar nuevas en este intento
            completadas = cargar_completadas()
            
    if intentos_globales >= 3:
        print("❌ Se superó el límite de intentos de ejecución global. Revisa el log de errores.")

if __name__ == "__main__":
    run()
