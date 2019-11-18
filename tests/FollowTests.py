from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
class FollowTests:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def follow_inputs(self, username):
        #Send keys to the follow box
        self.driver.find_element_by_id('follow-box').send_keys(username)
        
        #Wait for one second for the users div to populate
        self.driver.implicitly_wait(1)


        print(self.driver.page_source)