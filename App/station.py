import requests

class Station:
    def __init__(self, id: str, name: str, latitude: float, longitude: float, last_measure_tmax: int = 0,
                 first_measure_tmax: int = 0, last_measure_tmin: int = 0, first_measure_tmin: int = 0):
        """
        Creates a weather station.

        :param id: The unique ID of the station (str).
        :param latitude: The geographical latitude of the station (float).
        :param longitude: The geographical longitude of the station (float).
        :param last_measure_tmax: Last year of the TMAX measurement (int, optional).
        :param first_measure_tmax: First year of the TMAX measurement (int, optional).
        :param last_measure_tmin: Last year of the TMIN measurement (int, optional).
        :param first_measure_tmin: First year of the TMIN measurement (int, optional).
        """
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.last_measure_tmax = last_measure_tmax
        self.last_measure_tmin = last_measure_tmin
        self.first_measure_tmax = first_measure_tmax
        self.first_measure_tmin = first_measure_tmin

    def __repr__(self):
        """
        Representation of the station as a string.

        :return: String representation of the station.
        """
        return (f"ID={self.id}, Name={self.name} latitude={self.latitude}, longitude={self.longitude}, "
                f"measure tmax first/last={self.first_measure_tmax}/{self.last_measure_tmax},"
                f"measure tmin first/last={self.first_measure_tmin}/{self.last_measure_tmin})")


def load_stations_from_url(url_inventory: str, url_stations: str):
    """
    Loads the station data from a URL and creates a list of station objects.

    :param url_stations: The URL of the TXT file containing the station data.
    :param url_inventory: The URL of the TXT file containing the inventory data.
    :return: A list of station objects.
    """

    print(f"Loading data from {url_stations}...")
    response = requests.get(url_stations)
    print(f"Status-Code: {response.status_code}")

    station_dict = {}

    if response.status_code == 200:

        content = response.text

        for row in content.splitlines():
            station_id = row[:11]
            station_name = row[41:71].strip()
            station_dict[station_id] = station_name
    else:
        print(f"Failed to load the file: HTTP {response.status_code}")



    print(f"Loading data from {url_inventory}...")
    response = requests.get(url_inventory)
    print(f"Status-Code: {response.status_code}")

    stations = []

    if response.status_code == 200:

        content = response.text

        latest_station_id = ""

        station = Station(id="", name="", latitude=0, longitude=0) # Created so "station" variable exists.
        stations.append(station)

        for row in content.splitlines():
            station_id = row[:11]
            if latest_station_id != station_id:
                if station.last_measure_tmax == 0:
                    stations.remove(station)
                station = Station(
                    id=station_id,
                    name=station_dict[station_id],
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
        print(f"Failed to load the file: HTTP {response.status_code}")
        return []
