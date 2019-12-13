from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re

class RegexTest:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def regex_inputs(self, regex_text):
        #Click the follow link
        self.driver.find_element_by_xpath("//a[@href='/settings']").click()

        self.driver.find_element_by_xpath("//input[@value='Add']").click()

        self.driver.find_elements_by_class_name('text-input-small')[1].send_keys(regex_text)

        self.driver.find_element_by_xpath("//input[@value='Save']").click()


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