from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re

class RegexTest:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def regex_inputs(self, regex_text):
        #Click the settings link
        self.driver.find_element_by_xpath("//a[@href='/settings']").click()

        self.driver.find_element_by_xpath("//input[@value='Add']").click()

        self.driver.find_elements_by_class_name('text-input-small')[1].send_keys(regex_text)

        self.driver.find_element_by_xpath("//input[@value='Save']").click()

    def delete_regex(self, regex):
        #Click the settings link
        self.driver.find_element_by_xpath("//a[@href='/settings']").click()

        inputs = self.driver.find_elements_by_class_name('text-input-small')

        #Find the input with the regex we want to delete
        index = -1
        for i in range(len(inputs)):
            if inputs[i].get_attribute('value') == regex:
                index = i
                i = len(inputs)
        
        #If we do not find the setting the test failed
        if index == -1:
            return False

        #Click delete button
        self.driver.find_elements_by_class_name('delete-button')[index].click()

        #Save the settings
        self.driver.find_element_by_xpath("//input[@value='Save']").click()
        
        #Refresh the page and see if the save deleted the regex setting
        self.driver.get(self.url + '/settings')

        #Refresh the inputs list because a refresh occurred
        inputs = self.driver.find_elements_by_class_name('text-input-small')

        for i in range(len(inputs)):
            if inputs[i].get_attribute('value') == regex:
                return False
        return True


    def regex_test(self, regex_text):
        #Go to test url
        self.driver.back()
        self.driver.refresh()

        # Get posts
        posts = self.driver.find_elements_by_tag_name('p')

        for post in posts:
            if re.match(regex_text, post.text):
                return False
        return True