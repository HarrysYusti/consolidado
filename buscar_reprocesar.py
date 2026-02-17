import pandas as pd
import os
import shutil

# --- CONFIGURACIÓN DE RUTAS ---
# Usamos r"" para que Python interprete correctamente las barras invertidas de Windows

ruta_excel = r"C:\Users\331642\Desktop\harrys\interfaz\PEDIDOS COMPLETADOS EWM EN SEPARACION.xlsx"

# Carpetas donde buscaremos los archivos (Origen)
origen_cartoning = r"C:\Users\331642\Desktop\harrys\interfaz\procesar cartoning pendientes\Procesados Cartoning"
origen_wave = r"C:\Users\331642\Desktop\harrys\interfaz\procesar wave pendientes\Procesados Wave"

# Carpeta base donde se moverán (Destino)
base_reprocesar = r"C:\Users\331642\Desktop\harrys\interfaz\reprocesar"

# Rutas finales de destino
destino_cartoning = os.path.join(base_reprocesar, "Cartoning")
destino_wave = os.path.join(base_reprocesar, "Wave")

def procesar_archivos():
    # 1. Crear carpetas de destino si no existen
    os.makedirs(destino_cartoning, exist_ok=True)
    os.makedirs(destino_wave, exist_ok=True)
    
    print("--- Iniciando proceso ---")

    try:
        # 2. Leer el Excel
        # header=None porque indicaste que no tiene encabezado (Columna A es índice 0)
        df = pd.read_excel(ruta_excel, sheet_name="documentos", header=None)
        
        # Obtenemos la lista de archivos de la primera columna, eliminando vacíos
        lista_archivos = df[0].dropna().astype(str).tolist()
        
        print(f"Se encontraron {len(lista_archivos)} nombres de archivos en el Excel.")

    except Exception as e:
        print(f"Error al leer el Excel: {e}")
        return

    archivos_movidos = 0
    archivos_no_encontrados = 0

    # 3. Iterar sobre cada nombre de archivo
    for nombre_archivo in lista_archivos:
        nombre_archivo = nombre_archivo.strip() # Limpiar espacios en blanco
        archivo_encontrado = False
        ruta_origen_final = None

        # Buscamos primero en la carpeta de Cartoning
        if os.path.exists(os.path.join(origen_cartoning, nombre_archivo)):
            ruta_origen_final = os.path.join(origen_cartoning, nombre_archivo)
        # Si no está, buscamos en la carpeta de Wave
        elif os.path.exists(os.path.join(origen_wave, nombre_archivo)):
            ruta_origen_final = os.path.join(origen_wave, nombre_archivo)
        
        if ruta_origen_final:
            # 4. Determinar destino y mover
            nombre_lower = nombre_archivo.lower()
            ruta_destino_final = None

            if nombre_lower.startswith("cartoning"):
                ruta_destino_final = os.path.join(destino_cartoning, nombre_archivo)
            elif nombre_lower.startswith("wave"):
                ruta_destino_final = os.path.join(destino_wave, nombre_archivo)
            
            if ruta_destino_final:
                try:
                    shutil.move(ruta_origen_final, ruta_destino_final)
                    print(f"[OK] Movido: {nombre_archivo}")
                    archivos_movidos += 1
                except Exception as e:
                    print(f"[ERROR] No se pudo mover {nombre_archivo}: {e}")
            else:
                print(f"[OMITIDO] {nombre_archivo} no empieza con 'cartoning' ni 'Wave'.")
        else:
            print(f"[NO ENCONTRADO] El archivo {nombre_archivo} no está en las carpetas de origen.")
            archivos_no_encontrados += 1

    print("--- Proceso Finalizado ---")
    print(f"Total movidos: {archivos_movidos}")
    print(f"No encontrados: {archivos_no_encontrados}")

if __name__ == "__main__":
    procesar_archivos()