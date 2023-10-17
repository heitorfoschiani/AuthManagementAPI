from typing import Optional
from datetime import datetime

from database.dbconnection import connect_to_postgres


class User:
    def __init__(self, id: int, full_name: str, username: str, email: str, phone: Optional[str] = None):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.email = email
        self.phone = phone

    def register(self, password_hash: str):
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (full_name, creation_datetime)
                VALUES (%s, %s) 
                RETURNING id;
            """, (self.full_name, datetime.now()))
            user_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO useremails (user_id, email, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s);
            """, (user_id, self.email, 1, datetime.now(), None))

            cursor.execute("""
                INSERT INTO userphones (user_id, phone, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s);
            """, (user_id, self.phone, 1, datetime.now(), None))

            cursor.execute("""
                INSERT INTO usernames (user_id, username, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s);
            """, (user_id, self.username, 1, datetime.now(), None))

            cursor.execute("""
                INSERT INTO userpasswords (user_id, password, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s);
            """, (user_id, password_hash, 1, datetime.now(), None))
            conn.commit()
        except:
            return False
        finally:
            conn.close()

        if not user_id:
            return False
        
        self.id = user_id

        if self.id == 1:
            if not self.set_privilege(privilege="administrator"):
                return False
        else:
            if not self.set_privilege(privilege="basic"):
                return False

        return True
    
    def update(self, update_information: dict):
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            if "email" in update_information:
                cursor.execute("""
                    UPDATE useremails
                        SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), update_datetime = %s
                    WHERE 
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    user_id = %s;
                """, (datetime.now(), self.id))

                cursor.execute("""
                    INSERT INTO useremails (user_id, email, status_id, creation_datetime, update_datetime)
                    VALUES (%s, %s, %s, %s, %s);
                """, (self.id, update_information["email"], 1, datetime.now(), None))

                self.email = update_information["email"]

            if "phone" in update_information:
                cursor.execute("""
                    UPDATE userphones
                        SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), update_datetime = %s
                    WHERE 
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    user_id = %s;
                """, (datetime.now(), self.id))

                cursor.execute("""
                    INSERT INTO userphones (user_id, phone, status_id, creation_datetime, update_datetime)
                    VALUES (%s, %s, %s, %s, %s);
                """, (self.id, update_information["phone"], 1, datetime.now(), None))

                self.phone = update_information["phone"]

            if "username" in update_information:
                cursor.execute("""
                    UPDATE usernames
                        SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), update_datetime = %s
                    WHERE 
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    user_id = %s;
                """, (datetime.now(), self.id))

                cursor.execute("""
                    INSERT INTO usernames (user_id, username, status_id, creation_datetime, update_datetime)
                    VALUES (%s, %s, %s, %s, %s);
                """, (self.id, update_information["username"], 1, datetime.now(), None))

                self.username = update_information["username"]

            if "password" in update_information:
                cursor.execute("""
                    UPDATE userpasswords
                        SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), update_datetime = %s
                    WHERE 
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    user_id = %s;
                """, (datetime.now(), self.id))

                cursor.execute("""
                    INSERT INTO userpasswords (user_id, password, status_id, creation_datetime, update_datetime)
                    VALUES (%s, %s, %s, %s, %s);
                """, (self.id, update_information["password"], 1, datetime.now(), None))

            conn.commit()
        except:
            return False
        finally:
            conn.close()

        return True
    
    def inactivate(self):
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id FROM userprivileges
                WHERE privilege = 'inactive';
            """)
            fetch = cursor.fetchone()
            if not fetch:
                conn.close()
                return False
            privilege_id = int(fetch[0])

            cursor.execute("""
                UPDATE useraccess
                    SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), update_datetime = %s
                WHERE
                status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                user_id = %s;
            """, (datetime.now(), self.id))

            cursor.execute("""
                INSERT INTO useraccess (user_id, privilege_id, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s);
            """, (self.id, privilege_id, 1, datetime.now(), None))

            conn.commit()
        except:
            return False
        finally:
            conn.close()

        return True

    def set_privilege(self, privilege: str):
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id FROM userprivileges
                WHERE privilege = %s;
            """, (privilege,))
            fetch = cursor.fetchone()
            if not fetch:
                conn.close()
                return False
            privilege_id = int(fetch[0])

            if privilege == "basic":
                cursor.execute("""
                    UPDATE useraccess
                        SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), update_datetime = %s
                    WHERE 
                    privilege_id = (SELECT id FROM userprivileges WHERE privilege = 'inactive') AND 
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    user_id = %s;
                """, (datetime.now(), self.id))
                
            cursor.execute("""
                INSERT INTO useraccess (user_id, privilege_id, status_id, creation_datetime, update_datetime)
                VALUES (%s, %s, %s, %s, %s);
            """, (self.id, privilege_id, 1, datetime.now(), None))
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
            cursor.execute("""
                UPDATE useraccess
                    SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), update_datetime = %s
                WHERE 
                privilege_id = (SELECT id FROM userprivileges WHERE privilege = %s) AND 
                status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                user_id = %s;
            """, (datetime.now(), privilege, self.id))
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
            cursor.execute("""
                SELECT userprivileges.privilege FROM useraccess
                INNER JOIN userprivileges ON useraccess.privilege_id = userprivileges.id
                WHERE 
                useraccess.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND
                useraccess.user_id = %s;
            """, (self.id,))
            fetch = cursor.fetchall()
            privileges_list = [item[0] for item in fetch]
            if not fetch:
                return []
        except:
            return []
        finally:
            conn.close()

        return privileges_list
    
    def full_name_exists(self):
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute("SELECT full_name FROM users WHERE full_name = %s;", (self.full_name,))
        fetch = cursor.fetchone()
        conn.close()
        if not fetch:
            return False

        return True

    def username_exists(self):
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username FROM usernames 
            WHERE 
            status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
            username = %s;
        """, 
        (self.username,))
        fetch = cursor.fetchone()
        conn.close()
        if not fetch:
            return False

        return True

    def email_exists(self):
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT email FROM useremails 
            WHERE 
            status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
            email = %s;
        """, 
        (self.email,))
        fetch = cursor.fetchone()
        conn.close()
        if not fetch:
            return False

        return True
    
def get_user(user_information: dict):

    conn = connect_to_postgres()
    cursor = conn.cursor()
    if "user_id" in user_information:
        cursor.execute("""
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
            useremails.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND
            userphones.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND
            usernames.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
            users.id = %s;
        """, 
        (user_information["user_id"],))
        user_data = cursor.fetchone()
    elif "username" in user_information:
        cursor.execute("""
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
            useremails.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND
            userphones.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND
            usernames.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
            usernames.username = %s;
        """, 
        (user_information["username"],))
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