from app.database.connection import PostgresConnection
from app.database.creation import PostgresTableCreator


def create_table_useremails(postgres_connection: PostgresConnection):
    """
    This function creates 'useremails' table into the database
    """
    
    table_columns = [
        ("user_id", "INTEGER NOT NULL REFERENCES fkusers(id)"), 
        ("email", "VARCHAR(255)"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        postgres_connection=postgres_connection, 
        table_name="useremails"
    )

    postgres_table_creator.create_table(table_columns)