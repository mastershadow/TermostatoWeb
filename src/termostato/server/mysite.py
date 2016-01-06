from termostato.net import api
from termostato.data import db
import cherrypy
import datetime


def is_logged():
    if 'logged' in cherrypy.session:
        return True
    return False


class MySite(object):

    def validate_auth(self):
        if not is_logged():
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


class Api(object):

    def __init__(self):
        self.apiServer = api.Api()

    def validate_auth(self):
        if not is_logged():
            raise cherrypy.HTTPError(401, 'Not authorized')

    @cherrypy.expose
    def temperature_history(self):
        self.validate_auth()
        return "history"

    @cherrypy.expose
    def status(self):
        self.validate_auth()
        return "status"

    @cherrypy.expose
    def scheduling(self):
        self.validate_auth()
        return "scheduling"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def save_scheduling(self):
        self.validate_auth()
        body = cherrypy.request.json
        db.db.connect()
        newscheduling_data = []
        for day_idx, scheduling in enumerate(body):
            dotw = (day_idx + 1) % 7
            for hour_idx, status in enumerate(scheduling):
                tmins = hour_idx * 30
                hour = int(tmins / 60)
                min = tmins % 60
                start_time = datetime.time(hour, min)
                end_time = (datetime.datetime.combine(datetime.date.today(), start_time) +
                            datetime.timedelta(minutes=29, seconds=59)).time()
                item = {
                    'dotw': dotw,
                    'start_time': start_time,
                    'end_time': end_time,
                    'status': status
                }
                newscheduling_data.append(item)
        db.Scheduling().delete().execute()
        with db.db.atomic():
            for idx in range(0, len(newscheduling_data), 50):
                db.Scheduling.insert_many(newscheduling_data[idx:idx+50]).execute()
        db.db.close()
        return {'status': True}

    @cherrypy.expose
    def save_daytemp(self, t):
        self.validate_auth()
        return "save_daytemp"

    @cherrypy.expose
    def save_weektemp(self, t):
        self.validate_auth()
        return "save_weektemp"

    @cherrypy.expose
    def save_nighttemp(self, t):
        self.validate_auth()
        return "save_nighttemp"

    @cherrypy.expose
    def save_manualtemp(self, t):
        self.validate_auth()
        return "save_manualtemp"

    @cherrypy.expose
    def save_operatingmode(self, mode):
        self.validate_auth()
        return "save_operatingmode"

    @cherrypy.expose
    def gettemp(self):
        self.validate_auth()
        return self.apiServer.get_temp()

    @cherrypy.expose
    def getrelay(self):
        self.validate_auth()
        return self.apiServer.get_relay()

    @cherrypy.expose
    def setrelay(self, status=None):
        self.validate_auth()
        if status is not None:
            return self.apiServer.set_relay(int(status) == 1)
        return ''
