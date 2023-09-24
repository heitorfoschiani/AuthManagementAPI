from database.dbmanagement.users_table import *
from database.dbmanagement.privileges_table import *
from database.dbmanagement.useraccess_table import *


def create_dbtables():
    try:
        if not table_users_exists():
            if not create_table_users():
                print(f'Error when create table: users')
                return False

        if not table_userprivileges_exists():
            if not create_table_userprivileges():
                print(f'Error when create table: users')
                return False
            
        privileges_list = ['adm', 'manager', 'basic']
        for privilege in privileges_list:
            add_privilege(privilege)

        if not table_useraccess_exists():
            if not create_table_useraccess():
                print(f'Error when create table: users')
                return False
    except Exception as e:
        print(f'Error when create table: {e}')
        return False

    return True

