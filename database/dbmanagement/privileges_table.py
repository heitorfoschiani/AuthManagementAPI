from database.dbconnection import connect_to_postgres


def table_userprivileges_exists():
    # This function check if the table "userprivileges" already exists into the database
    
    conn = connect_to_postgres()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = 'userprivileges'
        );
    ''')
    if not cursor.fetchone()[0]:
        conn.close()
        return False

    conn.close()
    return True

def create_table_userprivileges():
    # This function creates the "userprivileges" table into the database

    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE userprivileges (
                id SERIAL PRIMARY KEY, 
                privilege VARCHAR(255) 
            );
        ''')
        conn.commit()
        
        return True
    except:
        return False
    finally:
        conn.close()

def add_privilege(privilege: str):
    # This function add a new privilege into the "userprivileges" table

    conn = connect_to_postgres()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT privilege FROM userprivileges
        WHERE privilege = %s
    ''', (privilege,))

    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO userprivileges (privilege)
            VALUES (%s);
        ''', (privilege,))
        conn.commit()

        cursor.execute('''
            SELECT id FROM userprivileges
            WHERE privilege = %s
        ''', (privilege,))
        fetch = cursor.fetchone()

        privilege_id = fetch[0]

        return privilege_id
    
    conn.close()
    
    return 0