import pytest
from flask import Flask
import requests
from data_services import haversine, get_stations_in_radius, get_datapoints_for_station, find_stations_within_radius, save_data_to_db
from datapoint import DataPoint, extract_average_value, download_and_create_datapoints, download_and_create_datapoints_local
from routes import init_routes
from station import Station
from unittest.mock import patch, MagicMock

# ----------------- Testing functions ----------------

# ----------------- data_services.py -----------------

@patch("data_services.connection_pool.get_connection")
@patch("data_services.st.load_stations_from_url")
@patch("data_services.dp.download_and_create_datapoints")
def test_save_data_to_db(mock_download_datapoints, mock_load_stations, mock_get_connection):
    """Tests if save_data_to_db correctly initializes the database when empty"""

    # Simulate an empty database (no stations or datapoints exist)
    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = [[], [], []]  # Extra empty list to prevent StopIteration

    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_get_connection.return_value = mock_connection

    # Mock station and datapoint download functions
    mock_load_stations.return_value = [
        MagicMock(id="ST123", name="Station A", latitude=48.0, longitude=8.0,
                  first_measure_tmax=2000, last_measure_tmax=2020,
                  first_measure_tmin=2000, last_measure_tmin=2020)
    ]
    mock_download_datapoints.return_value = [
        MagicMock(date=202001, tmax=25.5, tmin=10.2)
    ]

    # Execute function
    save_data_to_db()

    # Verify that database queries were executed
    mock_cursor.execute.assert_called()  # At least one DB operation should have been performed
    mock_connection.commit.assert_called()  # Changes should be committed

    print("save_data_to_db() test passed!")


def test_haversine():
    assert haversine(0, 0, 0, 0) == 0
    assert round(haversine(48.8566, 2.3522, 51.5074, -0.1278), 1) == 343.6


def test_haversine_extreme_cases():
    """Test haversine with real extreme cases"""

    # Zero distance (same coordinates)
    assert haversine(0, 0, 0, 0) == 0, "Error: Expected 0 km for two identical points"

    # North Pole → South Pole (maximum possible distance on Earth)
    assert round(haversine(90, 0, -90, 0), 1) == 20015.1, "Error: North Pole → South Pole should be 20015.1 km"

    # Distance between two far-apart cities (New York → Sydney)
    expected_ny_sydney = 15988
    actual_ny_sydney = round(haversine(40.7128, -74.0060, -33.8688, 151.2093), 0)
    assert abs(
        actual_ny_sydney - expected_ny_sydney) <= 1, f"Error: New York → Sydney should be ~{expected_ny_sydney} km, got {actual_ny_sydney} km"

    # Very close points (Berlin Central Station → Brandenburg Gate, ~1.1 km)
    expected_berlin = 1.1
    actual_berlin = round(haversine(52.5251, 13.3694, 52.5163, 13.3777), 1)
    assert abs(
        actual_berlin - expected_berlin) <= 1, f"Error: Berlin Central Station → Brandenburg Gate should be ~{expected_berlin} km, got {actual_berlin} km"

    # Equator circumference test (two points on the same latitude, 180° apart)
    assert round(haversine(0, 0, 0, 180), 0) == 20015, "Error: Equator 0° → 180° should be 20015 km"

    print("All extreme cases for haversine() successfully tested!")


def test_find_stations_within_radius():
    """Tests if the function correctly finds stations within the given radius"""

    # Example stations with coordinates (Lat, Lon)
    stations = [
        ("ST001", "Near Station", 48.1, 8.1),  # Should be ~10 km
        ("ST002", "Far Station", 49.5, 9.5),   # Should be ~150 km (outside radius)
        ("ST003", "Close Station", 48.2, 8.2), # Should be ~5 km
    ]

    radius = 100  # Max. 100 km allowed
    max_stations = 2

    # Execute function
    result = find_stations_within_radius(stations, 48.0, 8.0, radius, max_stations)

    # Ensure all returned stations are within the radius
    for station, distance in result:
        assert distance <= radius, f"Error: Station {station[0]} is outside the radius ({distance} km)"

    print("find_stations_within_radius() test passed!")


