import pandas as pd
import os
import shutil
from datetime import datetime

# --- CONFIGURACIÓN ---
ruta_base = r"C:\Users\331642\Desktop\problema de fase\jeremy\06"
nombre_excel = "analisis.xlsx"
hoja_excel = "Buscar"
columna_excel = "archivo"

# Carpetas donde vamos a BUSCAR los archivos
carpetas_origen = ["Procesados Wave", "Procesados Cartoning"]

def generar_nombre_con_ref(nombre_archivo):
    """
    Inserta '_ref_' después del tercer guion bajo.
    Estructura asumida: Parte1_Parte2_Fecha_Resto...
    """
    partes = nombre_archivo.split('_')
    
    # Verificamos que el archivo tenga al menos 3 guiones (4 partes) para no romper nombres cortos
    if len(partes) >= 4:
        # Unimos las 3 primeras partes (Ej: Wave_Confirm_2025...)
        prefijo = "_".join(partes[:3]) 
        
        # Unimos el resto (Ej: 342__hash.txt)
        sufijo = "_".join(partes[3:])
        
        # Retornamos con el ref intercalado
        return f"{prefijo}_ref_{sufijo}"
    else:
        # Si el nombre es muy corto o raro, solo le agregamos ref al inicio para que se note
        return f"ref_{nombre_archivo}"

def rescatar_archivos():
    print("--- Iniciando rescate y renombrado de archivos ---")

    ruta_excel = os.path.join(ruta_base, nombre_excel)
    fecha_actual = datetime.now().strftime("%d-%m-%y %H.%M") 
    nombre_carpeta_destino = f"Reprocesar ({fecha_actual})"
    ruta_destino = os.path.join(ruta_base, nombre_carpeta_destino)

    if not os.path.exists(ruta_excel):
        print(f"[ERROR] No se encuentra el archivo: {ruta_excel}")
        return

    try:
        print(f"Leyendo Excel...")
        df = pd.read_excel(ruta_excel, sheet_name=hoja_excel)
        
        if columna_excel not in df.columns:
            print(f"[ERROR] Columna '{columna_excel}' no encontrada.")
            return

        lista_archivos = df[columna_excel].dropna().astype(str).tolist()
        
        if not os.path.exists(ruta_destino):
            os.makedirs(ruta_destino)

        encontrados = 0
        no_encontrados = 0

        for archivo in lista_archivos:
            archivo = archivo.strip()
            archivo_encontrado = False

            for carpeta in carpetas_origen:
                ruta_origen = os.path.join(ruta_base, carpeta, archivo)
                
                if os.path.exists(ruta_origen):
                    # --- AQUÍ ESTÁ EL CAMBIO DE NOMBRE ---
                    nuevo_nombre = generar_nombre_con_ref(archivo)
                    ruta_final = os.path.join(ruta_destino, nuevo_nombre)
                    
                    # Copiamos con el nuevo nombre
                    shutil.copy2(ruta_origen, ruta_final)
                    
                    print(f"[OK] Copiado como: {nuevo_nombre}")
                    archivo_encontrado = True
                    encontrados += 1
                    break 
            
            if not archivo_encontrado:
                print(f"[X] NO ENCONTRADO: {archivo}")
                no_encontrados += 1

        print("-" * 30)
        print(f"Resumen:")
        print(f"Archivos rescatados: {encontrados}")
        print(f"Archivos perdidos: {no_encontrados}")
        print(f"Carpeta destino: {nombre_carpeta_destino}")

    except Exception as e:
        print(f"[CRITICO] Error: {e}")

if __name__ == "__main__":
    rescatar_archivos()