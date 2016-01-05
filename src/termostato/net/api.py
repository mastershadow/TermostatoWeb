from termostato import config
from StringIO import StringIO
import pycurl


class Api(object):
    def __init__(self):
        self.address = config.DeviceAddress

    def get_temp(self):
        return self.get("gettemp");

    def get_relay(self):
        return self.get("getrelay");

    def set_relay(self, status):
        if status is True:
            return self.get("setrelay/on");
        return self.get("setrelay/off");

    def get(self, path):
        _buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.address + "/api/" + path)
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.CONNECTTIMEOUT, 10)
        c.setopt(c.WRITEDATA, _buffer)
        c.perform()
        return _buffer.getvalue()
