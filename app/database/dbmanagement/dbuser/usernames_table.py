from app.database .dbconnection import connect_to_postgres


def create_table_usernames():
    # This function creates the "usernames" table into the database

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
            CREATE TABLE usernames (
                user_id INTEGER NOT NULL REFERENCES users(id), 
                username VARCHAR(255), 
                status_id INTEGER NOT NULL REFERENCES fkstatus(id) DEFAULT %s, 
                creation_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                update_datetime TIMESTAMP
            );
        """, (valid_status_id,))
        conn.commit()
    except Exception as e:
        raise Exception(f"Unable to create table 'usernames': {e}")
    finally:
        conn.close()