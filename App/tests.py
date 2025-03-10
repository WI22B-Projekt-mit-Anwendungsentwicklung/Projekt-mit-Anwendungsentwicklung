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

@patch("requests.get")
def test_load_stations_from_url(mock_requests_get):


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
    assert len(stations) == 2

    assert stations[0].id == "12345678901"
    assert stations[0].name == "Test Station 1"
    assert stations[0].latitude == 48.123
    assert stations[0].longitude == 8.456
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

# ----------------- Additional Tests -----------------

def test_invalid_coordinates():
    from data_services import get_stations_in_radius

    with pytest.raises(ValueError):
        get_stations_in_radius(95.0, 8.0, 100, 2000, 2020, 5)  # Breitengrad > 90 ist ungültig

    with pytest.raises(ValueError):
        get_stations_in_radius(48.0, 190.0, 100, 2000, 2020, 5)  # Längengrad > 180 ist ungültig

    with pytest.raises(ValueError):
        get_stations_in_radius("abc", 8.0, 100, 2000, 2020, 5)  # Ungültige Eingabe als String

import requests

def test_api_missing_params():
    response = requests.get("http://localhost:5000/get_weather_data")
    assert response.status_code == 400  # Bad Request
    assert "Missing parameters" in response.text  # Erwartete Fehlermeldung


