from termostato import config
import sys
import telnetlib


class Api(object):
    def __init__(self):
        self.address = config.DeviceAddress

    def parse_response(self, res):
        if res is not None:
            tokens = res.split()
            if len(tokens) > 1:
                return tokens[1]
        return None

    def get_temp(self):
        r = self.parse_response(self.get("GETTEMP"))
        if r is None:
            return 20.0
        return r

    def get_relay(self):
        r = self.parse_response(self.get("GETRELAY"))
        if r is not None:
            return r.lower() == 'on'
        #return None
        return False

    def set_relay(self, status):
        r = None
        if status is True:
            r = self.get("SETRELAY ON")
        else:
            r = self.get("SETRELAY OFF")
        r = self.parse_response(r)
        if r is not None:
            return r.lower() == 'on'
        return None

    def get(self, command):
        try:
            timeout = 3
            tn = telnetlib.Telnet(self.address, 23, timeout)
            tn.write(command + "\n")
            _buffer = tn.read_until("\n", timeout).rstrip()
            tn.close()
            return _buffer
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return None
