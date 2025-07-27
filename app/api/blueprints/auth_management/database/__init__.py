from .tables.fkusers import create_table_fkusers
from .tables.fkuserprivileges import create_table_fkuserprivileges
from .tables.useraccess import create_table_useraccess
from .tables.useremails import create_table_useremails
from .tables.usernames import create_table_usernames
from .tables.userpasswords import create_table_userpasswords
from .tables.userphones import create_table_userphones
from app.api.blueprints.auth_management.namespaces.privilege import Privilege


def initialize_database(app):
    postgres_connection = app.config["postgres_connection"]

    try:
        create_table_fkusers(postgres_connection)
    except Exception as e:
        raise Exception(f"An error occored when create users table: {e}")
    
    try:
        create_table_fkuserprivileges(postgres_connection)
        privileges_list = ["administrator", "manager", "basic", "inactive"]
        list(Privilege(name).register(postgres_connection) for name in privileges_list)
    except Exception as e:
        raise Exception(f"An error occored when create fkuserprivileges table: {e}")
    
    try:
        create_table_useraccess(postgres_connection)
    except Exception as e:
        raise Exception(f"An error occored when create useraccess table: {e}")
    
    try:
        create_table_useremails(postgres_connection)
    except Exception as e:
        raise Exception(f"An error occored when create useremails table: {e}")
    
    try:
        create_table_usernames(postgres_connection)
    except Exception as e:
        raise Exception(f"An error occored when create usernames table: {e}")
    
    try:
        create_table_userpasswords(postgres_connection)
    except Exception as e:
        raise Exception(f"An error occored when create userpasswords table: {e}")
    
    try:
        create_table_userphones(postgres_connection)
    except Exception as e:
        raise Exception(f"An error occored when create _userphones table: {e}")