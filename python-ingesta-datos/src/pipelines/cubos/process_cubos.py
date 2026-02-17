import os
import pandas as pd
import pendulum
import pymssql
import re
import shutil
import time
import yaml
from configuration import setup_logging
from datetime import datetime, UTC
from pathlib import Path
from resources.databricks_db import DatabricksClient
from resources.mssql_db import MSSQLClient

def load_config(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return yaml.safe_load(f)

current_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG = load_config(Path(current_dir) / 'config.yaml')

logger = setup_logging(CONFIG['etl']['logging_level'])

def get_mssql_cli():
    return MSSQLClient(
        server=CONFIG['mssql_params']['server'],
        username=CONFIG['mssql_params']['username'],
        password=CONFIG['mssql_params']['password'],
        database=CONFIG['mssql_params']['database'],
    )


def get_databricks_cli():
    return DatabricksClient(
        host=CONFIG['databricks_params']['host'],
        http_path=CONFIG['databricks_params']['http_path'],
        api_key=CONFIG['databricks_params']['api_key'],
    )


def databricks_process(cube_type: str):
    logger.info(f"Starting process for cube_type: {cube_type}")

    mssql_table = CONFIG['mssql_tables'][cube_type]
    databricks_table = CONFIG['databricks_tables'][cube_type]
    codigo_col = CONFIG['codigo_column'][cube_type]

    query = f"""
    select *
    FROM (
        select *,
            ROW_NUMBER() OVER (PARTITION BY Ciclo, [{codigo_col}] ORDER BY [Archivo Fecha Hora] DESC) AS rn
        FROM [AnalisisComercialCL].{mssql_table}
    ) t
    where rn = 1
    """
    mssql_cli = get_mssql_cli()
    try:
        logger.info(f"Fetching MSSQL table: {mssql_table}")
        df_mssql = mssql_cli.query_to_df(query)
    except Exception as e:
        logger.error(f"Error fetching MSSQL data: {e}")
        return

    # Rename because databrics have issues in the columns' names:
    df_mssql = df_mssql.rename(columns={
        'Items Total Unidad Avon Meta': 'Items Total\xa0Unidad Avon Meta',
        'Items Total Unidad Avon Real': 'Items Total\xa0Unidad Avon Real'
    })

    # Remove unused columns
    for x in ['id', 'rn']:
        if x in df_mssql.columns:
            del df_mssql[x]

    dataabricks_cli = get_databricks_cli()

    try:
        logger.info(f"Removing all rows in table: {databricks_table}")
        dataabricks_cli.execute_ddl(f"delete from {databricks_table}")
    except Exception as e:
        logger.error(f"Error removing Databricks data: {e}")
        return

    try:
        logger.info(f"Inserting new rows in table: {databricks_table}")
        dataabricks_cli.insert_dataframe(df_mssql, databricks_table)
    except Exception as e:
        logger.error(f"Error inserting Databricks data: {e}")
        return


def get_metadata_from_csv_path(csv_path: Path) -> dict:
    _, type_cube, date_str, hour, minute = csv_path.stem.split('_')
    return {
        'type_cube': type_cube.lower(),
        'year': int(date_str[4:]),
        'month': int(date_str[2:4]),
        'day': int(date_str[0:2]),
        'hour': int(hour),
        'minute': int(minute),
    }

def get_data_ts(csv_path: Path) -> str:
    metadata = get_metadata_from_csv_path(csv_path)
    dt = datetime(**{k: metadata[k] for k in ('year', 'month', 'day', 'hour', 'minute')})
    return dt.isoformat()

def get_dataframe_from_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, sep=';')
    if df.empty:
        raise ValueError('DataFrame from CSV is empty')

    df['Archivo Fuente'] = csv_path.name
    df['Archivo Fecha Hora'] = get_data_ts(csv_path)
    df['Insertado Fecha Hora'] = datetime.now(UTC).isoformat()

    df.rename(columns={
        'Items Total\xa0Unidad Avon Meta':'Items Total Unidad Avon Meta' ,
        'Items Total\xa0Unidad Avon Real':'Items Total Unidad Avon Real'
    }, inplace=True)

    return df

