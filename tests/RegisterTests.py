from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class RegisterTests:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def register_inputs(self, username, password, password_confirm):
        self.driver.get(self.url)
        #Click to go to register menu
        self.driver.find_element_by_xpath('//a[@href="/register.html"]').click()

        self.driver.find_element_by_name('username').send_keys(username)
        self.driver.find_element_by_name('password').send_keys(password)
        self.driver.find_element_by_name('password-confirm').send_keys(password_confirm)

    def register_pass(self, username):
        #Click to register
        self.driver.find_element_by_class_name('button').click()

        return self.driver.find_element_by_name('username').get_attribute('value') == username

    def register_mismatch(self):
        #Click to register
        self.driver.find_element_by_class_name('button').click()

        return 'do not match' in self.driver.page_source
