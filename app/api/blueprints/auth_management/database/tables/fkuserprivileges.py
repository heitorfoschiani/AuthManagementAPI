from app.database.connection import PostgresConnection
from app.database.creation import PostgresTableCreator


def create_table_fkuserprivileges(postgres_connection: PostgresConnection):
    """
    This function creates 'fkuserprivileges' table into the database
    """

    table_columns = [
        ("privilege", "VARCHAR(255)"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        postgres_connection=postgres_connection, 
        table_name="fkuserprivileges"
    )

    postgres_table_creator.create_table(table_columns, foreign_key=True)