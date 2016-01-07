from peewee import *

db = SqliteDatabase('../termostato.db')


def create_tables():
    db.connect()
    db.create_tables([Reading, Scheduling, OperatingMode, Setting])


def prepare_settings_if_needed():
    db.connect()
    try:
        s = Setting.get()
    except:
        s = Setting()
        s.day_temperature = 20.0
        s.night_temperature = 16.0
        s.weekend_temperature = 18.0
        s.manual_temperature = 20.0
        s.scheduled_temperature = 20.0
        s.operating_mode = 0
        s.over_hysteresis = 0.5
        s.below_hysteresis = 0.5
        s.last_automatic_status = 0
        s.current_relay_status = False
        s.desired_relay_status = False
        s.save()

    try:
        OperatingMode.get()
    except:
        OperatingMode.create(id=0, name="Automatic")
        OperatingMode.create(id=1, name="Manual")
        OperatingMode.create(id=2, name="Manual with override")
    db.close()


class Reading(Model):
    id = PrimaryKeyField()
    reading_timestamp = DateTimeField()
    temperature = DoubleField()
    relay_status = BooleanField()

    class Meta:
        database = db


class Scheduling(Model):
    id = PrimaryKeyField()
    dotw = IntegerField()
    start_time = TimeField()
    end_time = TimeField()
    status = IntegerField()  # 0 is Night, 1 is Day, 2 is Weekend

    class Meta:
        database = db


class OperatingMode(Model):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        database = db


class Setting(Model):
    id = PrimaryKeyField()
    day_temperature = DoubleField()
    night_temperature = DoubleField()
    weekend_temperature = DoubleField()
    manual_temperature = DoubleField()
    operating_mode = ForeignKeyField(OperatingMode)
    over_hysteresis = DoubleField()
    below_hysteresis = DoubleField()
    last_automatic_status = IntegerField()
    scheduled_temperature = DoubleField()
    current_relay_status = BooleanField()
    desired_relay_status = BooleanField()

    class Meta:
        database = db
        auto_increment = False
