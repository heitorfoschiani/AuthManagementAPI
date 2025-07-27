import psycopg2
from psycopg2 import sql
import sqlalchemy
import os
from dotenv import load_dotenv


class PostgresConnection:
    def __init__(self, environment: str):
        credentials_file_path, dbname = self._load_connection_information()
        dbhost, dbport, dbuser, dbpassword = self._load_connection_credentials(credentials_file_path)

        self.dbhost = dbhost
        self.dbport = dbport
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self.dbname = dbname
        self.environment = environment
        
    def connect(self, connection_type: str="connection", test_environment: bool=False):
        """
        This function creates a connection with a PostgreSQL database and returns the connection or the engine, as specified in 'connection_type'.
        """

        dbname = self.dbname + self.environment if self.environment != "Production" else self.dbname

        database_exists = self._database_exists(dbname)
        if not database_exists:
            self._create_database(dbname)

        if connection_type == "connection":
            conn = psycopg2.connect(
                host=self.dbhost, 
                port=self.dbport, 
                user=self.dbuser, 
                password=self.dbpassword, 
                dbname=dbname
            )

            return conn
        
        elif connection_type == "engine":
            engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{self.dbuser}:{self.dbpassword}@{self.dbhost}:{self.dbport}/{self.dbname}")

            return engine

    def _create_database(self, dbname: str):
        try:
            conn = psycopg2.connect(
                host=self.dbhost, 
                port=self.dbport, 
                user=self.dbuser, 
                password=self.dbpassword, 
                dbname="postgres"
            )
            conn.autocommit = True

            cursor = conn.cursor()

            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(dbname)
            ))

            cursor.close()
            conn.close()
        except Exception as e:
            raise Exception(f"Postgres Database creation has failed: {e}")
        finally:
            cursor.close()
            conn.close()

    def _database_exists(self, dbname: str) -> bool:
        try:
            conn = psycopg2.connect(
                host=self.dbhost, 
                port=self.dbport, 
                user=self.dbuser, 
                password=self.dbpassword, 
                dbname="postgres"
            )

            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (dbname,))

            exists = cursor.fetchone() is not None
        except:
            return False
        finally:
            cursor.close()
            conn.close()

        return exists
        
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
            dbhost = os.getenv("DBHOST")
            dbport = os.getenv("DBPORT")
            dbuser = os.getenv("DBUSER")
            dbpassword = os.getenv("DBPASSWORD")

            if not all([dbhost, dbport, dbuser, dbpassword]):
                raise ValueError("Database credentials are incomplete.")
            
        except Exception as e:
            raise Exception(f"Failed to load database credentials: {e}")

        return dbhost, dbport, dbuser, dbpassword
