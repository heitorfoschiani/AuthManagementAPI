from .dbmanagement.dbgeneral.status_table import *
from .dbmanagement.dbuser.users_table import *
from .dbmanagement.dbuser.usernames_table import *
from .dbmanagement.dbuser.useremails_table import *
from .dbmanagement.dbuser.userphones_table import *
from .dbmanagement.dbuser.userpasswords_table import *
from .dbmanagement.dbuser.userprivileges_table import *
from .dbmanagement.dbuser.useraccess_table import *
from app.api.blueprints.auth_management.namespaces.privilege import Privilege


class PostgresTableCreator:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def create_table(self, table_columns: list):
        if not self._table_exists():
            try:
                create_table_query = self._create_query(table_columns)
            except Exception as e:
                raise Exception(f"Unable to get create table query: {e}")
            
            conn = connect_to_postgres()
            cursor = conn.cursor()

            try:
                cursor.execute(create_table_query)
                conn.commit()
            except Exception as e:
                raise Exception(f"Unable to create {self.table_name} table: {e}")
            finally:
                conn.close()
    
    def _create_query(self, table_columns: list):
        """
        Generates a SQL query for creating a table in PostgreSQL.

        Parameters:
        - table_columns (list of tuples): A list where each tuple contains the column name and column type.

        Returns:
        - str: A SQL query string for creating the table.
        """

        query = f"CREATE TABLE {self.table_name} ("

        column_definitions = []
        for name, type in table_columns:
            column_definitions.append(f"{name} {type}")
        
        query += ", ".join(column_definitions)
        query += ");"
        
        return query

    def _table_exists(self):
        """
        Check if a table already exists into the database

        Returns:
        - bool: True or False for exists or not.        
        """
        
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_name = '{self.table_name}'
                );
            """)
            fetch = cursor.fetchone()
            exists = fetch[0]
        except Exception as e:
            raise Exception(f"Unable to check if table: '{self.table_name}' exists in database: {e}")
        finally:
            conn.close()

        return exists

def initialize_database():
    tables = {
        "fkstatus": (create_table_fkstatus, initialize_fkstatus),
        "users": (create_table_users, None),
        "usernames": (create_table_usernames, None),
        "useremails": (create_table_useremails, None),
        "userphones": (create_table_userphones, None),
        "userpasswords": (create_table_userpasswords, None),
        "userprivileges": (create_table_userprivileges, initialize_privileges),
        "useraccess": (create_table_useraccess, None)
    }

    for table_name, (create_table_func, init_table_func) in tables.items():
        try:
            if not table_exists(table_name):
                create_table_func()
            if init_table_func:
                init_table_func()
        except Exception as e:
            raise Exception(f"Error initializing table {table_name}: {e}")

def table_exists(table_name: str):
    # This function check if a table already exists into the database, returning True or False
    
    conn = connect_to_postgres()
    cursor = conn.cursor()

    try:
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = '{table_name}'
            );
        """)
        fetch = cursor.fetchone()
        exists = fetch[0]
    except Exception as e:
        raise Exception(f"Unable to check if table: '{table_name}' exists in database: {e}")
    finally:
        conn.close()

    return exists

def initialize_fkstatus():
    status_list = ["valid", "invalid"]
    list(add_status(status) for status in status_list)

def initialize_privileges():
    privileges_list = ["administrator", "manager", "basic", "inactive"]
    list(Privilege(name).register() for name in privileges_list)