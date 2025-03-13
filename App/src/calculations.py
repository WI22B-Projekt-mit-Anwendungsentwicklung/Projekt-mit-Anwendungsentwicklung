from math import radians, sin, cos, atan2, sqrt

def find_stations_within_radius(stations, latitude, longitude, radius, max_stations):
    """
    Finds all stations within a specified radius around a given coordinate.

    :param stations: List of stations.
    :param latitude: Geographical latitude of the center point (float).
    :param longitude: Geographical longitude of the center point (float).
    :param radius: Radius in kilometers (float).
    :param max_stations: Maximum number of stations.
    :return: List of stations within the radius.
    """

    result = []
    for station in stations:
        distance = haversine(latitude, longitude, station[2], station[3])
        if distance <= radius:
            result.append((station, distance))

    sorted_result = sorted(result, key=lambda x: x[1])

    if max_stations >= 0:
        sorted_result = sorted_result[:max_stations]

    return sorted_result

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two points on Earth in kilometers.

    :param lat1: Latitude of the first point (float).
    :param lon1: Longitude of the first point (float).
    :param lat2: Latitude of the second point (float).
    :param lon2: Longitude of the second point (float).
    :return: Distance in kilometers (float).
    """

    r = 6371  # Radius of the earth

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c

