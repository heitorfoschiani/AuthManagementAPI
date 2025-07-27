from typing import Optional
from datetime import datetime

from app.database.connection import PostgresConnection


class User:
    def __init__(self, id: int, full_name: str, username: str, email: str, phone: Optional[str] = None):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.email = email
        self.phone = phone

    def register(self, password_hash: str, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO fkusers (full_name)
                VALUES (%s) 
                RETURNING id;
            """, (self.full_name,))
            user_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO useremails (user_id, email)
                VALUES (%s, %s);
            """, (user_id, self.email))

            cursor.execute("""
                INSERT INTO userphones (user_id, phone)
                VALUES (%s, %s);
            """, (user_id, self.phone))

            cursor.execute("""
                INSERT INTO usernames (user_id, username)
                VALUES (%s, %s);
            """, (user_id, self.username))

            cursor.execute("""
                INSERT INTO userpasswords (user_id, password)
                VALUES (%s, %s);
            """, (user_id, password_hash))
            
            conn.commit()
        except Exception as e:
            raise Exception(f"Unable to register user: {e}")
        finally:
            cursor.close()
            conn.close()
        
        self.id = user_id

        if self.id == 1:
            self.set_privilege("administrator", postgres_connection)
        else:
            self.set_privilege("basic", postgres_connection)
    
    def update(self, update_information: dict, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            if "email" in update_information:
                cursor.execute("""
                    UPDATE useremails
                        SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), status_update_datetime = %s
                    WHERE 
                        status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        user_id = %s;
                """, (datetime.now(), self.id))

                cursor.execute("""
                    INSERT INTO useremails (user_id, email)
                    VALUES (%s, %s);
                """, (self.id, update_information["email"]))

                self.email = update_information["email"]

            if "phone" in update_information:
                cursor.execute("""
                    UPDATE userphones
                        SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), status_update_datetime = %s
                    WHERE 
                        status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        user_id = %s;
                """, (datetime.now(), self.id))

                cursor.execute("""
                    INSERT INTO userphones (user_id, phone)
                    VALUES (%s, %s);
                """, (self.id, update_information["phone"]))

                self.phone = update_information["phone"]

            if "username" in update_information:
                cursor.execute("""
                    UPDATE usernames
                        SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), status_update_datetime = %s
                    WHERE 
                        status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        user_id = %s;
                """, (datetime.now(), self.id))

                cursor.execute("""
                    INSERT INTO usernames (user_id, username)
                    VALUES (%s, %s);
                """, (self.id, update_information["username"]))

                self.username = update_information["username"]

            if "password" in update_information:
                cursor.execute("""
                    UPDATE userpasswords
                        SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), status_update_datetime = %s
                    WHERE 
                        status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        user_id = %s;
                """, (datetime.now(), self.id))

                cursor.execute("""
                    INSERT INTO userpasswords (user_id, password)
                    VALUES (%s, %s);
                """, (self.id, update_information["password"]))

            conn.commit()
        except Exception as e:
            raise Exception(f"Unable to update user information: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def inactivate(self, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id FROM fkuserprivileges
                WHERE privilege = 'inactive';
            """)
            fetch = cursor.fetchone()
            if not fetch:
                conn.close()
                raise Exception(f"Id not known in database for 'inactive' privilege")
            
            privilege_id = int(fetch[0])

            cursor.execute("""
                UPDATE useraccess
                    SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), status_update_datetime = %s
                WHERE
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    user_id = %s;
            """, (datetime.now(), self.id))

            cursor.execute("""
                INSERT INTO useraccess (user_id, privilege_id)
                VALUES (%s, %s);
            """, (self.id, privilege_id))

            conn.commit()
        except Exception as e:
            raise Exception(f"Unable to inactive user: {e}")
        finally:
            cursor.close()
            conn.close()

    def set_privilege(self, privilege: str, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id FROM fkuserprivileges
                WHERE privilege = %s;
            """, (privilege,))
            fetch = cursor.fetchone()
            if not fetch:
                raise Exception("Non-existing privilege")
            
            privilege_id = int(fetch[0])

            if privilege == "basic":
                cursor.execute("""
                    UPDATE useraccess
                        SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), status_update_datetime = %s
                    WHERE 
                        privilege_id = (SELECT id FROM fkuserprivileges WHERE privilege = 'inactive') AND 
                        status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        user_id = %s;
                """, (datetime.now(), self.id))
                
            cursor.execute("""
                INSERT INTO useraccess (user_id, privilege_id)
                VALUES (%s, %s);
            """, (self.id, privilege_id))
            conn.commit()
        except Exception as e:
            raise Exception(f"Unable to set user the '{privilege}' privilege: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def delete_privilege(self, privilege: str, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE useraccess
                    SET status_id = (SELECT id FROM fkstatus WHERE status = 'invalid'), status_update_datetime = %s
                WHERE 
                    privilege_id = (SELECT id FROM fkuserprivileges WHERE privilege = %s) AND 
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    user_id = %s;
            """, (datetime.now(), privilege, self.id))
            conn.commit()
        except Exception as e:
            raise Exception(f"Unable to remove the '{privilege}' privilege from user: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def privileges(self, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT fkuserprivileges.privilege FROM useraccess
                INNER JOIN fkuserprivileges ON useraccess.privilege_id = fkuserprivileges.id
                WHERE 
                    useraccess.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    useraccess.user_id = %s;
            """, (self.id,))
            fetch = cursor.fetchall()
            privileges_list = [item[0] for item in fetch]
            if not fetch:
                return []
        except Exception as e:
            return []
        finally:
            cursor.close()
            conn.close()

        return privileges_list
    
    def get_password_hash(self, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT password FROM userpasswords 
                WHERE 
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    user_id = %s;
            """, (self.id,))
            user_password_hash = cursor.fetchone()[0]
        except:
            return None
        finally:
            cursor.close()
            conn.close()

        return user_password_hash
    
    def full_name_exists(self, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT full_name FROM fkusers WHERE full_name = %s;
            """, (self.full_name,))
            fetch = cursor.fetchone()
        except:
            raise Exception("Unable to check if full_name already exists")
        finally:
            cursor.close()
            conn.close()

        if not fetch:
            return False

        return True

    def username_exists(self, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT username FROM usernames 
                WHERE 
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    username = %s;
            """, (self.username,))
            fetch = cursor.fetchone()
        except:
            raise Exception("Unable to check if username already exists")
        finally:
            cursor.close()
            conn.close()

        if not fetch:
            return False

        return True

    def email_exists(self, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT email FROM useremails 
                WHERE 
                    status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                    email = %s;
            """, (self.email,))
            fetch = cursor.fetchone()
        except:
            raise Exception("Unable to check if email already exists")
        finally:
            cursor.close()
            conn.close()

        if not fetch:
            return False

        return True
    
    @staticmethod
    def get(user_information: dict, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            if "user_id" in user_information:
                cursor.execute("""
                    SELECT 
                        fkusers.id, 
                        fkusers.full_name, 
                        useremails.email, 
                        userphones.phone, 
                        usernames.username 
                    FROM fkusers
                    LEFT JOIN useremails ON useremails.user_id = fkusers.id
                    LEFT JOIN userphones ON userphones.user_id = fkusers.id
                    LEFT JOIN usernames ON usernames.user_id = fkusers.id
                    WHERE 
                        useremails.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        userphones.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        usernames.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        fkusers.id = %s;
                """, 
                (user_information["user_id"],))
                user_data = cursor.fetchone()
            elif "username" in user_information:
                cursor.execute("""
                    SELECT 
                        fkusers.id, 
                        fkusers.full_name, 
                        useremails.email, 
                        userphones.phone, 
                        usernames.username
                    FROM fkusers
                    LEFT JOIN useremails ON useremails.user_id = fkusers.id
                    LEFT JOIN userphones ON userphones.user_id = fkusers.id
                    LEFT JOIN usernames ON usernames.user_id = fkusers.id
                    WHERE 
                        useremails.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        userphones.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        usernames.status_id = (SELECT id FROM fkstatus WHERE status = 'valid') AND 
                        usernames.username = %s;
                """, 
                (user_information["username"],))
                user_data = cursor.fetchone()
        except Exception as e:
            return None
        finally:
            cursor.close()
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