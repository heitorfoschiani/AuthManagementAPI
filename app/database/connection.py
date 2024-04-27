import psycopg2
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


def connect_to_postgres(connection_type="connection"):
    """
    This function creates a connection with a PostgreSQL database and returns the connection or the engine, as specified in 'connection_type'.
    """

    load_dotenv("app/database/credentials.env", override=True)
    credentials_file_path = os.getenv("CREDENTIALS_FILE_PATH")
    dbname = os.getenv("DBNAME")

    load_dotenv(credentials_file_path, override=True)
    dbhost = os.getenv('DBHOST')
    dbport = os.getenv('DBPORT')
    dbuser = os.getenv('DBUSER')
    dbpassword = os.getenv('DBPASSWORD')

    if connection_type == "connection":
        conn = psycopg2.connect(
            host=dbhost,
            port=dbport,
            user=dbuser,
            password=dbpassword,
            dbname=dbname,
        )
        return conn
    
    elif connection_type == "engine":
        engine = create_engine(f"postgresql+psycopg2://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}")
        return engine

