import pymssql
import pandas as pd
from contextlib import closing
from . import logger

class MSSQLClient:
    def __init__(self, server: str, username: str, password: str, database: str):
        """
        Initialize the MSSQL client with connection details.

        :param server: MSSQL server address
        :param username: MSSQL username
        :param password: MSSQL password
        :param database: MSSQL database name
        """
        self.server = server
        self.username = username
        self.password = password
        self.database = database

    def _conn(self):
        """Establishes a connection to the MSSQL server."""
        try:
            return pymssql.connect(
                server=self.server,
                user=self.username,
                password=self.password,
                database=self.database
            )
        except pymssql.DatabaseError as e:
            logger.error("Database connection failed", exc_info=True)
            raise ConnectionError("Failed when connecting to database") from e

    def _ensure_conn(self, conn=None):
        """Ensures the MSSQL connection is valid, reconnecting if necessary."""
        try:
            if conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('SELECT 1')
                    cursor.fetchall()
                return conn
        except Exception as e:
            logger.warning("Connection validation failed. Attempting to reconnect", exc_info=True)
        return self._conn()

    def insert_into_table(self, insert_sql: str, data: list, conn=None):
        """Inserts data into a table in the MSSQL database."""
        external_conn = conn is not None
        conn = self._ensure_conn(conn)

        try:
            with closing(conn.cursor()) as cursor:
                cursor.executemany(insert_sql, data)
                conn.commit()
            return conn
        except pymssql.DatabaseError as e:
            conn.rollback()
            logger.error("Error inserting data", exc_info=True)
            raise
        finally:
            if not external_conn:
                conn.close()

    def df_to_table(self, df: pd.DataFrame, table_name: str):
        try:
            df = df.astype(object).where(pd.notnull(df), None)

            columns = ', '.join(f"[{col}]" for col in df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            data = list(df.itertuples(index=False, name=None))

            self.insert_into_table(insert_sql=insert_sql, data=data)

        except pymssql.DatabaseError as e:
            logger.error(f"Failed when inserting into {table_name}", exc_info=True)
            raise e


    def query_to_df(self, query: str, conn=None) -> pd.DataFrame:
        """Executes a query and returns the result as a DataFrame."""
        external_conn = conn is not None
        conn = self._ensure_conn(conn)

        try:
            with closing(conn.cursor()) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                return pd.DataFrame(rows, columns=columns)
        except pymssql.DatabaseError as e:
            logger.error("Error executing query", exc_info=True)
            raise
        finally:
            if not external_conn:
                conn.close()

    def exec(self, sql: str, conn=None):
        """Executes a SQL command that doesn't require a return value (e.g., DELETE, UPDATE)."""
        external_conn = conn is not None
        conn = self._ensure_conn(conn)

        try:
            with closing(conn.cursor()) as cursor:
                cursor.execute(sql)
                conn.commit()  # Commit changes for non-query operations
        except pymssql.DatabaseError as e:
            conn.rollback()
            logger.error("Error executing non-query command", exc_info=True)
            raise
        finally:
            if not external_conn:
                conn.close()
