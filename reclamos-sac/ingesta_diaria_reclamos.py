import os, sys
import pandas as pd
import shutil
#import numpy as np
import time
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
#import xlrd
import re

# Importación de librería para manejar la conexión a Databricks
# 1. Obtener la ruta absoluta del directorio actual de my_script.py
#    Esto será '/home/rpauser/airflow/python-ingesta-datos/reclamos_sac'
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Navegar un nivel arriba para llegar a 'python-ingesta-datos'
#    Esto será '/home/rpauser/airflow/python-ingesta-datos'
project_root_dir = os.path.dirname(current_script_dir)

# 3. Construir la ruta completa a la carpeta 'src'
#    Esto será '/home/rpauser/airflow/python-ingesta-datos/src'
src_path = os.path.join(project_root_dir, 'src')

# 4. Añadir 'src_path' al sys.path si no está ya
#    Se recomienda insertarlo al principio para que Python lo encuentre primero.
if src_path not in sys.path:
    sys.path.insert(0, src_path) # Usar insert(0, ...) para que tenga prioridad

# Ahora puedes importar tus módulos de 'resources'
from resources import databricks_db as datadb

# Directorios de lectura de archivo de entrada
input_folder = r"/mnt/windows_share/Customer_Care/Reclamos_Sac/"
output_folder = r"/mnt/windows_share/Customer_Care/Reclamos_Sac/Old"

# Obtener credenciales SQL Server
# Path to the file
file_path = '/home/rpauser/airflow/notebooks/SQL2022.txt'

# Credenciales de databricks
with open(r"/home/rpauser/airflow/notebooks/token_databricks.txt", 'r') as file:
    token = file.readline().strip()
print("Credenciales inicializadas...")

