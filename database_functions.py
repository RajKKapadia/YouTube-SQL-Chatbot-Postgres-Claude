from psycopg2.extras import RealDictCursor
import datetime
import decimal
import os
import json

import psycopg2
import psycopg2.extras
import psycopg2.pool

import config


# Global pool variable
global_connection_pool = None


def connect_to_postgresql_pool() -> psycopg2.pool.SimpleConnectionPool | None:
    '''Create or retrieve a PostgreSQL connection pool as a singleton.'''
    global global_connection_pool
    if global_connection_pool is None:
        try:
            global_connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                host=config.POSTGRES_HOST,
                database=config.POSTGRES_DB_NAME,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD
            )
        except psycopg2.DatabaseError as e:
            print(f"Error creating PostgreSQL connection pool: {e}")
            global_connection_pool = None
    return global_connection_pool


def get_postgresql_pooled_cnx() -> psycopg2.extensions.connection | None:
    '''Get a new PostgreSQL connection from the connection pool
    '''
    pool = connect_to_postgresql_pool()
    if not pool:
        return None
    try:
        cnx = pool.getconn()
        return cnx
    except psycopg2.DatabaseError as e:
        print(f"Error getting connection from pool: {e}")
        return None


def close_postgresql_cnx(cnx: psycopg2.extensions.connection) -> None:
    '''Release a PostgreSQL connection back to the pool
    '''
    pool = connect_to_postgresql_pool()
    if pool is not None and cnx is not None:
        try:
            pool.putconn(cnx)
        except psycopg2.DatabaseError as e:
            print(f"Error putting connection back to pool: {e}")


def get_tables_name() -> list[str]:
    """Return a list of table names."""
    cnx = get_postgresql_pooled_cnx()
    cursor = cnx.cursor()
    table_names = []
    query = """SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"""
    cursor.execute(query)
    results = cursor.fetchall()
    for table in results:
        table_names.append(table[0])
    cursor.close()
    close_postgresql_cnx(cnx)
    return table_names


def get_columns_name(table_name: str) -> list[str]:
    """Return a list of column names."""
    cnx = get_postgresql_pooled_cnx()
    cursor = cnx.cursor()
    column_names = []
    query = f"""SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';"""
    cursor.execute(query)
    results = cursor.fetchall()
    for col in results:
        column_names.append(col)
    cursor.close()
    close_postgresql_cnx(cnx)
    return column_names


def get_database_definitions() -> dict:
    '''Get all the database definitions from the DEFINITION_DIR
    '''
    database_definitions = {
        "tables": []
    }
    for definition in os.listdir(config.DEFINITION_DIR):
        with open(os.path.join(config.DEFINITION_DIR, definition), 'r') as file:
            database_definitions['tables'].append(json.loads(file.read()))
    return database_definitions


def get_database_info() -> dict:
    """Return a list of dicts containing the table name and columns for each table in the database."""
    table_dicts = []
    for table_name in get_tables_name():
        columns_name = get_columns_name(table_name)
        table_dicts.append(
            {"table_name": table_name, "columns_name": columns_name})
    return table_dicts


def get_database_schema_string() -> str:
    '''Get database schema as a string
    '''
    database_schema_dict = get_database_info()
    database_schema_string = "\n".join(
        [
            f"Table: {table['table_name']}\nColumns: {table['columns_name']}"
            for table in database_schema_dict
        ]
    )
    return database_schema_string


def serialize_data(obj) -> str:
    print(f'Object type -> {type(obj)}')
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Object type not serializable - {type(obj)}")


def execute_database_query(query: str) -> list[dict[str, str]] | list:
    """Function to query SQLite database with a provided SQL query."""
    cnx = get_postgresql_pooled_cnx()
    response = []
    if cnx == None:
        return response
    try:
        cursor = cnx.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        results = cursor.fetchall()
        for data in results:
            response.append(json.dumps(data, default=serialize_data))
    except psycopg2.DatabaseError as e:
        print(f'Error at ask_database -> {e}')
    finally:
        close_postgresql_cnx(cnx)
    return response


def run_execute_database_query(query: str) -> list[dict[str, str]] | list:
    '''Execute a query and return the results
    '''
    try:
        return execute_database_query(query)
    except psycopg2.DatabaseError as e:
        print(f"Error executing query: {e}")
        return []
