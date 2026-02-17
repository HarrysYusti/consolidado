import pandas as pd
from databricks import sql
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import time
import os
import re

# Obtener token de databricks
with open(r"/home/rpauser/airflow/notebooks/token_databricks.txt", 'r') as file:
    token = file.readline().strip()

# Crear función cálculo SPP
def spp(clasificacion, nc, part_fact, avo, t_casa):
    # No diamantes
    if clasificacion != 'DIAMANTE':
        # Condición 1 + 2 +3
        if (nc <= 1 and part_fact < 0.05) or avo < 25000 or nc == 2:
            return 0
        # Condición 4
        elif avo >= 25000 and nc < 3:
            return 1
        # Condición 5, según facturación y tiempo en casa para 3 o más reclamos:
        else:
            # Definir los rangos de PART y T
            part_ranges = [(0, 0.05), (0.05, 0.1), (0.10, 0.15), (0.15, 0.20), (0.20, 0.25), (0.25, 0.30), (0.30, 0.35), (0.35, 0.40), (0.40, float('inf'))]
            t_ranges = [(0, 1), (1, 2), (2, 5), (5, float('inf'))]

            # Crear la matriz de valores
            values_matrix = [
            [1, 1, 1, 1],
            [2, 1, 1, 1],
            [2, 2, 1, 1],
            [3, 2, 2, 1],
            [3, 3, 2, 1],
            [3, 3, 3, 2],
            [3, 3, 3, 2],
            [3, 3, 3, 3],
            [3, 3, 3, 3]]

            # Convertir la matriz en un DataFrame
            df_matrix = pd.DataFrame(values_matrix, index=[f'{start}-{end}%' for start, end in part_ranges], columns=[f'<{end}' if end != float('inf') else f'>{start}' for start, end in t_ranges])

            # Función para obtener el valor de la matriz
            def get_value(part, t):
                part_index = next((i for i, (start, end) in enumerate(part_ranges) if start <= part < end), None)
                t_index = next((i for i, (start, end) in enumerate(t_ranges) if start <= t < end), None)
                if part_index is not None and t_index is not None:
                    return df_matrix.iloc[part_index, t_index]
                else:
                    return 0

            result = get_value(part_fact, t_casa)
            return result
    #Luego, si es diamante
    else:
        if nc <= 2 and part_fact < 0.05:
            return 0
        else:
            # Definir los rangos de PART y T
            part_ranges = [(0.05, 0.1), (0.10, 0.15), (0.15, 0.20), (0.20, 0.25), (0.25, 0.30), (0.30, 0.35), (0.35, 0.40), (0.40, 0.45), (0.45, 0.50), (0.50, float('inf'))]
            t_ranges = [(0, 1), (1, 2), (2, 5), (5, float('inf'))]

            # Crear la matriz de valores
            values_matrix = [
            [1, 1, 1, 1],
            [2, 1, 1, 1],
            [2, 2, 1, 1],
            [3, 2, 2, 1],
            [3, 3, 2, 1],
            [3, 3, 3, 2],
            [3, 3, 3, 2],
            [3, 3, 3, 2],
            [3, 3, 3, 3],
            [3, 3, 3, 3]]

            # Convertir la matriz en un DataFrame
            df_matrix = pd.DataFrame(values_matrix, index=[f'{start}-{end}%' for start, end in part_ranges], columns=[f'<{end}' if end != float('inf') else f'>{start}' for start, end in t_ranges])

            # Función para obtener el valor de la matriz
            def get_value(part, t):
                part_index = next((i for i, (start, end) in enumerate(part_ranges) if start <= part < end), None)
                t_index = next((i for i, (start, end) in enumerate(t_ranges) if start <= t < end), None)
                if part_index is not None and t_index is not None:
                    return df_matrix.iloc[part_index, t_index]
                else:
                    return 0

            result = get_value(part_fact, t_casa)
            return result

# Conectar a la base de datos de Databricks
connection = sql.connect(
                        server_hostname = "dbc-02543f96-daa5.cloud.databricks.com",
                        http_path = "/sql/1.0/warehouses/ec9f17d05dd2fb86",
                        access_token = token)