# Function to extract username and password
def extract_credentials(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    username_match = re.search(r'username="([^"]+)"', content)
    password_match = re.search(r'password="([^"]+)"', content)
    
    if username_match and password_match:
        username = username_match.group(1)
        password = password_match.group(1)
        return username , password
    else:
        return "Username or password not found in the file."

# Call the function and print the results
username_sql, password_sql = extract_credentials(file_path)

# Crear un DataFrame vacío
df_concatenado = pd.DataFrame()


try:
    archivos_encontrados = False
    for file in os.listdir(input_folder):
        if file.endswith(".xls"):  # Filtrar archivos .xls
            archivos_encontrados = True
            file_path = os.path.join(input_folder, file)
 
            # Leer el archivo y concatenarlo al DataFrame
            df = pd.read_excel(file_path)
            df_concatenado = pd.concat([df_concatenado, df], ignore_index=True)
            print(f'Archivo {file} concatenado exitosamente')
            
             # Mover el archivo a la carpeta destino
            shutil.move(file_path, os.path.join(output_folder, file))

    if not archivos_encontrados:
        raise FileNotFoundError("No se encontraron archivos .xls en la carpeta de entrada.")

except FileNotFoundError as e:
    print(e)
    print("Deteniendo el script.")

tabla_query = df_concatenado

# Suponiendo que tabla_query es el dataframe que contiene los datos
# Convertir las columnas a tipo datetime si no lo son ya
tabla_query['DT_ABERTURA'] = pd.to_datetime(tabla_query['DT_ABERTURA'], errors='coerce')
tabla_query['DT_FECHAMENTO'] = pd.to_datetime(tabla_query['DT_FECHAMENTO'], errors='coerce')
tabla_query['FECHA_PESAJE'] = pd.to_datetime(tabla_query['FECHA_PESAJE'], errors='coerce')
tabla_query['HORARIO_PESAJE'] = pd.to_datetime(tabla_query['HORARIO_PESAJE'], errors='coerce')

# Eliminar la información de zona horaria de las columnas datetime
tabla_query['DT_ABERTURA'] = tabla_query['DT_ABERTURA'].dt.tz_localize(None)
tabla_query['DT_FECHAMENTO'] = tabla_query['DT_FECHAMENTO'].dt.tz_localize(None)
tabla_query['FECHA_PESAJE'] = tabla_query['FECHA_PESAJE'].dt.tz_localize(None)
tabla_query['HORARIO_PESAJE'] = tabla_query['HORARIO_PESAJE'].dt.tz_localize(None)

# Definir los tipos de datos para cada columna
dtype_dict = {
    'CD_ATENDIMENTO': 'int64',
    'CD_PEDIDO': 'float64',
    'CAJA': 'float64',
    'DT_ABERTURA': 'datetime64[ns]',
    'CD_PESSOA': 'int64',
    'DC_PESSOA': 'object',  # VARCHAR(255) en SQL
    'TIPO': 'object',  # VARCHAR(255) en SQL
    'DC_SITUACAO': 'object',  # VARCHAR(255) en SQL
    'DC_RESPOSTA': 'object',  # VARCHAR(255) en SQL
    'COD_VENTA_PROD_ENVIADO': 'float64',
    'DESC_VENTA_PROD_ENVIADO': 'object',  # VARCHAR(255) en SQL
    'QT_VENTA_ENVIADO': 'float64',
    'COD_VENTA': 'float64',
    'COD_MATERIAL': 'float64',
    'DC_PRODUCTO': 'object',  # VARCHAR(255) en SQL
    'PRECIO_LIQ': 'float64',
    'QT_RECLAMADA': 'float64',
    'PESO_TEORICO': 'float64',
    'CATEGORIA': 'object',  # VARCHAR(255) en SQL
    'MARCA': 'object',  # VARCHAR(255) en SQL
    'PARTE_PROD_AFECTADA': 'object',  # VARCHAR(255) en SQL
    'PROD_CARACTERISTICAS': 'object',  # VARCHAR(255) en SQL
    'MOTIVO_DEVOLUCION': 'object',  # VARCHAR(255) en SQL
    'DC_PROBLEMA': 'object',  # VARCHAR(255) en SQL
    'DC_RESPOSTA_MOTIVO': 'object',  # VARCHAR(255) en SQL
    'DC_RESPOSTA_OBSERVACAO': 'object',  # VARCHAR(255) en SQL
    'DC_OBSERVACAO_ACAO': 'object',  # VARCHAR(255) en SQL
    'DC_OBSERVACAO_ATENCAO': 'object',  # VARCHAR(255) en SQL
    'NM_NOTA_FISCAL': 'float64',
    'CD_USUARIO': 'int64',
    'DC_USUARIO': 'object',  # VARCHAR(255) en SQL
    'CD_USUARIO_CRIACAO': 'int64',
    'DC_USUARIO_CRIACAO': 'object',  # VARCHAR(255) en SQL
    'CD_GERENCIA': 'int64',
    'DC_GERENCIA': 'object',  # VARCHAR(255) en SQL
    'CD_ESTRUTURA': 'int64',
    'DC_ESTRUTURA': 'object',  # VARCHAR(255) en SQL
    'ORIGEM': 'object',  # VARCHAR(255) en SQL
    'ORIGEM_SOLUCION': 'object',  # VARCHAR(255) en SQL
    'DC_INF': 'object',  # VARCHAR(255) en SQL
    'DT_FECHAMENTO': 'datetime64[ns]',
    'TRANSPORTISTA': 'object',  # VARCHAR(255) en SQL
    'TEMPO_CASA_MESES': 'int64',
    'PERFIL_CREDITICIO': 'object',  # VARCHAR(255) en SQL
    'CD_GRUPO': 'int64',
    'DC_PESSOA_RESPONSAVEL': 'object',  # VARCHAR(255) en SQL
    'NIVEL_GEO1_ENTREGA': 'object',  # VARCHAR(255) en SQL
    'NIVEL_GEO2_ENTREGA': 'object',  # VARCHAR(255) en SQL
    'NIVEL_GEO3_ENTREGA': 'object',  # VARCHAR(255) en SQL
    'NIVEL_GEO4_ENTREGA': 'object',  # VARCHAR(255) en SQL
    'DC_MEDIO_CAPTACION': 'object',  # VARCHAR(255) en SQL
    'DC_MODELO_COMERCIAL': 'object',  # VARCHAR(255) en SQL
    'CICLO_CAPTACION': 'float64',
    'CODIGO_LINEA_SEP': 'float64',
    'CANAL_DISTRIBUCION': 'object',  # VARCHAR(255) en SQL
    'FECHA_PESAJE': 'datetime64[ns]',
    'HORARIO_PESAJE': 'datetime64[ns]',
    'TIPO_CAJA': 'object',  # VARCHAR(255) en SQL
    'QT_ITENS_CAJA': 'float64',
    'PESO_FINAL': 'float64',
    'PESO_ESTIMADO': 'float64',
    'EMPRESA': 'object'  # VARCHAR(255) en SQL
}

# Verificar y limpiar los datos antes de la conversión
for column, dtype in dtype_dict.items():
    if dtype == 'float64':
        tabla_query[column] = pd.to_numeric(tabla_query[column], errors='coerce')

# Convertir los tipos de datos de las columnas del dataframe
tabla_query = tabla_query.astype(dtype_dict)

print("Tipos de datos convertidos exitosamente.")

# Insertar tabla en SQL Server

connection_url = URL.create(
    "mssql+pyodbc",
    username=username_sql,
    password=password_sql,
    host="10.156.16.46\\SQL2022",
    #port=1433,
    database="CustomerCare",
    query={
        "driver": "ODBC Driver 17 for SQL Server",
    #    "TrustServerCertificate": "yes",
    #    "authentication": "ActiveDirectoryIntegrated",
    },
)
engine = create_engine(connection_url)

with engine.begin() as connection:
    start_time = time.time()
    tabla_query.to_sql(
        name='reclamos',
        schema='customer_care',
        con=connection,
        method='multi',
        chunksize=30,
        if_exists='append',
        index=False,
    )
    print("Datos insertados exitosamente en SQL Server")
    print("--- %s seconds ---" % (time.time() - start_time))

# Ingesta de los datos en Databricks
def get_databricks_cli():
    return datadb.DatabricksClient(
        host = "dbc-02543f96-daa5.cloud.databricks.com",
        http_path = "/sql/1.0/warehouses/ec9f17d05dd2fb86",
        api_key = token,
    )

dataabricks_cli = get_databricks_cli()

dataabricks_cli.insert_dataframe(tabla_query, "sandbox.td_sql_chile.bbdd_customer_care")
print("Datos insertados exitosamente en Databricks")


