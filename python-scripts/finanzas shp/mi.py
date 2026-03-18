import time
import os
from playwright.sync_api import sync_playwright

# --- CONFIGURACIÓN ---
SHAREPOINT_URL = "https://naturabr.sharepoint.com/teams/Macros/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fteams%2FMacros%2FDocumentos%20Compartilhados%2F02%2E%20DICCIONARIOS&viewid=14ddb0f3%2De090%2D4042%2Db88c%2Dd02eb956fa2f"
DRIVE_URL = "https://drive.google.com/drive/folders/1Cf8c1SDr1ZhPy-TAsI11Qx4yR-5NLRso"

def run():
    # Validación básica de credenciales
    if not os.path.exists("auth_completo.json"):
        print("❌ ERROR: Falta 'auth_completo.json'.")
        return

    with sync_playwright() as p:
        print("🚀 INICIANDO ROBOT V8 (Estrategia Botón Nuevo + Espera de Carga)...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(storage_state="auth_completo.json", accept_downloads=True)
        
        # --- 1. CARGA DE PESTAÑAS ---
        print("🔵 Cargando SharePoint...")
        page_sp = context.new_page()
        try:
            page_sp.goto(SHAREPOINT_URL, timeout=60000)
        except:
            print("⚠️ SharePoint lento, pero continuamos.")
        
        print("🟢 Cargando Drive...")
        page_drive = context.new_page()
        page_drive.goto(DRIVE_URL)
        
        # --- 2. BUCLE DE MIGRACIÓN ---
        for i in range(1, 100): 
            try:
                # Volvemos a SharePoint para leer la lista
                page_sp.bring_to_front()
                
                filas = page_sp.get_by_role("row").all()
                if i >= len(filas):
                    print("🏁 Fin de la lista.")
                    break
                
                fila_actual = filas[i]
                if not fila_actual.is_visible():
                    fila_actual.scroll_into_view_if_needed()

                # --- ANÁLISIS ---
                texto_fila = fila_actual.inner_text().lower()
                nombre_archivo = texto_fila.split('\n')[0]
                
                # Detectamos si es carpeta
                es_carpeta = "elemento" in texto_fila
                tiene_ext = ".xlsx" in nombre_archivo or ".pdf" in nombre_archivo or ".csv" in nombre_archivo

                print(f"\n🔎 #{i}: {nombre_archivo}")

                if es_carpeta and not tiene_ext:
                    print("   ⏭️  Es carpeta. Saltando...")
                    continue

                # --- DESCARGA ---
                print("   ⬇️  Descargando de SharePoint...")
                fila_actual.click(button="right")
                
                with page_sp.expect_download(timeout=60000) as download_info: # Damos 60s por si es pesado
                    try:
                        # Buscamos botón descargar
                        if page_sp.get_by_role("menuitem", name="Descargar").is_visible():
                            page_sp.get_by_role("menuitem", name="Descargar").click()
                        elif page_sp.get_by_role("menuitem", name="Download").is_visible():
                            page_sp.get_by_role("menuitem", name="Download").click()
                        else:
                            page_sp.locator("button[name='Descargar']").click()
                    except:
                        print("   ⚠️ No pude dar clic en Descargar. Saltando.")
                        page_sp.locator("body").click()
                        continue

                download = download_info.value
                nombre_real = download.suggested_filename
                
                # Guardamos copia local segura
                ruta_segura = os.path.join(os.getcwd(), "temp_" + nombre_real)
                download.save_as(ruta_segura)
                
                # CÁLCULO DE PESO: Medimos el archivo para saber cuánto esperar luego
                tamano_mb = os.path.getsize(ruta_segura) / (1024 * 1024)
                print(f"   💾 Archivo guardado ({tamano_mb:.2f} MB).")

                # Validación Anti-ZIP
                if nombre_real.endswith(".zip") and not nombre_real.endswith(".xlsx"):
                     print(f"   🛑 Es un ZIP. Borrando y saltando.")
                     if os.path.exists(ruta_segura): os.remove(ruta_segura)
                     continue

                # --- SUBIDA A DRIVE (ESTRATEGIA NUEVA: BOTÓN "+ NUEVO") ---
                page_drive.bring_to_front()
                print("   📤 Subiendo a Drive...")

                # Usamos expect_file_chooser para interceptar la ventana de selección
                with page_drive.expect_file_chooser() as fc_info:
                    
                    # PASO CLAVE: En vez de clic derecho en el fondo, clic en botón "+ Nuevo"
                    # Esto evita hacer clic sobre otros archivos
                    try:
                        # Intentamos buscar el botón por nombre
                        if page_drive.get_by_role("button", name="Nuevo").is_visible():
                             page_drive.get_by_role("button", name="Nuevo").click()
                        elif page_drive.get_by_role("button", name="New").is_visible():
                             page_drive.get_by_role("button", name="New").click()
                        else:
                             # Selector de respaldo (clase CSS común del botón nuevo)
                             page_drive.locator(".e-f-y").first.click()
                    except:
                        print("   ⚠️ No encontré el botón 'Nuevo'. Intentando clic derecho emergencia...")
                        page_drive.locator("div[role='main']").click(button="right")

                    # Ahora clic en "Subir archivo" del menú desplegable
                    time.sleep(1) # Pequeña pausa para que el menú se despliegue
                    try:
                        if page_drive.get_by_role("menuitem", name="Subir archivo").is_visible():
                            page_drive.get_by_role("menuitem", name="Subir archivo").click()
                        else:
                            page_drive.get_by_role("menuitem", name="File upload").click()
                    except:
                         print("   ❌ No pude dar clic en 'Subir archivo'.")
                         # Si falla aquí, no borramos el archivo para que no lo pierdas
                         continue

                # Entregamos el archivo al navegador
                file_chooser = fc_info.value
                file_chooser.set_files(ruta_segura)

                # --- ESPERA INTELIGENTE (Dependiendo del peso) ---
                print("   ⏳ Esperando transferencia...")
                
                # 1. Esperamos que aparezca la alerta de "Subiendo"
                try:
                    page_drive.wait_for_selector("div[role='alert']", timeout=10000)
                except:
                    pass # Si no aparece, seguimos con la espera por tiempo

                # 2. Calculamos tiempo de espera según peso
                # Fórmula: 5 segundos base + 2 segundos por cada MB
                tiempo_espera = 5 + (tamano_mb * 2)
                
                # Tope máximo de 60 segundos para no bloquearse eternamente
                if tiempo_espera > 60: tiempo_espera = 60
                
                print(f"   ⏱️  Esperando {int(tiempo_espera)} segundos por seguridad (Archivo de {tamano_mb:.2f} MB)...")
                time.sleep(tiempo_espera)

                # --- AUTO-BORRADO ---
                print("   🧹 Limpiando disco local...")
                try:
                    if os.path.exists(ruta_segura):
                        os.remove(ruta_segura)
                        print("   ✨ Archivo eliminado.")
                except Exception as e:
                    print(f"   ⚠️ No pude borrar: {e}")

                # Vuelta a SharePoint
                page_sp.bring_to_front()
                
            except Exception as e:
                print(f"   ❌ Error crítico en fila {i}: {e}")
                if not page_sp.is_closed():
                    page_sp.bring_to_front()
                    page_sp.locator("body").click()
                continue

        print("\n🏁 MIGRACIÓN COMPLETADA.")
        input("Presiona ENTER para cerrar...")
        browser.close()

if __name__ == "__main__":
    run()