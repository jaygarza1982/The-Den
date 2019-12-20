from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class CommentTests:
    def __init__(self, driver):
        # self.url = url
        self.driver = driver

    def comment_inputs(self, username, comment):
        #Get account names of posts in order to find the comment button matched with post
        account_names = self.driver.find_elements_by_class_name('account-name')

        find = 0
        for i in range(len(account_names)):
            if account_names[i].text == username:
                find = i
                break

        #Click the comment icon of post, send the comment to the textarea, click the comment button, plus one because the post button is that class too
        self.driver.find_elements_by_class_name('comment-icon')[find].click()
        self.driver.find_elements_by_class_name('comment-area')[find].send_keys(comment)
        self.driver.find_elements_by_class_name('comment-button')[find+1].click()

        #Refresh the browser and check if the comment exists
        self.driver.refresh()

    def comment_pass(self, username, comment):
        return self.driver.find_elements_by_class_name('comment')[0].text == username + '\n' + comment