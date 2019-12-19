import sqlite3
import os
import hashlib

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

            return cursor.fetchall()
        finally:
            self.db_lock.release()
    
    def insert_username(self, username, password):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        hash_tuple = self.get_hash_and_salt(password)
        hashed_pass = hash_tuple[0]
        salt = hash_tuple[1]
        cursor.execute("INSERT INTO users VALUES (?, ?, ?);", (username, hashed_pass, salt,))
        connection.commit()
        connection.close()
    
    #Get a hash and a salt
    def get_hash_and_salt(self, password):
        salt = os.urandom(128) # Remember this

        key = hashlib.pbkdf2_hmac(
            'sha256', # The hash digest algorithm for HMAC
            password.encode('utf-8'), # Convert the password to bytes
            salt, # Provide the salt
            100000, # It is recommended to use at least 100,000 iterations of SHA-256 
            dklen=128 # Get a 128 byte key
        )

        return (key, salt,)

    #Get a hash with a salt
    def get_hash(self, password, salt):
        hash = hashlib.pbkdf2_hmac(
            'sha256', # The hash digest algorithm for HMAC
            password.encode('utf-8'), # Convert the password to bytes
            salt, # Provide the salt
            100000, # It is recommended to use at least 100,000 iterations of SHA-256 
            dklen=128 # Get a 128 byte key
        )

        return hash