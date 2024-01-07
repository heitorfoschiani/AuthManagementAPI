from app.database .dbconnection import connect_to_postgres


def create_table_fkstatus():
    # This function creates the "fkstatus" table into the database

    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE fkstatus (
                id SERIAL PRIMARY KEY, 
                status VARCHAR(255)
            );
        """)
        conn.commit()
    except Exception as e:
        raise Exception(f"Unable to create table 'fkstatus': {e}")
    finally:
        conn.close()

def add_status(status):
    # This function add a new privilege into the "fkstatus" table

    conn = connect_to_postgres()
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