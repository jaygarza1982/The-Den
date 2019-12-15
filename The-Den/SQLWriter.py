import sqlite3

class SQLWriter:
    def __init__(self, db_lock, database_path, table):
        self.db_lock = db_lock
        self.database_path = database_path
        self.table = table

    def create_users_table(self):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE users(
                username VARCHAR(24),
                password BINARY(128),
                hash BINARY(128)
            );
        """)
        
        connection.commit()
        connection.close()