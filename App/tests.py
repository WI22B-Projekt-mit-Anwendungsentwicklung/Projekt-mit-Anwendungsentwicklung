import pytest
import requests
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

def haversine_distance(lat1, lon1, lat2, lon2):
    """ Hilfsfunktion zur Berechnung der Entfernung zwischen zwei Punkten """
    from math import radians, cos, sin, asin, sqrt

    R = 6371  # Erdradius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c  # Entfernung in km

@pytest.fixture
def mock_db_connection(mocker):
    """Fixture zum Mocken der Datenbankverbindung"""
    mock_cursor = mocker.Mock()
    mock_conn = mocker.patch("data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_cursor

def test_stations_are_returned(mock_db_connection):
    """Testet, ob `get_stations_in_radius` mindestens eine Station zurückgibt."""
    mock_db_connection.fetchall.return_value = [
        ("ST001", "Station A", 48.001, 8.001)
    ]

    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 5)

    assert len(stations) > 0, "Es wurden keine Stationen zurückgegeben!"
    assert stations[0][0] == "ST001"

def test_multiple_stations_returned(mock_db_connection):
    """Testet, ob mehrere Stationen zurückgegeben werden."""
    mock_db_connection.fetchall.return_value = [
        ("ST001", "Station A", 48.001, 8.001),
        ("ST002", "Station B", 48.005, 8.005),
        ("ST003", "Station C", 48.003, 8.003)
    ]

    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 5)

    assert len(stations) == 3, "Nicht alle erwarteten Stationen wurden zurückgegeben!"

def test_stations_sorted_by_distance(mock_db_connection):
    """Testet, ob die Stationen korrekt nach Entfernung sortiert werden."""
    mock_db_connection.fetchall.return_value = [
        ("ST001", "Station A", 48.001, 8.001),  # Nächste
        ("ST003", "Station C", 48.003, 8.003),  # Mittelweit entfernt
        ("ST002", "Station B", 48.005, 8.005)   # Am weitesten entfernt
    ]

    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 5)

    distances = [haversine_distance(48.0, 8.0, s[2], s[3]) for s in stations]

    assert distances == sorted(distances), "Die Stationen sind nicht nach Entfernung sortiert!"

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

@patch("requests.get")
def test_load_stations_from_url(mock_requests_get):
    """
    Testet die Funktion load_stations_from_url, indem sie simulierte HTTP-Responses für
    die Stations- und Inventar-Daten verarbeitet.
    """

    stations_text = """12345678901                              Test Station 1
98765432109                              Test Station 2"""

    inventory_text = """12345678901  48.123  008.456   TMAX  2020  2023
12345678901  48.123  008.456   TMIN  2018  2022
98765432109  50.987  007.654   TMAX  2015  2021
98765432109  50.987  007.654   TMIN  2013  2020"""

    mock_requests_get.side_effect = [
        MagicMock(status_code=200, text=stations_text),
        MagicMock(status_code=200, text=inventory_text),
    ]

    stations = load_stations_from_url("fake_url_inventory", "fake_url_stations")

    for station in stations:
        print(f"Station ID: {station.id}, Name: {station.name}, Lat: {station.latitude}, Lon: {station.longitude}")

    assert isinstance(stations, list)
    assert len(stations) == 2  # Zwei Stationen sollten geladen werden

    assert stations[0].id == "12345678901"
    assert stations[0].name == "Test Station 1"
    assert stations[0].latitude == 48.123  # Prüfe, ob `latitude` korrekt ist
    assert stations[0].longitude == 8.456  # Prüfe, ob `longitude` korrekt ist
    assert stations[0].first_measure_tmax == 2020
    assert stations[0].last_measure_tmax == 2023
    assert stations[0].first_measure_tmin == 2018
    assert stations[0].last_measure_tmin == 2022

    assert stations[1].id == "98765432109"
    assert stations[1].name == "Test Station 2"
    assert stations[1].latitude == 50.987
    assert stations[1].longitude == 7.654
    assert stations[1].first_measure_tmax == 2015
    assert stations[1].last_measure_tmax == 2021
    assert stations[1].first_measure_tmin == 2013
    assert stations[1].last_measure_tmin == 2020


