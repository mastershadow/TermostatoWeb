from peewee import *

db = SqliteDatabase('termostato.db')


class Reading(Model):
    timestamp = DateTimeField()
    temperature = DoubleField()
    started = BooleanField()

    class Meta:
        database = db


class Scheduling(Model):
    dotw = IntegerField()
    starthour = IntegerField()
    startminute = IntegerField()
    endhour = IntegerField()
    endminute = IntegerField()
    temperature = DoubleField()

    class Meta:
        database = db


class BaseSettings(Model):
    nighttemperature = DoubleField()

    class Meta:
        database = db