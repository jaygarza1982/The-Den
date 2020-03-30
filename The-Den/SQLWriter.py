import mysql.connector
import os
import hashlib

class SQLWriter:
    def __init__(self, database_path):
        self.database_path = database_path
        self.sql_pass = os.getenv('sqlpass')

    def query_all(self, statement, args):
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            passwd = self.sql_pass,
            database = self.database_path
        )
        cursor = db.cursor()

        cursor.execute(statement, args)
        fetched = cursor.fetchall()
        db.close()

        return fetched

    def query(self, statement, args):
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            passwd = self.sql_pass,
            database = self.database_path
        )
        cursor = db.cursor()

        cursor.execute(statement, args)
        fetched = cursor.fetchone()
        db.close()

        return fetched[0]

    def fetch_all_usernames(self, prefix):
        #TODO: Use wildcards
        usernames_query = self.query_all('SELECT Username FROM Users WHERE 1=1;', tuple())

        usernames = []
        for username in usernames_query:
            if username[0].startswith(prefix):
                usernames.append(username[0])

        return usernames
    
    def execute_statement(self, statement, args):
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            passwd = self.sql_pass,
            database = self.database_path
        )
        cursor = db.cursor()

        cursor.execute(statement, args)

        db.commit()
        db.close()

    def fetch_username(self, username):
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            passwd = self.sql_pass,
            database = self.database_path
        )
        cursor = db.cursor()

        cursor.execute(
            "SELECT Username, Password, Salt FROM Users WHERE Username=%s;", (username,))

        fetched = cursor.fetchall()
        return fetched

    def insert_username(self, username, password):
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            passwd = self.sql_pass,
            database = self.database_path
        )
        cursor = db.cursor()

        hash_tuple = self.get_hash_and_salt(password)
        hashed_pass = hash_tuple[0]
        salt = hash_tuple[1]
        cursor.execute("INSERT INTO Users (Username, Password, Salt) VALUES (%s, %s, %s);",
                       (username, hashed_pass, salt,))
        db.commit()
        db.close()

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
