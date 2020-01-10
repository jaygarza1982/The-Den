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

test_server_url = sys.argv[1]
port = 3000

def startT():
    subprocess.call('cd thedentestingserver; python3 run.py ' + test_server_url + ' test', shell=True)

def clean_up():
    list_dir = os.listdir('.')
    

    if 'thedentestingserver' in list_dir:
        shutil.rmtree('./thedentestingserver')
    shutil.copytree('../The-Den', './thedentestingserver')

    if 'users' in list_dir:
        shutil.rmtree('./users')

    if 'database.db' in list_dir:
        os.remove('./database.db')

    try:
        os.remove('./thedentestingserver/database.db')
    except:
        print('error removing database.db')
    try:
        shutil.rmtree('./thedentestingserver/users')
    except:
        print('error removing users folder')


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

post_tests.post_inputs('hay')
post_test_pass = post_tests.post_test('hay')
print(post_test_pass, ' post pass with hay')

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

print('Done.')