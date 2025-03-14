
# =========================================================
# TESTS FOR .PY
# -> routes.py
# =========================================================

import pytest
from flask import Flask
from src.data_services import get_stations_in_radius, get_datapoints_for_station, save_data_to_db
from src.datapoint import DataPoint, extract_average_value, download_and_create_datapoints, download_and_create_datapoints_local
from src.routes import init_routes
from src.station import Station, load_stations_from_url
from src.calculations import find_stations_within_radius, haversine
from unittest.mock import patch, MagicMock
from mysql.connector import pooling
from unittest import mock

def test_home():
    """Tests if the home route ('/') returns a 200 OK response."""
    with patch("src.routes.render_template", return_value="dummy"):
         app = Flask(__name__)
         init_routes(app)
         client = app.test_client()
         response = client.get('/')
         assert response.status_code == 200

"""
def test_receive_data(mocker):
    'Tests if the '/submit' endpoint correctly processes a POST request and returns the expected station data.'
    app = Flask(__name__)
    init_routes(app)
    client = app.test_client()

    # Mocking the get_stations_in_radius function to return predefined station data
    mocker.patch("src.data_services.get_stations_in_radius", return_value=["Station1", "Station2"])

    response = client.post('/submit', json={
        "latitude": 48.0,
        "longitude": 8.0,
        "radius": 100,
        "yearStart": 2000,
        "yearEnd": 2020,
        "stations": []
    })

    # Check if the response status is 200 OK
    assert response.status_code == 200
    # Check if the returned JSON matches the mocked station data
    assert response.get_json() == ["Station1", "Station2"]


@pytest.fixture
def client():
    'Creates a test client for the Flask application.'

    app = Flask(__name__)
    init_routes(app)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_get_weather_data(client, mocker):
    'Tests whether weather data is correctly retrieved from the API and handles missing parameters'

    # Mock the data_services function to return predefined data
    mocker.patch("src.data_services.get_datapoints_for_station", return_value=[
        [("2020", -2.1)], [("2020", 15.3)],  # Annual Tmin & Tmax
        [("2020", 1.5)], [("2020", 10.8)],   # Spring Tmin & Tmax
        [("2020", 7.4)], [("2020", 22.1)],   # Summer Tmin & Tmax
        [("2020", 3.9)], [("2020", 13.4)],   # Autumn Tmin & Tmax
        [("2020", -1.7)], [("2020", 5.2)]    # Winter Tmin & Tmax
    ])

    # Test valid request
    response = client.post("/get_weather_data", json={
        "stationName": "ST123",
        "yearStart": 2020,
        "yearEnd": 2020
    })
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    json_data = response.get_json()
    assert isinstance(json_data, list), f"Unexpected response format: {json_data}"

    # Test missing `stationName`
    response = client.post("/get_weather_data", json={
        "yearStart": 2020,
        "yearEnd": 2020
    })
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert response.get_json() == {"message": "Fehlende Parameter"}

    # Test missing `yearStart`
    response = client.post("/get_weather_data", json={
        "stationName": "ST123",
        "yearEnd": 2020
    })
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert response.get_json() == {"message": "Fehlende Parameter"}

    # Test missing `yearEnd`
    response = client.post("/get_weather_data", json={
        "stationName": "ST123",
        "yearStart": 2020
    })
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert response.get_json() == {"message": "Fehlende Parameter"}

    # Test completely empty request
    response = client.post("/get_weather_data", json={})
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert response.get_json() == {"message": "Fehlende Parameter"}
"""