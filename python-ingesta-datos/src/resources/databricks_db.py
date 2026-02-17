import pandas as pd
from databricks import sql
from . import logger

class DatabricksClient:
    def __init__(self, host: str, http_path: str, api_key: str):
        """
        Initialize the Databricks client with necessary parameters.

        :param host: Databricks server hostname (e.g. 'my-databricks-instance')
        :param http_path: HTTP path for the Databricks cluster (e.g. '/sql/1.0/warehouses/...')
        :param api_key: Databricks API key (personal access token)
        """
        self.server_hostname = host
        self.http_path = http_path
        self.access_token = api_key

    def _connect(self):
        """Establishes a connection to the Databricks instance."""
        return sql.connect(
            server_hostname=self.server_hostname,
            http_path=self.http_path,
            access_token=self.access_token
        )

    def get_df(self, query: str) -> pd.DataFrame:
        """Executes a SQL query and returns the result as a DataFrame."""
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return pd.DataFrame(rows, columns=columns)

    def execute_ddl(self, ddl: str):
        """Executes a DDL statement on Databricks."""
        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(ddl)
                    logger.info(f"DDL executed successfully: {ddl}")
        except Exception as e:
            logger.error(f"Failed when executing DDL: {ddl}", exc_info=True)
            raise

    def insert_dataframe(self, df: pd.DataFrame, table_name: str, batch_size: int = 50):
        """Inserts a DataFrame into a Databricks table in batches."""
        if df.empty:
            logger.info(f"No data to insert into {table_name}. DataFrame is empty.")
            return

        # Convert datetimes to ISO format
        df = df.copy()
        for col in df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

        columns = df.columns.tolist()
        col_names = ", ".join(f"`{col}`" for col in columns)

        def sql_literal(value):
            if pd.isna(value):
                return "NULL"
            if isinstance(value, str):
                return f"'{value.replace('\'', '\'\'')}'"
            return f"{value}"

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    for i in range(0, len(df), batch_size):
                        batch = df.iloc[i:i + batch_size]
                        values_sql = ",\n".join([
                            f"({', '.join([sql_literal(val) for val in row])})"
                            for row in batch.itertuples(index=False, name=None)
                        ])
                        insert_sql = f"INSERT INTO {table_name} ({col_names}) VALUES \n{values_sql}"
                        cursor.execute(insert_sql)
                logger.info(f"Inserted {len(df)} rows into {table_name}")
        except Exception as e:
            logger.error(f"Failed when inserting DataFrame into {table_name}", exc_info=True)
            raise

    def delete_keys(self, table_name: str, key_cols: list, keys_df: pd.DataFrame, batch_size: int = 1000):
        """Deletes rows from a Databricks table based on keys in the provided DataFrame."""
        if keys_df.empty:
            logger.info(f"No keys to delete from {table_name}. DataFrame is empty.")
            return

        # Validate that all necessary columns are present
        missing_cols = [col for col in key_cols if col not in keys_df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns in keys_df required for deletion: {missing_cols}")

        # Convert datetime keys to string if necessary
        keys_df = keys_df.copy()
        for col in keys_df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns:
            keys_df[col] = keys_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

        def format_condition(row):
            conditions = []
            for col, val in zip(key_cols, row):
                if pd.isna(val):
                    conditions.append(f"`{col}` IS NULL")
                elif isinstance(val, str):
                    val = val.replace("'", "''")
                    conditions.append(f"`{col}` = '{val}'")
                else:
                    conditions.append(f"`{col}` = {val}")
            return "(" + " AND ".join(conditions) + ")"

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    for i in range(0, len(keys_df), batch_size):
                        batch = keys_df.iloc[i:i + batch_size]
                        where_clauses = " OR ".join(batch.apply(format_condition, axis=1))
                        delete_sql = f"DELETE FROM {table_name} WHERE {where_clauses}"
                        cursor.execute(delete_sql)
                        logger.info(f"Deleted {len(batch)} rows from {table_name}")
        except Exception as e:
            logger.error(f"Failed when deleting keys from {table_name}", exc_info=True)
            raise

    def delete_all(self, table_name: str):
        """Deletes all records from the specified Databricks table."""
        delete_sql = f"DELETE FROM {table_name}"
        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(delete_sql)
                    logger.info(f"All data deleted successfully from {table_name}")
        except Exception as e:
            logger.error(f"Failed when deleting all records from {table_name}", exc_info=True)
            raise
