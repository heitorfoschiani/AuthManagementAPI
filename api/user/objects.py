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
                INSERT INTO useraccess (user_id, privilege_id, status_id, creation_datetime, change_datetime)
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
                    SET status_id = 1, change_datetime = %s
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