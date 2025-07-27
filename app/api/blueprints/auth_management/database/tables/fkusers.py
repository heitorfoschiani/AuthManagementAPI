from app.database.connection import PostgresConnection
from app.database.creation import PostgresTableCreator


def create_table_fkusers(postgres_connection: PostgresConnection):
    """
    This function creates 'fkusers' table into the database
    """

    table_columns = [
        ("full_name", "VARCHAR(255)"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        postgres_connection=postgres_connection, 
        table_name="fkusers"
    )

    postgres_table_creator.create_table(table_columns, foreign_key=True)