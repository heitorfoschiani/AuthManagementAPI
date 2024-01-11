from .dbmanagement.dbgeneral.status_table import *
from .dbmanagement.dbuser.users_table import *
from .dbmanagement.dbuser.usernames_table import *
from .dbmanagement.dbuser.useremails_table import *
from .dbmanagement.dbuser.userphones_table import *
from .dbmanagement.dbuser.userpasswords_table import *
from .dbmanagement.dbuser.userprivileges_table import *
from .dbmanagement.dbuser.useraccess_table import *
from app.api.namespaces.privilege import Privilege


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