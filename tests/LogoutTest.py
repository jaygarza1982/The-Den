from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class LogoutTest:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def test_logout(self):
        #Go home
        self.driver.get(self.url + '/home')

        #Click logout link
        self.driver.find_element_by_xpath('//a[@href="#logout"]').click()

        #Try to go home
        self.driver.get(self.url + '/home')
        
        #Check to see that the url redirected to the login page
        return self.driver.current_url == (self.url + '/')