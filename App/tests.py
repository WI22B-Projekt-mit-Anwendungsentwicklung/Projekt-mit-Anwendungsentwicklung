import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from data_services import haversine, get_stations_in_radius, get_datapoints_for_station
from datapoint import DataPoint, extract_average_value, download_and_create_datapoints, download_and_create_datapoints_local
from routes import init_routes
from station import Station, load_stations_from_url

# ----------------- data_services.py -----------------

def test_haversine():
    assert haversine(0, 0, 0, 0) == 0
    assert round(haversine(48.8566, 2.3522, 51.5074, -0.1278), 1) == 343.6

def test_get_stations_in_radius(mocker):
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [("ST123", "Station Name", 48.0, 8.0)]
    mock_conn = mocker.patch("data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 5)
    assert len(stations) > 0
    assert stations[0][0][0] == "ST123"

# ----------------- datapoint.py -----------------

def test_datapoint_init():
    dp = DataPoint(202401, 25.5, 10.3, "ST123")
    assert dp.date == 202401
    assert dp.tmax == 25.5
    assert dp.tmin == 10.3

def test_datapoint_repr():
    dp = DataPoint(202401, 25.5, 10.3, "ST123")
    assert "DataPoint(date=202401" in repr(dp)


def test_extract_average_value():
    line = "01234567890123456789   250   300   -9999  "
    assert round(extract_average_value(line), 2) == 51.63

# ----------------- routes.py -----------------

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

    mocker.patch("data_services.get_stations_in_radius", return_value=["Station1", "Station2"])

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


# ----------------- station.py -----------------

def test_station_init():
    station = Station("ID123", "TestStation", 48.0, 8.0, 2020, 2000, 2020, 2000)
    assert station.id == "ID123"
    assert station.name == "TestStation"
    assert station.latitude == 48.0
    assert station.longitude == 8.0


def test_station_repr():
    station = Station("ID123", "TestStation", 48.0, 8.0)
    assert "ID=ID123, Name=TestStation" in repr(station)

def test_load_stations_with_noaa_data():
    """
    Testet die load_stations_from_url-Funktion mit Mock-Daten der NOAA-Stationen.
    """

    # Mock-Inhalte der Dateien (Angabe fester Texte)
    mock_stations_data = """\
ACW00011604  -17.116  -145.500  00185  RAROTONGA           CK
AGM00060420   36.850    3.030   00024  ALGIERS-HYDRA       DZ
AGE00147704   41.727   44.765   05555  TBILISI             GE
"""

    mock_inventory_data = """\
ACW00011604  -17.116  -145.500 TMIN 1928 2013
ACW00011604  -17.116  -145.500 PRCP 1928 2013
AGM00060420   36.850    3.030 TMAX 1891 2012
AGM00060420   36.850    3.030 TMIN 1892 2012
AGE00147704   41.727   44.765 PRCP 1881 2011
"""

    # Mocking requests.get, um die URLs zu simulieren
    with patch("requests.get") as mock_get:
        def mock_response(url):
            if "stations" in url:
                return MockResponse(mock_stations_data, 200)
            elif "inventory" in url:
                return MockResponse(mock_inventory_data, 200)
            return MockResponse("", 404)

        mock_get.side_effect = mock_response

        # URLs simulieren
        url_stations = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
        url_inventory = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt"

        # Test: Funktion aufrufen
        stations = load_stations_from_url(url_inventory, url_stations)

        # Sicherstellen, dass Daten geladen wurden
        assert len(stations) == 3, "Es sollten 3 Stationen geladen werden."

        # Prüfen der Daten jeder Station
        assert stations[0]["id"] == "ACW00011604", "Station ID sollte ACW00011604 sein."
        assert stations[0]["name"] == "RAROTONGA", "Stationsname sollte RAROTONGA sein."
        assert stations[0]["latitude"] == -17.116, "Latitude von Station 0 ist falsch."
        assert stations[0]["longitude"] == -145.500, "Longitude von Station 0 ist falsch."

        assert stations[1]["id"] == "AGM00060420", "Station ID sollte AGM00060420 sein."
        assert stations[2]["id"] == "AGE00147704", "Station ID sollte AGE00147704 sein."


# Mock-Klasse für die Simulation von requests.get
class MockResponse:
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code




# ----------------- Additional Tests -----------------




