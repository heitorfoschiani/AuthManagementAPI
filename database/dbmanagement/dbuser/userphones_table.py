from database.dbconnection import connect_to_postgres


def create_table_userphones():
    # This function creates the "userphones" table into the database

    conn = connect_to_postgres()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id FROM fkstatus 
            WHERE status = 'valid';
        """)
        fetch = cursor.fetchone()
        valid_status_id = fetch[0]

        cursor.execute("""
            CREATE TABLE userphones (
                user_id INTEGER NOT NULL REFERENCES users(id), 
                phone VARCHAR(20), 
                status_id INTEGER NOT NULL REFERENCES fkstatus(id) DEFAULT %s, 
                creation_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                update_datetime TIMESTAMP
            );
        """, (valid_status_id,))
        conn.commit()
    except Exception as e:
        raise Exception(f"Unable to create table 'userphones': {e}")
    finally:
        conn.close()