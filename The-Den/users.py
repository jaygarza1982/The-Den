import sqlite3
import random
import os
import time
import re
import threading
from SQLWriter import SQLWriter
from datetime import date
from flask import make_response, redirect, session, render_template

class user:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.following_file_path = 'users/' + self.username + '/following'

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

    def make_post(self, sql_writer, caption):
        sql_writer.insert_post(self.username, caption, date.today().strftime("%b %d %Y"))

    def get_posts(self, sql_writer, filters):
        posts = [{}]

        posts_query = sql_writer.query_all("""
            SELECT caption, date, pid FROM posts WHERE uid=(SELECT uid FROM users WHERE username=?);
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
            
            posts.append({})

        return posts

    def get_post_comments(self, sql_writer, post_id):
        comments = [{}]

        comments_query = sql_writer.query_all('SELECT uid, comment FROM comments WHERE pid=?;', (post_id,))

        for i in range(len(comments_query)):
            current_comment= comments_query[i]

            username = sql_writer.query('SELECT username FROM users WHERE uid=?;', (current_comment[0],))
            comment_text = current_comment[1]

            comments[i]['user'] = username
            comments[i]['text'] = comment_text

            comments.append({})
            
        return comments[:-1]

    def make_comment(self, sql_writer, post_id, comment):
        sql_writer.execute_statement('INSERT INTO comments (pid, uid, comment) VALUES (?, (SELECT uid FROM users WHERE username=?), ?);',
        (post_id, self.username, comment,))

    def follow_user(self, sql_writer, user_to_follow):
        sql_writer.execute_statement("""INSERT INTO follows (uid, followed_user_id) VALUES ((SELECT uid FROM users WHERE username=?), (SELECT uid FROM users WHERE username=?));""",
        (self.username, user_to_follow,))

    def get_following(self, sql_writer):  
        follow_query = sql_writer.query_all('SELECT username FROM users WHERE uid IN (SELECT followed_user_id FROM follows WHERE uid=(SELECT uid FROM users WHERE username=?));', (self.username,))
        #Query returns a list of tuples so we convert this to just one list
        followed = []
        for follow in follow_query:
            followed.append(follow[0])
        return set(followed)

    def is_following(self, username):
        return username in self.get_following()

    def unfollow_user(self, sql_writer, username):
        sql_writer.execute_statement("""DELETE FROM follows WHERE
        uid=(SELECT uid FROM users WHERE username=?) AND followed_user_id=(SELECT uid FROM users WHERE username=?);""", (self.username, username,))

    def save_regex_filter(self, sql_writer, regex_list):
        #First drop all from this user
        sql_writer.execute_statement('DELETE FROM RegexFilters WHERE uid=(SELECT uid FROM users WHERE username=?);', (self.username,))
        regex_list = regex_list.split('\n')[:-1]

        #Insert all filters into the table
        for i in range(len(regex_list)):
            sql_writer.execute_statement('INSERT INTO RegexFilters (uid, filter) VALUES ((SELECT uid FROM users WHERE username=?), ?);', (self.username, regex_list[i],))

    def get_regex_filters(self, sql_writer):
        regex_filters_query = sql_writer.query_all('SELECT filter FROM RegexFilters WHERE uid=(SELECT uid FROM users WHERE username=?);', (self.username,))
        
        regex_filters = []

        for regex_filter in regex_filters_query:
            #Remove the last character because this inserts as a carriage return
            regex_filters.append(regex_filter[0][:-1])
        return regex_filters