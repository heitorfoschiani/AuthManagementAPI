from database.dbconnection import connect_to_postgres

class userinfos_db:
    # Table "userinfos" management
    def table_userinfos_exists():
        # connecting to the database
        conn = connect_to_postgres()
        cursor = conn.cursor()

        # checking if the table "userinfos" exists
        cursor.execute(
            '''
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_name = 'userinfos'
                );
            '''
        )

        if not cursor.fetchone()[0]:
            conn.close()
            return False

        conn.close()
        return True

    def create_table_userinfos():
        # connecting to the database
        conn = connect_to_postgres()
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''
                    CREATE TABLE userinfos (
                        user_id SERIAL PRIMARY KEY, 
                        full_name VARCHAR(255), 
                        email VARCHAR(255), 
                        phone VARCHAR(20), 
                        username VARCHAR(255), 
                        password TEXT,
                        creation_datetime TIMESTAMP
                    );
                '''
            )
            conn.commit()
            
            return True
        except:
            return False
        finally:
            conn.close()