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
    @cherrypy.tools.json_out()
    def temperature_history(self):
        self.validate_auth()
        db.db.connect()
        results = []
        for r in db.Reading.select().order_by(-db.Reading.reading_timestamp).limit(250):
            results.append({
                'timestamp': r.reading_timestamp.isoformat(),
                'temperature': r.temperature,
                'status': r.relay_status
            })
        db.db.close()
        return results

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def status(self):
        self.validate_auth()
        db.db.connect()
        s = db.Setting.get()
        r = db.Reading.select().order_by(-db.Reading.reading_timestamp).get()

        results = dict()
        results['current_temperature'] = r.temperature
        results['relay_status'] = r.relay_status
        results['operating_mode'] = s.operating_mode.id
        results['night_temperature'] = s.night_temperature
        results['day_temperature'] = s.day_temperature
        results['weekend_temperature'] = s.weekend_temperature
        results['manual_temperature'] = s.manual_temperature
        results['scheduled_temperature'] = s.scheduled_temperature

        db.db.close()
        return results

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def scheduling(self):
        self.validate_auth()
        db.db.connect()
        scheduling = db.Scheduling.select().order_by(+db.Scheduling.dotw, +db.Scheduling.start_time)
        results = []
        # prepare days
        for x in range(7):
            results.append([])
        for s in scheduling:
            dotw = s.dotw - 1
            if dotw < 0:
                dotw = 6
            results[dotw].append(s.status)
        db.db.close()
        return results

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

    # @cherrypy.expose
    # def gettemp(self):
    #     self.validate_auth()
    #     return self.apiServer.get_temp()
    #
    # @cherrypy.expose
    # def getrelay(self):
    #     self.validate_auth()
    #     return self.apiServer.get_relay()
    #
    # @cherrypy.expose
    # def setrelay(self, status=None):
    #     self.validate_auth()
    #     if status is not None:
    #         return self.apiServer.set_relay(int(status) == 1)
    #     return ''
