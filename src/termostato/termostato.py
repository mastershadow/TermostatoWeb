from server import server
import scheduler
import logging


_author_ = "Eduard Roccatello"
_project_ = 'Termostato'


class Termostato(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.server = server.Server()
        self.scheduler = scheduler.Scheduler()

    def start(self):
        self.logger.info("Starting Termostato.")
        self.logger.info("Starting scheduler...")
        self.scheduler.start()
        self.logger.info("Starting web server...")
        self.server.start()
        self.logger.info("Started")

    def stop(self):
        self.logger.info("Stopping scheduler...")
        self.scheduler.stop()
        self.logger.info("Stopping web server...")
        self.server.stop()
