import config
import threading
import time


class Scheduler(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.interval = config.Interval

    def run(self):
        while not self.stopEvent.is_set():
            self.pull()
            self.push()
            time.sleep(self.interval)

    def stop(self):
        if self.isAlive():
            self.stopEvent.set()
            self.join()

    def pull(self):
        print "Pull"

    def push(self):
        print "Push"
