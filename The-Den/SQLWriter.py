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

    def fetch_username(self, username):
        try:
            while self.db_lock.locked():
                continue
            self.db_lock.acquire()
            
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE username=?;", (username,))

            return cursor.fetchone()
        finally:
            self.db_lock.release()