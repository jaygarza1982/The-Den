import sqlite3
import os
import hashlib


class SQLWriter:
    def __init__(self, db_lock, database_path):
        self.db_lock = db_lock
        self.database_path = database_path

    def fetch_username(self, username):
        try:
            while self.db_lock.locked():
                continue
            self.db_lock.acquire()

            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()

            cursor.execute(
                "SELECT username, password, salt FROM users WHERE username=?;", (username,))

            fetched = cursor.fetchall()
            return fetched
        finally:
            self.db_lock.release()

    def fetch_all_usernames(self, prefix):
        #TODO: Use wildcards
        usernames_query = self.query_all('SELECT username FROM users WHERE 1=1;', tuple())

        usernames = []
        for username in usernames_query:
            if username[0].startswith(prefix):
                usernames.append(username[0])

        return usernames

    def insert_username(self, username, password):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        hash_tuple = self.get_hash_and_salt(password)
        hashed_pass = hash_tuple[0]
        salt = hash_tuple[1]
        cursor.execute("INSERT INTO users (username, password, salt) VALUES (?, ?, ?);",
                       (username, hashed_pass, salt,))
        connection.commit()
        connection.close()

    def insert_post(self, username, caption, date):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO posts (uid, caption, date) VALUES ((SELECT uid FROM users WHERE username=?), ?, ?);
        """, (username, caption, date,))

        connection.commit()
        connection.close()

    def execute_statement(self, statement, args):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute(statement, args)

        connection.commit()
        connection.close()

    def execute_many(self, statement, args):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.executemany(statement, args)

        connection.commit()
        connection.close()
    

    def query_all(self, statement, args):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute(statement, args)
        fetched = cursor.fetchall()
        connection.close()

        return fetched

    def query(self, statement, args):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        cursor.execute(statement, args)
        fetched = cursor.fetchone()
        connection.close()

        return fetched[0]

    # Get a hash and a salt
    def get_hash_and_salt(self, password):
        salt = os.urandom(128)  # Remember this

        key = hashlib.pbkdf2_hmac(
            'sha256',  # The hash digest algorithm for HMAC
            password.encode('utf-8'),  # Convert the password to bytes
            salt,  # Provide the salt
            100000,  # It is recommended to use at least 100,000 iterations of SHA-256
            dklen=128  # Get a 128 byte key
        )

        return (key, salt,)

    # Get a hash with a salt
    def get_hash(self, password, salt):
        hash = hashlib.pbkdf2_hmac(
            'sha256',  # The hash digest algorithm for HMAC
            password.encode('utf-8'),  # Convert the password to bytes
            salt,  # Provide the salt
            100000,  # It is recommended to use at least 100,000 iterations of SHA-256
            dklen=128  # Get a 128 byte key
        )

        return hash
