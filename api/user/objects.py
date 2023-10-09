from datetime import datetime

from database.dbconnection import connect_to_postgres


class User:
    def __init__(self, id: int, full_name: str, email: str, phone: str, username: str):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.username = username

    def register(self, password_hash: str):
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (full_name, creation_datetime)
                VALUES (%s, %s) RETURNING id
            ''', (self.full_name, datetime.now()))
            user_id = cursor.fetchone()[0]

            cursor.execute('''
                INSERT INTO useremails (user_id, email, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, self.email, 1, datetime.now(), None))

            cursor.execute('''
                INSERT INTO userphones (user_id, phone, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, self.phone, 1, datetime.now(), None))

            cursor.execute('''
                INSERT INTO usernames (user_id, username, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, self.username, 1, datetime.now(), None))

            cursor.execute('''
                INSERT INTO userpasswords (user_id, password, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, password_hash, 1, datetime.now(), None))
            conn.commit()
        except:
            return False
        finally:
            conn.close()

        if not user_id:
            return False
        
        self.id = user_id

        if self.id == 1:
            if not self.set_privilege(privilege='administrator'):
                return False
        else:
            if not self.set_privilege(privilege='basic'):
                return False

        return True

    def set_privilege(self, privilege: str):
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id FROM userprivileges
                WHERE privilege = %s
            ''', (privilege,))
            fetch = cursor.fetchone()
            if not fetch:
                conn.close()
                return False
            privilege_id = int(fetch[0])

            cursor.execute('''
                INSERT INTO useraccess (user_id, privilege_id, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s)
            ''', (self.id, privilege_id, 0, datetime.now(), None))
            conn.commit()
        except:
            return False
        finally:
            conn.close()

        return True
    
    def delete_privilege(self, privilege: str):
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id FROM userprivileges
                WHERE privilege = %s
            ''', (privilege,))
            fetch = cursor.fetchone()
            if not fetch:
                conn.close()
                return False
            privilege_id = int(fetch[0])

            cursor.execute('''
                UPDATE useraccess
                    SET status_id = 1, update_datetime = %s
                WHERE privilege_id = %s AND user_id = %s AND status_id = 0
            ''', (datetime.now(), privilege_id, self.id))
            conn.commit()
        except:
            return False
        finally:
            conn.close()

        return True
    
    def privileges(self):
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT userprivileges.privilege FROM useraccess
                INNER JOIN userprivileges ON useraccess.privilege_id = userprivileges.id
                WHERE useraccess.user_id = %s AND useraccess.status_id = 0
            ''', (self.id,))
            fetch = cursor.fetchall()
            privileges_list = [item[0] for item in fetch]
            if not fetch:
                return []
        except:
            return []
        finally:
            conn.close()

        return privileges_list

    def username_exists(self):
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM usernames WHERE username = %s AND status_id = 1', (self.username,))
        fetch = cursor.fetchone()
        conn.close()
        if not fetch:
            return False

        return True

    def email_exists(self):
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM useremails WHERE email = %s AND status_id = 1', (self.email,))
        fetch = cursor.fetchone()
        conn.close()
        if not fetch:
            return False

        return True
    
def get_user(user_id: int):
    conn = connect_to_postgres()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            users.id,
            users.full_name,
            useremails.email,
            userphones.phone,
            usernames.username
        FROM users
        LEFT JOIN useremails ON useremails.user_id = users.id
        LEFT JOIN userphones ON userphones.user_id = users.id
        LEFT JOIN usernames ON usernames.user_id = users.id
        WHERE 
        useremails.status_id = 1 AND
        userphones.status_id = 1 AND
        usernames.status_id = 1 AND 
        users.id = %s
    ''', 
    (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        user = User(
            id = user_data[0], 
            full_name = user_data[1], 
            email = user_data[2], 
            phone = user_data[3], 
            username = user_data[4]
        )
        return user
    
    return None