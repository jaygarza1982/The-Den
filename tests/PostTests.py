from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class PostTests:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def post_inputs(self, caption):
        #Go to main page
        # self.driver.get(self.url)

        #Click post link
        self.driver.find_element_by_xpath('//a[@href="#post"]').click()
        
        #Send input to caption textarea
        self.driver.find_element_by_class_name('caption-area').send_keys(caption)

    def post_test(self, caption):
        #Click post button
        self.driver.find_element_by_class_name('comment-button').click()

        #Validate that posted
        #Click post link
        self.driver.find_element_by_xpath('//a[@href="#post"]').click()

        self.driver.refresh()

        #Get posts
        posts = self.driver.find_elements_by_tag_name('p')

        for post in posts:
            if post.text == caption:
                return True
        return False