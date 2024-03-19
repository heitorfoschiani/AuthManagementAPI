from app.database.creation import PostgresTableCreator


def create_table_useremails():
    """
    This function creates 'useremails' table into the database
    """
    
    table_columns = [
        ("user_id", "INTEGER NOT NULL REFERENCES fkusers(id)"), 
        ("email", "VARCHAR(255)"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        table_name="useremails"
    )

    postgres_table_creator.create_table(table_columns)