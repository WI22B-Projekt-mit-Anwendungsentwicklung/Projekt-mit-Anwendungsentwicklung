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


# ----------------- Testing functions ----------------

# ----------------- data_services.py -----------------

@patch("src.data_services.connection_pool.get_connection")
@patch("src.data_services.st.load_stations_from_url")
@patch("src.data_services.dp.download_and_create_datapoints")
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

def fake_haversine(lat1, lon1, lat2, lon2):
    mapping = {
        (48.0, 8.0): 10.5,
        (48.1, 8.1): 5.0,
        (49.0, 9.0): 50.0,
    }
    return mapping.get((lat2, lon2), 1000)

def test_get_stations_in_radius_order(mocker):
    """Unit test for the `get_stations_in_radius` function using mocking."""

    # Mock database query results
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [
        ("ST123", "Station A", 48.0, 8.0),
        ("ST456", "Station B", 48.1, 8.1),
        ("ST789", "Station C", 49.0, 9.0),
    ]

    # Mock database connection
    mock_conn = mocker.patch("src.data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    # Mock haversine function to return specific distances for each station
    mocker.patch("src.calculations.haversine", side_effect=fake_haversine)

    # Execute the function
    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 3)

    # 1. Test: Ensure exactly 3 stations are returned
    assert len(stations) == 3, f"Error: Expected 3 stations, got {len(stations)}"

    # 2. Test: Ensure stations are sorted by distance (ascending order)
    expected_order = ["ST456", "ST123", "ST789"]
    actual_order = [station[0][0] for station in stations]

    assert actual_order == expected_order, f"Error: Expected order {expected_order}, got {actual_order}"


# ----------------- datapoint.py -----------------


def test_datapoint_init():
    """Tests if the DataPoint object is correctly initialized with the given values."""

    dp = DataPoint(202401, 25.5, 10.3, "ST123")
    assert dp.date == 202401
    assert dp.tmax == 25.5
    assert dp.tmin == 10.3

def test_datapoint_repr():
    """Tests if the `repr` method of DataPoint correctly represents the object as a string."""

    dp = DataPoint(202401, 25.5, 10.3, "ST123")
    assert "DataPoint(date=202401" in repr(dp)

def test_extract_average_value():
    """Tests the `extract_average_value` function for different cases."""

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


@pytest.fixture
def mock_noaa_data():
    """Mock NOAA data file content for a station"""

    return """ACW00011604194901TMAX  289  X  289  X  283  X  283  X  289  X  289  X  278  X  267  X  272  X  278  X  267  X  278  X  267  X  267  X  278  X  267  X  267  X  272  X  272  X  272  X  278  X  272  X  267  X  267  X  267  X  278  X  272  X  272  X  272  X  272  X  272  X
               ACW00011604194901TMIN  217  X  228  X  222  X  233  X  222  X  222  X  228  X  217  X  222  X  183  X  189  X  194  X  161  X  183  X  178  X  222  X  211  X  211  X  194  X  217  X  217  X  217  X  211  X  211  X  200  X  222  X  217  X  211  X  222  X  206  X  217  X"""


@mock.patch("requests.get")
def test_download_and_create_datapoints(mock_get):
    """Tests whether data points are correctly extracted from NOAA file"""

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
    assert datapoints[0].tmax == 27.461, "Error: Expected tmax to be 27.461"
    assert datapoints[0].tmin == 20.984, "Error: Expected tmin to be 20.984"


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

    with mock.patch("src.datapoint.extract_average_value", side_effect=[27.23, 21.02]):
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

    station_id = "ACW00011604"
    datapoints = download_and_create_datapoints_local(station_id)

    # Ensure the function returns the expected list of DataPoint objects
    assert len(datapoints) == 1, f"Error: Expected 1 data point, got {len(datapoints)}"
    assert datapoints[0].date == 194901, f"Error: Expected date 194901, got {datapoints[0].date}"
    assert datapoints[0].tmax == 27.23, f"Error: Expected tmax 27.23, got {datapoints[0].tmax}"
    assert datapoints[0].tmin == 21.02, f"Error: Expected tmin 21.02, got {datapoints[0].tmin}"
    assert datapoints[0].station == station_id, f"Error: Expected station {station_id}, got {datapoints[0].station}"


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


# Initialize the connection pool based on the configuration from the code
dbconfig = {
    "user": "root",
    "password": "root",
    "host": "mysql",
    "port": "3306",
    "database": "db"
}


connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    **dbconfig
)


@pytest.fixture(scope="module")
def real_db_connection():
    """Establishes a real connection to the database via the pool."""
    connection = connection_pool.get_connection()
    yield connection  # Passes the connection to the test
    connection.close()  # Closes the connection after the test


@pytest.fixture
def db_cursor(real_db_connection):
    """Returns a cursor for the test database."""
    cursor = real_db_connection.cursor()
    yield cursor
    cursor.close()


