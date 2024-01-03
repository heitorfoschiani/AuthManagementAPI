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


def create_dbtables():
    try:
        # general tables
        if not table_fkstatus_exists():
            if not create_table_fkstatus():
                logging.error(f"Error when create table: fkstatus")
                return False
            
        status_list = ["valid", "invalid"]
        for status in status_list:
            add_status(status)

        # user tables
        if not table_users_exists():
            if not create_table_users():
                logging.error(f"Error when create table: users")
                return False
            
        if not table_usernames_exists():
            if not create_table_usernames():
                logging.error(f"Error when create table: usernames")
                return False
            
        if not table_useremails_exists():
            if not create_table_useremails():
                logging.error(f"Error when create table: emails")
                return False
            
        if not table_userphones_exists():
            if not create_table_userphones():
                logging.error(f"Error when create table: phones")
                return False
            
        if not table_userpasswords_exists():
            if not create_table_userpasswords():
                logging.error(f"Error when create table: passwords")
                return False

        # privilege tables
        if not table_userprivileges_exists():
            if not create_table_userprivileges():
                logging.error(f"Error when create table: userprivileges")
                return False
            
        privileges_list = ["administrator", "manager", "basic", "inactive"]
        for privileg_name in privileges_list:
            privilege = Privilege(privileg_name)
            if not privilege.register():
                return False

        if not table_useraccess_exists():
            if not create_table_useraccess():
                logging.error(f"Error when create table: useraccess")
                return False
            
    except Exception as e:
        logging.error(f"Error when create tables: {e}")

        return False

    return True

