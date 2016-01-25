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
            cherrypy.config.update({"tools.sessions.on": True })
            cherrypy.server.socket_port = config.Port
            cherrypy.server.socket_host = '0.0.0.0'

            main_controller = mysite.MySite()
            api_controller = mysite.Api()

            d = cherrypy.dispatch.RoutesDispatcher()
            d.connect('default', '/', controller=main_controller, action="index")
            d.connect("api", "/api/:action", controller=api_controller)
            d.connect("api", "/api/:action/:status", controller=api_controller)
            d.connect("main", "/:action", controller=main_controller)

            cherrypy.tree.mount(None, config={
                '/': {
                    'tools.sessions.on': True,
                    'request.dispatch': d
                },
                '/static': {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': '../public',
                    'tools.staticdir.root': os.path.abspath(os.getcwd())
                }
            })
            cherrypy.engine.start()
        cherrypy.engine.block()

    def stop(self):
        with self.sync:
            cherrypy.engine.exit()
            cherrypy.server.stop()

