from termostato import config
from StringIO import StringIO
import pycurl


class Api(object):
    def __init__(self):
        self.address = config.DeviceAddress
        self.port = config.DevicePort

    def get(self, path):
        _buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, "http://" + self.address + ":" + self.port + "/" + path)
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.CONNECTTIMEOUT, 10)
        c.setopt(c.WRITE, _buffer)
        c.perform()
        return _buffer.getvalue()
