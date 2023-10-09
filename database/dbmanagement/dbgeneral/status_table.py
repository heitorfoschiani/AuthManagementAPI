from database.dbconnection import connect_to_postgres


def table_fkstatus_exists():
    # This function check if the table "fkstatus" already exists into the database
    
    conn = connect_to_postgres()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = 'fkstatus'
        );
    ''')
    if not cursor.fetchone()[0]:
        conn.close()
        return False

    conn.close()
    return True

def create_table_fkstatus():
    # This function creates the "fkstatus" table into the database

    conn = connect_to_postgres()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE fkstatus (
                id SERIAL PRIMARY KEY, 
                status VARCHAR(255)
            );
        ''')
        conn.commit()
        
        return True
    except:
        return False
    finally:
        conn.close()

def add_status(status: str):
    # This function add a new privilege into the "fkstatus" table

    conn = connect_to_postgres()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT status FROM fkstatus
        WHERE status = %s
    ''', (status,))

    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO fkstatus (status)
            VALUES (%s);
        ''', (status,))
        conn.commit()

        cursor.execute('''
            SELECT id FROM fkstatus
            WHERE status = %s
        ''', (status,))
        fetch = cursor.fetchone()

        status_id = fetch[0]

        conn.close()

        return status_id
    
    conn.close()

    return 0