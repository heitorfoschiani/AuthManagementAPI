from .tables.status_table import create_table_fkstatus, add_status


def initialize_database():
    try:
        create_table_fkstatus()
        status_list = ["valid", "invalid"]
        list(add_status(status) for status in status_list)
    except Exception as e:
        raise Exception(f"An error occored when create fkstatus table: {e}")