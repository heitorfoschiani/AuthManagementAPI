import psycopg2
import sqlalchemy
import os
from dotenv import load_dotenv


class PostgresConnection:
    def __init__(self):
        credentials_file_path, dbname = self._load_connection_information()
        dbhost, dbport, dbuser, dbpassword = self._load_connection_credentials(credentials_file_path)

        self.dbhost = dbhost
        self.dbport = dbport
        self.dbuser = dbuser
        self.dbname = dbname
        self.dbpassword = dbpassword
        
    def connect(self, connection_type="connection"):
        """
        This function creates a connection with a PostgreSQL database and returns the connection or the engine, as specified in 'connection_type'.
        """

        if connection_type == "connection":
            conn = psycopg2.connect(
                host=self.dbhost, 
                port=self.dbport, 
                user=self.dbuser, 
                password=self.dbpassword, 
                dbname=self.dbname
            )
            return conn
        
        elif connection_type == "engine":
            engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{self.dbuser}:{self.dbpassword}@{self.dbhost}:{self.dbport}/{self.dbname}")
            return engine
        
    @staticmethod
    def _load_connection_information():
        """
        Load the path to the database credentials file from an environment file.
        Returns the path and the database name.
        """

        try:
            load_dotenv("app/database/db_access_information.env", override=True)
            credentials_file_path = os.getenv("CREDENTIALS_FILE_PATH")
            dbname = os.getenv("DBNAME")

            if not credentials_file_path:
                raise ValueError("Credentials file path not found in the environment variables.")

            if not dbname:
                raise ValueError("Database name not found in the environment variables.")
        except Exception as e:
            raise Exception(f"Failed to load credentials file path: {e}")
        
        return credentials_file_path, dbname
    
    @staticmethod
    def _load_connection_credentials(credentials_file_path: str):
        """
        Load the database credentials from the specified credentials file path.
        Returns the host, port, user, and password of the database.
        """

        try:
            load_dotenv(credentials_file_path, override=True)
            dbhost = os.getenv('DBHOST')
            dbport = os.getenv('DBPORT')
            dbuser = os.getenv('DBUSER')
            dbpassword = os.getenv('DBPASSWORD')

            if not all([dbhost, dbport, dbuser, dbpassword]):
                raise ValueError("Database credentials are incomplete.")
        except Exception as e:
            raise Exception(f"Failed to load database credentials: {e}")

        return dbhost, dbport, dbuser, dbpassword
