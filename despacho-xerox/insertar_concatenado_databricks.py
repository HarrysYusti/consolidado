import os
import sys
import pandas as pd
from datetime import datetime
import shutil
import gc
import numpy as np 

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
path_concatenado = r"/mnt/windows_share/Customer_Care/Despacho Xerox/Concatenado/"
path_concatenado_old = r"/mnt/windows_share/Customer_Care/Despacho Xerox/Concatenado/Old/"

os.makedirs(path_concatenado_old, exist_ok=True)
# --- Fin Rutas ---

# Lectura de archivo concatenado
xlsx_files = [f for f in os.listdir(path_concatenado) if f.endswith('.xlsx')]

if not xlsx_files:
    raise FileNotFoundError(f"Error: No se encontró ningún archivo .xlsx en la carpeta: {path_concatenado}. Asegúrate de que el DAG de concatenación haya generado el archivo.")
    
if len(xlsx_files) > 1:
    raise Exception(f"Error: Se encontraron múltiples archivos .xlsx en la carpeta: {path_concatenado}. Se esperaba solo uno. Archivos encontrados: {', '.join(xlsx_files)}")

nombre_archivo_concatenado = xlsx_files[0]
ruta_completa_archivo_concatenado = os.path.join(path_concatenado, nombre_archivo_concatenado)

print(f"Leyendo archivo: {ruta_completa_archivo_concatenado}")

try:
    detalle_df = pd.read_excel(ruta_completa_archivo_concatenado)
    if detalle_df.empty:
        raise ValueError(f"El archivo Excel '{nombre_archivo_concatenado}' está vacío. No hay datos para procesar.")
    print(f"Archivo leído exitosamente. {len(detalle_df)} filas.")
    # Optimizar memoria de detalle_df
    #detalle_df = optimize_dataframe_memory(detalle_df)
except Exception as e:
    raise Exception(f"Error al leer el archivo Excel '{ruta_completa_archivo_concatenado}': {e}")

# Ajuste de la columna 'ID_Producto'
# Paso 1: Convertir la columna 'ID_Producto' a tipo string
# Esto es crucial para manejar valores como 2000001036512.0 y usar métodos de string.
detalle_df['ID_Producto'] = detalle_df['ID_Producto'].astype(str)

# Paso 2: Remover el '.0' si existe
# Limpiamos el string antes de aplicar la lógica principal de los '00'.
detalle_df['ID_Producto'] = detalle_df['ID_Producto'].apply(
    lambda x: x.replace('.0', '') if x.endswith('.0') else x
)

# Paso 3: Definir la longitud mínima para los ID_Producto "grandes"
# Ajusta este valor según la longitud real de tus IDs que no deben ser modificados.
# Por ejemplo, '2000001036512' tiene 13 caracteres. Un ID "pequeño" como '607766700' tiene 9.
longitud_minima_id_grande = 10 # Si un ID tiene 10 o más caracteres, se considera "grande".

# Paso 4: Remover los últimos '00' si el ID no es "grande"
# La condición ahora es explícitamente que termine en '00'.
detalle_df['ID_Producto'] = detalle_df['ID_Producto'].apply(
    lambda x: x[:-2] if x.endswith('00') and len(x) < longitud_minima_id_grande else x
)

