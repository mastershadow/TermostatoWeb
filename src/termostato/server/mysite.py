import cherrypy


class MySite(object):

    def is_logged(self):
        if 'logged' in cherrypy.session:
            return True
        return False

    def validate_auth(self):
        if not self.is_logged():
            raise cherrypy.HTTPRedirect("/login")

    @cherrypy.expose
    def index(self):
        self.validate_auth()
        return open("../views/dashboard.html")

    @cherrypy.expose
    def login(self, username=None, password=None):
        if username == "admin" and password == "admin":
            cherrypy.session['logged'] = "logged"
            raise cherrypy.HTTPRedirect("/")
        return open("../views/login.html")


    @cherrypy.expose
    def logout(self):
        del cherrypy.session['logged']
        raise cherrypy.HTTPRedirect("/")
