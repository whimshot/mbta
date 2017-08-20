"""Docstring goes here."""
import configparser
import logging
import logging.handlers

import kivy.app
import kivy.clock
import kivy.core.window
import kivy.uix.boxlayout
import kivy.uix.button
import kivy.uix.gridlayout
import kivy.uix.image
import kivy.uix.label


kivy.config.Config.set('graphics', 'resizable', 0)
kivy.config.Config.set('graphics', 'width', 800)
kivy.config.Config.set('graphics', 'height', 480)
kivy.core.window.Window.size = (800, 480)
config = configparser.ConfigParser()

try:
    assert __name__ == '__main__'
    config.read('mbta.conf')
except AssertionError:
    print('mbtaui assertion error')
    logger = logging.getLogger(__name__)
    config.read('mbta.conf')
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
    import mbta


# class BusLabel(kivy.uix.button.Button):
class BusLabel(kivy.uix.label.Label):
    """docstring for BusLabel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass


class MBTABoxTitle(BusLabel):
    """docstring for BoxTitle."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass


class BusHeader(BusLabel):
    """docstring for BusHeader."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass


class RouteLabel(BusLabel):
    """docstring for RouteLabel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass


class ETALabel(BusLabel):
    """docstring for ETALabel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass


class NoPredictionsLabel(BusLabel):
    """docstring for NoPredictionsLabel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass


class HeadSignLabel(BusLabel):
    """docstring for HeadSignLabel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass


class BusGrid(kivy.uix.gridlayout.GridLayout):
    """docstring for BusGrid."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self._outbound = mbta.BusStop('599')
            self._inbound = mbta.BusStop('639')
        except Exception as e:
            raise
        else:
            self._grid = {}
            self.add_widget(BusHeader())
            self.add_widget(
                BusHeader(text=self._inbound.predictions['stop_name']))
            self.add_widget(
                BusHeader(text=self._outbound.predictions['stop_name']))
            self.add_widget(BusHeader(text='Destination'))
            for _, _rt in zip(self._inbound.routes, self._outbound.routes):
                _row = []
                _route_name = RouteLabel(text=_rt)
                self.add_widget(_route_name)
                _row.append(_route_name)

                try:
                    _inbound_etas = ', '.join(
                        self._inbound.predictions['routes'][_rt]['etas'])
                    _stop_a_eta = ETALabel(text=_inbound_etas)
                except LookupError:
                    _inbound_etas = '[sub]No Predictions[/sub]'
                    _stop_a_eta = ETALabel(
                        text=_inbound_etas, color=[1, 0, 0, 0.75],
                        markup=True)
                finally:
                    self.add_widget(_stop_a_eta)
                    _row.append(_stop_a_eta)

                try:
                    _outbound_etas = ', '.join(
                        self._outbound.predictions['routes'][_rt]['etas'])
                    _stop_b_eta = ETALabel(text=_outbound_etas)
                except LookupError:
                    _outbound_etas = '[sub]No Predictions[/sub]'
                    _stop_b_eta = ETALabel(
                        text=_outbound_etas, color=[1, 0, 0, 0.75],
                        markup=True)
                finally:
                    self.add_widget(_stop_b_eta)
                    _row.append(_stop_b_eta)

                try:
                    _headsign = self._outbound.predictions[
                        'routes'][_rt]['trip_headsign']
                    _headsign_widget = HeadSignLabel(text=_headsign)
                except LookupError:
                    _headsign = ''
                    _headsign_widget = HeadSignLabel(text=_headsign)
                finally:
                    self.add_widget(_headsign_widget)
                    _row.append(_headsign_widget)

                self._grid[_rt] = _row
                logger.info('seting up %s with (%s) (%s) [%s]',
                            _rt, _inbound_etas, _outbound_etas, _headsign)
            kivy.clock.Clock.schedule_interval(self.update, 60)

    def update(self, dt):
        for _rt in self._grid:
            try:
                _inbound_etas = ', '.join(
                    self._inbound.predictions['routes'][_rt]['etas'])
                self._grid[_rt][1].text = _inbound_etas
                self._grid[_rt][1].color = [1, 1, 1, 1]
            except LookupError:
                _inbound_etas = '[sub]No Predictions[/sub]'
                self._grid[_rt][1].text = _inbound_etas
                self._grid[_rt][1].color = [1, 0, 0, 0.75]
                self._grid[_rt][1].markup = True
            try:
                _outbound_etas = ', '.join(
                    self._outbound.predictions['routes'][_rt]['etas'])
                self._grid[_rt][2].text = _outbound_etas
                self._grid[_rt][2].color = [1, 1, 1, 1]
            except LookupError:
                _outbound_etas = '[sub]No Predictions[/sub]'
                self._grid[_rt][2].text = _outbound_etas
                self._grid[_rt][2].color = [1, 0, 0, 0.75]
                self._grid[_rt][2].markup = True
            try:
                _headsign = self._outbound.predictions[
                    'routes'][_rt]['trip_headsign']
                self._grid[_rt][3].text = _headsign
            except LookupError:
                _headsign = ''
                self._grid[_rt][3].text = _headsign
            logger.info('updating %s with (%s) (%s) [%s]',
                        _rt, _inbound_etas, _outbound_etas, _headsign)


class BusBox(kivy.uix.boxlayout.BoxLayout):
    """docstring for BusBox."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bt = MBTABoxTitle(text='[b]Bus ETAs[/b]', markup=True)
        self.add_widget(self.bt)
        self.bg = BusGrid()
        self.add_widget(self.bg)


class BusApp(kivy.app.App):
    """docstring for BusApp."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def build(arg):
        bb = BusBox()
        return bb


if __name__ == '__main__':
    BusApp().run()
