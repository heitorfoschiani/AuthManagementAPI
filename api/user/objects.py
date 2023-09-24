from datetime import datetime

from database.dbconnection import connect_to_postgres


class User:
    def __init__(self, id: int, full_name: str, email: str, phone: str, username: str):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.username = username

    def register(self, password: str):
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (full_name, email, phone, username, password, creation_datetime)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (self.full_name, self.email, self.phone, self.username, password, datetime.now(),))
            conn.commit()

            cursor.execute('''
                SELECT id FROM users WHERE username = %s
            ''', (self.username,))
            user_id = cursor.fetchone()[0]
        except:
            return None
        finally:
            conn.close()

        return user_id

    def username_exists(self):
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute(f'SELECT username FROM users WHERE username = %s', (self.username,))
        fetch = cursor.fetchone()
        conn.close()
        if not fetch:
            return False

        return True

    def email_exists(self):
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute(f'SELECT email FROM users WHERE email = %s', (self.email,))
        fetch = cursor.fetchone()
        conn.close()
        if not fetch:
            return False

        return True