from app.database.connection import PostgresConnection
from app.database.creation import PostgresTableCreator


def create_table_userphones(postgres_connection: PostgresConnection):
    """
    This function creates 'userphones' table into the database
    """

    table_columns = [
        ("user_id", "INTEGER NOT NULL REFERENCES fkusers(id)"), 
        ("phone", "VARCHAR(20)"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        postgres_connection=postgres_connection, 
        table_name="userphones"
    )

    postgres_table_creator.create_table(table_columns)