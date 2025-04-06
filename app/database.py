import mysql.connector
from sqlalchemy import create_engine
# from langchain.sql_database import SQLDatabase
from langchain_community.utilities import SQLDatabase
from urllib.parse import quote
import os

# Database connection parameters
"""
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root@123")
DB_NAME = os.getenv("DB_NAME", "sales_schema")
"""

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_PASSWORD_ENCODED = quote(DB_PASSWORD)
DB_NAME = os.getenv("DB_NAME")

# SQLAlchemy URI
DB_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

def get_db_connection():
    """Create and return a MySQL connection"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            port=3306,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as e:
        raise Exception(f"Database connection error: {str(e)}")

def get_langchain_db():
    """Create and return a LangChain SQLDatabase object"""
    engine = create_engine(DB_URI)
    db = SQLDatabase(engine)
    return db