# Ejecución de queries de LEGO y merge
# 3. Obtener el código consultor y el correo registrado en LEGO (df_query)
print("Ejecutando Query 1 en Databricks para obtener datos de LEGO...")
query_lego = """
        SELECT o.order_number AS numero_pedido, o.order_cycle AS ciclo_pedido, o.person_id AS id_consultor, pace.candidate_id AS codigo_consultor , pace.full_name AS nombre_consultor, UPPER(pace.email_address) AS email_lego, pace.country_code AS codigo_pais, pace.area_code AS codigo_area, pace.number AS telefono
        FROM platform.gdp_gsp_orders_order_replica.order o
        LEFT JOIN (
            SELECT DISTINCT p.person_id, p.full_name, ac.candidate_id, e.email_address, t.country_code, t.area_code, t.number
            FROM platform.gdp_gpp_cadwf_people_replica.person p
            LEFT JOIN platform.gdp_gpp_cadwf_people_replica.approved_candidate ac
                ON p.person_id = ac.person_id
            LEFT JOIN platform.gdp_gpp_cadwf_people_replica.email e
                ON p.person_id = e.person_id
            LEFT JOIN platform.gdp_gpp_cadwf_people_replica.telephone t
                ON p.person_id = t.person_id
            WHERE p.country_id = 4 AND ac.type_id = 0) pace
            ON o.person_id = pace.person_id
        WHERE o.country_code = 'CL' AND o.order_date >= '2025-06-01'
        UNION ALL
        SELECT pe.NM_PEDIDO_EXTERNO AS numero_pedido, pe.NM_CICLO_CAPTACAO as ciclo_pedido, c.person_id AS id_consultor, pe.CD_REVENDEDOR AS codigo_consultor, p.full_name AS nombre_consultor, UPPER(e.email_address) AS email_lego, t.country_code AS codigo_pais, t.area_code AS codigo_area, t.number AS telefono
        FROM platform.dw_o01dw_sisdmi_replica.t_prj_2go_f_pedido pe
        LEFT JOIN platform.gdp_gpp_cadwf_people_replica.approved_candidate c
            ON pe.CD_REVENDEDOR = c.candidate_id
        LEFT JOIN platform.gdp_gpp_cadwf_people_replica.person p
            ON c.person_id = p.person_id
        LEFT JOIN platform.gdp_gpp_cadwf_people_replica.email e
            ON c.person_id = e.person_id
        LEFT JOIN platform.gdp_gpp_cadwf_people_replica.telephone t
            ON c.person_id = t.person_id
        WHERE pe.CD_PAIS = 2 AND c.type_id = 0 AND pe.DT_CAPTACAO >= '2025-06-01'
    """
df_lego = dataabricks_cli.get_df(query_lego)
print(f"Query 1 ejecutada. {len(df_lego)} filas obtenidas.")
    # Optimizar memoria de df_lego
    #df_lego = optimize_dataframe_memory(df_lego)

    # Asegurar tipos compatibles para el merge
    # Si ID_Producto de detalle_df es string, numero_pedido de df_lego también debe serlo
if str(detalle_df['ID_Producto'].dtype) == 'object':
    df_lego['numero_pedido'] = df_lego['numero_pedido'].astype(str)
else: # Si ID_Producto es Int64
    df_lego['numero_pedido'] = pd.to_numeric(df_lego['numero_pedido'], errors='coerce').astype('Int64')

lego_df = pd.merge(detalle_df, df_lego, 
                       left_on='ID_Producto', right_on='numero_pedido', 
                       how='left')
print(f"Merge con datos de LEGO completado. {len(lego_df)} filas.")

    # 4. Obtener datos de consultoras desde Databricks (query2)
print("Ejecutando Query 2 en Databricks para obtener datos de consultores...")
query_consultant_index = """
    SELECT sales_management_code, sales_management_name, sector_code, sector_name, 
           leader_code, leader_name, group_code, person_code, operational_cycle
    FROM product.elo_modelo_combinado.commercial_consultant_index
    WHERE country = 'CL'
    """
df_consultants = dataabricks_cli.get_df(query_consultant_index)
print(f"Query 2 ejecutada. {len(df_consultants)} filas obtenidas.")
    # Optimizar memoria de df_consultants
    #df_consultants = optimize_dataframe_memory(df_consultants)

   # Asegurar tipos compatibles para el merge
lego_df['codigo_consultor'] = lego_df['codigo_consultor'].astype(str)
df_consultants['person_code'] = df_consultants['person_code'].astype(str)
lego_df['ciclo_pedido'] = lego_df['ciclo_pedido'].astype(str)
df_consultants['operational_cycle'] = df_consultants['operational_cycle'].astype(str)
    
