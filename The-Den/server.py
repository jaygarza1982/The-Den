from flask import *
import sqlite3
import random
import re
import os
import time
import users
import threading
import logging
from SQLWriter import SQLWriter
from DBCreator import DBCreator

class server:
    def __init__(self, ip, logging_setting):
        if not logging_setting:
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
        self.ip = ip
        
        dirpath = os.getcwd()
        print("current directory is : " + dirpath)

        app = Flask(__name__)
        app.secret_key = str(os.urandom(512))
        app.config['SESSION_TYPE'] = 'filesystem'

        db_lock = threading.Lock()
        sql_writer = SQLWriter(db_lock, 'database.db')
        
        if ('database.db' not in os.listdir()):
            print('!!!database.db not found. Attempting to insert table users!!!')
            db_creator = DBCreator('database.db')
            db_creator.create()

        def get_username(self, request):
            if 'logintoken' in request.cookies:
                cookie = request.cookies['logintoken']
                if cookie in session:
                    return session[cookie]
            return None
            
        @app.route('/<path:path>')
        def static_proxy(path):
            #Handle profile pic request
            if path.startswith('users') and path.endswith('.jpg'):
                if (os.path.exists(path)):
                    response = make_response(open(path, 'rb').read())
                    response.headers.set('Content-Type', 'image/jpeg')
                    return response
                else:
                    return b''
            else:
                return send_from_directory('public', path)

        @app.route('/')
        def index():
            return send_from_directory('public', 'index.html')

        @app.route('/home')
        def indexHome():
            username = get_username(self, request)

            if (username != None):
                logged_in_user = users.user(username, '')

                followers = logged_in_user.get_following(sql_writer) #open('users/' + username + '/following', 'r').read().strip().split('\n')
                follower_posts = []
                
                for follower in followers:
                    user = users.user(follower, '')
                    follower_posts += user.get_posts(sql_writer, logged_in_user.get_regex_filters(sql_writer))

                return render_template('home-template.html', posts=follower_posts, current_user=username)
            else:
                return make_response(redirect('/'))

        @app.route('/user')
        def indexUserPage():
            username = get_username(self, request)
            regex_filters = {}
            
            user_to_display = request.args.get('user')
            if username != None:
                logged_in_user = users.user(username, '')
                regex_filters = logged_in_user.get_regex_filters(sql_writer)

            user_posts = users.user(user_to_display, '').get_posts(sql_writer, regex_filters)

            return render_template('user-template.html', posts=user_posts, current_user=username)

        @app.route('/settings')
        def indexSettings():
            username = get_username(self, request)
            if username != None:
                user = users.user(username, '')
                return render_template('settings-template.html', regex_filters=user.get_regex_filters(sql_writer))
            return make_response(redirect('/'))

        @app.route('/comment', methods=['POST'])
        def comment():
            #Get the username of logged in client
            username = get_username(self, request)

            if username != None:
                comment = request.form['comment']
                if comment.strip() != '':
                    user = users.user(username, '')
                    user.make_comment(sql_writer, request.form['postID'], request.form['comment'])
                    return 'Success!'
                else:
                    print('Comment: ' + comment)
                    #Not modified
                    # abort(304)
            return make_response(redirect('/'))

        @app.route('/post', methods=['POST'])
        def post():
            username = get_username(self, request)
            if username != None:
                user = users.user(username, '')
                user.make_post(sql_writer, request.form['caption'])
                
                return 'Success!'
            return make_response(redirect('/'))

        @app.route('/login', methods=['POST'])
        def login():
            username = request.form['username']
            password = request.form['password']
            
            user = users.user(username, password)

            return user.authUser(sql_writer)

        @app.route('/register', methods=['POST'])
        def indexRegister():
            username = request.form['username']
            password = request.form['password']
            password_confirm = request.form['password-confirm']
            
            user = users.user(username, password)

            return user.register(sql_writer, password_confirm)

        @app.route('/user-query')
        def indexUserQuery():
            username = get_username(self, request)
            if username != None:
                current_user = users.user(username, '')
                following = current_user.get_following(sql_writer)

                following_status = [{}]

                username_prefix = request.args.get('prefix')
                possible_users = ''
                if (username_prefix.strip() != ''):
                    usernames = sql_writer.fetch_all_usernames(username_prefix)
                    
                    for user in usernames:
                        following_status[-1]['username'] = user
                        following_status[-1]['following'] = user in following
                        following_status.append({})

                return jsonify(following_status[:-1])
            return make_response(redirect('/'))

        @app.route('/follow', methods=['POST'])
        def indexFollow():
            current_user = get_username(self, request)
            username_to_follow = request.form['username']
            
            user = users.user(current_user, '')
            user.follow_user(sql_writer, username_to_follow)

            return 'Good.'

        @app.route('/unfollow', methods=['POST'])
        def indexUnfollow():
            current_username = get_username(self, request)
            user_to_unfollow = request.form['username']

            current_user = users.user(current_username, '')
            current_user.unfollow_user(sql_writer, user_to_unfollow)

            return 'Unfollowed'

        @app.route('/regex', methods=['POST'])
        def indexRegex():
            current_username = get_username(self, request)
            user = users.user(current_username, '')
            user.save_regex_filter(sql_writer, request.form['regex-filters'])
            return 'Sent.'

        app.run(self.ip, port=3000)
