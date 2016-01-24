from termostato import termostato, config
from termostato.data import db
import signal
import sys
import ConfigParser
import logging
import logging.config


def signal_handler(signal, frame):
    t.stop()
    sys.exit(0)

if __name__ == '__main__':
    logging.config.fileConfig('../logging.ini')
    # read config
    cParser = ConfigParser.ConfigParser()
    cParser.read("../termostato.ini")
    config.Port = cParser.getint("Termostato", "Port")
    config.Interval = cParser.getint("Termostato", "Interval")
    config.DeviceAddress = cParser.get("Termostato", "DeviceAddress")

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    db.prepare_settings_if_needed()

    t = termostato.Termostato()
    t.start()
    signal.pause()

