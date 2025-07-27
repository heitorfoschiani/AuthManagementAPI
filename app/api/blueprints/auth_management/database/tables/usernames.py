from app.database.connection import PostgresConnection
from app.database.creation import PostgresTableCreator


def create_table_usernames(postgres_connection: PostgresConnection):
    """
    This function creates 'usernames' table into the database
    """

    table_columns = [
        ("user_id", "INTEGER NOT NULL REFERENCES fkusers(id)"), 
        ("username", "VARCHAR(255)"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        postgres_connection=postgres_connection, 
        table_name="usernames"
    )

    postgres_table_creator.create_table(table_columns)