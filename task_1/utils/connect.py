import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Create and return database connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=os.getenv('POSTGRES_PORT')
    )

