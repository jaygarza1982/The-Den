import RegisterTests
import LoginTests
import FollowTests
import shutil
import subprocess
import os
import time
import threading
import sys

from selenium import webdriver

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

    if 'users.db' in list_dir:
        os.remove('./users.db')

    try:
        os.remove('./thedentestingserver/users.db')
    except:
        print('error removing users.db')
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
print(register_pass)

register_tests.register_inputs('mrhi02', 'FiencX02', 'FiencX02')
register_pass = register_tests.register_pass('mrhi02')
print(register_pass)

register_tests.register_inputs('mrhi03', 'jcnen&*63hx01', 'jcnen&*63hx01')
register_pass = register_tests.register_pass('mrhi03')
print(register_pass)

register_tests.register_inputs('mrhi04', 'passfor4', 'passfor4')
register_pass = register_tests.register_pass('mrhi04')
print(register_pass)

register_tests.register_inputs('a', '123', '132')
register_mismatch_pass = register_tests.register_mismatch()
print(register_mismatch_pass)

login_tests = LoginTests.LoginTests(test_server_url, driver)

login_tests.login_inputs('mrhi01', '132')
login_fail = login_tests.login_fail()
print(login_fail)

login_tests.login_inputs('mrhi02', '132423')
login_fail = login_tests.login_fail()
print(login_fail)

login_tests.login_inputs('mrhi01', '123')
login_pass = login_tests.login_pass()
print(login_pass)

follow_tests = FollowTests.FollowTests(test_server_url, driver)
follow_tests.follow_inputs('m')

validate_users_pass = follow_tests.validate_users(('mrhi01', 'mrhi02', 'mrhi03', 'mrhi04'))
print(validate_users_pass)