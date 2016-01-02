from server import server
import scheduler

_author_ = "Eduard Roccatello"
_project_ = 'Termostato'


class Termostato(object):

    def __init__(self):
        self.server = server.Server()
        self.scheduler = scheduler.Scheduler()

    def start(self):
        print "Starting Termostato."
        print "Starting scheduler..."
        self.scheduler.start()
        print "Starting web server..."
        self.server.start()
        print "Started"

    def stop(self):
        print "Stopping scheduler..."
        self.scheduler.stop()
        print "Stopping web server..."
        self.server.stop()
