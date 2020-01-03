import sqlite3
import os


class DBCreator:
    def __init__(self, filename):
        self.filename = filename

    def create(self):
        # If the database file does not exist, create the file
        if self.filename not in os.listdir():
            open(self.filename, 'w').close()

        connection = sqlite3.connect(self.filename)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE users (
                uid INTEGER PRIMARY KEY,
                username VARCHAR(24),
                password BINARY(128),
                salt BINARY(128)
            );
        """)

        cursor.execute("""
            CREATE TABLE posts (
                pid INTEGER PRIMARY KEY,
                uid INTEGER,
                caption VARCHAR(500),
                date TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE follows (
                fid INTEGER PRIMARY KEY,
                uid INTEGER,
                followed_user_id INTEGER
            );
        """)

        cursor.execute("""
            CREATE TABLE comments (
                cid INTEGER PRIMARY KEY,
                uid INTEGER,
                pid INTEGER,
                comment varchar(500)
            );
        """)

        cursor.execute("""
            CREATE TABLE likes (
                lid INTEGER PRIMARY KEY,
                pid INTEGER,
                uid INTEGER
            );
        """)

        cursor.execute("""
            CREATE TABLE RegexSettings (
                lid INTEGER PRIMARY KEY,
                pid INTEGER,
                uid INTEGER
            );
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX idx_users_username ON users (username);
        """)

        cursor.execute("""
            CREATE INDEX idx_posts_uid ON posts (uid);
        """)

        cursor.execute("""
            CREATE INDEX idx_follows_uid ON follows (uid);
        """)

        cursor.execute("""
            CREATE INDEX idx_comments_pid ON comments (pid);
        """)

        cursor.execute("""
            CREATE INDEX idx_likes_pid ON likes (pid);
        """)

        connection.commit()
