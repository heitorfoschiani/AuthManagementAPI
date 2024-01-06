import logging

from database.dbmanagement.dbgeneral.status_table import *
from database.dbmanagement.dbuser.users_table import *
from database.dbmanagement.dbuser.usernames_table import *
from database.dbmanagement.dbuser.useremails_table import *
from database.dbmanagement.dbuser.userphones_table import *
from database.dbmanagement.dbuser.userpasswords_table import *
from database.dbmanagement.dbuser.userprivileges_table import *
from database.dbmanagement.dbuser.useraccess_table import *
from api.namespaces.privilege.objects import Privilege


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

def create_dbtables():
    # general tables
    if not table_exists("fkstatus"):
        create_table_fkstatus()
        
    status_list = ["valid", "invalid"]
    all(add_status(status) for status in status_list)


    # user tables
    if not table_exists("users"):
        create_table_users()
        
    if not table_exists("usernames"):
        create_table_usernames()
        
    if not table_exists("useremails"):
        create_table_useremails()
        
    if not table_exists("userphones"):
        create_table_userphones()
        
    if not table_exists("userpasswords"):
        create_table_userpasswords()

    if not table_exists("userprivileges"):
        create_table_userprivileges()

    privileges_list = ["administrator", "manager", "basic", "inactive"]
    all(Privilege(name).register() for name in privileges_list)

    if not table_exists("useraccess"):
        create_table_useraccess()

