import os
import pandas as pd
import pendulum
import pymssql
import time
import yaml
from datetime import datetime
from pathlib import Path
from contextlib import closing
from configuration import setup_logging
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

def get_formatted_value(value, column) -> str:
    if value is None or pd.isna(value):
        return 'NULL'
    elif column in ['management_id','sector_id', 'group_id', 'leader',
                    'cn_code', 'month', 'year', 'p_digital', 'ingreso_mn',
                    'mixed', 'impersonation', 'magazine', 'status']:
        return str(int(value))
    else:
        return f"'{str(value).replace("'", "''")}'"

def split_into_batches_by_size(data, batch_size):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def insert_into_table(insert_statements):
    mssql_cli = get_mssql_cli()
    conn = mssql_cli._ensure_conn()
    try:
        with closing(conn.cursor()) as cursor:
            for stmt in insert_statements:
                cursor.execute(stmt)
            conn.commit()
    except pymssql.DatabaseError as e:
        conn.rollback()
        logger.error("Error inserting data", exc_info=True)
        raise
    finally:
        conn.close()

def fill_management(df: pd.DataFrame, databricks_cli: DatabricksClient) -> pd.DataFrame:
    management_df = databricks_cli.get_df("""
    SELECT
        sales_management_code as management_id,
        sales_management_name as management_name
    FROM (
        SELECT
        sales_management_code,
        sales_management_name,
        ROW_NUMBER() OVER (
            PARTITION BY sales_management_code
            ORDER BY order_date DESC
        ) AS rn
        FROM product.elo_modelo_combinado.commercial_orders_index
        WHERE country_code = 152
        AND DATE(order_date) >= '2024-01-01'
        AND sales_management_code is not null
        AND sales_management_name is not null
    ) t
    WHERE rn = 1
    """)

    management_dict = dict(zip(management_df['management_id'], management_df['management_name']))

    df['management_name'] = df.apply(
        lambda row: management_dict.get(row['management_id'], row['management_name']) 
        if pd.isna(row['management_name']) or row['management_name'] == '' 
        else row['management_name'], 
        axis=1
    )

    return df

def fill_sector(df: pd.DataFrame, databricks_cli: DatabricksClient) -> pd.DataFrame:
    sector_df = databricks_cli.get_df("""
    SELECT 
        sales_management_code as management_id,
        sector_code as sector_id,
        sector_name as sector_name
    FROM (
        SELECT
        sales_management_code,
        sector_code,
        sector_name,
        ROW_NUMBER() OVER (
            PARTITION BY sector_code
            ORDER BY order_date DESC
        ) AS rn
        FROM product.elo_modelo_combinado.commercial_orders_index
        WHERE country_code = 152
        AND DATE(order_date) >= '2024-01-01'
        AND sales_management_code is not null
        AND sector_code is not null
        AND sector_name is not null
    ) t
    WHERE rn = 1
    """)

    def get_sector_name(row):
        if pd.isna(row['sector_name']) or row['sector_name'] is None:
            filtered_df = sector_df[(sector_df['sector_id'] == row['sector_id']) & (sector_df['management_id'] == row['management_id'])]

            if filtered_df.empty:
                filtered_df = sector_df[sector_df['sector_id'] == row['sector_id']]
                
            if filtered_df.empty:
                return row['sector_name']
            
            return filtered_df['sector_name'].iloc[0]
        return row['sector_name']

    df['sector_name'] = df.apply(get_sector_name, axis=1)

    return df 


def get_databricks_df():
    logger.info("Connecting to Databricks")
    databricks_cli = get_databricks_cli()

    with open(Path(__file__).parent / CONFIG['queries']['detalle_cn'], 'r') as f:
        query = f.read()

    logger.info("Getting dataframe from databricks")

    logger.info("cleaning dataframe")
    df = databricks_cli.get_df(query=query)
    df['status'] = 1
    df['origen'] = 'origen'

    if 'leader_code' in df.columns:
        df = df.rename(columns={'leader_code': 'leader'})

    df['leader'] = df['leader'].apply(lambda x: str(int(x)) if pd.notnull(x) else None)

    df = df[~df['management_id'].isna()]
    df = df[~df['sector_id'].isna()]

    df = fill_management(df, databricks_cli)
    df = fill_sector(df, databricks_cli)


    target_columns = ['management_id', 'management_name', 'sector_id', 'sector_name',
                      'group_id', 'leader', 'color', 'cn_code', 'cn_name', 'month',
                      'year', 'p_digital', 'ingreso_mn', 'mixed', 'impersonation', 'magazine',
                      'origen', 'status']
    df = df[target_columns]

    return df

def execute_deltas():
    try:
        logger.info("Executing delta queries")
        mssql_cli = get_mssql_cli()
        delta_queries = CONFIG['queries'].get('deltas', {})

        for name, path in delta_queries.items():
            try:
                logger.info(f"Executing delta: {name}")
                with open(Path(__file__).parent / path, 'r') as f:
                    query = f.read()
                mssql_cli.exec(query)
            except Exception as e2:
                logger.error(f"Error executing delta {name}: {e2}", exc_info=True)
    except Exception as e:
        logger.error(f"Process failed: {e}", exc_info=True)

    logger.info("Deltas finished")

def execute_task():
    try:
        logger.info("Task execution started")
        df = get_databricks_df()
        mssql_cli = get_mssql_cli()

        logger.info("Merging data and getting new rows")
        mssql_df = mssql_cli.query_to_df(f"select {','.join(df.columns)} from [panel_digital].[detalle_cn]")
        mssql_df['status'] = mssql_df['status'].fillna(0).infer_objects().astype(int)

        common_columns = list(set(df.columns) & set(mssql_df.columns))
        df = df[common_columns]
        mssql_df = mssql_df[common_columns]

        delta_df = df.merge(
            mssql_df.drop_duplicates(),
            on=common_columns,
            how='left',
            indicator=True
        )

        only_in_databricks = delta_df[delta_df['_merge'] == 'left_only'].drop(columns=['_merge'])

        table_name = CONFIG['mssql_tables']['panel_digital']
        columns = ', '.join(f"[{col}]" for col in only_in_databricks.columns)
        script = []

        for _, row in only_in_databricks.iterrows():
            values = ','.join([get_formatted_value(row[col], col) for col in only_in_databricks.columns])
            stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
            script.append(stmt)

        batch_size = 1000
        for i, batch in enumerate(split_into_batches_by_size(script, batch_size), start=1):
            logger.info(f"Inserting {len(batch)} rows for batch {i}")
            insert_into_table(batch)

    except Exception as e:
        logger.error(f"Process failed: {e}", exc_info=True)

    logger.info("Task finished")

def get_next_execution():
    now = pendulum.now()
    scheduled_hour = CONFIG['etl']['scheduled_hour']
    scheduled_minute = CONFIG['etl']['scheduled_minute']

    if now.hour < scheduled_hour or (now.hour == scheduled_hour and now.minute < scheduled_minute):
        next_time = now.set(hour=scheduled_hour, minute=scheduled_minute, second=0)
    else:
        next_time = now.add(days=1).set(hour=scheduled_hour, minute=scheduled_minute, second=0)
    return next_time

def panel_digital_main():
    while True:
        execute_task()
        execute_deltas()
        next_run = get_next_execution()
        seconds_until_next = (next_run - pendulum.now()).total_seconds()
        logger.info(f"Next execution at: {next_run.to_datetime_string()} (in {int(seconds_until_next)} seconds)")
        time.sleep(seconds_until_next)

if __name__ == '__main__':
    panel_digital_main()
