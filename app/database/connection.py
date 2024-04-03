import psycopg2
from sqlalchemy import create_engine


db_connection_file_path = "C:/Users/heito/OneDrive/Heitor/Projects/Database/local_postgres_connection_information.txt"
with open(db_connection_file_path, "r") as file:
    for line in file:
        split_line = line.split("=")
        if split_line[0] == "dbhost":
            dbhost = split_line[1].strip()
        elif split_line[0] == "dbport":
            dbport = split_line[1].strip()
        elif split_line[0] == "dbuser":
            dbuser = split_line[1].strip()
        elif split_line[0] == "dbpassword":
            dbpassword = split_line[1].strip()
            
dbname = "AuthenticationManagement"


def connect_to_postgres(connection_type="connection", host=dbhost, port=dbport, dbname=dbname, user=dbuser, password=dbpassword):
    """
    This function create a connection with a PostgreSQL database and return the connection or the engine, as informed into 'connection_type'
    """

    if connection_type == "connection":
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
        )

        return conn
    
    elif connection_type == "engine":
        engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}")

        return engine
