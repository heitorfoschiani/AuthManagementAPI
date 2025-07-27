from .tables.fkstatus import create_table_fkstatus, add_status


def initialize_database(app):
    postgres_connection = app.config["postgres_connection"]
    
    try:
        create_table_fkstatus(postgres_connection)
        status_list = ["valid", "invalid"]
        list(add_status(status, postgres_connection) for status in status_list)
    except Exception as e:
        raise Exception(f"An error occored when create fkstatus table: {e}")