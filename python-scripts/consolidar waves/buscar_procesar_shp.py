"""
PROCESO: RESCATE Y REPORTE DE ARCHIVOS CON ACTUALIZACIÓN EN EXCEL
=====================================================================

1. CONFIGURACIÓN INICIAL
    - Define rutas base, nombre del archivo Excel y columnas de referencia
    - Especifica carpetas origen donde buscar los archivos

2. LECTURA DEL EXCEL
    - Abre el archivo Excel especificado (hoja "Buscar")
    - Lee la columna "archivo" que contiene los nombres a buscar
    - Crea columna "Estado" si no existe

3. CREACIÓN DE CARPETA DESTINO
    - Genera carpeta con timestamp: "Reprocesar (DD-MM-YY HH.MM)"
    - Donde se copiarán los archivos encontrados

4. BÚSQUEDA Y PROCESAMIENTO
    - Para cada archivo en Excel:
      a) Extrae primeros 46 caracteres como clave de búsqueda
      b) Busca coincidencia en carpetas origen (búsqueda case-insensitive)
      c) Si encuentra: copia archivo a destino con prefijo "_ref_" en nombre
      d) Si NO encuentra: registra como no encontrado

5. ACTUALIZACIÓN DE ESTADO
    - Marca cada fila como "ENCONTRADO" o "NO ENCONTRADO"
    - Guarda Excel original con cambios

6. REPORTE FINAL
    - Imprime resumen: cantidad de encontrados y no encontrados
    - Confirma actualización del Excel
"""

import pandas as pd
import os
import shutil
from datetime import datetime

# --- CONFIGURACIÓN ---
ruta_base = r"C:\Users\331642\Desktop\harrys\interfaz"
nombre_excel = "analisis.xlsx"
hoja_excel = "Buscar"
columna_excel = "archivo"

# Nombre de la columna que se creará/usará para marcar si se encontró
columna_estado = "Estado" 

carpetas_origen = ["procesar shpcfrm pendientes"]

def generar_nombre_con_ref(nombre_archivo):
    """
    Inserta '_ref_' después del tercer guion bajo.
    """
    partes = nombre_archivo.split('_')
    if len(partes) >= 4:
        prefijo = "_".join(partes[:3]) 
        sufijo = "_".join(partes[3:])
        return f"{prefijo}_ref_{sufijo}"
    else:
        return f"ref_{nombre_archivo}"

def rescatar_archivos():
    print("--- Iniciando rescate con reporte en Excel ---")

    ruta_excel = os.path.join(ruta_base, nombre_excel)
    fecha_actual = datetime.now().strftime("%d-%m-%y %H.%M") 
    nombre_carpeta_destino = f"Reprocesar ({fecha_actual})"
    ruta_destino = os.path.join(ruta_base, nombre_carpeta_destino)

    if not os.path.exists(ruta_excel):
        print(f"[ERROR] No se encuentra el archivo Excel: {ruta_excel}")
        return

    try:
        print(f"Leyendo Excel...")
        # Leemos el Excel
        df = pd.read_excel(ruta_excel, sheet_name=hoja_excel)
        
        if columna_excel not in df.columns:
            print(f"[ERROR] Columna '{columna_excel}' no encontrada.")
            return

        # Inicializamos la columna de estado si no existe
        if columna_estado not in df.columns:
            df[columna_estado] = ""

        if not os.path.exists(ruta_destino):
            os.makedirs(ruta_destino)

        encontrados = 0
        no_encontrados = 0

        # Iteramos usando iterrows para poder modificar el DataFrame por índice
        for index, row in df.iterrows():
            archivo_buscado = str(row[columna_excel]).strip()
            
            # Si la celda está vacía o es nan, saltamos
            if not archivo_buscado or archivo_buscado.lower() == 'nan':
                continue

            # Tomamos los primeros 46 caracteres para la búsqueda
            clave_busqueda = archivo_buscado[:46]
            fue_encontrado = False

            for carpeta in carpetas_origen:
                ruta_carpeta_origen = os.path.join(ruta_base, carpeta)
                
                if not os.path.exists(ruta_carpeta_origen):
                    continue

                # Listamos archivos reales
                try:
                    archivos_en_disco = os.listdir(ruta_carpeta_origen)
                except OSError:
                    continue

                for archivo_real in archivos_en_disco:
                    # Comparación de los primeros 46 caracteres
                    if archivo_real[:46].lower() == clave_busqueda.lower():
                        
                        ruta_origen_completa = os.path.join(ruta_carpeta_origen, archivo_real)
                        nuevo_nombre = generar_nombre_con_ref(archivo_real)
                        ruta_final = os.path.join(ruta_destino, nuevo_nombre)
                        
                        shutil.copy2(ruta_origen_completa, ruta_final)
                        
                        print(f"[OK] Encontrado: {archivo_real}")
                        
                        fue_encontrado = True
                        encontrados += 1
                        break 
                
                if fue_encontrado:
                    break 

            # --- ACTUALIZAMOS EL EXCEL EN MEMORIA ---
            if fue_encontrado:
                df.at[index, columna_estado] = "ENCONTRADO"
            else:
                print(f"[X] No encontrado: {archivo_buscado}")
                df.at[index, columna_estado] = "NO ENCONTRADO"
                no_encontrados += 1

        print("-" * 30)
        print("Guardando cambios en el Excel...")
        
        # Guardamos el Excel sobreescribiendo el original
        # index=False evita que se guarde el número de fila (0, 1, 2...) como una columna extra
        df.to_excel(ruta_excel, sheet_name=hoja_excel, index=False)
        
        print(f"Resumen:")
        print(f"Archivos encontrados: {encontrados}")
        print(f"Archivos no encontrados: {no_encontrados}")
        print(f"Excel actualizado: {ruta_excel}")

    except PermissionError:
        print("[ERROR CRÍTICO] El archivo Excel está ABIERTO. Ciérrelo e intente de nuevo.")
    except Exception as e:
        print(f"[CRÍTICO] Error: {e}")


if __name__ == "__main__": 
    rescatar_archivos()