import net.api as api
import data.db as db
import config
import threading
import time
import datetime


class Scheduler(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.interval = config.Interval
        self.apiServer = api.Api()
        self.temperature = None
        self.relay = None

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
        self.temperature = self.apiServer.get_temp()
        self.relay = self.apiServer.get_relay()
        if self.temperature is not None and self.relay is not None:
            db.db.connect()
            reading = db.Reading()
            reading.reading_timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            reading.temperature = self.temperature
            reading.relay_status = self.relay
            reading.save()
            db.db.close()

    def push(self):
        dt = datetime.datetime.today()
        n_dotw = dt.isoweekday()
        n_time = dt.time().strftime("%H:%M:00")
        db.db.connect()
        scheduling = db.Scheduling.select().where(db.Scheduling.dotw == n_dotw,
                                             db.Scheduling.start_time >= n_time,
                                             n_time <= db.Scheduling.end_time).get()
        setting = db.Setting.get()
        # TODO analise scheduling to send command to arduino
        db.db.close()
        return ''
