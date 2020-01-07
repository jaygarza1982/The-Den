from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from FollowTests import FollowTests


class UserViewTest:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def test_user_view(self, username):
        self.driver.get(self.url + '/user?user=' + username)

        account_names = self.driver.find_elements_by_class_name('account-name')

        for account_name in account_names:
            if account_name.text != username:
                return False
        
        return True

    def test_user_view_from_follow_menu(self, username):
        follow_test = FollowTests(self.url, self.driver)

        #Type in username
        follow_test.follow_inputs(username)

        account_names = self.driver.find_elements_by_class_name('account-name')
        account_names[0].click()

        return self.driver.title == 'Den - ' + username


    def test_user_view_logout(self, username):
        #Delete logintoken cookie to log out
        self.driver.delete_cookie('logintoken')
        
        return self.test_user_view(username)