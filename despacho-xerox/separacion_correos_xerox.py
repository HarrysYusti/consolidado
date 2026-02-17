import os
import sys
import pandas as pd
from datetime import datetime
import shutil
import re

# --- Configuración de rutas e importación de DatabricksClient ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.dirname(current_script_dir)
src_path = os.path.join(project_root_dir, 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from resources import databricks_db as datadb

with open(r"/home/rpauser/airflow/notebooks/token_databricks.txt", 'r') as file:
    token = file.readline().strip()

def get_databricks_cli():
    return datadb.DatabricksClient(
        host = "dbc-02543f96-daa5.cloud.databricks.com",
        http_path = "/sql/1.0/warehouses/ec9f17d05dd2fb86",
        api_key = token,
    )

dataabricks_cli = get_databricks_cli()
# --- Fin Configuración ---

# --- Rutas de archivos y carpetas ---
path_archivos = r"/mnt/windows_share/Customer_Care/Despacho Xerox/Sectores/"

# --- Fin Rutas ---

# Obtener la fecha de hoy en el formato 'YYYY-MM-DD'
fecha_hoy = datetime.now().strftime('%Y-%m-%d')

# Construir la query con la fecha dinámica
query = f"""SELECT *
           FROM sandbox.td_sql_chile.envio_correos_xerox
           WHERE Tipo_Error IS NOT NULL AND time_ingest >= '{fecha_hoy}'
        """

correos = dataabricks_cli.get_df(query)

# Filtrar los correos que fallaron, pero que en Lego tenemos un correo distinto (correo que debería estar correcto)
# Función para validar el formato de correo electrónico
def is_valid_email(email):
    if email is None:
        return False
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email) is not None

# Filtrar el dataframe
correos = correos[
    (correos['email_envio_xerox'] == correos['email_lego']) |
    (~correos['email_lego'].apply(is_valid_email))
]

# Convertir campos de teléfono a string y unificar
correos['telefono_full'] =  correos['codigo_area'].astype('str')+''+correos['telefono'].astype('str')

# Si el teléfono comienza con 56, se remueve del string
correos['telefono_full'] = correos['telefono_full'].apply(lambda x: x[2:] if x.startswith('56') else x)

# Remover codigo pais, area y telefono reemplazar por telefono full
correos['telefono'] = correos['telefono_full']
correos.drop(columns = ['codigo_pais', 'codigo_area', 'telefono_full'], inplace = True)

# CORREGIR NOMBRE DE SECTOR PARA QUE NO TENGA ESPACIOS NI ANTES NI DESPUÉS DEL STRING
correos['nombre_sector'] = correos['nombre_sector'].str.strip()

# Generar nuevos valores para motivo de rechazo
reemplazos = {
    "No Sent": "Correo inválido: solicitar cambiar correo",
    "Supression": "Nos tiene en SPAM: solicitar que nos libere de SPAM",
    "Soft Bounce": "Bandeja llena: cambiar a otro correo o liberar espacio en bandeja",
    "Hard Bounce": "Correo inválido: solicitar cambiar correo",
    "Otros Rebotes": "Correo inválido: solicitar cambiar correo",
    "Rebote": "Correo inválido: solicitar cambiar correo"
}

correos['Motivo'] = correos['Tipo_Error'].map(reemplazos)

# Generar archivos iterando sobre cada SECTOR
# Crear una lista con los sectores únicos
sectores = correos['nombre_sector'].unique()

nombres_nuevos = ['Gerencia', 'Sector', 'Nombre Líder', 'Código Grupo', 'Código Consultora', 'Nombre Consultora', 'Correo Registrado', 'Motivo Falla Entrega de Correo', 'Teléfono Consultora']

# Ruta de la carpeta donde deseas guardar los archivos
ruta_carpeta = path_archivos

# Eliminar archivos en la carpeta de destino
for filename in os.listdir(ruta_carpeta):
        file_path = os.path.join(ruta_carpeta, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path) # Elimina el archivo o el enlace simbólico
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path) # Elimina subdirectorios (si los hay y también quieres borrarlos)
        except Exception as e:
            print(f'Falló al eliminar {file_path}. Razón: {e}')

for sector in sectores:
    # Filtrar registros por sector actual
    df_sector = correos[correos['nombre_sector'] == sector][['nombre_gerencia', 'nombre_sector', 'nombre_lider', 'codigo_grupo', 'codigo_consultor', 'nombre_consultor', 'email_envio_xerox',
                                                            'Motivo', 'telefono']]
    # Remover duplicados
    df_sector = df_sector.drop_duplicates()

    # Cambiar nombre de columnas para el archivo
    df_sector.columns = nombres_nuevos
    
    # Crear el archivo Excel con el nombre del sector
    nombre_archivo = f"{sector}.xlsx"
    ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo)

    # Guardar el archivo Excel
    df_sector.to_excel(ruta_archivo, index=False, engine='openpyxl')
    
    print(f"Archivo generado: {sector}.xlsx")