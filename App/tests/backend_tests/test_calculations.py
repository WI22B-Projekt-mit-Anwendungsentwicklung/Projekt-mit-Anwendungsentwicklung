
# =========================================================
# TESTS FOR .PY
# -> calculations.py
# =========================================================


from src.calculations import find_stations_within_radius, haversine


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
