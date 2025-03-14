
# =========================================================
# TESTS FOR .PY
# -> stations.py
# =========================================================

import pytest
from src.station import Station, load_stations_from_url
from unittest import mock

def test_station_repr():
    """Tests the string representation (__repr__) of a Station object."""

    station = Station(
        id="ST789",
        name="Repr Station",
        latitude=49.5,
        longitude=9.5,
        last_measure_tmax=2025,
        first_measure_tmax=2010,
        last_measure_tmin=2024,
        first_measure_tmin=2011
    )

    expected_repr = (
        "ID=ST789, Name=Repr Station latitude=49.5, longitude=9.5, "
        "measure tmax first/last=2010/2025,"
        "measure tmin first/last=2011/2024)"
    )

    assert repr(station) == expected_repr


def test_station_initialization():
    """Tests if the Station object is correctly initialized with given parameters."""

    station = Station(
        id="ST123",
        name="Test Station",
        latitude=48.0,
        longitude=8.0,
        last_measure_tmax=2020,
        first_measure_tmax=2000,
        last_measure_tmin=2019,
        first_measure_tmin=1999
    )

    # Assert that all attributes are correctly set
    assert station.id == "ST123"
    assert station.name == "Test Station"
    assert station.latitude == 48.0
    assert station.longitude == 8.0
    assert station.last_measure_tmax == 2020
    assert station.first_measure_tmax == 2000
    assert station.last_measure_tmin == 2019
    assert station.first_measure_tmin == 1999


def test_station_default_values():
    """Tests if default values are correctly assigned when optional parameters are not provided."""

    station = Station(
        id="ST456",
        name="Default Station",
        latitude=50.5,
        longitude=10.5
    )

    # Assert that required attributes are correctly set
    assert station.id == "ST456"
    assert station.name == "Default Station"
    assert station.latitude == 50.5
    assert station.longitude == 10.5

    # Assert that default values are correctly assigned
    assert station.last_measure_tmax == 0
    assert station.first_measure_tmax == 0
    assert station.last_measure_tmin == 0
    assert station.first_measure_tmin == 0


def test_station_init():
    """Tests the initialization of a Station object with correct attribute values."""
    station = Station("ID123", "TestStation", 48.0, 8.0, 2020, 2000, 2020, 2000)
    assert station.id == "ID123"
    assert station.name == "TestStation"
    assert station.latitude == 48.0
    assert station.longitude == 8.0


@pytest.fixture
def mock_station_data():
    """Mock data for stations.txt containing three stations."""

    return """\
ACW00011604  17.1167  -61.7833   10.1    ST JOHNS COOLIDGE FLD                        
ACW00011647  17.1333  -61.7833   19.2    ST JOHNS                                    
AE000041196  25.3330   55.5170   34.0    SHARJAH INTER. AIRP            GSN     41196
"""

@pytest.fixture
def mock_inventory_data():
    """Mock data for inventory.txt containing measurement periods of the stations."""

    return """\
ACW00011604  17.1167  -61.7833 TMAX 1949 1949
ACW00011604  17.1167  -61.7833 TMIN 1949 1949
ACW00011604  17.1167  -61.7833 PRCP 1949 1949
ACW00011647  17.1333  -61.7833 TMAX 1961 1961
ACW00011647  17.1333  -61.7833 TMIN 1961 1961
ACW00011647  17.1333  -61.7833 PRCP 1957 1970
AE000041196  25.3330   55.5170 TMAX 1944 2025
AE000041196  25.3330   55.5170 TMIN 1944 2025
AE000041196  25.3330   55.5170 PRCP 1944 2025
"""

@mock.patch("requests.get")
def test_load_stations_from_url(mock_get, mock_station_data, mock_inventory_data):
    """Tests loading stations from mock URLs with mock data for stations.txt and inventory.txt."""

    # Simulated responses for the URLs
    mock_get.side_effect = [
        mock.Mock(status_code=200, text=mock_station_data),  # Response for stations.txt
        mock.Mock(status_code=200, text=mock_inventory_data)  # Response for inventory.txt
    ]

    # Testing the function with mock URLs
    stations = load_stations_from_url("mock_inventory_url", "mock_stations_url")

    # Expected results as `Station` objects
    expected_stations = [
        Station("ACW00011604", "ST JOHNS COOLIDGE FLD", 17.1167, -61.7833, last_measure_tmax=1949,
                first_measure_tmax=1949),
        Station("ACW00011647", "ST JOHNS", 17.1333, -61.7833, last_measure_tmax=1961, first_measure_tmax=1961),
        Station("AE000041196", "SHARJAH INTER. AIRP", 25.3330, 55.5170, last_measure_tmax=2025,
                first_measure_tmax=1944),
    ]

    assert len(stations) == len(
        expected_stations), f"Error: Expected {len(expected_stations)} stations, got {len(stations)}"

    for expected, actual in zip(expected_stations, stations):
        assert expected.id == actual.id, f"Error: Expected ID {expected.id}, got {actual.id}"
        assert expected.name == actual.name, f"Error: Expected Name {expected.name}, got {actual.name}"
        assert expected.latitude == actual.latitude, f"Error: Expected Latitude {expected.latitude}, got {actual.latitude}"
        assert expected.longitude == actual.longitude, f"Error: Expected Longitude {expected.longitude}, got {actual.longitude}"
        assert expected.first_measure_tmax == actual.first_measure_tmax, f"Error: Expected First Measure TMAX {expected.first_measure_tmax}, got {actual.first_measure_tmax}"
        assert expected.last_measure_tmax == actual.last_measure_tmax, f"Error: Expected Last Measure TMAX {expected.last_measure_tmax}, got {actual.last_measure_tmax}"

@mock.patch("requests.get")
def test_load_stations_from_url_http_error(mock_get):
    """Tests the behavior when HTTP errors occur (e.g., 404, 500)."""
    mock_get.side_effect = [
        mock.Mock(status_code=404, text=""),
        mock.Mock(status_code=200, text="")
    ]
    stations = load_stations_from_url("mock_inventory_url", "mock_stations_url")
    stations = [s for s in stations if s.id]
    assert stations == [], f"Error: Expected empty list when stations.txt request fails, but got: {stations}"
