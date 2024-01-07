from app.database .dbconnection import connect_to_postgres


def create_table_userprivileges():
    # This function creates the "userprivileges" table into the database

    conn = connect_to_postgres()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE userprivileges (
                id SERIAL PRIMARY KEY, 
                privilege VARCHAR(255) 
            );
        """)
        conn.commit()
    except Exception as e:
        raise Exception(f"Unable to create table 'userprivileges': {e}")
    finally:
        conn.close()