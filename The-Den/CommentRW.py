import threading
import queue
from time import sleep

class CommentRW:
    def __init__(self):
        self.queue = queue.Queue()

    def execute_queue(self, delay):
        while True:
            if (not self.queue.empty()):
                next_comment = self.queue.get()

                # print(next_comment)
                self.make_comment(next_comment[0], next_comment[1], next_comment[2], next_comment[3])
            sleep(delay)

    def start(self, delay):
        t = threading.Thread(target=self.execute_queue, args=(delay,))
        t.start()
        # threading._start_new_thread(self.execute_queue, args=(delay,))


    def make_comment(self, current_user, username, post_id, comment0):
        comment_file_path = 'users/' + username + '/' + post_id + '/comments'
        
        comment = '\n<USER>' + current_user + '</USER><COMMENT>' + comment0 + '</COMMENT><LIKES></LIKES>'

        with open(comment_file_path, 'a') as comment_file:
            comment_file.write(comment)