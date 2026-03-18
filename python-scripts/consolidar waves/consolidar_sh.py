import pandas as pd
import os
import glob
import math
import shutil
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
# Ruta 
ruta_carpeta = r"C:\Users\331642\Desktop\harrys\interfaz\procesar shpcfrm pendientes"

# Prefijo y etiqueta actualizados
prefijo_archivo = "SHP" 
etiqueta_busqueda = "E1BPOBDLVHDRCON"

# Nombre base para el archivo Excel de salida
nombre_salida_base = "Consolidado_SHP"

def extraer_fecha(nombre_archivo):
    """
    Extrae fecha del nombre. 
    Ejemplo: SHP_OBDLV_CONFIRM_DECENTRAL_20260109033134...
    La fecha está en la posición 4 (separada por _)
    """
    try:
        partes = nombre_archivo.split('_')
        # En SHP_OBDLV_CONFIRM_DECENTRAL_20260109033134, la fecha es el índice 4
        fecha_raw = partes[4] 
        
        dt_obj = datetime.strptime(fecha_raw, "%Y%m%d%H%M%S")
        # Ajuste de 2 horas (según lógica original)
        dt_nueva = dt_obj - timedelta(hours=2)
        return dt_nueva.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return "Error Fecha"

def obtener_siguiente_correlativo(ruta, nombre_base):
    """Busca archivos existentes y devuelve el siguiente número disponible."""
    patron = os.path.join(ruta, f"{nombre_base}_*.xlsx")
    archivos_existentes = glob.glob(patron)
    
    max_num = 0
    for ruta_archivo in archivos_existentes:
        try:
            nombre = os.path.basename(ruta_archivo)
            nombre_sin_ext = os.path.splitext(nombre)[0]
            partes = nombre_sin_ext.split('_')
            num = int(partes[-1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            continue
            
    return max_num + 1

def procesar_shp():
    print(f"--- Iniciando proceso SHP para archivos '{prefijo_archivo}*.txt' ---")
    
    patron = os.path.join(ruta_carpeta, f"{prefijo_archivo}*.txt")
    archivos = glob.glob(patron)
    
    if not archivos:
        print(f"No se encontraron archivos que empiecen con '{prefijo_archivo}' en: {ruta_carpeta}")
        return

    lista_datos = []
    archivos_leidos_correctamente = [] 

    print(f"Se encontraron {len(archivos)} archivos. Filtrando contenido...")

    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        fecha_formateada = extraer_fecha(nombre_archivo)
        
        try:
            with open(archivo, 'r', encoding='latin-1') as f:
                for linea in f:
                    if linea.startswith(etiqueta_busqueda):
                        # Ejemplo linea: E1BPOBDLVHDRCON;26032810;
                        partes = linea.split(';')
                        
                        # El pedido es el segundo elemento (índice 1)
                        if len(partes) > 1:
                            pedido = partes[1]
                            
                            lista_datos.append({
                                'pedido': pedido,
                                'archivo': nombre_archivo,
                                'fecha procesada': fecha_formateada
                            })
            
            archivos_leidos_correctamente.append(archivo)
            
        except Exception as e:
            print(f"[ERROR] Fallo al leer {nombre_archivo}: {e}")

    # --- GENERACIÓN DE EXCEL ---
    if lista_datos:
        df_consolidado = pd.DataFrame(lista_datos)
        df_consolidado = df_consolidado[['pedido', 'archivo', 'fecha procesada']]
        
        total_filas = len(df_consolidado)
        print(f"Datos filtrados. Total pedidos encontrados: {total_filas}")
        
        limite_excel = 1000000
        num_archivos_necesarios = math.ceil(total_filas / limite_excel)
        indice_inicio = obtener_siguiente_correlativo(ruta_carpeta, nombre_salida_base)
        
        try:
            for i in range(num_archivos_necesarios):
                inicio = i * limite_excel
                fin = inicio + limite_excel
                df_subset = df_consolidado.iloc[inicio:fin]
                
                numero_actual = indice_inicio + i
                nombre_salida = f"{nombre_salida_base}_{numero_actual}.xlsx"
                ruta_salida = os.path.join(ruta_carpeta, nombre_salida)
                
                print(f"Guardando Excel: {nombre_salida} ...")
                df_subset.to_excel(ruta_salida, index=False)
            
            # --- MOVER ARCHIVOS TXT ---
            ruta_procesados = os.path.join(ruta_carpeta, "Procesados SHP")
            if not os.path.exists(ruta_procesados):
                os.makedirs(ruta_procesados)
                
            for archivo_origen in archivos_leidos_correctamente:
                nombre = os.path.basename(archivo_origen)
                archivo_destino = os.path.join(ruta_procesados, nombre)
                
                if os.path.exists(archivo_destino):
                    os.remove(archivo_destino)
                shutil.move(archivo_origen, archivo_destino)
                
            print(f"¡Proceso terminado! Archivos movidos a: {ruta_procesados}")

        except Exception as e:
            print(f"[CRITICO] Error guardando Excel o moviendo archivos: {e}")
    else:
        print(f"No se encontraron líneas con la etiqueta {etiqueta_busqueda}")

if __name__ == "__main__":
    procesar_shp()