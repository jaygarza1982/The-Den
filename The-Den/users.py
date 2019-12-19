import sqlite3
import random
import os
import time
import re
import CommentRW
import threading
from SQLWriter import SQLWriter
from datetime import date
from flask import make_response, redirect, session, render_template_string

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
                cookie = str(os.urandom(1024))
                session[cookie] = str(self.username)
                resp = make_response(redirect('/home'))
                resp.set_cookie('logintoken', cookie)
                return resp
        return 'Invalid credentials'

    def register(self, sql_writer, password_confirm):
        resp = ''
        # Check to see if user exists in database
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        if (len(sql_writer.fetch_username(self.username)) == 0):
            if self.password != password_confirm:
                return 'Passwords do not match.'
                
            sql_writer.insert_username(self.username, self.password)

            user_folder = 'users/' + self.username
            os.mkdir(user_folder)

            following_file = open(user_folder + '/' + 'following', 'w')
            following_file.write(self.username)
            following_file.close()

            self.save_regex_filter('')

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

        #Make creation date file
        date_str = date.today().strftime("%b %d %Y")
        with open(post_path + '/creation', 'w') as creation_file:
            creation_file.write(date_str)

        caption_file = open(post_path + '/caption', 'w')
        caption_file.write(caption)
        caption_file.close()

        comments_file = open(post_path + '/comments', 'w')
        comments_file.close()

    def get_posts(self, filters):
        posts = [{}]
        count = 0
        for file in os.listdir('users/' + self.username + '/'):

            if file.startswith('post'):
                post_text = open('users/' + self.username + '/' + file + '/caption', 'r').read()
                for filter in filters:
                    if re.match(filter, post_text):
                        post_text = 'Filtered.'
                        break
                posts[count]['user'] = self.username
                posts[count]['post_text'] = post_text
                posts[count]['pic_url'] = 'users/' + self.username + '/pic.jpg'
                posts[count]['comments'] = self.get_post_comments(self.username + '/' + file)
                posts[count]['date'] = self.get_post_time(self.username + '/' + file)
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

    def get_post_time(self, post_stamp):
        if 'creation' in os.listdir('users/' + post_stamp):
            return open('users/' + post_stamp + '/creation', 'r').read()
        return ''

    def save_regex_filter(self, regex_list):
        with open('users/' + self.username + '/regex', 'w') as regex_settings_file:
            regex_settings_file.write(regex_list)

    def get_regex_filters(self):
        #Load filters from file
        regex_filters = set(open('users/' + self.username + '/regex', 'r').read().split('\n'))

        #Remove empty line and return the filters
        regex_filters.remove('')
        return regex_filters