from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EditPostTest:
    def __init__(self, driver, url):
        self.driver = driver
        self.url = url

    def edit_test(self, caption, new_caption):
        posts = self.driver.find_elements_by_class_name('post')
        index = -1
        for i in range(len(posts)):
            post = posts[i]
            if str(post.text).split('\n')[1] == caption:
                index = i
                i = len(posts)

        self.driver.find_elements_by_class_name('post-options-link')[index].click()

        edit_buttons = self.driver.find_elements_by_xpath('//a[@href="#edit"]')
        for edit_button in edit_buttons:
            if edit_button.text != '':
                #TODO: Find a better way to wait
                try:
                    WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#edit" text()="Edit"]')))
                except:
                    None
                edit_button.click()


        caption_area = self.driver.find_element_by_class_name('caption-area')

        #Clear the caption area
        caption_area.clear()

        caption_area.send_keys(new_caption)

        #Click post button
        self.driver.find_element_by_class_name('comment-button').click()

        self.driver.get(self.url + '/home')

        posts = self.driver.find_elements_by_class_name('post')
        for post in posts:
            if post.text.split('\n')[1] == new_caption:
                return True

        return False