def test_get_stations_in_radius(mocker):
    # Mock database query results
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [
        ("ST123", "Station A", 48.0, 8.0),
        ("ST456", "Station B", 48.1, 8.1),
        ("ST789", "Station C", 49.0, 9.0),
    ]

    # Mock database connection
    mock_conn = mocker.patch("data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    # Mock haversine function to return specific distances for each station
    mocker.patch("data_services.haversine", side_effect=[10.5, 5.0, 50.0])

    # Execute the function
    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 3)

    # 1. Test: Ensure exactly 3 stations are returned
    assert len(stations) == 3, f"Error: Expected 3 stations, got {len(stations)}"

    # 2. Test: Ensure stations are sorted by distance (ascending order)
    expected_order = ["ST456", "ST123", "ST789"]
    actual_order = [station[0][0] for station in stations]

    assert actual_order == expected_order, f"Error: Expected order {expected_order}, got {actual_order}"

    print("Test passed successfully!")


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
    # Test Case 1: Normal case with positive values
    line1 = "AO000066422195802TMIN  200  I  200  I  228  I  200  I  200  I  178  I  189  I  200  I  200  I  200  I  178  I  178  I  178  I  172  I  178  I  150  I  161  I  161  I  139  I  161  I  178  I  189  I  178  I  161  I  178  I  178  I  189  I  178  I-9999   -9999   -9999"
    assert extract_average_value(line1) == 18.143, f"Error: Expected 18.143, got {extract_average_value(line1)}"

    # Test Case 2: No valid values
    line2 = "AO000066422195501TMAX-9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999"
    assert extract_average_value(line2) == 0, f"Error: Expected 0, got {extract_average_value(line2)}"

    # Test Case 3: Only one valid value
    line3 = "AO000066422195501TMAX-9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999     278  I-9999   -9999   -9999"
    assert extract_average_value(line3) == 27.800, f"Error: Expected 27.800, got {extract_average_value(line3)}"

    # Test Case 4: Multiple valid values
    line4 = "AO000066422195512TMAX-9999   -9999   -9999   -9999   -9999   -9999     278  I-9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999     250  I  222  I-9999   -9999     239  I-9999     250  I-9999   -9999   -9999     250  I  222  I-9999     250  I  261  I  239  I"
    assert extract_average_value(line4) == 24.610, f"Error: Expected 24.610, got {extract_average_value(line4)}"

    # Test Case 5: Negative values allowed
    line5 = "AR000087860195608TMIN   -4  G  -16  G   -4  G   28  G   70  G   58  G   79  G   60  G   40  G   44  G   46  G  118  G  108  G   76  G   43  G    4  G   42  G  142  G  108  G   74  G   18  G    0  G    2  G   84  G   37  G   60  G   68  G   70  G   21  G   -7  G    4  G"
    assert extract_average_value(line5) == 4.752, f"Error: Expected 4.752, got {extract_average_value(line5)}"

    print('All test cases passed!')

from unittest import mock

@pytest.fixture
def mock_noaa_data():
    """Mock NOAA data file content for a station"""
    return """ACW00011604194901TMAX  289  X  289  X  283  X  283  X  289  X  289  X  278  X  267  X  272  X  278  X  267  X  278  X  267  X  267  X  278  X  267  X  267  X  272  X  272  X  272  X  278  X  272  X  267  X  267  X  267  X  278  X  272  X  272  X  272  X  272  X  272  X
               ACW00011604194901TMIN  217  X  228  X  222  X  233  X  222  X  222  X  228  X  217  X  222  X  183  X  189  X  194  X  161  X  183  X  178  X  222  X  211  X  211  X  194  X  217  X  217  X  217  X  211  X  211  X  200  X  222  X  217  X  211  X  222  X  206  X  217  X"""


@mock.patch("requests.get")
def test_download_and_create_datapoints(mock_get):
    """Tests whether data points are correctly extracted from NOAA file"""

    # Simulated NOAA data format
    mock_noaa_data = (
        "ACW00011604194901TMAX  289  X  289  X  283  X  283  X  289  X  289  X  278  X  267  X  272  X  278  X  267  X  278  X  267  X  267  X  278  X  267  X  267  X  272  X  272  X  272  X  278  X  272  X  267  X  267  X  267  X  278  X  272  X  272  X  272  X  272  X  272  X\n"
        "ACW00011604194901TMIN  217  X  228  X  222  X  233  X  222  X  222  X  228  X  217  X  222  X  183  X  189  X  194  X  161  X  183  X  178  X  222  X  211  X  211  X  194  X  217  X  217  X  217  X  211  X  211  X  200  X  222  X  217  X  211  X  222  X  206  X  217  X\n"
    )

    # Mock response from NOAA
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = mock_noaa_data.encode()

    # Execute function
    station_id = "ACW00011604194901"
    datapoints = download_and_create_datapoints(station_id)

    # Verify results
    assert len(datapoints) == 1, f"Error: Expected 3 data points, got {len(datapoints)}"
    assert datapoints[0].tmax == 28.9, "Error: Expected tmax to be 28.9"
    assert datapoints[0].tmin == 21.7, "Error: Expected tmin to be 21.7"

    print("download_and_create_datapoints() test passed!")


