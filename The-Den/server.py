from flask import *
import sqlite3
import random
import re
import os
import time
import users
import CommentRW
import threading
import logging
from SQLWriter import SQLWriter

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

        commentRW = CommentRW.CommentRW()
        commentRW.start(0.05)

        db_lock = threading.Lock()
        sql_writer = SQLWriter(db_lock, 'users.db', 'users')

        if ('users' not in os.listdir()):
            os.mkdir('users')

        if ('users.db' not in os.listdir()):
            print('!!!users.db not found. Attempting to insert table users!!!')
            #Touch the users.db file
            open('users.db', 'w').close()
            #Create users.db with table
            sql_writer.create_users_table()

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

                followers = open('users/' + username + '/following', 'r').read().strip().split('\n')
                follower_posts = []
                
                for follower in followers:
                    user = users.user(follower, '')
                    follower_posts += user.get_posts(logged_in_user.get_regex_filters())

                return render_template_string(open('public/templates/home-template.html', 'r').read(), posts=follower_posts, current_user=username)
            else:
                return make_response(redirect('/'))

        @app.route('/user')
        def indexUserPage():
            username = get_username(self, request)
            regex_filters = {}
            
            user_to_display = request.args.get('user')
            if username != None:
                logged_in_user = users.user(username, '')
                
                regex_filters = logged_in_user.get_regex_filters()

            user_posts = users.user(user_to_display, '').get_posts(regex_filters)

            return render_template_string(open('public/templates/user-template.html', 'r').read(), posts=user_posts, current_user=username)

        @app.route('/settings')
        def indexSettings():
            username = session[request.cookies.get('logintoken')]
            user = users.user(username, '')
            return render_template_string(open('public/templates/settings-template.html', 'r').read(), regex_filters=user.get_regex_filters())

        @app.route('/comment', methods=['POST'])
        def comment():
            #Get the username of logged in client
            username = session[request.cookies.get('logintoken')] #request.form['user']

            comment = request.form['comment']
            if comment.strip() != '':
                user = users.user(username, '')
                user.make_comment(commentRW, request.form['user'], request.form['postID'], request.form['comment'])
                # user.make_comment(request.form['user'], request.form['postID'], request.form['comment'])
                return 'Success!'
            else:
                #Not modified
                abort(304)

        @app.route('/post', methods=['POST'])
        def post():
            username = session[request.cookies.get('logintoken')]
            user = users.user(username, '')
            user.make_post(request.form['caption'])
            
            return 'Success!'

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
            current_user = users.user(session[request.cookies.get('logintoken')], '')
            following = current_user.get_following()

            following_status = [{}]

            username_prefix = request.args.get('prefix')
            possible_users = ''
            if (username_prefix.strip() != ''):
                usernames = os.listdir('./users')
                
                for user in usernames:
                    if (user.startswith(username_prefix)):
                        following_status[-1]['username'] = user
                        following_status[-1]['following'] = user in following
                        # following_status[user] = user in following
                        following_status.append({})

            return jsonify(following_status[:-1])
            # return possible_users[:-1]

        @app.route('/follow', methods=['POST'])
        def indexFollow():
            current_user = session[request.cookies.get('logintoken')]
            username_to_follow = request.form['username']
            
            user = users.user(current_user, '')
            user.follow_user(username_to_follow)

            return 'Good.'

        @app.route('/unfollow', methods=['POST'])
        def indexUnfollow():
            current_username = session[request.cookies.get('logintoken')]
            user_to_unfollow = request.form['username']

            current_user = users.user(current_username, '')
            current_user.unfollow_user(user_to_unfollow)

            return 'Unfollowed'

        @app.route('/regex', methods=['POST'])
        def indexRegex():
            current_username = session[request.cookies.get('logintoken')]
            user = users.user(current_username, '')
            user.save_regex_filter(request.form['regex-filters'])
            return 'Sent.'

        app.run(self.ip, port=3000)