final_df_processed = pd.merge(lego_df, df_consultants,
                                  left_on=['codigo_consultor', 'ciclo_pedido'],
                                  right_on=['person_code', 'operational_cycle'],
                                  how='left')
print(f"Merge con datos de consultores completado. {len(final_df_processed)} filas.")

# Modificaciones en campos del dataframe resultante
final_df_processed = final_df_processed.rename(columns={
        #'ID_Producto': 'numero_pedido',
        'Pers3': 'rut',
        'Address': 'email_envio_xerox',
        'TipoError': 'Tipo_Error',
        'Descripcion': 'Descripción'
    })

# 5. Seleccionar campos relevantes y renombrar
columnas_finales = [
        'numero_pedido',
        'ciclo_pedido',
        'codigo_consultor',
        'nombre_consultor',
        'codigo_pais',
        'codigo_area',
        'telefono',
        'rut',
        'codigo_gerencia',
        'nombre_gerencia',
        'codigo_sector',
        'nombre_sector',
        'codigo_lider',
        'nombre_lider',
        'codigo_grupo',
        'email_envio_xerox',
        'email_lego',
        'Estatus',
        'Reason',
        'Tipo_Error',
        'Descripción',
        'Created',
        'Opened'
    ]

# Crear un diccionario de mapeo para renombrar las columnas
# La clave es el nombre nuevo (el de columnas_finales), el valor es el nombre original
mapeo_columnas = {
    'codigo_gerencia': 'sales_management_code',
    'nombre_gerencia': 'sales_management_name',
    'codigo_sector': 'sector_code',
    'nombre_sector': 'sector_name',
    'codigo_lider': 'leader_code',
    'nombre_lider': 'leader_name',
    'codigo_grupo': 'group_code'
}

# Invertir el mapeo para usarlo con .rename()
# .rename() toma {nombre_original: nombre_nuevo}
rename_dict = {v: k for k, v in mapeo_columnas.items()}

# Renombrar las columnas en una copia del DataFrame para evitar SettingWithCopyWarning
# y asegurar que el DataFrame original no se modifica si no es deseado
final_df_renamed = final_df_processed.rename(columns=rename_dict)

# Si 'Reason' no existe, añadirla con valores por defecto
if 'Reason' not in final_df_renamed.columns:
    final_df_renamed['Reason'] = None # O puedes usar '' o pd.NA según tu preferencia

# Seleccionar las columnas en el orden especificado por columnas_finales
# Esto también manejará la columna 'Reason' si la acabamos de añadir
final_df_filtered = final_df_renamed[columnas_finales]

# 6. Columnas que deben ser STRING sin '.0'
cols_to_clean_string = ['codigo_pais', 'codigo_area']
for col in cols_to_clean_string:
    # Convertir a string, luego usar regex para eliminar '.0' al final
    # .astype(str) es crucial para manejar NaNs sin errores antes del replace
    final_df_filtered[col] = final_df_filtered[col].astype(str).str.replace(r'\.0$', '', regex=True)

# 7. Columnas que deben ser NÚMERO (entero) sin '.0'
cols_to_clean_int = ['codigo_gerencia', 'codigo_sector', 'codigo_lider', 'codigo_grupo']
for col in cols_to_clean_int:
    # Para manejar NaNs, primero convertimos a un tipo numérico flotante
    # y luego a Int64 (el tipo de entero de Pandas que maneja NaNs)
    # Esto asegura que 1.0 se convierte a 1 y NaN sigue siendo NaN
    final_df_filtered[col] = pd.to_numeric(final_df_filtered[col], errors='coerce') \
                               .astype('Int64') # Int64 puede manejar valores nulos
    
