from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class LoginTests:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def login_inputs(self, username, password):
        #Go to main page
        self.driver.get(self.url)

        #Type username and password
        self.driver.find_element_by_name('username').send_keys(username)
        self.driver.find_element_by_name('password').send_keys(password)
    
    def login_pass(self):
        #Click to login
        self.driver.find_element_by_class_name('button').click()

        try:
            self.driver.find_element_by_id('posts')
            return True
        except:
            return False

    def login_fail(self):
        #Click to login
        self.driver.find_element_by_class_name('button').click()

        return 'Invalid' in self.driver.page_source