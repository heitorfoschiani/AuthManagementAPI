from app.database.connection import PostgresConnection
from flask import current_app


class Privilege:
    def __init__(self, name):
        self.name = name

    def register(self, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT privilege FROM fkuserprivileges
                WHERE privilege = %s
            """, (self.name,))

            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO fkuserprivileges (privilege)
                    VALUES (%s);
                """, (self.name,))
                conn.commit()
        except Exception as e:
            raise Exception(f"Unable to register privilege: {e}")
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_privilege(privilege_name: str, postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT privilege FROM fkuserprivileges 
                WHERE privilege = %s;
            """, (privilege_name,)
            )
            fetch = cursor.fetchone()
            if not fetch:
                return None

            privilege = Privilege(fetch[0])
        except Exception as e:
            raise Exception(f"Unable to get '{privilege_name}' privilege: {e}")
        finally:
            cursor.close()
            conn.close()

        return privilege
    
    @staticmethod
    def get_user_privileges(postgres_connection: PostgresConnection):
        conn = postgres_connection.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    fkuserprivileges.privilege,
                    usernames.username
                FROM fkuserprivileges
                LEFT JOIN useraccess ON fkuserprivileges.id = useraccess.privilege_id AND useraccess.status_id = (SELECT id FROM fkstatus WHERE status = 'valid')
                LEFT JOIN usernames ON useraccess.user_id = usernames.user_id AND usernames.status_id = (SELECT id FROM fkstatus WHERE status = 'valid')
                ORDER BY fkuserprivileges.privilege;
            """)
            user_privileges = cursor.fetchall()
        except Exception as e:
            raise Exception(f"Unable to get user privileges: {e}")
        finally:
            cursor.close()
            conn.close()
        
        dict_user_privileges = {}
        for row in user_privileges:
            if not row[0] in dict_user_privileges:
                dict_user_privileges[row[0]] = []
            dict_user_privileges[row[0]].append(row[1])

        return dict_user_privileges
