from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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