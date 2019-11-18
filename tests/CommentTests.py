from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class CommentTests:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver