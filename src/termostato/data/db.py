from peewee import *

db = SqliteDatabase('termostato.db')


class Reading(Model):
    id = PrimaryKeyField()
    timestamp = DateTimeField()
    temperature = DoubleField()
    relay_status = BooleanField()

    class Meta:
        database = db
        order_by = ('timestamp')


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
    current_relay_status = BooleanField()

    class Meta:
        database = db
        auto_increment = False
