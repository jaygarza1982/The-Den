from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from PostTests import PostTests

class SortedPostsTest:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def post_test(self, caption):
        self.driver.get(self.url + '/home')

        post_test = PostTests(self.url, self.driver)
        post_test.post_inputs(caption)
        
        #Click post button
        self.driver.find_element_by_class_name('comment-button').click()

        #Validate that posted
        #Click post link
        self.driver.find_element_by_xpath('//a[@href="#post"]').click()
        
        self.driver.refresh()

        #Get posts
        posts = self.driver.find_elements_by_tag_name('p')
        return posts[0].text == caption