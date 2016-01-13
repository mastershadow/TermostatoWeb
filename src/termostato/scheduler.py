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
            self.fetch_data()
            self.actuate()
            for i in range(self.interval):
                if not self.stopEvent.is_set():
                    time.sleep(1)

    def stop(self):
        if self.isAlive():
            self.stopEvent.set()
            self.join()

    def fetch_data(self):
        self.temperature = self.apiServer.get_temp()
        self.relay = self.apiServer.get_relay()
        if self.temperature is not None and self.relay is not None:
            db.db.connect()
            reading = db.Reading()
            reading.reading_timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            reading.temperature = self.temperature
            reading.relay_status = self.relay
            reading.save()

            setting = db.Setting.get()
            if self.relay != setting.current_relay_status:
                setting.current_relay_status = self.relay
                setting.save()

            db.db.close()

    def actuate(self):
        dt = datetime.datetime.today()
        n_dotw = dt.isoweekday()
        n_time = dt.time().strftime("%H:%M:00")
        db.db.connect()
        scheduling = db.Scheduling.select().where(db.Scheduling.dotw == n_dotw,
                                             db.Scheduling.start_time >= n_time,
                                             n_time <= db.Scheduling.end_time).get()
        setting = db.Setting.get()

        if setting.operating_mode == 0:
            # automatic
            t = None
            if scheduling.status == 0: # night
                t = setting.night_temperature
            elif scheduling.status == 1: # day
                t = setting.day_temperature
            elif scheduling.status == 2: # weekend
                t = setting.weekend_temperature

            self.set_relay_with_conditions(t,
                                           True,
                                           setting.over_hysteresis,
                                           setting.below_hysteresis)
            setting.last_automatic_status = scheduling.status
            setting.save()

        elif setting.operating_mode == 1:
            # manual with override

            if setting.last_automatic_status != scheduling.status:
                # return to automatic
                setting.operating_mode = 0
                setting.save()
            else:
                # still in manual mode
                self.set_relay_with_conditions(setting.manual_temperature,
                                               setting.desired_relay_status,
                                               setting.over_hysteresis,
                                               setting.below_hysteresis)

        elif setting.operating_mode == 2:
            # manual
            self.set_relay_with_conditions(setting.manual_temperature,
                                           setting.desired_relay_status,
                                           setting.over_hysteresis,
                                           setting.below_hysteresis)
        db.db.close()
        return

    def set_relay_with_conditions(self, desired_temperature, desired_status=True, over_h=0.0, below_h=0.0):
        if not desired_status: # if should be off, switch it off
            next_status = False
        else:
            if self.relay:
                # relay is on
                if self.temperature > desired_temperature + over_h:
                    # temperature is above T + tolerance. switch it off
                    next_status = False
                else:
                    # temperature is below T + tolerance. keep it on
                    next_status = True
            else:
                # relay is off
                if self.temperature < desired_temperature - below_h:
                    # temperature is below T - tolerance. switch if on
                    next_status = True
                else:
                    # temperature is above T - tolerance. keep it off
                    next_status = False

        self.apiServer.set_relay(next_status)
        return next_status