# 8. Transformaciones adicionales (manteniendo tipos como están definidos para DB)
for col_to_upper in ['email_envio_xerox', 'nombre_consultor', 'nombre_lider']:
    if col_to_upper in final_df_filtered.columns:
            # Solo convertir a string si no lo es ya, y luego a mayúsculas
        final_df_filtered[col_to_upper] = final_df_filtered[col_to_upper].astype(str).str.upper()

for col_to_str in ['codigo_pais', 'codigo_area', 'telefono']:
    if col_to_str in final_df_filtered.columns:
            # Asegurar que se convierte a string para coincidir con DB si es necesario
        final_df_filtered[col_to_str] = final_df_filtered[col_to_str].astype(str)

# 9. Incorporar la fecha de ingesta de los datos
final_df_filtered['time_ingest'] = datetime.now()

# 10. Eliminar duplicados
original_rows = len(final_df_filtered)
final_df_filtered.drop_duplicates(inplace=True)
print(f"Duplicados eliminados. {original_rows - len(final_df_filtered)} filas duplicadas removidas. Total: {len(final_df_filtered)} filas.")

# 11. Iterar sobre cada columna para manejar los nulos
for col in final_df_filtered.columns:
    dtype = final_df_filtered[col].dtype
    
    # Manejar nulos para tipos numéricos (float, int, etc.)
    if pd.api.types.is_numeric_dtype(dtype):
        # Convertir a numérico, transformando 'nan' strings o no-números a np.nan.
        final_df_filtered[col] = pd.to_numeric(final_df_filtered[col], errors='coerce')

    # Manejar nulos para tipos de texto (object o string)
    elif pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
        # Primero, reemplaza la cadena literal 'nan' por el nulo de NumPy (np.nan)
        final_df_filtered[col] = final_df_filtered[col].replace('nan', np.nan)
        
        # Ahora, maneja el objeto Python 'None'.
        # Es más seguro usar .fillna() para convertir None/NaN a np.nan en object dtypes
        # o usar .apply(lambda x: np.nan if x is None else x)
        final_df_filtered[col] = final_df_filtered[col].apply(lambda x: np.nan if x is None else x)

    # Manejar nulos para tipos de fecha y hora
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        # Asegurarse de que los valores sean datetime y que los no válidos sean NaT.
        final_df_filtered[col] = pd.to_datetime(final_df_filtered[col], errors='coerce')

# 12. Eliminar codigo_consultor = null (no identificables)
final_df_filtered.dropna(subset=['codigo_consultor'], inplace=True)

# 13. Insertar en databricks  CAMBIAR TABLA DESTINO
if not final_df_filtered.empty:
        print(f"Insertando {len(final_df_filtered)} filas en Databricks (sandbox.td_sql_chile.envio_correos_xerox)...")
        try:
            dataabricks_cli.insert_dataframe(final_df_filtered, "sandbox.td_sql_chile.envio_correos_xerox_test")
            print("Datos insertados exitosamente en Databricks.")
        except Exception as e:
            print(f"Error crítico en el script y los datos no fueron insertados en Databricks: {e}")
            raise # Relaunch the exception for Airflow to catch
else:
        print("DataFrame final vacío. No se insertaron datos en Databricks.")
        # Si un DataFrame vacío al final no debería insertarse, pero tampoco es un error del script, 
        # puedes mantener este mensaje y no lanzar excepción.
        # Si un DataFrame vacío significa que algo está mal y el DAG debe fallar:
        # raise ValueError("DataFrame final vacío. No se insertaron datos en Databricks.")

# 14. Mover el archivo Concatenado.xlsx a la carpeta 'Old' después de la inserción exitosa
destino_archivo_old = os.path.join(path_concatenado_old, nombre_archivo_concatenado)
try:
    shutil.move(ruta_completa_archivo_concatenado, destino_archivo_old)
    print(f"Archivo '{nombre_archivo_concatenado}' movido exitosamente a '{path_concatenado_old}'.")
except Exception as e:
    print(f"Advertencia: No se pudo mover el archivo '{nombre_archivo_concatenado}' a '{path_concatenado_old}'. Error: {e}")