# Author: Heitor Foschiani de Souza
# Email: heitor.foschiani@outlook.com
# Number: (11) 9 4825-3334

# Importing libraries
import psycopg2
from sqlalchemy import create_engine

# Setting databse infos to connection in postgreSQL
with open('C:/Users/heito/OneDrive - Fundação São Paulo/Heitor/Projects/Database/postgres_connection_infos.txt') as f:
    lines = f.readlines()

dbhost = lines[0].strip()
dbport = lines[1].strip()
dbuser = lines[2].strip()
dbpassword = lines[3].strip()
dbname = 'LoginManagement'


# Creating postgresSQL connection
def connect_to_postgres(connection_type='connection', host=dbhost, port=dbport, dbname=dbname, user=dbuser, password=dbpassword):
    if connection_type == 'connection':
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
        )

        return conn
    
    elif connection_type == 'engine':
        engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}")

        return engine
    
    