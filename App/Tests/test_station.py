import pytest
from App.station import Station, load_stations_from_url


def test_station_init():
    station = Station("ID123", "TestStation", 48.0, 8.0, 2020, 2000, 2020, 2000)
    assert station.id == "ID123"
    assert station.name == "TestStation"
    assert station.latitude == 48.0
    assert station.longitude == 8.0


def test_station_repr():
    station = Station("ID123", "TestStation", 48.0, 8.0)
    assert "ID=ID123, Name=TestStation" in repr(station)


@pytest.fixture
def mock_requests_get(mocker):
    return mocker.patch("requests.get")


def test_load_stations_from_url(mock_requests_get):
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.text = "12345678901    Test Station"
    stations = load_stations_from_url("fake_url_inventory", "fake_url_stations")
    assert isinstance(stations, list)
    assert len(stations) > 0
    assert stations[0].id == "12345678901"