# Create a cursor from the connection
cursor = connection.cursor()  # Added this line to create a cursor

# Leer cada tabla obtenida del archivo de texto Tablas Principales y guardar el restulado en el dataframe creado
print("Conectando a la base de datos de Databricks y ejecutando query...")
query = 'SELECT * FROM sandbox.td_sql_chile.customer_care_resumen_consultor_chl'
cursor.execute(query)

rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
tabla_query = pd.DataFrame(rows, columns=columns)

# Cerrar el cursor y la conexión
cursor.close()
connection.close()

# Cargar la tabla en un DataFrame
df = tabla_query

# Calcular el SPP de cada consultora y agregarlo al DataFrame
df['SPP'] = ''
for index, row in df.iterrows():
    clasificacion = row['CLASIFICACION']
    nc = row['CANTIDAD_NC']
    part_fact = row['PORCENTAJE_FACTURACION_RECLAMADA']
    avo = row['AVO_NC']
    t_casa =  row['TIEMPO_CASA']
    df.at[index, 'SPP'] = spp(clasificacion, nc, part_fact, avo, t_casa)

# Obtener dataframe con las columnas de código consultor y su spp
df_pandas = df[['CODIGO_CONSULTOR', 'SPP']]

# Eliminar filas duplicadas basadas en CODIGO_CONSULTOR
df_final = df_pandas.drop_duplicates(subset=['CODIGO_CONSULTOR'])
df_final['CODIGO_CONSULTOR'] = df_final['CODIGO_CONSULTOR'].astype(str)

# Diccionario de mapeo para reclasificar
spp_mapping = {
    0: 'SSPP',
    1: 'SPP 1',
    2: 'SPP 2',
    3: 'SPP 3'
}

df_final['SPP'] = df_final['SPP'].map(spp_mapping)

# Reemplazar valores SPP con SPP F según archivo
# Path to the directory
directory_path = r"/mnt/windows_share/Customer_Care/SPPF/"

try:
    # List all files in the directory
    files = os.listdir(directory_path)
    print("Intentando abrir SPP F")
 
    # Filter out the .xlsx files
    xlsx_files = [file for file in files if file.endswith('.xlsx')]

    # Check if there is exactly one .xlsx file
    if len(xlsx_files) == 1:
        # Load the .xlsx file into a dataframe
        file_path = os.path.join(directory_path, xlsx_files[0])
        sppf = pd.read_excel(file_path, engine='openpyxl')
        print("SPPF cargado exitosamente.")

        # Reemplazar el valor de cada match de df_final en sppf
        # Crear un conjunto de los valores de CN en sppf
        #cn_set = set(sppf['CN'])

        # Reemplazar los valores en df_final['SPP']
        #df_final.loc[df_final['CODIGO_CONSULTOR'].isin(cn_set), 'SPP'] = 'SPP F'

        
        # Supongamos que sppf y df_final son tus dataframes
        # Realizar un merge para obtener los valores coincidentes
        sppf['CN'] = sppf['CN'].astype(str)  # Asegurarse de que los tipos coincidan
        merged_df = df_final.merge(sppf[['CN']], left_on='CODIGO_CONSULTOR', right_on='CN', how='left')
        print(merged_df.head(10))

        # Actualizar los valores en df_final['SPP']
        df_final.loc[merged_df['CN'].notnull(), 'SPP'] = 'SPP F'

    else:
        print("No .xlsx archivo encontrado o multiples .xlsx encontrados. No se cargó ningún archivo.")
except Exception as e:
    print(f"Ocurrió un error: {e}")


# Obtener credenciales SQL Server
# Path to the file
file_path = '/home/rpauser/airflow/notebooks/SQL2022.txt'

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


# Inicia proceso de ingesta
# Conexión e insertar en SQL Server
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

print("Iniciando ingesta de datos...")
# Insertar en SQL Server
with engine.begin() as connection:
    start_time = time.time()
    df_final.to_sql(
        name='spp',
        schema='customer_care',
        con=connection,
        method='multi',
        chunksize=30,
        if_exists='replace',
        index=False,
    )

