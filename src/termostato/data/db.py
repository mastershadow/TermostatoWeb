from peewee import *

db = SqliteDatabase('termostato.db')


class Reading(Model):
    id = PrimaryKeyField()
    timestamp = DateTimeField()
    temperature = DoubleField()
    status = BooleanField()

    class Meta:
        database = db
        order_by = ('timestamp')


class Scheduling(Model):
    id = PrimaryKeyField()
    dotw = IntegerField()
    start_time = TimeField()
    end_time = TimeField()

    class Meta:
        database = db


class State(Model):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        database = db


class Setting(Model):
    id = PrimaryKeyField()
    day_temperature = DoubleField()
    night_temperature = DoubleField()
    state = ForeignKeyField(State)

    class Meta:
        database = db
        auto_increment = False
