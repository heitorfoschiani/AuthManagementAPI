from database.dbconnection import connect_to_postgres


def table_userpasswords_exists():
    # This function check if the table "userpasswords" already exists into the database
    
    conn = connect_to_postgres()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = 'userpasswords'
        );
    ''')
    if not cursor.fetchone()[0]:
        conn.close()
        return False

    conn.close()
    return True

def create_table_userpasswords():
    # This function creates the "userpasswords" table into the database

    conn = connect_to_postgres()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE userpasswords (
                user_id INTEGER NOT NULL REFERENCES users(id), 
                password TEXT, 
                status_id SMALLSERIAL, 
                creation_datetime TIMESTAMP, 
                update_datetime TIMESTAMP, 
                PRIMARY KEY(user_id, status_id)
            );
        ''')
        conn.commit()
        
        return True
    except:
        return False
    finally:
        conn.close()