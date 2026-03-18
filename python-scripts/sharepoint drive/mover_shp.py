import time
import os
from playwright.sync_api import sync_playwright

# --- CONFIGURACIÓN ---
# Usamos r"" para que Python entienda las barras invertidas de Windows sin problemas
RUTA_DESTINO = r"G:\Unidades compartidas\TD BACKOFFICE\sharepoint finanzas"
ARCHIVO_AUTH = "auth_sharepoint.json"

SHAREPOINT_URL = "https://naturabr.sharepoint.com/:f:/r/teams/Macros/Documentos%20Compartilhados/02.%20DICCIONARIOS?csf=1&web=1&e=haEQfy"

def realizar_login_inicial(p):
    """Función auxiliar para loguearse si no existe el archivo"""
    print("\n⚠️  NO SE DETECTÓ SESIÓN GUARDADA.")
    print("   Abriendo navegador para inicio de sesión manual...")
    
    browser = p.chromium.launch(headless=False) # Sin slow_mo para el login humano
    context = browser.new_context()
    page = context.new_page()
    
    page.goto(SHAREPOINT_URL)
    
    print("\n" + "="*50)
    print("🔓 ACCIÓN REQUERIDA:")
    print("1. Por favor, inicia sesión en Microsoft en la ventana abierta.")
    print("2. Aprueba el acceso en tu celular si es necesario.")
    print("3. Marca 'Sí' en '¿Mantener sesión iniciada?'.")
    print("4. Espera a ver la lista de archivos de SharePoint.")
    input("👉 Cuando ya veas los archivos, presiona ENTER aquí para guardar y continuar...")
    print("="*50 + "\n")
    
    # Guardamos la sesión
    context.storage_state(path=ARCHIVO_AUTH)
    print("✅ Credenciales guardadas en 'auth_sharepoint.json'.")
    browser.close()

def run():
    # Asegurarnos que la carpeta destino existe (por si acaso la unidad G no está montada)
    if not os.path.exists(RUTA_DESTINO):
        print(f"❌ ERROR CRÍTICO: No encuentro la ruta: {RUTA_DESTINO}")
        print("   Asegúrate de que Google Drive de escritorio esté abierto.")
        return

    with sync_playwright() as p:
        # 1. VERIFICAR SI NECESITAMOS LOGIN
        if not os.path.exists(ARCHIVO_AUTH):
            realizar_login_inicial(p)
        
        # 2. INICIAR ROBOT DE DESCARGA
        print(f"🚀 INICIANDO ROBOT (Destino: {RUTA_DESTINO})...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        
        # Cargamos la sesión guardada
        context = browser.new_context(storage_state=ARCHIVO_AUTH, accept_downloads=True)
        page = context.new_page()
        
        print("🔵 Entrando a SharePoint...")
        try:
            page.goto(SHAREPOINT_URL, timeout=60000)
        except:
            print("⚠️ SharePoint tardó en cargar, pero continuamos.")

        # 3. BUCLE DE TRABAJO
        for i in range(1, 100): 
            try:
                page.bring_to_front()
                
                # Obtener filas
                filas = page.get_by_role("row").all()
                if i >= len(filas):
                    print("🏁 Fin de la lista visible.")
                    break
                
                fila_actual = filas[i]
                if not fila_actual.is_visible():
                    fila_actual.scroll_into_view_if_needed()

                # --- ANÁLISIS ---
                texto_fila = fila_actual.inner_text().lower()
                nombre_archivo = texto_fila.split('\n')[0]
                
                # Detectar carpeta vs archivo
                es_carpeta = "elemento" in texto_fila
                tiene_ext = ".xlsx" in nombre_archivo or ".pdf" in nombre_archivo or ".csv" in nombre_archivo

                print(f"\n🔎 #{i}: {nombre_archivo}")

                if es_carpeta and not tiene_ext:
                    print("   ⏭️  Es carpeta. Saltando...")
                    continue

                # --- DESCARGA ---
                print("   ⬇️  Descargando...")
                fila_actual.click(button="right")
                
                with page.expect_download(timeout=60000) as download_info:
                    try:
                        # Buscamos botón descargar
                        if page.get_by_role("menuitem", name="Descargar").is_visible():
                            page.get_by_role("menuitem", name="Descargar").click()
                        elif page.get_by_role("menuitem", name="Download").is_visible():
                            page.get_by_role("menuitem", name="Download").click()
                        else:
                            page.locator("button[name='Descargar']").click()
                    except:
                        print("   ⚠️ No pude dar clic en Descargar. Saltando.")
                        page.locator("body").click()
                        continue

                download = download_info.value
                nombre_real = download.suggested_filename
                
                # --- GUARDADO DIRECTO EN G: ---
                # Esta es la magia: Guardamos directo en la carpeta de Google Drive
                ruta_final = os.path.join(RUTA_DESTINO, nombre_real)
                
                # Validación ZIP (Por si SharePoint agrupa algo)
                if nombre_real.endswith(".zip") and not nombre_real.endswith(".xlsx"):
                     print(f"   🛑 Es un ZIP. Ignorando.")
                     continue
                
                print(f"   💾 Guardando en G: ...")
                download.save_as(ruta_final)
                
                print(f"   ✅ ¡Listo! ({nombre_real})")
                
                # No necesitamos esperar a Google ni borrar nada.
                # Windows y Drive Desktop se encargan del resto.

            except Exception as e:
                print(f"   ❌ Error en fila {i}: {e}")
                # Recuperar foco
                if not page.is_closed():
                    page.locator("body").click()
                continue

        print("\n🏁 PROCESO TERMINADO.")
        input("Presiona ENTER para cerrar...")
        browser.close()

if __name__ == "__main__":
    run()