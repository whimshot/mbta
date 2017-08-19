import pytest
import datetime
now = datetime.datetime.now()
then = now - datetime.timedelta(days=90)


@pytest.fixture
def busstop():
    import mbta
    busstop = mbta.BusStop('599')
    return busstop


@pytest.fixture
def routelist():
    return ['30', '34', '34E', '35', '36', '37',
            '39', '40', '40/50', '50', '51']


def test_predictions(busstop):
    """Is today a dictionary."""
    assert isinstance(busstop.predictions, dict)
    assert 'routes' in busstop.predictions
    assert isinstance(busstop.predictions['routes'], dict)
    assert 'stop_id' in busstop.predictions
    assert 'stop_name' in busstop.predictions


def test_routes(busstop, routelist):
    """Is today a dictionary."""
    assert isinstance(busstop.routes, list)
    assert any(x in routelist for x in busstop.routes)


def test_schedule(busstop):
    """Is today a dictionary."""
    assert isinstance(busstop.schedule, dict)
    assert 'routes' in busstop.schedule
    assert isinstance(busstop.schedule['routes'], dict)
    assert 'stop_id' in busstop.schedule
    assert 'stop_name' in busstop.schedule


def test_alerts(busstop):
    """Is today a dictionary."""
    assert isinstance(busstop.alerts, dict)
