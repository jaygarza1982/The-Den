import sqlite3
import random
import os
import hashlib
import time
import re
import CommentRW
import threading
from flask import make_response, redirect, session, render_template_string

#db_lock = threading.Lock()

class user:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.following_file_path = 'users/' + self.username + '/following'

    def authUser(self, db_lock):
        resp = ''
        try:
            while db_lock.locked():
                continue
            
            db_lock.acquire()
            connection = sqlite3.connect('users.db')
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE username=?;", (self.username,))

            credentials = cursor.fetchone()
            verify = None
            if not credentials == None:
                #Hash password 
                verify = self.get_hash(self.password, credentials[2]) == credentials[1]

                cookie = str(random.uniform(0, 10000000))
                session[cookie] = str(self.username)
                resp = make_response(redirect('/home'))
                resp.set_cookie('logintoken', cookie)
                # return resp if self.username == credentials[0] and self.password == credentials[1] else 'Invalid credentials'
            
        finally:
            db_lock.release()

        return resp if verify else 'Invalid credentials'

    def register(self, password_confirm):
        resp = ''
        # Check to see if user exists in database
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        #TODO: Fix SQL injection
        cursor.execute("SELECT * FROM users WHERE username='" + str(self.username) + "';")
        rows = cursor.fetchall()
        if (len(rows) == 0):
            if self.password != password_confirm:
                return 'Passwords do not match.'
            #print("User has not yet registered.")
            hash_tuple = self.get_hash_and_salt(self.password)
            hashed_pass = hash_tuple[0]
            salt = hash_tuple[1]
            cursor.execute("INSERT INTO users VALUES (?, ?, ?);", (self.username, hashed_pass, salt,))
            connection.commit()
            connection.close()

            user_folder = 'users/' + self.username
            os.mkdir(user_folder)

            following_file = open(user_folder + '/' + 'following', 'w')
            following_file.write(self.username)
            following_file.close()

            self.make_post('This is the first post by ' + self.username + '.')
        else:
            print("The username is not available.")
            return 'The username ' + self.username + ' is not available'

        resp = render_template_string(open('public/templates/index-template.html', 'r').read(), new_user=self.username)

        return resp

    def make_post(self, caption):
        #Append random number for security
        #post-time-random_number
        post_stamp = 'post-' + str(time.time()) + '-' + str(random.uniform(0, 999999))
        post_path = 'users/' + self.username + '/' + post_stamp
        os.mkdir(post_path)

        caption_file = open(post_path + '/caption', 'w')
        caption_file.write(caption)
        caption_file.close()

        comments_file = open(post_path + '/comments', 'w')
        comments_file.close()

    def get_posts(self):
        posts = [{}]
        count = 0
        for file in os.listdir('users/' + self.username + '/'):

            if file.startswith('post'):
                posts[count]['user'] = self.username
                posts[count]['post_text'] = open('users/' + self.username + '/' + file + '/caption', 'r').read()
                posts[count]['pic_url'] = 'users/' + self.username + '/pic.jpg'
                posts[count]['comments'] = self.get_post_comments(self.username + '/' + file)
                posts[count]['id'] = file

                count += 1
                posts.append({})
        return posts

    def get_post_comments(self, post_stamp):
        comments = [{}]

        comment_file = open('users/' + post_stamp + '/comments', 'r', encoding='utf-8').read().strip()
        lines = comment_file.split('\n')

        count = 0
        if lines[0] != '':
            for line in lines:
                current = line
                user = re.findall("<USER>(.*?)</USER>", current, re.DOTALL)[0]
                text = re.findall("<COMMENT>(.*?)</COMMENT>", current, re.DOTALL)[0]
                comments[count]['user'] = user
                comments[count]['text'] = text
                if (count < len(lines)-1):
                    comments.append({}) #Add a new dict
                    count += 1
            return comments
        return {}

    def make_comment(self, commentRW, username, post_id, comment0):
        commentRW.queue.put((self.username, username, post_id, comment0))
        # comment_file_path = 'users/' + username + '/' + post_id + '/comments'
        # # comment_file_contents = open(comment_file_path, 'r', encoding='utf-8').read().strip()
        
        # comment = '\n<USER>' + self.username + '</USER><COMMENT>' + comment0 + '</COMMENT><LIKES></LIKES>'


        # with open(comment_file_path, 'a') as comment_file:
        #     comment_file.write(comment)

    def follow_user(self, user_to_follow):
        with open(self.following_file_path, 'a') as following_file:
            following_file.write('\n' + user_to_follow)

    def get_following(self):
        #Return a set of users that the user is following
        return set(open(self.following_file_path, 'r').read().split('\n'))

    def is_following(self, username):
        return username in self.get_following()

    def unfollow_user(self, username):
        current_following = self.get_following()
        current_following.remove(username)
        current_following = list(current_following)

        with open(self.following_file_path, 'w') as following_file:
            for follower in current_following:
                following_file.write(follower + '\n')

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