@pytest.fixture
def mock_db_cursor(mocker):
    """Mocks a database cursor"""
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.side_effect = [
        [("2020", -2.1)],  # Annual Tmin
        [("2020", 15.3)],  # Annual Tmax
        [("2020", 1.5)], [("2020", 10.8)],  # Spring Tmin & Tmax
        [("2020", 7.4)], [("2020", 22.1)],  # Summer Tmin & Tmax
        [("2020", 3.9)], [("2020", 13.4)],  # Autumn Tmin & Tmax
        [("2020", -1.7)], [("2020", 5.2)],  # Winter Tmin & Tmax
    ]
    return mock_cursor


@pytest.fixture
def mock_extract_average_value():
    """Mock the extract_average_value function to return predefined values"""
    with mock.patch("datapoint.extract_average_value", side_effect=[27.23, 21.02]):
        yield

@pytest.fixture
def mock_path_exists():
    """Mock os.path.exists to always return True"""
    with mock.patch("os.path.exists", return_value=True):
        yield

@pytest.fixture
def mock_open_file():
    """Mock open() to return predefined file content"""
    mock_data = (
        "ACW00011604194901TMAX  289  X  289  X  283  X  283  X  289  X  289  X  278  X  267  X  272  X  278  X  267  X  278  X  267  X  267  X  278  X  267  X  267  X  272  X  272  X  272  X  278  X  272  X  267  X  267  X  267  X  278  X  272  X  272  X  272  X  272  X  272  X\n"
        "ACW00011604194901TMIN  217  X  228  X  222  X  233  X  222  X  222  X  228  X  217  X  222  X  183  X  189  X  194  X  161  X  183  X  178  X  222  X  211  X  211  X  194  X  217  X  217  X  217  X  211  X  211  X  200  X  222  X  217  X  211  X  222  X  206  X  217  X\n"
    )
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_data)):
        yield

def test_download_and_create_datapoints_local(mock_path_exists, mock_open_file, mock_extract_average_value):
    """Tests if data is correctly extracted when the file exists"""

    station_id = "ACW00011604194901"
    datapoints = download_and_create_datapoints_local(station_id)

    # Ensure the function returns the expected list of DataPoint objects
    assert len(datapoints) == 1, f"Error: Expected 1 data point, got {len(datapoints)}"
    assert datapoints[0].date == 194901, f"Error: Expected date 194901, got {datapoints[0].date}"
    assert datapoints[0].tmax == 27.23, f"Error: Expected tmax 27.23, got {datapoints[0].tmax}"
    assert datapoints[0].tmin == 21.02, f"Error: Expected tmin 21.02, got {datapoints[0].tmin}"
    assert datapoints[0].station == station_id, f"Error: Expected station {station_id}, got {datapoints[0].station}"

    print("Test passed: File exists and data is extracted correctly")



@mock.patch("os.path.exists", return_value=False)  # Mock file does NOT exist
@mock.patch("builtins.print")  # Mock print to suppress output
def test_download_and_create_datapoints_local_not_existing_file(mock_print, mock_path_exists):
    """Tests the behavior when the file does not exist"""

    station_id = "UNKNOWN_STATION"
    datapoints = download_and_create_datapoints_local(station_id)

    # Ensure the function returns an empty list
    assert datapoints == [], "Error: Expected an empty list when the file is missing"

    # Ensure the error message is printed
    mock_print.assert_called_once_with(f"Error: File /data/ghcnd_all/{station_id}.dly not found.")

    print("Test passed: File not found case handled correctly")


