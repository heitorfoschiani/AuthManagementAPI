from app.database.creation import PostgresTableCreator


def create_table_useraccess():
    """
    This function creates 'useraccess' table into the database
    """

    table_columns = [
        ("user_id", "INTEGER NOT NULL REFERENCES fkusers(id)"), 
        ("privilege_id", "INTEGER NOT NULL REFERENCES fkuserprivileges(id)"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        table_name="useraccess"
    )

    postgres_table_creator.create_table(table_columns)