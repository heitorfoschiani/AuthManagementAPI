from database.dbconnection import connect_to_postgres


def table_usernames_exists():
    # This function check if the table "usernames" already exists into the database
    
    conn = connect_to_postgres()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = 'usernames'
        );
    """)
    if not cursor.fetchone()[0]:
        conn.close()
        return False

    conn.close()
    return True

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
        
        return True
    except:
        return False
    finally:
        conn.close()