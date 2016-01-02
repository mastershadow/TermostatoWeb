import cherrypy


class MySite(object):

    @cherrypy.expose
    def index(self):
        return "Hello worm"