@pytest.fixture
def mock_db_cursor():
    """Mocks a database cursor with predefined fetchall() results"""
    mock_cursor = mock.MagicMock()
    mock_cursor.fetchall.side_effect = [
        [("2020", -2.1)], [("2020", 15.3)],  # Annual Tmin & Tmax
        [("2020", 1.5)], [("2020", 10.8)],   # Spring Tmin & Tmax
        [("2020", 7.4)], [("2020", 22.1)],   # Summer Tmin & Tmax
        [("2020", 3.9)], [("2020", 13.4)],   # Autumn Tmin & Tmax
        [("2020", -1.7)], [("2020", 5.2)]    # Winter Tmin & Tmax
    ]
    return mock_cursor

@pytest.fixture
def mock_db_connection(mocker, mock_db_cursor):
    """Mocks a database connection"""
    mock_conn = mocker.patch("data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_db_cursor
    return mock_conn

def test_get_datapoints_for_station(mock_db_connection, mock_db_cursor):
    """Tests whether temperature data is correctly retrieved from the database"""

    station_id = "ST123"
    first_year = 2020
    last_year = 2020

    # Execute function
    result = get_datapoints_for_station(station_id, first_year, last_year)

    # Expected results
    expected_result = [
        [("2020", -2.1)], [("2020", 15.3)],  # Annual Tmin & Tmax
        [("2020", 1.5)], [("2020", 10.8)],   # Spring Tmin & Tmax
        [("2020", 7.4)], [("2020", 22.1)],   # Summer Tmin & Tmax
        [("2020", 3.9)], [("2020", 13.4)],   # Autumn Tmin & Tmax
        [("2020", -1.7)], [("2020", 5.2)]    # Winter Tmin & Tmax
    ]

    # Verify the returned data
    assert result == expected_result, f"Error: Unexpected response {result}"

    # Verify that fetchall() was called the expected number of times (5 queries)
    assert mock_db_cursor.fetchall.call_count == 5, "fetchall() was not called the expected number of times"

    print("get_datapoints_for_station() test passed!")


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



@pytest.fixture
def client():
    """Creates a test client for the Flask application."""
    app = Flask(__name__)
    init_routes(app)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_get_weather_data(client, mocker):
    """Tests whether weather data is correctly retrieved from the API and handles missing parameters"""

    # Mock the data_services function to return predefined data
    mocker.patch("data_services.get_datapoints_for_station", return_value=[
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

    print("get_weather_data() test passed with missing parameter checks!")


# ----------------- station.py -----------------

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
    print("test_station_repr() passed!")


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

    print("test_station_initialization() passed!")

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

    print("test_station_default_values() passed!")


def test_station_init():
    station = Station("ID123", "TestStation", 48.0, 8.0, 2020, 2000, 2020, 2000)
    assert station.id == "ID123"
    assert station.name == "TestStation"
    assert station.latitude == 48.0
    assert station.longitude == 8.0


def load_stations_from_url(url_inventory: str, url_stations: str):
    """
    Loads and processes station and inventory data from NOAA URLs.
    """
    response = requests.get(url_stations)
    if response.status_code != 200:
        raise Exception(f"Error loading station data: HTTP {response.status_code}")

    station_dict = {}
    for row in response.text.splitlines():
        station_id = row[:11]
        station_name = row[41:71].strip()
        station_dict[station_id] = station_name

    response = requests.get(url_inventory)
    if response.status_code != 200:
        raise Exception(f"Error loading inventory data: HTTP {response.status_code}")

    stations = []
    latest_station_id = None
    for row in response.text.splitlines():
        station_id = row[:11]
        if latest_station_id != station_id:
            station = {
                "id": station_id,
                "name": station_dict.get(station_id, "Unknown"),
                "latitude": float(row[12:20]),
                "longitude": float(row[21:30]),
                "first_measure": int(row[36:40]),
                "last_measure": int(row[41:45]),
            }
            stations.append(station)
            latest_station_id = station_id

    return stations

def test_load_stations_from_url():
    """
    Tests the function load_stations_from_url.
    """
    url_stations = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
    url_inventory = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt"

    stations = load_stations_from_url(url_inventory, url_stations)

    # Assertions: Ensure that the data has been correctly loaded
    assert len(stations) > 0, "No stations were loaded!"  # There should be stations available

    first_station = stations[0]
    assert "id" in first_station, "First station does not contain an ID"
    assert "name" in first_station, "First station does not contain a name"
    assert "latitude" in first_station, "First station does not contain latitude coordinates"
    assert "longitude" in first_station, "First station does not contain longitude coordinates"

    print(f"First station: {first_station}")




