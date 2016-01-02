from __future__ import with_statement
from termostato import config
import cherrypy
import threading
import mysite
import os


class Server(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.sync = threading.Condition()

    def run(self):
        with self.sync:
            cherrypy.server.socket_port = config.Port
            cherrypy.tree.mount(mysite.MySite(), "/", {
                 '/': {
                     'tools.sessions.on': True,
                     'tools.staticdir.root': os.path.abspath(os.getcwd())
                 },
                 '/static': {
                     'tools.staticdir.on': True,
                     'tools.staticdir.dir': '../public'
                 }
            })
            cherrypy.engine.start()
        cherrypy.engine.block()

    def stop(self):
        with self.sync:
            cherrypy.engine.exit()
            cherrypy.server.stop()

