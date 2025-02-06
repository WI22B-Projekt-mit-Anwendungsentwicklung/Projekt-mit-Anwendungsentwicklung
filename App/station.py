import csv
import requests
from math import radians, sin, cos, atan2, sqrt

class Station:
    def __init__(self, id: str, latitude: float, longitude: float, last_measure_tmax: int = 0, first_measure_tmax: int = 0,
                 last_measure_tmin: int = 0, first_measure_tmin: int = 0):
        """
        Erstellt eine Wetterstation.

        :param id: Die eindeutige ID der Station (int).

        :param latitude: Die geografische Breite der Station (float).
        :param longitude: Die geografische Länge der Station (float).
        :param data: Eine Liste der Daten, die für diese Station gespeichert wurden (z. B. Wetterdaten).
        """
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.last_measure_tmax = last_measure_tmax
        self.last_measure_tmin = last_measure_tmin
        self.first_measure_tmax = first_measure_tmax
        self.first_measure_tmin = first_measure_tmin

    def __repr__(self):
        """
        Repräsentation der Station als String.

        :return: String-Repräsentation der Station.
        """
        return (f"Station(id={self.id}, latitude={self.latitude}, longitude={self.longitude}, "
                f"measure tmax first/last={self.first_measure_tmax}/{self.last_measure_tmax},"
                f"measure tmin first/last={self.first_measure_tmin}/{self.last_measure_tmin})")

# Funktion zur Berechnung der Entfernung (Haversine-Formel)
def haversine(lat1, lon1, lat2, lon2):
    """
    Berechnet die Entfernung zwischen zwei Punkten auf der Erde in Kilometern.

    :param lat1: Breite des ersten Punkts (float).
    :param lon1: Länge des ersten Punkts (float).
    :param lat2: Breite des zweiten Punkts (float).
    :param lon2: Länge des zweiten Punkts (float).
    :return: Entfernung in Kilometern (float).
    """
    R = 6378.14  # Erdradius in Kilometern

    # Koordinaten in Bogenmaß umrechnen
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine-Formel
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def load_stations_from_url(url_inventory: str):
    """
    Lädt die Stationsdaten von einer URL und erstellt eine Liste von Station-Objekten.

    :param url_inventory: Die URL der TXT-Datei mit dem Inventory.
    :return: Eine Liste von Station-Objekten.
    """

    stations = []

    print(f"Lade Inventory-Daten von {url_inventory}...")
    response = requests.get(url_inventory)
    print(f"Status-Code: {response.status_code}")

    if response.status_code == 200:
        # Datei speichern
        content = response.text

        latest_station_id = ""

        station = Station(id="", latitude=0, longitude=0)
        stations.append(station)

        for row in content.splitlines():
            station_id = row[:11]
            if latest_station_id != station_id:
                if station.last_measure_tmax == 0:
                    stations.remove(station)
                station = Station(
                    id=station_id,
                    latitude=float(row[12:20]),
                    longitude=float(row[21:30])
                )
                latest_station_id = station_id
                stations.append(station)
            if row[31:35] == "TMAX":
                station.first_measure_tmax = int(row[36:40])
                station.last_measure_tmax = int(row[41:45])
            if row[31:35] == "TMIN":
                station.first_measure_tmin = int(row[36:40])
                station.last_measure_tmin = int(row[41:45])
        return stations
    else:
        print(f"Fehler beim Abrufen der Datei: HTTP {response.status_code}")
        return []


# Stationen im Radius finden
def find_stations_within_radius(stations, latitude, longitude, radius, max_stations=0):
    """
    Findet alle Stationen innerhalb eines bestimmten Radius um eine gegebene Koordinate.

    :param max_stations: Maximale Anzahl der Stationen.
    :param stations: Liste der Stationen.
    :param latitude: Geografische Breite des Mittelpunkts (float).
    :param longitude: Geografische Länge des Mittelpunkts (float).
    :param radius: Radius in Kilometern (float).
    :return: Liste der Stationen innerhalb des Radius.
    """
    result = []
    for station in stations:
        distance = haversine(latitude, longitude, station[1], station[2])
        if distance <= radius:
            result.append((station, distance))

    sorted_result = sorted(result, key=lambda x: x[1])

    if max_stations > 0:
        sorted_result = sorted_result[:max_stations]

    return sorted_result

if __name__ == "__main__":
    load_stations_from_url("https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt")