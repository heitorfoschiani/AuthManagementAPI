from database.dbconnection import connect_to_postgres


def table_users_exists():
    # This function check if the table "users" already exists into the database
    
    conn = connect_to_postgres()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = 'users'
        );
    """)
    if not cursor.fetchone()[0]:
        conn.close()
        return False

    conn.close()
    return True

def create_table_users():
    # This function creates the "users" table into the database

    conn = connect_to_postgres()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY, 
                full_name VARCHAR(255), 
                creation_datetime TIMESTAMP
            );
        """)
        conn.commit()
        
        return True
    except:
        return False
    finally:
        conn.close()