import RegisterTests
import LoginTests
import FollowTests
import PostTests
import CommentTests
from RegexTests import RegexTest
import shutil
import subprocess
import os
import time
import threading
import sys

from selenium import webdriver
from UserViewTests import UserViewTest
from SortedPostTests import SortedPostsTest
from LogoutTest import LogoutTest
from DeletePostTests import DeletePostTests
from EditPostTests import EditPostTest

import mysql.connector


conf_contents = []
with open(sys.argv[1], 'r') as conf_file:
    conf_contents = conf_file.readlines()



test_server_url = conf_contents[0]
port = 3000

def startT():
    subprocess.call('cd thedentestingserver; python3 run.py ' + sys.argv[1], shell=True)

def clean_up():
    list_dir = os.listdir('.')
    password = os.getenv('sqlpass')
    subprocess.call('/usr/bin/mysqldump -h localhost -P 3306 -u root -p' + password + ' TheDen | mysql -h localhost -P 3306 -u root -p' + password + ' TheDenTesting', shell=True)
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd=password,
    )

    cursor = db.cursor()

    cursor.execute('USE TheDenTesting')
    cursor.execute('SHOW TABLES')
    fetched = cursor.fetchall()
    tables = fetched

    #Clear each table
    for table in tables:
        if 'Keys' not in table[0]:
            cursor.execute('DELETE FROM ' + table[0] + ' WHERE 1=1')
    db.commit()
    db.close()

    if 'thedentestingserver' in list_dir:
        shutil.rmtree('./thedentestingserver')
    shutil.copytree('../The-Den', './thedentestingserver')

    # if 'users' in list_dir:
    #     shutil.rmtree('./users')

    # if 'database.db' in list_dir:
    #     os.remove('./database.db')

    # try:
    #     os.remove('./thedentestingserver/database.db')
    # except:
    #     print('error removing database.db')
    # try:
    #     shutil.rmtree('./thedentestingserver/users')
    # except:
    #     print('error removing users folder')


clean_up()

threading.Thread(target=startT).start()
time.sleep(0.1)
test_server_url = 'http://' + test_server_url + ':' + str(port)

driver = webdriver.Firefox()

register_tests = RegisterTests.RegisterTests(test_server_url, driver)
register_tests.register_inputs('mrhi01', '123', '123')
register_pass = register_tests.register_pass('mrhi01')
print(register_pass, ' registering')

register_tests.register_inputs('mrhi02', 'FiencX02', 'FiencX02')
register_pass = register_tests.register_pass('mrhi02')
print(register_pass, ' registering')

register_tests.register_inputs('mrhi03', 'jcnen&*63hx01', 'jcnen&*63hx01')
register_pass = register_tests.register_pass('mrhi03')
print(register_pass, ' registering')

register_tests.register_inputs('mrhi04', 'passfor4', 'passfor4')
register_pass = register_tests.register_pass('mrhi04')
print(register_pass, ' registering')

register_tests.register_inputs('a', '123', '132')
register_mismatch_pass = register_tests.register_mismatch()
print(register_mismatch_pass, ' registering mismatch')

login_tests = LoginTests.LoginTests(test_server_url, driver)

login_tests.login_inputs('mrhi01', '132')
login_fail = login_tests.login_fail()
print(login_fail, ' login fail')

login_tests.login_inputs('mrhi02', '132423')
login_fail = login_tests.login_fail()
print(login_fail, ' login fail')

current_username = 'mrhi01'
login_tests.login_inputs(current_username, '123')
login_pass = login_tests.login_pass()
print(login_pass, ' login pass')

follow_tests = FollowTests.FollowTests(test_server_url, driver)
follow_tests.follow_inputs('m')

validate_users_pass = follow_tests.validate_users(('mrhi01', 'mrhi02', 'mrhi03', 'mrhi04'))
print(validate_users_pass, ' validate users')

follow_user_pass = follow_tests.follow_user('mrhi02')
print(follow_user_pass, ' follow user pass')

follow_user_pass = follow_tests.follow_user('mrhi04')
print(follow_user_pass, ' follow user pass')

follow_user_posts = follow_tests.validate_user_follow('mrhi02')
print(follow_user_posts, ' follow user posts')

follow_tests.follow_inputs('mr')
follow_tests.follow_user('mrhi04')
unfollow_user_pass = follow_tests.validate_user_unfollow('mrhi04')
print(unfollow_user_pass, ' unfollow user pass')

post_tests = PostTests.PostTests(test_server_url, driver)
post_tests.post_inputs('This post is a test post. It is a good test post.')
post_test_pass = post_tests.post_test('This post is a test post. It is a good test post.')
print(post_test_pass, ' post pass')


post_tests.post_inputs('This post is a test post. It is contains a needle.')
post_test_pass = post_tests.post_test('This post is a test post. It is contains a needle.')
print(post_test_pass, ' post pass with needle')

edit_post_tests = EditPostTest(driver, test_server_url)
edit_pass = edit_post_tests.edit_test('This post is a test post. It is contains a needle.', 'New caption with needle. It has been edited.')
print(edit_pass, ' Edit post pass')

post_tests.post_inputs('hay')
post_test_pass = post_tests.post_test('hay')
print(post_test_pass, ' post pass with hay')

post_tests.post_inputs('This post will be deleted later!')
post_test_pass = post_tests.post_test('This post will be deleted later!')
print(post_test_pass, ' post pass with deleted later')

comment_tests = CommentTests.CommentTests(driver)

test_comment = 'This is a comment written by the unit test program.'
comment_tests.comment_inputs('mrhi02', test_comment)
#Pass the user who commented with their comment
comment_pass = comment_tests.comment_pass(current_username, test_comment)
print(comment_pass, ' comment pass')

regex_test = RegexTest(test_server_url, driver)
regex_text = '.*needle.*'
regex_test.regex_inputs(regex_text)
regex_pass = regex_test.regex_test(regex_text)
print(regex_pass, ' regex pass')

regex_text = '.*hay.*'
regex_test.regex_inputs(regex_text)
regex_pass = regex_test.regex_test(regex_text)
print(regex_pass, ' regex pass')

user_view_test = UserViewTest(test_server_url, driver)
user_view_pass = user_view_test.test_user_view('mrhi01')
print(user_view_pass, ' user view pass')

#Test viewing user account while logged out
user_view_pass = user_view_test.test_user_view_logout('mrhi01')
print(user_view_pass, ' user view pass')

#Log back in
login_tests.login_inputs(current_username, '123')
login_pass = login_tests.login_pass()
print(login_pass, ' login pass')

user_view_test2 = user_view_test.test_user_view_from_follow_menu('mrhi01')
print(user_view_test2, ' user view from follow menu pass')

delete_regex_test = regex_test.delete_regex('.*hay.*')
print(delete_regex_test, ' delete regex test with hay')

sorted_posts_test = SortedPostsTest(test_server_url, driver)
sorted_pass = sorted_posts_test.post_test('Testing this is at top')
print(sorted_pass, ' Sorted posts pass')

delete_post_tests = DeletePostTests(test_server_url, driver)
delete_post_pass = delete_post_tests.test_delete('This post will be deleted later!')
print(delete_post_pass, ' Delete post pass')

logout_test = LogoutTest(test_server_url, driver)
logout_pass = logout_test.test_logout()
print(logout_pass, ' logout test')

print('Done.')