import psycopg2
from sqlalchemy import create_engine


with open("C:/Users/heito/OneDrive/Heitor/Projects/Database/local_postges_connection_information.txt") as f:
    lines = f.readlines()

dbhost = lines[0].strip()
dbport = lines[1].strip()
dbuser = lines[2].strip()
dbpassword = lines[3].strip()
dbname = "AuthenticationManagement"


def connect_to_postgres(connection_type="connection", host=dbhost, port=dbport, dbname=dbname, user=dbuser, password=dbpassword):
    # This function create a connection with a PostgreSQL database and return the connection or the engine, as informed into "connection_type"

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
