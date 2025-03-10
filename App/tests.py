import pytest
from flask import Flask
from data_services import haversine, get_stations_in_radius, get_datapoints_for_station
from datapoint import DataPoint, extract_average_value, download_and_create_datapoints, download_and_create_datapoints_local
from routes import init_routes
from station import Station, load_stations_from_url


# ----------------- TESTS FÜR data_services.py -----------------

def test_haversine():
    assert haversine(0, 0, 0, 0) == 0
    assert round(haversine(48.8566, 2.3522, 51.5074, -0.1278), 1) == 343.6


def test_get_stations_in_radius(mocker):
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [("ST123", "Station Name", 48.0, 8.0)]
    mock_conn = mocker.patch("App.data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 5)
    assert len(stations) > 0
    assert stations[0][0][0] == "ST123"


# ----------------- TESTS FÜR datapoint.py -----------------

def test_datapoint_init():
    dp = DataPoint(202401, 25.5, 10.3, "ST123")
    assert dp.date == 202401
    assert dp.tmax == 25.5
    assert dp.tmin == 10.3


def test_datapoint_repr():
    dp = DataPoint(202401, 25.5, 10.3, "ST123")
    assert "DataPoint(date=202401" in repr(dp)


def test_extract_average_value():
    line = """01234567890123456789   250   300   -9999  """
    assert extract_average_value(line) == 27.5


# ----------------- TESTS FÜR routes.py -----------------

def test_home():
    app = Flask(__name__)
    init_routes(app)
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200


def test_receive_data(mocker):
    app = Flask(__name__)
    init_routes(app)
    client = app.test_client()

    mocker.patch("App.data_services.get_stations_in_radius", return_value=["Station1", "Station2"])

    response = client.post('/submit', json={
        "latitude": 48.0,
        "longitude": 8.0,
        "radius": 100,
        "yearStart": 2000,
        "yearEnd": 2020,
        "stations": []
    })

    assert response.status_code == 200
    assert response.get_json() == ["Station1", "Station2"]


# ----------------- TESTS FÜR station.py -----------------

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
