"""MBTA arrival predictions for buses at a given stop from the MBTA."""
import configparser
import datetime
import logging
import logging.handlers
import math
import pprint
import string
import xml.etree.ElementTree as ET
import time
import requests
import sys
import inspect

config = configparser.ConfigParser()

try:
    assert __name__ == '__main__'
    config.read('mbta.conf')
except AssertionError:
    logger = logging.getLogger(__name__)
    config.read('mbta.conf')
    # MAXLOGSIZE = config.getint('Logging', 'maxlogsize')
    # ROTATIONCOUNT = config.getint('Logging', 'rotationcount')
    # LOGGERNAME = config.get('Logging', 'loggername')
    #
    # # create logger
    # logger = logging.getLogger(LOGGERNAME)
    # # logger.setLevel(logging.INFO)
    # logger.setLevel(logging.DEBUG)
    # # create file handler which logs even debug messages
    # logger_fh = logging.handlers.RotatingFileHandler(LOGGERNAME + '.log',
    #                                                  maxBytes=MAXLOGSIZE,
    #                                                  backupCount=ROTATIONCOUNT)
    # logger_fh.setLevel(logging.DEBUG)
    # # create console handler with a higher log level
    # logger_ch = logging.StreamHandler()
    # logger_ch.setLevel(logging.ERROR)
    # # create formatter and add it to the handlers
    # logger_formatter = logging.Formatter('%(asctime)s'
    #                                      + ' %(levelname)s'
    #                                      + ' %(name)s[%(process)d]'
    #                                      + ' %(message)s')
    # logger_fh.setFormatter(logger_formatter)
    # logger_ch.setFormatter(logger_formatter)
    # # add the handlers to the logger
    # logger.addHandler(logger_fh)
    # logger.addHandler(logger_ch)
else:
    MAXLOGSIZE = config.getint('Logging', 'maxlogsize')
    ROTATIONCOUNT = config.getint('Logging', 'rotationcount')
    LOGFILE = config.get('Logging', 'logfile')

    # create logger
    logger = logging.getLogger(__name__)
    # logger.setLevel(logging.INFO)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    logger_fh = logging.handlers.RotatingFileHandler(LOGFILE,
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
finally:
    pass


class BusStop(object):
    """Class representing a stop for an MBTA bus or buses."""

    def __init__(self, stop, **kwargs):
        """Create Stop object."""
        super().__init__(**kwargs)
        try:
            # self.logger = \
            #     logging.getLogger(__name__ + '.' + __name__ + '.'
            #                       + self.__class__.__name__)
            self.api_key = config.get('MBTA', 'apikey')

            self.stop = stop
            logger.info('Instantiating %s %s',
                        self.__class__.__name__, self.stop)
            self.base = 'http://realtime.mbta.com/developer/api'
            self.version = 'v2'
            self.endpoint = 'predictionsbystop'
            self.url = self.base + '/' + self.version + '/' + self.endpoint
            self.payload = {'api_key': self.api_key,
                            'stop': self.stop,
                            'format': 'xml'}
            self._predictions_last_updated = time.time()
            self.predictionsbystop()
            self.routesbystop()
            self.schedulebystop()
            self.alertsbystop()
        except Exception as e:
            raise
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
            self._predictions = {}
            self._predictions['routes'] = {}
            for elem in root.iter():
                if elem.tag == 'predictions':
                    self._predictions['stop_name'] = elem.get('stop_name')
                    self._predictions['stop_id'] = elem.get('stop_id')
                if elem.tag != 'route':
                    continue
                self._predictions['routes'][elem.get('route_name')] = {}
                _etas = []
                for trip in elem.iter():
                    if trip.tag != 'trip':
                        continue
                    _etas.append(
                        str(math.floor(int(trip.get('pre_away'))
                                       / 60)) + chr(160) + 'min.')
                    _trip_headsign = trip.get('trip_headsign')
                self._predictions['routes'][elem.get(
                    'route_name')]['etas'] = _etas
                self._predictions['routes'][elem.get(
                    'route_name')]['trip_headsign'] = _trip_headsign
                logger.info('Predictions <%s> %s %s [%s]',
                            self._predictions['stop_name'],
                            elem.get('route_name'),
                            _etas, _trip_headsign)
        except Exception as e:
            raise
        finally:
            pass

    @property
    def predictions(self):
        pass

    @predictions.getter
    def predictions(self):
        _now = time.time()
        if (_now - self._predictions_last_updated) > 59:
            self.predictionsbystop()
            self._predictions_last_updated = _now
        return self._predictions

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
            self._routes = [route.get('route_name')
                            for route in root.findall('.//*[@route_id]')]
        except Exception as e:
            raise
        finally:
            pass

    @property
    def routes(self):
        pass

    @routes.getter
    def routes(self):
        return self._routes

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
            self._schedule = {}
            self._schedule['routes'] = {}
            for elem in root.iter():
                if elem.tag == 'schedule':
                    self._schedule['stop_name'] = elem.get('stop_name')
                    self._schedule['stop_id'] = elem.get('stop_id')
                if elem.tag != 'route':
                    continue
                self._schedule['routes'][elem.get('route_name')] = []
                for trip in elem.iter():
                    if trip.tag != 'trip':
                        continue
                    self._schedule['routes'][elem.get('route_name')].append(
                        datetime.datetime.fromtimestamp(
                            int(trip.get(
                                'sch_arr_dt'))).strftime('%I:%M:%S %p'))
        except Exception as e:
            raise
        finally:
            pass

    @property
    def schedule(self):
        pass

    @schedule.getter
    def schedule(self):
        return self._schedule

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
            self._alerts = {}
        except Exception as e:
            raise
        finally:
            pass

    @property
    def alerts(self):
        pass

    @alerts.getter
    def alerts(self):
        return self._alerts


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=4)
    foo = BusStop('639')
    pp.pprint(foo.predictions)
    pp.pprint(foo.routes)
    pp.pprint(foo.schedule)
    pp.pprint(foo.alerts)
    bar = BusStop('599')
    pp.pprint(bar.predictions)
    pp.pprint(bar.routes)
    pp.pprint(bar.schedule)
    pp.pprint(bar.alerts)
