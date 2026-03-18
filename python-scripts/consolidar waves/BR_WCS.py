# ==============================================================================
# PROCESO DE RESCATE UNIFICADO DE ARCHIVOS (SHIPCONFIRM, WAVE, CARTONING)
# ==============================================================================
#
# 1. LECTURA DE DATOS:
#    El script lee el archivo "analisis.xlsx" (hoja "Buscar") ubicado en:
#    -> C:\Users\331642\Desktop\harrys\interfaz
#
# 2. BÚSQUEDA INTELIGENTE:
#    Toma cada nombre de archivo del Excel y lo busca en las siguientes carpetas
#    (en este orden exacto):
#       a) procesar shpcfrm pendientes
#       b) Procesados Wave
#       c) Procesados Cartoning
#
#    IMPORTANTE: La búsqueda coincide si los primeros 46 CARACTERES son iguales.
#
# 3. PROCESAMIENTO (Si encuentra el archivo):
#    - Crea una carpeta destino llamada "Reprocesar (Día-Mes-Año Hora.Min)".
#    - COPIA el archivo original (no lo borra del origen).
#    - RENOMBRA la copia agregando "_ref_" en su estructura.
#    - Actualiza el Excel escribiendo "ENCONTRADO" en la columna "Estado".
#
# 4. REPORTE (Si no lo encuentra):
#    - Escribe "NO ENCONTRADO" en la columna "Estado" del Excel.
#
# 5. CIERRE:
#    - Guarda los cambios en el Excel y muestra un resumen en pantalla.
# ==============================================================================

import pandas as pd
import os
import shutil
from datetime import datetime

# --- CONFIGURACIÓN ---
ruta_base = r"C:\Users\331642\Desktop\harrys\interfaz"
nombre_excel = "analisis.xlsx"
hoja_excel = "Buscar"
columna_excel = "archivo"
columna_estado = "Estado"

# Lista unificada de carpetas donde buscar
carpetas_origen = [
    "procesar shpcfrm pendientes",
    "Procesados Wave",
    "Procesados Cartoning"
]

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
    print("--- Iniciando rescate unificado (ShipConfirm, Wave, Cartoning) ---")

    ruta_excel = os.path.join(ruta_base, nombre_excel)
    fecha_actual = datetime.now().strftime("%d-%m-%y %H.%M")
    nombre_carpeta_destino = f"Reprocesar ({fecha_actual})"
    ruta_destino = os.path.join(ruta_base, nombre_carpeta_destino)

    # Verificamos existencia del Excel
    if not os.path.exists(ruta_excel):
        print(f"[ERROR] No se encuentra el archivo Excel: {ruta_excel}")
        return

    try:
        print(f"Leyendo Excel...")
        df = pd.read_excel(ruta_excel, sheet_name=hoja_excel)

        if columna_excel not in df.columns:
            print(f"[ERROR] Columna '{columna_excel}' no encontrada.")
            return

        # Inicializamos columna de estado si no existe
        if columna_estado not in df.columns:
            df[columna_estado] = ""

        # Creamos carpeta destino solo si es necesario (se creará si encontramos al menos uno)
        carpeta_creada = False

        encontrados = 0
        no_encontrados = 0

        # Iteramos por cada fila del Excel
        for index, row in df.iterrows():
            archivo_buscado = str(row[columna_excel]).strip()

            # Validación básica
            if not archivo_buscado or archivo_buscado.lower() == 'nan':
                continue

            # Clave de búsqueda (logica original: primeros 46 caracteres)
            clave_busqueda = archivo_buscado[:46]
            fue_encontrado = False
            
            # --- BÚSQUEDA EN LAS 3 CARPETAS ---
            for carpeta in carpetas_origen:
                ruta_carpeta_actual = os.path.join(ruta_base, carpeta)

                # Si la carpeta no existe, pasamos a la siguiente
                if not os.path.exists(ruta_carpeta_actual):
                    continue

                try:
                    archivos_en_disco = os.listdir(ruta_carpeta_actual)
                except OSError:
                    continue

                # Buscamos coincidencia en la carpeta actual
                for archivo_real in archivos_en_disco:
                    if archivo_real[:46].lower() == clave_busqueda.lower():
                        
                        # ¡Encontrado! Preparamos rutas
                        ruta_origen_completa = os.path.join(ruta_carpeta_actual, archivo_real)
                        nuevo_nombre = generar_nombre_con_ref(archivo_real)
                        
                        # Crear carpeta destino si es el primero que encontramos
                        if not carpeta_creada:
                            if not os.path.exists(ruta_destino):
                                os.makedirs(ruta_destino)
                            carpeta_creada = True

                        ruta_final = os.path.join(ruta_destino, nuevo_nombre)

                        # Copiar
                        shutil.copy2(ruta_origen_completa, ruta_final)
                        
                        print(f"[OK] Encontrado en '{carpeta}': {archivo_real}")
                        
                        fue_encontrado = True
                        encontrados += 1
                        break # Rompe el ciclo de archivos_en_disco
                
                if fue_encontrado:
                    break # Rompe el ciclo de carpetas (ya lo encontramos, no buscamos en las otras)

            # --- ACTUALIZAR DATAFRAME ---
            if fue_encontrado:
                df.at[index, columna_estado] = "ENCONTRADO"
            else:
                print(f"[X] No encontrado en ninguna carpeta: {archivo_buscado}")
                df.at[index, columna_estado] = "NO ENCONTRADO"
                no_encontrados += 1

        print("-" * 30)
        print("Guardando cambios en el Excel...")
        
        df.to_excel(ruta_excel, sheet_name=hoja_excel, index=False)

        print(f"Resumen Final:")
        print(f"Archivos encontrados: {encontrados}")
        print(f"Archivos no encontrados: {no_encontrados}")
        if carpeta_creada:
            print(f"Archivos guardados en: {ruta_destino}")
        else:
            print("No se creó carpeta de destino porque no se encontraron archivos.")

    except PermissionError:
        print("[ERROR CRÍTICO] El archivo Excel está ABIERTO. Ciérrelo e intente de nuevo.")
    except Exception as e:
        print(f"[CRÍTICO] Error inesperado: {e}")

if __name__ == "__main__":
    rescatar_archivos()