def upload_df_to_mssql(df: pd.DataFrame, type_cube: str, source_filename: str):
    mssql_cli = get_mssql_cli()
    table_name = CONFIG['mssql_tables'][type_cube]

    try:
        mssql_cli.exec(f"DELETE FROM {table_name} WHERE [Archivo Fuente] = '{source_filename}'")
    except pymssql.DatabaseError:
        logger.error(f"Failed when deleting rows from file `{source_filename}`", exc_info=True)
        raise

    try:
        columns = ', '.join(f"[{col}]" for col in df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        data = list(df.itertuples(index=False, name=None))

        mssql_cli.insert_into_table(insert_sql=insert_sql, data=data)

    except pymssql.DatabaseError as e:
        logger.error(f"Failed when inserting into {table_name}", exc_info=True)
        raise e
    

def move_csv_to_processed(csv_path: Path) -> None:
    metadata = get_metadata_from_csv_path(csv_path)
    target_dir = Path(CONFIG['files']['processed_root_dir']) / f"{metadata['year']}" / f"{metadata['month']:02d}" / f"{metadata['day']:02d}"
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(csv_path, target_dir / csv_path.name)


def is_valid_csv_name(filename: str | Path) -> bool:
    return bool(re.match(r'^CUBO_(GRUPO|SECTOR)_\d{8}_\d{2}_\d{2}\.csv$', str(filename)))


def process_csv_file(csv_path: Path) -> bool:
    logger.info(f"Processing file: {csv_path}")

    try:
        # Read and validate CSV
        try:
            df = get_dataframe_from_csv(csv_path)
            logger.debug(f"DataFrame shape: {df.shape}")
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")

        # Metadata extraction
        metadata = get_metadata_from_csv_path(csv_path)

        # Upload
        upload_df_to_mssql(df, metadata['type_cube'], csv_path.name)

        return True

    except (ValueError, KeyError, pymssql.DatabaseError) as e:
        logger.exception(f"Upload failed for {csv_path.name}")
        return False


def try_csv_upload_and_move(csv_path : Path) -> bool:
    inserted = process_csv_file(csv_path)
    if inserted:
        try:
            move_csv_to_processed(csv_path)
        except Exception as move_err:
            logger.warning(f"Moving file failed: {csv_path.name} — {move_err}")
        else:
            logger.info(f"File moved: {csv_path.name}")
    return inserted


def mssql_process(throttle_seconds: float = 1.0) -> int:
    files_inserted = 0

    for csv_path in Path(CONFIG['files']['source_root_dir']).iterdir():
        if not csv_path.is_file() or not is_valid_csv_name(csv_path.name):
            continue

        inserted = try_csv_upload_and_move(csv_path)
        if inserted:
            files_inserted += 1

        time.sleep(throttle_seconds)

    logger.info(f"Total files inserted: {files_inserted}")
    return files_inserted


def execute_task(force : bool = False):
    try:
        logger.info(f"Task execution started!")

        files_inserted = mssql_process()

        if files_inserted or force:
            databricks_process("sector")
            databricks_process("grupo")
    except Exception as e:
        logger.error(f"Process failed: {e}")

def get_next_execution():
    now = pendulum.now()
    scheduled_minute = CONFIG['etl']['scheduled_minute']

    if now.minute < scheduled_minute:
        next_time = now.set(minute=scheduled_minute, second=0)
    else:
        next_time = now.add(hours=1).set(minute=scheduled_minute, second=0)
    return next_time

def cubos_main():
    while True:
        execute_task()

        next_run = get_next_execution()
        seconds_until_next = (next_run - pendulum.now()).total_seconds()
        logger.info(f"Next execution at: {next_run.to_datetime_string()} (in {int(seconds_until_next)} seconds)")
        
        time.sleep(seconds_until_next)

