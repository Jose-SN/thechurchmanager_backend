import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('')

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRESQL_DB_HOST"),
        port=os.getenv("POSTGRESQL_DB_PORT"),
        user=os.getenv("POSTGRESQL_DB_USER"),
        password=os.getenv("POSTGRESQL_DB_PASS"),
        dbname=os.getenv("POSTGRESQL_DB_NAME")
    )
