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

def test_load_stations_from_url():
    stations_text = """
    12345678901        Station Alpha
    22345678901        Station Beta
    32345678901        Station Gamma
    """

    inventory_text = """
    12345678901  12.3450  67.8900 TMAX 1980 2020
    12345678901  12.3450  67.8900 TMIN 1985 2015
    22345678901  23.4560  78.9010 TMAX 1990 2021
    32345678901  34.5670  89.0120 TMAX 2000 2022
    32345678901  34.5670  89.0120 TMIN 2005 2018
    """

    with patch("requests.get") as mock_requests_get:
        mock_requests_get.side_effect = [
            MagicMock(status_code=200, text=stations_text),
            MagicMock(status_code=200, text=inventory_text)
        ]

        stations = load_stations_from_url("url_stations_placeholder", "url_inventory_placeholder")

        expected_stations = [
            Station(id="12345678901", name="Station Alpha", latitude=12.345, longitude=67.89,
                    last_measure_tmax=2020, first_measure_tmax=1980, last_measure_tmin=2015, first_measure_tmin=1985),
            Station(id="22345678901", name="Station Beta", latitude=23.456, longitude=78.901,
                    last_measure_tmax=2021, first_measure_tmax=1990, last_measure_tmin=0, first_measure_tmin=0),
            Station(id="32345678901", name="Station Gamma", latitude=34.567, longitude=89.012,
                    last_measure_tmax=2022, first_measure_tmax=2000, last_measure_tmin=2018, first_measure_tmin=2005)
        ]

        # Assertions
        assert len(stations) == len(expected_stations)
        for station, expected_station in zip(stations, expected_stations):
            assert station.id == expected_station.id
            assert station.name == expected_station.name
            assert station.latitude == expected_station.latitude
            assert station.longitude == expected_station.longitude
            assert station.last_measure_tmax == expected_station.last_measure_tmax
            assert station.first_measure_tmax == expected_station.first_measure_tmax
            assert station.last_measure_tmin == expected_station.last_measure_tmin
            assert station.first_measure_tmin == expected_station.first_measure_tmin



# ----------------- Additional Tests -----------------




