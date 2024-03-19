from app.database.creation import PostgresTableCreator


def create_table_userphones():
    """
    This function creates 'userphones' table into the database
    """

    table_columns = [
        ("user_id", "INTEGER NOT NULL REFERENCES fkusers(id)"), 
        ("phone", "VARCHAR(20)"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        table_name="userphones"
    )

    postgres_table_creator.create_table(table_columns)