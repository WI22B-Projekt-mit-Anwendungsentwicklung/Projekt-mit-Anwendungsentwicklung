
# =========================================================
# TESTS FOR .PY
# -> data_services.py
# =========================================================


from src.data_services import get_stations_in_radius, get_datapoints_for_station, save_data_to_db
from src.datapoint import download_and_create_datapoints
from src.station import load_stations_from_url
from src.calculations import haversine
from unittest.mock import patch, MagicMock


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
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [
        ("ST123", "Station A", 48.0, 8.0),
        ("ST456", "Station B", 48.1, 8.1),
        ("ST789", "Station C", 49.0, 9.0),
    ]

    mock_conn = mocker.patch("src.data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("src.calculations.haversine", side_effect=fake_haversine)
    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 3)
    assert len(stations) == 2, f"Error: Expected 2 stations, got {len(stations)}"

    expected_order = ["ST123", "ST456"]
    actual_order = [station[0][0] for station in stations]
    assert actual_order == expected_order, f"Error: Expected order {expected_order}, got {actual_order}"