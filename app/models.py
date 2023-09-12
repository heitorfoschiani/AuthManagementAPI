# Importing libraries
from flask_restx import fields
from datetime import datetime

# Importing python files from the project
import dbconnection
from app.extensions import api


user_model = api.model('User', {
    'id': fields.Integer,
    'full_name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'username': fields.String,
})

get_user_model = api.model('GetUser', {
    'id': fields.Integer,
})

register_user_model = api.model('RegisterUser', {
    'full_name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'username': fields.String,
    'password': fields.String,
})

authenticate_user_model = api.model('AuthenticateUser', {
    'username': fields.String,
    'password': fields.String,
})


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
        fetch = cursor.fetchone()
        conn.close()
        if not fetch:
            return False

        return True

    def email_exists(self):
        # connecting to the database
        conn = dbconnection.connect_to_postgres()
        cursor = conn.cursor()

        # checking if email already exists
        cursor.execute(f'SELECT email FROM userinfos WHERE email = %s', (self.email,))
        fetch = cursor.fetchone()
        conn.close()
        if not fetch:
            return False

        return True

    def register(self, password: str):
        # connecting to the database
        conn = dbconnection.connect_to_postgres()
        cursor = conn.cursor()

        try:
            # creating user into database
            cursor.execute('''
                INSERT INTO userinfos (full_name, email, phone, username, password, creation_datetime)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (self.full_name, self.email, self.phone, self.username, password, datetime.now(),))
            conn.commit()

            # getting user_id
            cursor.execute('''
                SELECT user_id FROM userinfos WHERE username = %s
            ''', (self.username,))
            user_id = cursor.fetchone()[0]
        except:
            return None
        finally:
            conn.close()

        return user_id
    
    def set_as_free_access(self):
        pass

    def set_as_privileged_access(self):
        pass

    def set_as_adm_access(self):
        pass