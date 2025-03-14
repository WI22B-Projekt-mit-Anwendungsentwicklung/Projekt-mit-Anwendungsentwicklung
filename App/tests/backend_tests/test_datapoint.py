
# =========================================================
# TESTS FOR .PY
# -> datapoint.py
# =========================================================

import pytest
from src.data_services import get_datapoints_for_station
from src.datapoint import DataPoint, extract_average_value, download_and_create_datapoints, download_and_create_datapoints_local
from mysql.connector import pooling
from unittest import mock

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