from termostato import config
from StringIO import StringIO
import pycurl
import sys


class Api(object):
    def __init__(self):
        self.address = config.DeviceAddress

    def parseResponse(self, res):
        if res is not None:
            tokens = res.split()
            if len(tokens) > 1:
                return tokens[1]
        return None

    def get_temp(self):
        return self.parseResponse(self.get("gettemp"));

    def get_relay(self):
        r = self.parseResponse(self.get("getrelay"));
        if r is not None:
            return r.lower() == 'on'
        return None

    def set_relay(self, status):
        r = None
        if status is True:
            r = self.get("setrelay/on");
        else:
            r = self.get("setrelay/off")
        r = self.parseResponse(r);
        if r is not None:
            return r.lower() == 'on'
        return None

    def get(self, path):
        try:
            _buffer = StringIO()
            c = pycurl.Curl()
            c.setopt(c.URL, self.address + "/api/" + path)
            c.setopt(c.FOLLOWLOCATION, True)
            c.setopt(c.CONNECTTIMEOUT, 10)
            c.setopt(c.WRITEDATA, _buffer)
            c.perform()
            return _buffer.getvalue()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None
