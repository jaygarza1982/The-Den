import sqlite3
import random
import os
import time
# import datetime
import re
import threading
from SQLWriter import SQLWriter
from datetime import datetime
from flask import make_response, redirect, session, render_template

class user:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.following_file_path = 'sers/' + self.username + '/following'

    def authUser(self, sql_writer):
        resp = ''
        fetched = sql_writer.fetch_username(self.username)
        if len(fetched) != 0:
            credentials = fetched[0]

            verify = sql_writer.get_hash(self.password, credentials[2]) == credentials[1]
            if verify:
                #Create a secure random number for cookies
                cookie = self.username + '-' + str(os.urandom(32))
                session[cookie] = str(self.username)
                resp = make_response(redirect('/home'))
                resp.set_cookie('logintoken', cookie)
                return resp
        return 'Invalid credentials'

    def register(self, sql_writer, password_confirm):
        resp = ''
        #Check to see if user is in database
        if (len(sql_writer.fetch_username(self.username)) == 0):
            if self.password != password_confirm:
                return 'Passwords do not match.'
                
            sql_writer.insert_username(self.username, self.password)
            self.follow_user(sql_writer, self.username)

            self.save_regex_filter(sql_writer, '')

            self.make_post(sql_writer, 'This is the first post by ' + self.username + '.')
        else:
            print("The username is not available.")
            return 'The username ' + self.username + ' is not available'

        resp = render_template('index-template.html', new_user=self.username)

        return resp

    def like_post(self, sql_writer, pid):
        likes_from_user = sql_writer.query_all('SELECT UserID FROM Likes WHERE PostID=%s AND UserID=(SELECT UserID FROM Users WHERE Username=%s)', (pid, self.username,))

        if len(likes_from_user) == 0:
            sql_writer.execute_statement('INSERT INTO Likes (UserID, PostID) VALUES ((SELECT UserID FROM Users WHERE Username=%s), %s);', (self.username, pid,))
        else:
            sql_writer.execute_statement('DELETE FROM Likes WHERE UserID=(SELECT UserID FROM Users WHERE Username=%s) AND PostID=%s;', (self.username, pid,))

    def make_post(self, sql_writer, caption):
        sql_writer.execute_statement("""
            INSERT INTO Posts (UserID, Caption, Date) VALUES ((SELECT UserID FROM Users WHERE Username=%s), %s, %s);
        """, (self.username, caption, int(time.time()),))
        # sql_writer.insert_post(self.username, caption, int(time.time()))

    def edit_post(self, sql_writer, id, caption):
        sql_writer.execute_statement('UPDATE Posts SET Caption = %s WHERE PostID=%s;', (caption, id,))

    def delete_post(self, sql_writer, post_id):
        sql_writer.execute_statement('DELETE FROM Posts WHERE PostID=%s;', (post_id,))

    def get_posts(self, sql_writer, current_user, filters):
        posts = [{}]

        posts_query = sql_writer.query_all("""
            SELECT Caption, Date, PostID FROM Posts WHERE UserID=(SELECT UserID FROM Users WHERE Username=%s);
        """, (self.username,))

        for i in range(len(posts_query)):
            current_query = posts_query[i]

            caption = current_query[0]
            for regex_filter in filters:
                if re.match(regex_filter, caption):
                    caption = 'Filtered.'
                    break
            date = current_query[1]
            pid = current_query[2]

            posts[i]['user'] = self.username
            posts[i]['post_text'] = caption
            posts[i]['comments'] = self.get_post_comments(sql_writer, pid)
            posts[i]['date'] = date
            posts[i]['id'] = pid
            posts[i]['current_user'] = self.username == current_user
            posts[i]['likes'] = self.get_post_likes(sql_writer, pid)
            
            posts.append({})

        return posts

    def get_post_comments(self, sql_writer, post_id):
        comments = [{}]

        comments_query = sql_writer.query_all('SELECT UserID, Comment FROM Comments WHERE PostID=%s;', (post_id,))

        for i in range(len(comments_query)):
            current_comment= comments_query[i]

            username = sql_writer.query('SELECT Username FROM Users WHERE UserID=%s;', (current_comment[0],))
            comment_text = current_comment[1]

            comments[i]['user'] = username
            comments[i]['text'] = comment_text

            comments.append({})
            
        return comments[:-1]

    def get_post_likes(self, sql_writer, post_id):
        return len(sql_writer.query_all('SELECT UserID FROM Likes WHERE PostID=%s', (post_id,)))

    def make_comment(self, sql_writer, post_id, comment):
        sql_writer.execute_statement('INSERT INTO Comments (PostID, UserID, Comment) VALUES (%s, (SELECT UserID FROM Users WHERE Username=%s), %s);',
        (post_id, self.username, comment,))

    def follow_user(self, sql_writer, user_to_follow):
        sql_writer.execute_statement("""INSERT INTO Follows (UserID, FollowedUserID)
        VALUES ((SELECT UserID FROM Users WHERE Username=%s), (SELECT UserID FROM Users WHERE Username=%s));""",
        (self.username, user_to_follow,))

    def get_following(self, sql_writer):  
        follow_query = sql_writer.query_all('SELECT Username FROM Users WHERE UserID IN (SELECT FollowedUserID FROM Follows WHERE UserID=(SELECT UserID FROM Users WHERE Username=%s));', (self.username,))
        #Query returns a list of tuples so we convert this to just one list
        followed = []
        for follow in follow_query:
            followed.append(follow[0])
        return set(followed)

    def is_following(self, username):
        return username in self.get_following()

    def unfollow_user(self, sql_writer, username):
        sql_writer.execute_statement("""DELETE FROM Follows WHERE
        UserID=(SELECT UserID FROM Users WHERE Username=%s) AND FollowedUserID=(SELECT UserID FROM Users WHERE Username=%s);""", (self.username, username,))

    def save_regex_filter(self, sql_writer, regex_list):
        #First drop all from this user
        sql_writer.execute_statement('DELETE FROM RegexFilters WHERE UserID=(SELECT UserID FROM Users WHERE username=%s);', (self.username,))
        regex_list = regex_list.split('\n')[:-1]

        #Insert all filters into the table
        for i in range(len(regex_list)):
            sql_writer.execute_statement('INSERT INTO RegexFilters (UserID, filter) VALUES ((SELECT UserID FROM Users WHERE Username=%s), %s);', (self.username, regex_list[i],))

    def get_regex_filters(self, sql_writer):
        regex_filters_query = sql_writer.query_all('SELECT Filter FROM RegexFilters WHERE UserID=(SELECT UserID FROM Users WHERE Username=%s);', (self.username,))
        
        regex_filters = []

        for regex_filter in regex_filters_query:
            #Remove the last character because this inserts as a carriage return
            regex_filters.append(regex_filter[0][:-1])
        return regex_filters