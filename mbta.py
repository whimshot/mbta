"""MBTA arrival predictions for buses at a given stop from the MBTA."""
import configparser
import json
import logging
import logging.handlers
import math
import pprint
import string
import xml.etree.ElementTree as ET

import requests


config = configparser.ConfigParser()
config.read('mbta.conf')

MAXLOGSIZE = config.getint('Logging', 'maxlogsize')
ROTATIONCOUNT = config.getint('Logging', 'rotationcount')
LOGGERNAME = config.get('Logging', 'loggername')

# create logger
logger = logging.getLogger(LOGGERNAME)
# logger.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
logger_fh = logging.handlers.RotatingFileHandler(LOGGERNAME + '.log',
                                                 maxBytes=MAXLOGSIZE,
                                                 backupCount=ROTATIONCOUNT)
logger_fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
logger_ch = logging.StreamHandler()
logger_ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
logger_formatter = logging.Formatter('%(asctime)s'
                                     + ' %(levelname)s'
                                     + ' %(name)s[%(process)d]'
                                     + ' %(message)s')
logger_fh.setFormatter(logger_formatter)
logger_ch.setFormatter(logger_formatter)
# add the handlers to the logger
logger.addHandler(logger_fh)
logger.addHandler(logger_ch)


class BusStop(object):
    """Class representing a stop for an MBTA bus or buses."""

    def __init__(self, stop, **kwargs):
        """Create Stop object."""
        super().__init__(**kwargs)
        try:
            self.logger = \
                logging.getLogger(LOGGERNAME + '.' + __name__ + '.'
                                  + self.__class__.__name__)
            self.api_key = config.get('MBTA', 'apikey')

            self.stop = stop
            self.logger.info('Instantiating %s %s',
                             self.__class__.__name__, self.stop)
            self.base = 'http://realtime.mbta.com/developer/api'
            self.version = 'v2'
            self.endpoint = 'predictionsbystop'
            self.url = self.base + '/' + self.version + '/' + self.endpoint
            self.payload = {'api_key': self.api_key,
                            'stop': self.stop,
                            'format': 'xml'}
        except Exception as e:
            raise
        finally:
            pass

    def get_predictions(self):
        """Get predicted arrival times from MBTA."""
        try:
            ROUTE_MAX = config.getint('Default', 'route_max')
            self.letters = list(string.ascii_lowercase)[:ROUTE_MAX:]
            response = requests.get(self.url, params=self.payload)
            self.logger.info('response for stop %s %s',
                             self.stop, response)
            root = ET.fromstring(response.text)
            self.logger.info('got stop data %s', root.attrib)
            stop_name = root.attrib.get('stop_name')
            routes = root.find('.//*[@route_type="3"]')
            self.predictions = {}
            for route in routes:
                self.logger.info('got route data %s', route.attrib)
                directions = route.findall('.//*[@direction_name]')
                direction_name = directions[0].attrib.get('direction_name')
                route_id = route.attrib.get('route_id')
                trips = route.findall('.//*[@trip_id]')
                eta_string = '{0}' + chr(160) + 'min'
                etas = ', '.join([eta_string.format(eta) for eta
                                  in [math.floor(int(raw_eta) / 60)
                                      for raw_eta in
                                      [trip.attrib.get('pre_away')
                                       for trip in trips]]])
                trip_headsign = [trip.attrib.get('trip_headsign') for trip
                                 in trips][0]
                letter = self.letters.pop(0)
                self.predictions[letter] = {}
                self.predictions[letter]['route_id'] = route_id
                self.predictions[letter]['direction_name'] = direction_name
                self.predictions[letter]['etas'] = etas
                self.predictions[letter]['trip_headsign'] = trip_headsign
                self.predictions[letter]['stop_name'] = stop_name
        except Exception as e:
            self.predictions = {}
            for letter in self.letters:
                self.predictions[letter] = {}
                self.predictions[letter]['route_id'] = ''
                self.predictions[letter]['direction_name'] = ''
                self.predictions[letter]['etas'] = ''
                self.predictions[letter]['trip_headsign'] = ''
                self.predictions[letter]['stop_name'] = ''
            self.logger.warning('Failed to get predictions. {0}'.format(e))
        finally:
            pass

    def predictionsbystop(self):
        "Docstring goes here."
        try:
            BASE = config.get('MBTA', 'base')
            VERSION = config.get('MBTA', 'version')
            _payload = {'api_key': self.api_key,
                        'stop': self.stop,
                        'format': 'xml'}
            _url = BASE + '/' + VERSION + '/predictionsbystop'
            response = requests.get(_url, params=_payload)
            root = ET.fromstring(response.text)
            stop_name = root.attrib.get('stop_name')
            _predictions = {}
            return _predictions
        except Exception as e:
            raise
        finally:
            pass

    @property
    def predictions(self):
        pass

    @predictions.getter
    def predictions(self):
        return self.predictionsbystop()

    def routesbystop(self):
        "Docstring goes here."
        try:
            BASE = config.get('MBTA', 'base')
            VERSION = config.get('MBTA', 'version')
            _payload = {'api_key': self.api_key,
                        'stop': self.stop,
                        'format': 'xml'}
            _url = BASE + '/' + VERSION + '/routesbystop'
            response = requests.get(_url, params=_payload)
            root = ET.fromstring(response.text)
            stop_name = root.attrib.get('stop_name')
            _routes = [route.get('route_name')
                       for route in root.findall('.//*[@route_id]')]
            return _routes
        except Exception as e:
            raise
        finally:
            pass

    @property
    def routes(self):
        pass

    @routes.getter
    def routes(self):
        return self.routesbystop()

    def schedulebystop(self):
        "Docstring goes here."
        try:
            BASE = config.get('MBTA', 'base')
            VERSION = config.get('MBTA', 'version')
            _payload = {'api_key': self.api_key,
                        'stop': self.stop,
                        'format': 'xml'}
            _url = BASE + '/' + VERSION + '/schedulebystop'
            response = requests.get(_url, params=_payload)
            root = ET.fromstring(response.text)
            _schedule = {}
            return _schedule
        except Exception as e:
            raise
        finally:
            pass

    @property
    def schedule(self):
        pass

    @schedule.getter
    def schedule(self):
        return self.schedulebystop()

    def alertsbystop(self):
        "Docstring goes here."
        try:
            BASE = config.get('MBTA', 'base')
            VERSION = config.get('MBTA', 'version')
            _payload = {'api_key': self.api_key,
                        'stop': self.stop,
                        'format': 'xml'}
            _url = BASE + '/' + VERSION + '/alertsbystop'
            response = requests.get(_url, params=_payload)
            root = ET.fromstring(response.text)
            _alerts = {}
            return _alerts
        except Exception as e:
            raise
        finally:
            pass

    @property
    def alerts(self):
        pass

    @alerts.getter
    def alerts(self):
        return self.alertsbystop()


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=4)
    foo = BusStop('639')
    pp.pprint(foo.predictions)
    pp.pprint(foo.routes)
    pp.pprint(foo.schedule)
    pp.pprint(foo.alerts)
    bar = BusStop('599')
    pp.pprint(bar.predictions)
