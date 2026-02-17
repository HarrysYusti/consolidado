import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import time
import re

# Obtener credenciales SQL Server
# Path to the file
file_path = r'/home/rpauser/airflow/notebooks/SQL2022.txt'

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

# Se crea función que carga un .xlsx a dataframe en Pandas, con try & catch.
def crear_dataframe(ruta_archivo):
    """
    Crea un DataFrame de pandas a partir de un archivo Excel.

    Args:
        ruta_archivo (str): La ruta completa del archivo Excel.

    Returns:
        pd.DataFrame: El DataFrame 'productos' creado a partir del archivo,
                      o None si ocurre un error.
    """
    try:
        productos = pd.read_excel(ruta_archivo)
        print("DataFrame creado exitosamente.")
        return productos
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta especificada: {ruta_archivo}")
        return None
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo Excel: {e}")
        return None

# Creación de dataframes a partir de archivos Excel
productos = crear_dataframe(r'/mnt/windows_share/CPV/Códigos por Ciclo_2025CPV_2406.xlsx')
metas_cpv = crear_dataframe(r"/mnt/windows_share/CPV/Metas_CPV.xlsx")
metas_rb = crear_dataframe(r"/mnt/windows_share/CPV/Meta_Receta_Bruta.xlsx")

# Renombrar columnas de una sola vez
productos.rename(columns={
    'Ciclo': 'ciclo',
    'CV': 'cv',
    'Nombre': 'producto'
}, inplace=True)

# Ajustar tipos de datos
# Usamos .loc para asegurar que la asignación es robusta y explícita
productos['ciclo'] = productos['ciclo'].astype('Int64')
productos['cv'] = productos['cv'].astype('Int64') # 'Int64' permite valores nulos (NaN)
productos['producto'] = productos['producto'].astype(str)

# Renombrar columnas de una sola vez
metas_rb.rename(columns={
    'CICLO': 'ciclo',
    'RB\n$ML META': 'meta_rb' # Asegúrate que este nombre de columna sea exacto
}, inplace=True)

# Ajustar tipos de datos
metas_rb['ciclo'] = metas_rb['ciclo'].astype('Int64')
metas_rb['meta_rb'] = metas_rb['meta_rb'].astype('Float64') # 'Int64' permite valores nulos (NaN)

# Renombrar columnas de una sola vez
metas_cpv.rename(columns={
    'Ciclo': 'ciclo',
    'Meta_Ajustada_Modelo_Comerciales_FV': 'meta_cpv'
}, inplace=True)

# Ajustar tipos de datos
metas_cpv['ciclo'] = metas_cpv['ciclo'].astype('Int64')
metas_cpv['meta_cpv'] = metas_cpv['meta_cpv'].astype('Float64') # 'Float64' permite valores nulos (NaN)

def insertar_df_sql(
    df: pd.DataFrame,
    database_name: str,
    schema_name: str,
    table_name: str,
    server_address: str = "10.156.16.46\\SQL2022",
    driver_name: str = "ODBC Driver 17 for SQL Server",
    username_sql: str = None, # Puedes pasarlo como parámetro o cargarlo de forma segura
    password_sql: str = None, # Puedes pasarlo como parámetro o cargarlo de forma segura
    if_exists_option: str = 'append',
    chunk_size: int = 1000 # Un chunksize más grande suele ser más eficiente
) -> None:
    """
    Inserta un DataFrame de pandas en una tabla de SQL Server.

    Args:
        df (pd.DataFrame): El DataFrame a insertar.
        database_name (str): El nombre de la base de datos (ej. "CustomerCare").
        schema_name (str): El nombre del esquema (ej. "customer_care").
        table_name (str): El nombre de la tabla (ej. "reclamos").
        server_address (str): Dirección del servidor SQL Server (por defecto "10.156.16.46\\SQL2022").
        driver_name (str): Nombre del driver ODBC (por defecto "ODBC Driver 17 for SQL Server").
        username_sql (str, optional): Nombre de usuario para la conexión SQL. Si no se provee,
                                      la función buscará en variables de entorno o usará autenticación integrada.
        password_sql (str, optional): Contraseña para la conexión SQL.
        if_exists_option (str): Cómo manejar la tabla si ya existe ('fail', 'replace', 'append').
                                Por defecto 'append'.
        chunk_size (int): Número de filas a escribir por lote. Por defecto 1000.
    """
    # --- Configuración de autenticación (ejemplo) ---
    # Construcción de la URL de conexión
    connection_url = URL.create(
        "mssql+pyodbc",
        username=username_sql, # Podría ser None si usas autenticación integrada o variables de entorno
        password=password_sql, # Podría ser None
        host=server_address,
        database=database_name,
        query={
            "driver": driver_name,
            #"TrustServerCertificate": "yes", # Es común necesitar esto si no tienes certificados configurados
            # "authentication": "ActiveDirectoryIntegrated", # Descomenta si usas esta autenticación
        },
    )

    try:
        # Crear el motor de conexión
        engine = create_engine(connection_url)

        with engine.begin() as connection:
            start_time = time.time()
            df.to_sql(
                name=table_name,
                schema=schema_name,
                con=connection,
                method='multi',
                chunksize=chunk_size,
                if_exists=if_exists_option,
                index=False, # Generalmente no queremos el índice de pandas como columna en SQL
            )
            elapsed_time = time.time() - start_time
            print(f"{len(df)} Datos insertados en '{database_name}.{schema_name}.{table_name}' exitosamente en {elapsed_time:.2f} segundos.")

    except Exception as e:
        print(f"Error al insertar datos en la base de datos: {e}")

# Insertar tabla productos
insertar_df_sql(
        df=productos,
        database_name="Marketing",
        schema_name="cpv",
        table_name="productos", # Usa un nombre de tabla temporal para pruebas
        username_sql=username_sql,
        password_sql=password_sql,
        if_exists_option='replace' # 'replace' para crearla de cero cada vez en pruebas
    )

# Insertar tabla meta_rb
insertar_df_sql(
        df=metas_rb,
        database_name="Marketing",
        schema_name="cpv",
        table_name="meta_rb", # Usa un nombre de tabla temporal para pruebas
        username_sql=username_sql,
        password_sql=password_sql,
        if_exists_option='replace' # 'replace' para crearla de cero cada vez en pruebas
    )

# Insertar tabla meta_cpv
insertar_df_sql(
        df=metas_cpv,
        database_name="Marketing",
        schema_name="cpv",
        table_name="meta_cpv", # Usa un nombre de tabla temporal para pruebas
        username_sql=username_sql,
        password_sql=password_sql,
        if_exists_option='replace' # 'replace' para crearla de cero cada vez en pruebas
    )