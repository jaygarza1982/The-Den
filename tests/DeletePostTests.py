from selenium import webdriver

class DeletePostTests:
    def __init__(self, url, driver):
        self.url = url
        self.driver = driver

    def test_delete(self, caption):
        posts_from_driver = self.driver.find_elements_by_class_name('post')

        index = -1
        for i in range(len(posts_from_driver)):
            post = posts_from_driver[i]
            #Check if the post is from our currently logged into account
            if 'class="post-options-link fa fa-bars hvr-float"' in post.get_attribute('outerHTML'):
                index += 1
                post_caption = str(post.text).split('\n')[1]
                if post_caption == caption:
                    #Click the post option hamburger button
                    self.driver.find_elements_by_class_name('post-options-link')[index].click()

                    #Get all the delete buttons from the page, click the one that has text
                    delete_buttons = self.driver.find_elements_by_xpath('//a[@href="#delete"]')
                    for delete_button in delete_buttons:
                        if delete_button.text != '':
                            delete_button.click()

                    #The 'Are you sure' button will appear, click that one
                    delete_buttons = self.driver.find_elements_by_xpath('//a[@href="#delete"]')
                    for delete_button in delete_buttons:
                        if delete_button.text != '':
                            delete_button.click()
                            i = len(posts_from_driver)
        #Go home
        self.driver.get(self.url + '/home')

        #Make sure the caption is not found within the page
        return caption not in self.driver.page_source