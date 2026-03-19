import psycopg2
import os

def get_conn():
    conn = psycopg2.connect(
        dbname = "inventario",
        user = "api_db_user",
        password = os.getenv("DB_PASSWORD"),
        host = "localhost",
        port = 0000
    )
    conn.set_client_encoding('UTF8')
    return conn