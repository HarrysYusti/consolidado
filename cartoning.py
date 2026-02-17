import pandas as pd
import os
import glob
import math
import shutil
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
ruta_carpeta = r"C:\Users\331642\Desktop\harrys\interfaz\procesar cartoning pendientes"

# IMPORTANTE: Define aquí cómo empiezan los archivos que quieres leer.
# Si tus archivos de cartoning se llaman "Wave_Confirm...", deja "Wave".
# Si se llaman "Cartoning_...", cambia esto por "Cartoning".
prefijo_archivo = "CARTONING" 

# La etiqueta que vamos a buscar dentro del archivo
etiqueta_busqueda = "ZSIEWM_CARTONIZACAO_PEDIDO;"

# Nombre base para el archivo Excel de salida
nombre_salida_base = "Consolidado_Cartoning"

def extraer_fecha(nombre_archivo):
    """
    Extrae fecha del nombre (posición 2 separada por _), resta 2 horas.
    Formato salida: DD-MM-AAAA hh:mm
    """
    try:
        partes = nombre_archivo.split('_')
        # Ajusta este índice [2] si la fecha está en otra posición en el nombre
        fecha_raw = partes[2] 
        
        dt_obj = datetime.strptime(fecha_raw, "%Y%m%d%H%M%S")
        dt_nueva = dt_obj - timedelta(hours=2)
        return dt_nueva.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return "Error Fecha"

def obtener_siguiente_correlativo(ruta, nombre_base):
    """
    Busca archivos existentes tipo 'Consolidado_Cartoning_X.xlsx'
    y devuelve el siguiente número disponible (X+1).
    """
    patron = os.path.join(ruta, f"{nombre_base}_*.xlsx")
    archivos_existentes = glob.glob(patron)
    
    max_num = 0
    for ruta_archivo in archivos_existentes:
        try:
            nombre = os.path.basename(ruta_archivo)
            nombre_sin_ext = os.path.splitext(nombre)[0]
            partes = nombre_sin_ext.split('_')
            # Se asume que el número es la última parte del nombre
            num = int(partes[-1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            continue
            
    return max_num + 1

def procesar_cartoning():
    print(f"--- Iniciando proceso Cartoning para archivos '{prefijo_archivo}*.txt' ---")
    
    patron = os.path.join(ruta_carpeta, f"{prefijo_archivo}*.txt")
    archivos = glob.glob(patron)
    
    if not archivos:
        print(f"No se encontraron archivos que empiecen con '{prefijo_archivo}' en la ruta.")
        return

    lista_datos = []
    archivos_leidos_correctamente = [] 

    print(f"Se encontraron {len(archivos)} archivos. Filtrando contenido...")

    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        fecha_formateada = extraer_fecha(nombre_archivo)
        
        try:
            # Abrimos el archivo y leemos línea por línea
            # 'latin-1' ayuda a evitar errores si hay caracteres extraños
            with open(archivo, 'r', encoding='latin-1') as f:
                for linea in f:
                    if linea.startswith(etiqueta_busqueda):
                        # Ejemplo linea: ZSIEWM_CARTONIZACAO_PEDIDO;25661989;10393467;...
                        partes = linea.split(';')
                        
                        # El pedido es el segundo elemento (índice 1)
                        pedido = partes[1]
                        
                        # Guardamos en un diccionario
                        lista_datos.append({
                            'pedido': pedido,
                            'archivo': nombre_archivo,
                            'fecha wave': fecha_formateada
                        })
            
            # Si terminó de leer sin error, lo marcamos para mover
            archivos_leidos_correctamente.append(archivo)
            
        except Exception as e:
            print(f"[ERROR] Fallo al leer {nombre_archivo}: {e}")

    # --- GENERACIÓN DE EXCEL ---
    if lista_datos:
        df_consolidado = pd.DataFrame(lista_datos)
        
        # Aseguramos el orden de las columnas
        df_consolidado = df_consolidado[['pedido', 'archivo', 'fecha wave']]
        
        total_filas = len(df_consolidado)
        print(f"Datos filtrados listos. Total pedidos: {total_filas}")
        
        limite_excel = 1000000
        num_archivos_necesarios = math.ceil(total_filas / limite_excel)
        
        # Obtenemos el número correlativo para el nombre del archivo
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
            
            print("--- Archivos Excel guardados correctamente ---")
            
            # --- MOVER ARCHIVOS TXT ---
            ruta_procesados = os.path.join(ruta_carpeta, "Procesados Cartoning")
            if not os.path.exists(ruta_procesados):
                os.makedirs(ruta_procesados)
                
            print(f"Moviendo {len(archivos_leidos_correctamente)} archivos a 'Procesados'...")
            
            for archivo_origen in archivos_leidos_correctamente:
                nombre = os.path.basename(archivo_origen)
                archivo_destino = os.path.join(ruta_procesados, nombre)
                
                if os.path.exists(archivo_destino):
                    os.remove(archivo_destino)
                shutil.move(archivo_origen, archivo_destino)
                
            print("¡Proceso terminado con éxito!")

        except Exception as e:
            print(f"[CRITICO] Error guardando Excel o moviendo archivos: {e}")

    else:
        print("No se encontraron líneas de pedido (ZSIEWM_CARTONIZACAO_PEDIDO) en los archivos.")

if __name__ == "__main__":
    procesar_cartoning()