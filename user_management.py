# Importing libraries
from datetime import datetime

# Importing python files from the project
import dbconnection

# User object
class User:
    def __init__(self, user_id: int, full_name: str, email: str, phone: str, username: str):
        self.id = user_id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.username = username

    def username_exists(self):
        # connecting to the database
        conn = dbconnection.connect_to_postgres()
        cursor = conn.cursor()

        # checking if username already exists
        cursor.execute(f'SELECT username FROM userinfos WHERE username = %s', (self.username,))
        if cursor.fetchone() is not None:
            conn.close()
            return True

        conn.close()
        return False

    def email_exists(self):
        # connecting to the database
        conn = dbconnection.connect_to_postgres()
        cursor = conn.cursor()

        # checking if email already exists
        cursor.execute(f'SELECT email FROM userinfos WHERE email = %s', (self.email,))
        if cursor.fetchone() is not None:
            conn.close()
            return True

        conn.close()
        return False

    def register(self, password: str):
        # connecting to the database
        conn = dbconnection.connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO userinfos (full_name, email, phone, username, password, creation_datetime)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (self.full_name, self.email, self.phone, self.username, password, datetime.now(),))
            conn.commit()
        except Exception as e:
            conn.close()
            return 0

        # getting user_id
        cursor.execute('''
            SELECT user_id FROM userinfos WHERE username = %s
        ''', (self.username,))
        user_id = cursor.fetchone()[0]

        conn.close()
        return user_id

    def check_password():
            pass
    

def table_userinfos_exists():
    # connecting to the database
    conn = dbconnection.connect_to_postgres()
    cursor = conn.cursor()

    # checking if the table "userinfos" exists
    cursor.execute(
        '''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = 'userinfos'
            );
        '''
    )

    if not cursor.fetchone()[0]:
        conn.close()
        return False

    conn.close()
    return True

def create_table_userinfos():
    # connecting to the database
    conn = dbconnection.connect_to_postgres()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
                CREATE TABLE userinfos(
                    user_id SERIAL PRIMARY KEY, 
                    full_name VARCHAR(255), 
                    email VARCHAR(255), 
                    phone VARCHAR(20), 
                    username VARCHAR(255), 
                    password TEXT,
                    creation_datetime TIMESTAMP
                );
            '''
        )
        conn.commit()
        
        return True
    except:
        return False
    finally:
        conn.close()
