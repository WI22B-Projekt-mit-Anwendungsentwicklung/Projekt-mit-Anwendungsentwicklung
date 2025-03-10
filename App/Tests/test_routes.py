import pytest
from flask import Flask
from App.routes import init_routes


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