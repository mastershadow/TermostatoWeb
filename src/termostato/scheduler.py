import net.api as api
import data.db as db
import config
import threading
import time
import datetime
import logging


class Scheduler(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.stopEvent = threading.Event()
        self.interval = config.Interval
        self.apiServer = api.Api()
        self.temperature = None
        self.relay = None

    def run(self):
        while not self.stopEvent.is_set():
            if self.fetch_data():
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
            return True
        return False

    def actuate(self):
        dt = datetime.datetime.today()
        # print dt
        # There is no need for this as today is already local
        # utc = pytz.utc
        # tz = pytz.timezone("Europe/Rome")
        # dt = utc.localize(dt).astimezone(tz)

        n_dotw = dt.isoweekday()
        n_time = dt.time().strftime("%H:%M:00")
        db.db.connect()
        scheduling = db.Scheduling.select().where(db.Scheduling.dotw == n_dotw,
                                                  db.Scheduling.start_time <= n_time,
                                                  n_time <= db.Scheduling.end_time).get()
        setting = db.Setting.get()
        print "OpMode: " + str(setting.operating_mode.id)
        if setting.operating_mode.id == 0:
            # automatic
            t = None
            if scheduling.status == 0:  # night
                t = setting.night_temperature
            elif scheduling.status == 1:  # day
                t = setting.day_temperature
            elif scheduling.status == 2:  # weekend
                t = setting.weekend_temperature

            drs = self.set_relay_with_conditions(t,
                                                 True,
                                                 setting.over_hysteresis,
                                                 setting.below_hysteresis)
            setting.desired_relay_status = drs
            setting.last_automatic_status = scheduling.status
            setting.scheduled_temperature = t
            setting.save()

        elif setting.operating_mode.id == 1:
            # manual with override
            self.logger.debug("MODE: Manual with override")

            if setting.last_automatic_status != scheduling.status:
                self.logger.debug("Back to automatic")
                # return to automatic
                setting.operating_mode = db.OperatingMode.get(db.OperatingMode.id == 0)
                setting.save()
            else:
                # still in manual mode
                drs = self.set_relay_with_conditions(setting.manual_temperature,
                                                     setting.desired_relay_status,
                                                     setting.over_hysteresis,
                                                     setting.below_hysteresis)

                setting.desired_relay_status = drs
                setting.scheduled_temperature = setting.manual_temperature
                setting.save()

        elif setting.operating_mode.id == 2:
            # manual
            self.logger.debug("MODE: Manual")
            drs = self.set_relay_with_conditions(setting.manual_temperature,
                                                 setting.desired_relay_status,
                                                 setting.over_hysteresis,
                                                 setting.below_hysteresis)
            setting.desired_relay_status = drs
            setting.scheduled_temperature = setting.manual_temperature

            setting.save()
        db.db.close()
        return

    def set_relay_with_conditions(self, desired_temperature, desired_status=True, over_h=0.0, below_h=0.0):
        self.logger.debug("T:" + str(self.temperature) + " R:" + str(self.relay) + " " +
                          str(desired_temperature) + " " + str(desired_status) + " " + str(over_h) + " " + str(below_h))
        if not desired_status:  # if should be off, switch it off
            next_status = False
        else:
            if self.relay is True:
                # relay is on
                max_temp = float(desired_temperature + over_h)
                if self.temperature > max_temp:
                    # temperature is above T + tolerance. switch it off
                    self.logger.debug("Relay on and Above T+. Off")
                    next_status = False
                else:
                    # temperature is below T + tolerance. keep it on
                    self.logger.debug("Relay on and Below T+. On")
                    next_status = True
            else:
                # relay is off
                min_temp = float(desired_temperature - below_h)
                if self.temperature < min_temp:
                    # temperature is below T - tolerance. switch if on
                    self.logger.debug("Relay off and Below T-. On")
                    next_status = True
                else:
                    # temperature is above T - tolerance. keep it off
                    self.logger.debug("Relay off and Above T-. Off")
                    next_status = False

        self.logger.debug("Next: " + str(next_status))
        if next_status != self.relay:
            self.apiServer.set_relay(next_status)
        return next_status
