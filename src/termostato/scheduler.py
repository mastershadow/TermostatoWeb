import net.api as api
import config
import threading
import time


class Scheduler(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.interval = config.Interval
        self.apiServer = api.Api()

    def run(self):
        while not self.stopEvent.is_set():
            self.pull()
            self.push()
            for i in range(self.interval):
                if not self.stopEvent.is_set():
                    time.sleep(1)

    def stop(self):
        if self.isAlive():
            self.stopEvent.set()
            self.join()

    def pull(self):
        temp = self.apiServer.get_temp()
        relay = self.apiServer.get_relay()
        print temp + " " + relay

    def push(self):
        return ''
