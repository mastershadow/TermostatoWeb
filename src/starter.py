from termostato import termostato, config
import signal
import sys
import ConfigParser

def signal_handler(signal, frame):
    t.stop()
    sys.exit(0)

if __name__ == '__main__':
    # read config
    cParser = ConfigParser.ConfigParser()
    cParser.read("../termostato.ini")
    config.Port = cParser.getint("Termostato", "Port")
    config.Interval = cParser.getint("Termostato", "Interval")
    config.DeviceAddress = cParser.get("Termostato", "DeviceAddress")

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    t = termostato.Termostato()
    t.start()
    signal.pause()

