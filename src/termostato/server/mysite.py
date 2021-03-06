from termostato.net import api
from termostato.data import db
import cherrypy
import datetime
import pytz
from decimal import Decimal


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
        db_results = db.Reading.raw("select "
                                    "datetime((strftime('%s', reading_timestamp) / 600) * 600, 'unixepoch') interval, "
                                    "avg(temperature) temperature from reading "
                                    "group by interval "
                                    "having reading_timestamp  >= datetime('now', '-1 day') "
                                    "order by interval").execute()
        # db_results = db.Reading.select().order_by(-db.Reading.reading_timestamp).limit(250)
        utc = pytz.utc
        tz = pytz.timezone("Europe/Rome")
        fmt = "%Y-%m-%d %H:%M:%S"

        for r in db_results:
            results.append({
                'timestamp': utc.localize(datetime.datetime.strptime(r.interval, fmt)).astimezone(tz).strftime(fmt),
                'temperature': Decimal(r.temperature).quantize(Decimal(10) ** -1)
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
        results['desired_relay_status'] = s.desired_relay_status

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
            dotw = day_idx + 1
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
        db.db.connect()
        s = db.Setting.get()
        s.day_temperature = t
        s.save()
        db.db.close()
        return t

    @cherrypy.expose
    def save_weektemp(self, t):
        self.validate_auth()
        db.db.connect()
        s = db.Setting.get()
        s.weekend_temperature = t
        s.save()
        db.db.close()
        return t

    @cherrypy.expose
    def save_nighttemp(self, t):
        self.validate_auth()
        db.db.connect()
        s = db.Setting.get()
        s.night_temperature = t
        s.save()
        db.db.close()
        return t

    @cherrypy.expose
    def save_manualtemp(self, t):
        self.validate_auth()
        db.db.connect()
        s = db.Setting.get()
        s.manual_temperature = t
        s.save()
        db.db.close()
        return t

    @cherrypy.expose
    def save_operatingmode(self, mode):
        self.validate_auth()
        db.db.connect()
        s = db.Setting.get()
        s.operating_mode = db.OperatingMode.get(db.OperatingMode.id == mode)
        if mode == "0":
            s.desired_relay_status = True
        s.save()
        db.db.close()
        return mode

    @cherrypy.expose
    def save_relaystatus(self, status):
        self.validate_auth()
        if status == "false":
            status = False
        else:
            status = True
        db.db.connect()
        s = db.Setting.get()
        s.desired_relay_status = status
        s.save()
        db.db.close()
        return str(status)
