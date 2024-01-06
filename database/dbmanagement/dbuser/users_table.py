from database.dbconnection import connect_to_postgres


def create_table_users():
    # This function creates the "users" table into the database

    conn = connect_to_postgres()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY, 
                full_name VARCHAR(255), 
                creation_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        
        return True
    except:
        return False
    finally:
        conn.close()