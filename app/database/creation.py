from .connection import PostgresConnection


class PostgresTableCreator:
    def __init__(self, postgres_connection: PostgresConnection, table_name: str):
        self.table_name = table_name
        self.postgres_connection = postgres_connection

    def create_table(self, table_columns: list, foreign_key: bool=False):
        if self._table_exists():
            return None
        
        table_columns.append(("creation_datetime", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
        
        if foreign_key:
            table_columns.insert(0, ("id", "SERIAL PRIMARY KEY"))
        else:
            table_columns.append(("status_id", f"INTEGER NOT NULL REFERENCES fkstatus(id) DEFAULT {self._get_valid_status_id()}"))
            table_columns.append(("status_update_datetime", "TIMESTAMP"))

        try:
            create_table_query = self._create_query(table_columns)
        except Exception as e:
            raise Exception(f"Unable to get create table query: {e}")
        
        postgres_connection = self.postgres_connection
        conn = postgres_connection.connect()
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
        
        postgres_connection = self.postgres_connection
        conn = postgres_connection.connect()
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
    
    def _get_valid_status_id(self):
        postgres_connection = self.postgres_connection
        conn = postgres_connection.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id FROM fkstatus 
                WHERE status = 'valid';
            """)
            fetch = cursor.fetchone()
            valid_status_id = fetch[0]
        except Exception as e:
            raise Exception(f"Unable to get valid status id: {e}")
        finally:
            conn.close()

        if not valid_status_id:
            raise Exception(f"No valid status id")

        return valid_status_id