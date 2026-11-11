import mysql.connector
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
import os
from urllib.parse import quote_plus

# Database connection parameters (read from .env)
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# SQLAlchemy URI
# Password is URL-encoded so characters like "@" or ":" do not break the URI
DB_URI = f"mysql+mysqlconnector://{DB_USER}:{quote_plus(DB_PASSWORD or '')}@{DB_HOST}/{DB_NAME}"

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