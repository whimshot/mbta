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
    return ['30', '34', '34E', '35', '36', '37', '40', '40/50', '50', '51']


def test_predictions(busstop):
    """Is today a dictionary."""
    assert isinstance(busstop.predictionsbystop(), dict)
    assert isinstance(busstop.predictions, dict)


def test_routes(busstop, routelist):
    """Is today a dictionary."""
    assert isinstance(busstop.routesbystop(), list)
    assert isinstance(busstop.routes, list)
    assert any(x in routelist for x in busstop.routes)


def test_schedule(busstop):
    """Is today a dictionary."""
    assert isinstance(busstop.schedulebystop(), dict)
    assert isinstance(busstop.schedule, dict)


def test_alerts(busstop):
    """Is today a dictionary."""
    assert isinstance(busstop.alertsbystop(), dict)
    assert isinstance(busstop.alerts, dict)