def test_get_datapoints_for_station_real_db(db_cursor):
    """Tests the `get_datapoints_for_station()` function with real database values."""

    station_id = "GME00129634"  # Replace with a valid station ID from your database
    first_year = 2020
    last_year = 2020

    # Check if the station exists
    db_cursor.execute("SELECT COUNT(*) FROM Station WHERE station_id = %s;", (station_id,))
    station_exists = db_cursor.fetchone()[0]
    assert station_exists > 0, f"Station {station_id} not found in the database!"

    # Check if data exists for this station
    db_cursor.execute("SELECT COUNT(*) FROM Datapoint WHERE SID = (SELECT SID FROM Station WHERE station_id = %s);", (station_id,))
    record_count = db_cursor.fetchone()[0]
    assert record_count > 0, f"No data points found for station {station_id}!"

    # Execute function with real data
    result = get_datapoints_for_station(station_id, first_year, last_year)

    # Check if the result contains 10 values (annual & seasonal average values)
    assert len(result) == 10, f"Missing values! Expected: 10, Received: {len(result)}"

    # **Expected values for the tests (based on test data)**
    expected_values = [
        [(2020, 3.36)], [(2020, 14.93)],  # Annual Tmin & Tmax
        [(2020, 1.36)], [(2020, 15.50)],  # Spring Tmin & Tmax
        [(2020, 10.13)], [(2020, 23.60)],  # Summer Tmin & Tmax
        [(2020, 3.67)], [(2020, 14.50)],  # Autumn Tmin & Tmax
        [(2020, -1.87)], [(2020, 6.76)],  # Winter Tmin & Tmax
    ]

    # **Debugging: Comparing received values with expected values**
    print("**Received values from `get_datapoints_for_station`**:")
    for i, dataset in enumerate(result):
        print(f"Dataset {i + 1}: {dataset}")

    print("**Expected values:**")
    for i, dataset in enumerate(expected_values):
        print(f"Dataset {i + 1}: {dataset}")

    # **Compare calculated values with expected database values**
    for i in range(len(expected_values)):
        # Unpack expected and received values correctly from the list structure
        (expected_year, expected_value) = expected_values[i][0]  # Expected result as tuple
        (result_year, result_value) = result[i][0]  # Received result as tuple

        # Verify the year (as a string for safety)
        assert str(result_year) == str(expected_year), (
            f"Year mismatch! Expected: {expected_year}, Received: {result_year}"
        )

        # Runde den erhaltenen Wert aus der Datenbank auf zwei Nachkommastellen
        rounded_result_value = round(result_value, 2)

        # Verify the value after rounding
        assert rounded_result_value == expected_value, (
            f"Deviation too large in Dataset {i + 1}: "
            f"Expected {expected_value}, Received {rounded_result_value} "
            f"(Original: {result_value})"
        )

# ----------------- routes.py -----------------


def test_home():
    """Tests if the home route ('/') returns a 200 OK response."""
    with patch("src.routes.render_template", return_value="dummy"):
         app = Flask(__name__)
         init_routes(app)
         client = app.test_client()
         response = client.get('/')
         assert response.status_code == 200


def test_receive_data(mocker):
    """Tests if the '/submit' endpoint correctly processes a POST request and returns the expected station data."""
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
    """Creates a test client for the Flask application."""

    app = Flask(__name__)
    init_routes(app)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_get_weather_data(client, mocker):
    """Tests whether weather data is correctly retrieved from the API and handles missing parameters"""

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


# ----------------- calculations.py -----------------


def test_haversine():
    """Test haversine"""
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


def test_find_stations_in_radius():
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

    # Assertions
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

    # Simulating a failed response for stations.txt
    mock_get.side_effect = [
        mock.Mock(status_code=404, text=""),  # Failed response for stations.txt
        mock.Mock(status_code=200, text="")   # Successful response for inventory.txt
    ]

    stations = load_stations_from_url("mock_inventory_url", "mock_stations_url")
    stations = [s for s in stations if s.id]

    assert stations == [], f"Error: Expected empty list when stations.txt request fails, but got: {stations}"

# ----------------- Run Tests -----------------

def run_backend_tests():
    """
    Runs the Python tests (Pytest) with coverage.
    """
    import sys
    print("Running Python backend tests with coverage...")
    pytest_args = [
        "-q",
        "--cov=src.data_services",
        "--cov=src.datapoint",
        "--cov=src.routes",
        "--cov=src.calculations",
        "--cov=src.station",
        "--cov-report=term",
        "tests"
    ]

    exit_code = pytest.main(pytest_args)
    if exit_code != 0:
        print("\nPython tests failed! Exiting...")
        sys.exit(1)
    else:
        print("\nPython tests passed successfully.")


def run_frontend_tests():
    """
    Runs the frontend (JS) tests by calling 'npm test'.
    """
    import sys
    import os

    print("Running frontend tests with 'npm test'...")
    exit_code = os.system("npm test")
    if exit_code != 0:
        print("\nFrontend tests failed! Exiting...")
        sys.exit(1)
    else:
        print("\nFrontend tests passed successfully.")


def run_all_tests():
    """
    Runs both backend and frontend tests in sequence.
    This is the single function we will call from app.py.
    """
    run_frontend_tests()
    run_backend_tests()


