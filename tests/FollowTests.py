from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
class FollowTests:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def follow_inputs(self, username):
        #Click the follow link
        self.driver.find_element_by_id('follow-link').click()
        
        #Send keys to the follow box
        self.driver.find_element_by_id('follow-box').send_keys(username)
        
        #Wait for one second for the users div to populate
        self.driver.implicitly_wait(1)

        self.driver.find_element_by_class_name('user')
    
    def validate_users(self, users):
        users_in_page = self.driver.find_elements_by_class_name('username')

        #Sort the users we are supposed to see, sort the users we see
        users = sorted(users)
        users_in_page = sorted(self.__return_elements_as_text(users_in_page))

        #Check equality
        return users_in_page == users

    # def follow_user(self, user):


    def __return_elements_as_text(self, elements):
        text_list = []
        for i in range(len(elements)):
            text_list.append(elements[i].text)
        return text_list