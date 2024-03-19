from app.database.creation import PostgresTableCreator


def create_table_usernames():
    """
    This function creates 'usernames' table into the database
    """

    table_columns = [
        ("user_id", "INTEGER NOT NULL REFERENCES fkusers(id)"), 
        ("username", "VARCHAR(255)"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        table_name="usernames"
    )

    postgres_table_creator.create_table(table_columns)