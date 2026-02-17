import pandas as pd
import os
import glob
import math
import shutil
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
ruta_carpeta = r"C:\Users\331642\Desktop\problema de fase\jeremy\06"
columnas_txt = ['fase', 'pedido', 'vacio', 'dato']
prefijo_archivo = "Wave" 

def extraer_fecha(nombre_archivo):
    """
    Extrae fecha, resta 2 horas. Formato DD-MM-AAAA hh:mm
    """
    try:
        partes = nombre_archivo.split('_')
        fecha_raw = partes[2] # Ajustar índice si el formato del nombre cambia
        dt_obj = datetime.strptime(fecha_raw, "%Y%m%d%H%M%S")
        dt_nueva = dt_obj - timedelta(hours=2)
        return dt_nueva.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return "Error Fecha"

def obtener_siguiente_correlativo(ruta, prefijo):
    """
    Busca archivos existentes tipo 'Consolidado_Wave_X.xlsx'
    Devuelve el siguiente número disponible para no sobrescribir.
    """
    patron = os.path.join(ruta, f"Consolidado_{prefijo}_*.xlsx")
    archivos_existentes = glob.glob(patron)
    
    max_num = 0
    for ruta_archivo in archivos_existentes:
        try:
            nombre = os.path.basename(ruta_archivo)
            # Quitamos extensión .xlsx y dividimos por '_'
            # Ejemplo: Consolidado_Wave_5.xlsx -> ['Consolidado', 'Wave', '5']
            nombre_sin_ext = os.path.splitext(nombre)[0]
            partes = nombre_sin_ext.split('_')
            
            # El número debería ser el último elemento
            num = int(partes[-1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            continue # Si hay un archivo con nombre raro, lo ignoramos
            
    return max_num + 1

def procesar_archivos():
    print(f"--- Iniciando proceso para prefijo: '{prefijo_archivo}' ---")
    
    patron = os.path.join(ruta_carpeta, f"{prefijo_archivo}*.txt")
    archivos = glob.glob(patron)
    
    if not archivos:
        print(f"No hay nuevos archivos '{prefijo_archivo}*.txt' para procesar.")
        return

    lista_dataframes = []
    archivos_leidos_correctamente = [] 

    print(f"Se encontraron {len(archivos)} archivos nuevos. Leyendo...")

    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        try:
            df_temp = pd.read_csv(
                archivo, 
                sep=';', 
                header=None, 
                usecols=[0, 1, 2, 3], 
                names=columnas_txt,
                dtype=str 
            )
            
            df_temp['fecha wave'] = extraer_fecha(nombre_archivo)
            df_temp['archivo'] = nombre_archivo
            
            lista_dataframes.append(df_temp)
            archivos_leidos_correctamente.append(archivo) 
            
        except Exception as e:
            print(f"[ERROR] Omitiendo {nombre_archivo}: {e}")

    if lista_dataframes:
        df_consolidado = pd.concat(lista_dataframes, ignore_index=True)
        df_consolidado = df_consolidado[['fase', 'pedido', 'vacio', 'dato', 'fecha wave', 'archivo']]

        total_filas = len(df_consolidado)
        print(f"Datos consolidados. Total filas: {total_filas}")
        
        # --- LÓGICA DE NUMERACIÓN ---
        limite_excel = 1000000
        num_archivos_necesarios = math.ceil(total_filas / limite_excel)
        
        # Buscamos desde qué número empezar
        indice_inicio = obtener_siguiente_correlativo(ruta_carpeta, prefijo_archivo)
        
        try:
            for i in range(num_archivos_necesarios):
                inicio_fila = i * limite_excel
                fin_fila = inicio_fila + limite_excel
                
                df_subset = df_consolidado.iloc[inicio_fila:fin_fila]
                
                # El número del archivo será el (indice encontrado + el iterador actual)
                numero_actual = indice_inicio + i
                
                nombre_salida = f"Consolidado_{prefijo_archivo}_{numero_actual}.xlsx"
                ruta_salida = os.path.join(ruta_carpeta, nombre_salida)
                
                print(f"Guardando : {nombre_salida} ...")
                df_subset.to_excel(ruta_salida, index=False)
            
            print("--- Archivos Excel generados exitosamente ---")
            
            # Mover TXTs a Procesados
            ruta_procesados = os.path.join(ruta_carpeta, "Procesados Wave")
            if not os.path.exists(ruta_procesados):
                os.makedirs(ruta_procesados)
                
            print(f"Moviendo {len(archivos_leidos_correctamente)} archivos a carpeta Procesados...")
            
            for archivo_origen in archivos_leidos_correctamente:
                nombre = os.path.basename(archivo_origen)
                archivo_destino = os.path.join(ruta_procesados, nombre)
                if os.path.exists(archivo_destino):
                    os.remove(archivo_destino)
                shutil.move(archivo_origen, archivo_destino)
                
            print("¡Todo listo!")

        except Exception as e:
            print(f"[CRITICO] Error al escribir disco: {e}")

    else:
        print("No se generaron datos válidos.")

if __name__ == "__main__":
    procesar_archivos()