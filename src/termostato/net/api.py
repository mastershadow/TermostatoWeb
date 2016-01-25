from termostato import config
import sys
import telnetlib
import logging


class Api(object):
    def __init__(self):
        self.address = config.DeviceAddress
        self.logger = logging.getLogger(__name__)

    def parse_response(self, res):
        if res is not None:
            tokens = res.split()
            if len(tokens) > 1:
                return tokens[1]
        return None

    def get_temp(self):
        r = float(self.parse_response(self.get("GETTEMP")))
        return r

    def get_relay(self):
        r = self.parse_response(self.get("GETRELAY"))
        if r is not None:
            return r.lower() == 'on'
        return None

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
            self.logger.debug("API: %s - %s", command, _buffer)
            tn.close()
            if _buffer == '+WHAT?':
                _buffer = None
            return _buffer
        except:
            self.logger.error("Unexpected error: %s", sys.exc_info()[0])
            return None
