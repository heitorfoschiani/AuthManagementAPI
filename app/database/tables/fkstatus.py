from app.database.connection import PostgresConnection
from app.database.creation import PostgresTableCreator


def create_table_fkstatus(postgres_connection: PostgresConnection):
    """
    This function creates 'status' table into the database
    """

    table_columns = [
        ("status", "VARCHAR(255)"), 
    ]

    postgres_table_creator = PostgresTableCreator(
        postgres_connection=postgres_connection, 
        table_name="fkstatus"
    )

    postgres_table_creator.create_table(table_columns, foreign_key=True)


def add_status(status: str, postgres_connection: PostgresConnection):
    """
    This function add a new privilege into the 'fkstatus' table
    """

    conn = postgres_connection.connect()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT status FROM fkstatus
            WHERE status = %s
        """, (status,))
        fetch = cursor.fetchone()

        if not fetch:
            cursor.execute("""
                INSERT INTO fkstatus (status)
                VALUES (%s)
            """, (status,))
            conn.commit()
    except Exception as e:
        raise Exception(f"Unable to add '{status}' into the table 'fkstatus': {e}")
    finally:
        conn.close()