import pandas as pd
import os
import shutil
from datetime import datetime

# Define la ruta de la carpeta de origen
path_origen = r"/mnt/windows_share/Customer_Care/Despacho Xerox/Descarga Diaria/" 
# Define la ruta de la carpeta de destino para el archivo concatenado
path_destino = r"/mnt/windows_share/Customer_Care/Despacho Xerox/Concatenado/"
# Define la ruta de la carpeta para los archivos procesados
path_old = r"/mnt/windows_share/Customer_Care/Despacho Xerox/Descarga Diaria/Old/"

# Asegúrate de que las carpetas de destino existan, si no, las crea
os.makedirs(path_destino, exist_ok=True)
os.makedirs(path_old, exist_ok=True)

# Lista todos los archivos .csv en la carpeta de origen
files = [f for f in os.listdir(path_origen) if f.endswith('.csv')]

# --- Nueva Verificación ---
# Si no hay archivos CSV, lanza una excepción y detén el script
if not files:
    raise Exception(f"No se encontraron archivos CSV para procesar en la ruta: {path_origen}")
# --- Fin Nueva Verificación ---

# Lista para almacenar los dataframes
dataframes = []
# Lista para almacenar los nombres de los archivos CSV que fueron procesados exitosamente
processed_files = []

# Leer cada archivo CSV y agregarlo a la lista
for file in files:
    filepath = os.path.join(path_origen, file)
    try:
        df = pd.read_csv(filepath, sep=';', encoding='latin1')
        dataframes.append(df)
        processed_files.append(file) # Añade el nombre del archivo a la lista de procesados
    except UnicodeDecodeError:
        print(f"Advertencia: Error de codificación al leer el archivo '{file}'. Este archivo será omitido.")
    except Exception as e:
        print(f"Advertencia: Error inesperado al leer el archivo '{file}': {e}. Este archivo será omitido.")


# Concatenar todos los dataframes en uno solo
if dataframes: # Solo concatenar si hay dataframes leídos correctamente
    final_dataframe = pd.concat(dataframes, ignore_index=True)

    # Obtener la fecha actual y formatearla
    fecha_actual = datetime.now().strftime("%d.%m.%Y")
    
    # Crear el nombre del archivo con la fecha
    nombre_archivo = f"Concatenado_{fecha_actual}.xlsx"
    
    # Unir la ruta de destino con el nombre del archivo
    ruta_completa_destino = os.path.join(path_destino, nombre_archivo)

    try:
        # Exportar el dataframe concatenado a un archivo Excel en la ruta especificada
        final_dataframe.to_excel(ruta_completa_destino, index=False)
        print(f"¡Archivos concatenados y exportados exitosamente en: {ruta_completa_destino}!")

        # Mover los archivos CSV procesados a la carpeta 'Old'
        print("\nMoviendo archivos CSV procesados a la carpeta 'Old'...")
        for file_name in processed_files:
            source_path = os.path.join(path_origen, file_name)
            destination_path = os.path.join(path_old, file_name)
            try:
                shutil.move(source_path, destination_path)
                print(f"'{file_name}' movido a '{path_old}'")
            except Exception as e:
                print(f"Error al mover el archivo '{file_name}': {e}")
        
        print("\nMovimiento de archivos completado.")

    except Exception as e:
        # Si falla la exportación del Excel, lanza una excepción
        raise Exception(f"Error crítico al exportar el archivo Excel: {e}. Los archivos CSV no fueron movidos.")

else:
    # Si no se pudo leer ningún dataframe (todos fallaron por codificación o estaban vacíos)
    # y ya pasamos la primera verificación, este caso indica un problema con los archivos existentes.
    raise Exception(f"No se pudo leer ningún archivo CSV válido de {len(files)} archivos encontrados, posiblemente debido a problemas de codificación o formato incorrecto. No se generó ningún Excel.")