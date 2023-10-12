from database.dbmanagement.dbgeneral.status_table import *
from database.dbmanagement.dbuser.users_table import *
from database.dbmanagement.dbuser.usernames_table import *
from database.dbmanagement.dbuser.emails_table import *
from database.dbmanagement.dbuser.phones_table import *
from database.dbmanagement.dbuser.passwords_table import *
from database.dbmanagement.dbuser.privileges_table import *
from database.dbmanagement.dbuser.useraccess_table import *


def create_dbtables():
    try:
        if not table_fkstatus_exists():
            if not create_table_fkstatus():
                print(f"Error when create table: fkstatus")
                return False
            
        status_list = ["valid", "invalid"]
        for status in status_list:
            add_status(status)

        if not table_users_exists():
            if not create_table_users():
                print(f"Error when create table: users")
                return False
            
        if not table_usernames_exists():
            if not create_table_usernames():
                print(f"Error when create table: usernames")
                return False
            
        if not table_useremails_exists():
            if not create_table_useremails():
                print(f"Error when create table: emails")
                return False
            
        if not table_userphones_exists():
            if not create_table_userphones():
                print(f"Error when create table: phones")
                return False
            
        if not table_userpasswords_exists():
            if not create_table_userpasswords():
                print(f"Error when create table: passwords")
                return False

        if not table_userprivileges_exists():
            if not create_table_userprivileges():
                print(f"Error when create table: userprivileges")
                return False
            
        privileges_list = ["administrator", "manager", "basic", "inactive"]
        for privilege in privileges_list:
            add_privilege(privilege)

        if not table_useraccess_exists():
            if not create_table_useraccess():
                print(f"Error when create table: useraccess")
                return False
    except Exception as e:
        print(f"Error when create table: {e}")
        return False

    return True

