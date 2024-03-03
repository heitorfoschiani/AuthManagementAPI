from app.database.creation import PostgresTableCreator


def create_table_userpasswords():
    """
    This function creates 'userpasswords' table into the database
    """

    table_columns = [
        ("user_id", "INTEGER NOT NULL REFERENCES fkusers(id)"), 
        ("password", "TEXT"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        table_name="userpasswords"
    )

    postgres_table_creator.create_table(table_columns)