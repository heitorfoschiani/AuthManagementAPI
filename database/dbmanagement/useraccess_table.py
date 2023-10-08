from database.dbconnection import connect_to_postgres


def table_useraccess_exists():
    # This function check if the table "useraccess" already exists into the database
    
    conn = connect_to_postgres()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = 'useraccess'
        );
    ''')
    if not cursor.fetchone()[0]:
        conn.close()
        return False

    conn.close()
    return True

def create_table_useraccess():
    # This function creates the "useraccess" table into the database

    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE useraccess (
                user_id INTEGER NOT NULL REFERENCES users(id), 
                privilege_id INTEGER NOT NULL REFERENCES userprivileges(id), 
                status_id SMALLSERIAL, 
                creation_datetime TIMESTAMP, 
                change_datetime TIMESTAMP, 
                PRIMARY KEY(user_id, privilege_id)
            );
        ''')
        conn.commit()
        
        return True
    except:
        return False
    finally:
        conn.close()