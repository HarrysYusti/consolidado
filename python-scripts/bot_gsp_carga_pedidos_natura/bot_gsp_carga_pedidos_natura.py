# -*- coding: utf-8 -*-

import os
import asyncio
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Union, Iterable, List, Tuple, Dict
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError
import nest_asyncio
import pandas as pd

# Importamos toda nuestra configuración desde el archivo config.py
import config

# --- LÓGICA DE BÚSQUEDA DE ARCHIVOS ---
def _iter_xlsx(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.xlsx"):
        if p.is_file() and not p.name.startswith("~$") and "pedidos_leidos" not in str(p.parent).lower():
            yield p

def _parse_name(filename: str) -> Tuple[str, str]:
    m = config.FILENAME_REGEX.search(filename)
    return (m.group("id"), m.group("date")) if m else ("", "")

def find_pedido_files_with_id(root: Union[Path, str], filtra_fecha: bool) -> List[Tuple[Path, str]]:
    root_path = Path(root)
    if not root_path.exists(): return []
    
    target_date = config.CODIGO_FECHA_ESPECIFICO if filtra_fecha else None
    
    results: List[Tuple[Path, str]] = []
    for file_path in _iter_xlsx(root_path):
        cid, datecode = _parse_name(file_path.name)
        if not cid: continue
        if filtra_fecha and datecode != target_date: continue
        results.append((file_path, cid))
    return results

# --- FUNCIÓN DE PROCESO "MONOLÍTICA" (SIN CAMBIOS) ---
async def process_single_order_session(playwright, order_file_path: Path, consultant_id: str) -> Dict[str, str]:
    status = "Error"
    error_message = ""
    browser = await playwright.chromium.launch(channel="msedge", headless=False, args=["--start-maximized"])
    context = await browser.new_context(accept_downloads=True, no_viewport=True)
    page = await context.new_page()
    print("Navegador Edge iniciado para nueva sesión.")
    
    try:
        print(f"Navegando a la página de login: {config.LOGIN_URL}")
        await page.goto(config.LOGIN_URL, timeout=90000)
        await page.fill("#username", config.USUARIO)
        await page.fill("#password", config.PASSWORD)
        await page.click('button:has-text("acceso")')
        await page.wait_for_load_state('networkidle', timeout=90000)
        print("Login exitoso.")
        
        try:
            await page.locator('label[for="id_1"]').click(timeout=7000)
            await page.get_by_role("button", name="Aceptar").first.click()
            print("Pop-up de 'Venta Directa' gestionado.")
        except PlaywrightTimeoutError:
            print("ℹ️  El pop-up de 'Venta Directa' no apareció.")

        await page.get_by_text("¿Para quién deseas hacer el pedido?").wait_for(state="visible", timeout=15000)
        await page.locator('label[for="id_2"]').click()
        await page.get_by_role("button", name="Aceptar").click()
        print("Opción 'Para otra Consultora' confirmada.")

        await page.wait_for_url("**/select-consultant", timeout=90000)
        await page.locator('input[placeholder="Digita el código de Consultoría"]').type(consultant_id, delay=100)
        await page.locator('button:has-text("Buscar")').click()
        print(f"Buscando consultora con código: {consultant_id}")

        await page.get_by_role("button", name="Confirmar").click(timeout=10000)
        print("Consultora confirmada.")
        
        max_attempts = 8
        for attempt in range(max_attempts):
            print(f"\nCiclo de decisión #{attempt + 1}: Observando la página...")
            await page.wait_for_timeout(2000)

            if "/cart" in page.url:
                print("✅ Objetivo alcanzado: Ya estamos en la página del carrito.")
                break

            try:
                ciclo_option = page.locator('label[for="id_0"]')
                await ciclo_option.wait_for(state="visible", timeout=2000)
                print("Pop-up de ciclo detectado. Gestionando...")
                await ciclo_option.click()
                await page.wait_for_timeout(1000)
                aceptar_vA = page.locator('button[data-dismiss="modal"]:has-text("Aceptar")')
                aceptar_vB = page.locator('[data-testid="cycle-accept-button"]')
                aceptar_button = aceptar_vA.or_(aceptar_vB)
                button_box = await aceptar_button.bounding_box()
                if button_box:
                    await page.mouse.move(button_box['x'] + button_box['width'] / 2, button_box['y'] + button_box['height'] / 2)
                    await page.mouse.down()
                    await page.mouse.up()
                    print("Ciclo confirmado con clic humano.")
                else: raise Exception("No se pudieron obtener coordenadas del botón 'Aceptar'")
                continue
            except PlaywrightTimeoutError:
                pass

            try:
                await page.locator('label[for="id_1"]').click(timeout=1000)
                print("Pop-up opcional de 'Venta Directa' detectado. Gestionando...")
                await page.get_by_role("button", name="Aceptar").first.click()
                continue
            except PlaywrightTimeoutError:
                pass
            
            try:
                await page.get_by_role("button", name="LISTO").click(timeout=1000)
                print("Pop-up '¡Aviso!' o 'LISTO' detectado y presionado.")
                continue
            except PlaywrightTimeoutError:
                pass
            
            try:
                await page.get_by_text("Este pedido esta guardado desde el día").wait_for(state="visible", timeout=1000)
                print("Pop-up 'Recuperar Pedido' detectado. Gestionando...")
                await page.get_by_role("button", name="Eliminar Pedido").click()
                print("Clic en 'Eliminar Pedido' realizado.")
                continue
            except PlaywrightTimeoutError:
                pass

            try:
                await page.get_by_role("button", name="Mi Carrito").first.click(timeout=1000)
                print("Página principal detectada. Haciendo clic en 'Mi Carrito'...")
                continue
            except PlaywrightTimeoutError:
                pass
            
            print("⚠️ No se reconoce un estado accionable. Forzando recarga...")
            await page.reload()
            await page.wait_for_load_state("networkidle")
            
        else:
            raise Exception(f"El bot no pudo llegar al carrito de compras después de {max_attempts} intentos.")
        
        print("Confirmado: en la página del carrito de compras.")
        
        await page.wait_for_timeout(3000)
        file_input = page.locator('input[type="file"]')
        await file_input.wait_for(state="visible", timeout=15000)
        await file_input.set_input_files(order_file_path)
        await page.wait_for_timeout(15000)
        print("✅ Archivo de pedido subido correctamente.")
        status = "Subido Correctamente"

        try:
            await page.get_by_text("No podemos encontrar los Códigos de productos").wait_for(state="visible", timeout=5000)
            message_element = page.locator("div.modal-body")
            error_message = (await message_element.inner_text()).replace("\n", " ")
            print(f"Pop-up de error encontrado. Mensaje: {error_message}")
            await page.get_by_role("button", name="LISTO").click()
        except PlaywrightTimeoutError:
            print("ℹ️  No hubo productos no encontrados.")
            error_message = "N/A"
        
        try:
            await page.get_by_text("hemos detectado inconsistencias").wait_for(state="visible", timeout=5000)
            print("Pop-up de 'inconsistencias' detectado. Haciendo clic en 'LISTO'.")
            await page.get_by_role("button", name="LISTO").click()
        except PlaywrightTimeoutError:
            print("ℹ️  No apareció el pop-up de inconsistencias.")
        
        source_dir = order_file_path.parent
        try:
            processed_folder_path = next(source_dir.glob('pedidos_leidos*'))
            print(f"Carpeta de destino encontrada: {processed_folder_path}")
        except StopIteration:
            print(f"ADVERTENCIA: No se encontró carpeta 'pedidos_leidos*'. Creando una nueva...")
            processed_folder_path = source_dir / "pedidos_leidos"
            processed_folder_path.mkdir(exist_ok=True)
            print(f"Carpeta creada: {processed_folder_path}")

        destination_path = processed_folder_path / order_file_path.name
        shutil.move(order_file_path, destination_path)
        print(f"✅ Archivo movido a: {destination_path}")
            
    except Exception as e:
        print(f"❌ Error fatal procesando el pedido: {e}")
        error_message = str(e)
    
    finally:
        print("Cerrando navegador.")
        await context.close()
        await browser.close()
        
    return {"CB": consultant_id, "Estado": status, "Mensaje de Error": error_message}


# --- FUNCIÓN main() ACTUALIZADA CON TRY...FINALLY ---
async def main():
    """Función que orquesta todo el proceso."""
    print("\n" + "="*50)
    print(f"Iniciando Bot de Carga de Pedidos a las {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    if config.FILTRA_FECHA:
        print(f"[INFO] Filtrado por código de fecha específico: {config.CODIGO_FECHA_ESPECIFICO}")

    pedidos_a_procesar = find_pedido_files_with_id(config.BASE_PEDIDOS_PATH, config.FILTRA_FECHA)
    
    if not pedidos_a_procesar:
        print("No hay pedidos pendientes para procesar. El proceso ha finalizado.")
        return

    print(f"Se encontraron {len(pedidos_a_procesar)} pedidos para procesar.")
    
    # 1. Mover 'results_log' fuera del bloque 'try'
    results_log = []
    
    try:
        # 2. El bloque 'try' ahora envuelve el procesamiento
        async with async_playwright() as playwright:
            for i, (order_file_path, consultant_id) in enumerate(pedidos_a_procesar, 1):
                if i > 1:
                    print(f"\n⏸️ Pausando por {config.PAUSA_ENTRE_PEDIDOS} segundos antes de la siguiente sesión...")
                    await asyncio.sleep(config.PAUSA_ENTRE_PEDIDOS)

                print("\n" + "-"*20 + f" PROCESANDO PEDIDO {i}/{len(pedidos_a_procesar)} " + "-"*20)
                print(f"Archivo: {order_file_path.name}")
                print(f"Consultora ID: {consultant_id}")
                
                start_time = datetime.now()
                print(f"Hora de inicio de sesión: {start_time.strftime('%H:%M:%S')}")
                result = await process_single_order_session(playwright, order_file_path, consultant_id)
                results_log.append(result) # Los resultados se añaden a la lista
                end_time = datetime.now()
                duration = end_time - start_time
                minutes, seconds = divmod(duration.total_seconds(), 60)
                print(f"Hora de fin de sesión: {end_time.strftime('%H:%M:%S')}")
                print(f"✓ Duración de la sesión: {int(minutes)} minutos y {seconds:.2f} segundos.")

    except KeyboardInterrupt: # Captura si presionas Ctrl+C
        print("\n\n🛑 Proceso interrumpido por el usuario. Guardando reporte parcial...")
    except Exception as e: # Captura cualquier otro crash inesperado
        print(f"\n\n❌ ERROR INESPERADO: {e}. Guardando reporte parcial...")
    
    finally:
        # 3. El bloque 'finally' se asegura de guardar el reporte SIEMPRE.
        if not results_log:
            print("No se procesó ningún pedido, no se generará reporte.")
        else:
            print(f"\nGenerando reporte de resultados ({len(results_log)} filas)...")
            try:
                df = pd.DataFrame(results_log)
                now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_filename = f"Reporte_Carga_Pedidos_{now_str}.xlsx"

                # Guardar en la primera ubicación
                ruta_principal = config.RUTA_REPORTE_PRINCIPAL / report_filename
                ruta_principal.parent.mkdir(parents=True, exist_ok=True)
                df.to_excel(ruta_principal, index=False, sheet_name="Pedidos")
                print(f"✅ Reporte principal guardado en: {ruta_principal}")

                # Guardar la copia en la segunda ubicación
                ruta_copia = config.RUTA_REPORTE_COPIA / report_filename
                ruta_copia.parent.mkdir(parents=True, exist_ok=True)
                df.to_excel(ruta_copia, index=False, sheet_name="Pedidos")
                print(f"✅ Copia del reporte guardada en: {ruta_copia}")

            except Exception as e:
                print(f"❌ No se pudo generar el reporte en Excel. Error: {e}")

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())