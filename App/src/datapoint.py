import requests
import os

class DataPoint:
    def __init__(self, date: int, tmax: float, tmin: float, station: str = None):
        """
        Creates a data point with date, maximum temperature, minimum temperature, and associated station ID.

        :param date: Year and month in the format YYYYMM (e.g., 202401).
        :param tmax: The maximum temperature as a float.
        :param tmin: The minimum temperature as a float.
        :param station: The station ID as a string to which this data point belongs.
        """

        self.date = date
        self.tmax = tmax
        self.tmin = tmin
        self.station = station

    def __repr__(self):
        """
        Representation of the data point as a string.

        :return: String representation of the data point.
        """

        station_name = self.station if self.station else "None"
        return f"DataPoint(date={self.date}, station='{station_name}, tmax={self.tmax}, tmin={self.tmin}')"

def extract_average_value(line: str):
    """
    Extracts the VALUE values from the given string and calculates the average.

    :param line: The given string containing the data.
    :return: The average of the VALUE values.
    """

    value_werte = []

    # Loop over the starting position for the values (22, 30, 38, ..., 262)
    for start in range(21, len(line), 8):
        value_str = line[start:start + 5].strip()

        if value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit() and value_str != '-9999'):
            value_werte.append(int(value_str))

    if len(value_werte) > 0:
        average_value = sum(value_werte) / len(value_werte) / 10
        return float(f"{average_value:.3f}")
    else:
        return 0

def download_and_create_datapoints(station_id: str):
    """
    Downloads the file for a given station ID, extracts the relevant lines, and creates DataPoint objects.

    :param station_id: The station ID used to download the file (e.g., 'ACW00011604').
    :return: A list of DataPoint objects containing the extracted temperatures and the associated date.
    """

    url = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/{station_id}.dly"
    response = requests.get(url)
    list_datapoints = []

    if response.status_code == 200:
        file_name = f"{station_id}.dly"

        with open(file_name, 'wb') as file:
            file.write(response.content)

        tmax_data = 0
        tmin_data = 0

        with open(file_name, 'r') as file:
            for line in file:
                temp_element = line[17:21]
                if len(line) > 21 and (temp_element == "TMAX" or temp_element == "TMIN"):
                    # Extract date
                    current_date = int(line[11:17])  # YYYYMM

                    if temp_element == "TMAX":
                        tmax_data = extract_average_value(line)
                    elif temp_element == "TMIN":
                        tmin_data = extract_average_value(line)

                    if tmin_data != 0 and tmax_data != 0:
                        data_point = DataPoint(date=current_date, tmax=tmax_data, tmin=tmin_data,
                                               station=station_id)
                        list_datapoints.append(data_point)
                        tmax_data = 0
                        tmin_data = 0

        os.remove(file_name)
    else:
        print(f"Failed to load the file: HTTP {response.status_code}")

    return list_datapoints

def download_and_create_datapoints_local(station_id: str):
    """
    Reads the file for a given station ID from the local directory,
    extracts the relevant lines, and creates DataPoint objects.

    :param station_id: The station ID of the file (e.g., 'ACW00011604').
    :return: A list of DataPoint objects containing the extracted temperatures and the associated date.
    """

    file_path = f"/data/ghcnd_all/{station_id}.dly"
    list_datapoints = []

    if os.path.exists(file_path):

        tmax_data = 0
        tmin_data = 0

        with open(file_path, 'r') as file:
            for line in file:
                line_17 = line[17:21]
                if len(line) > 21 and (line_17 == "TMAX" or line_17 == "TMIN"):

                    current_date = int(line[11:17])

                    if line_17 == "TMAX":
                        tmax_data = extract_average_value(line)
                    elif line_17 == "TMIN":
                        tmin_data = extract_average_value(line)

                    if tmin_data != 0 and tmax_data != 0:
                        data_point = DataPoint(date=current_date, tmax=tmax_data, tmin=tmin_data,
                                               station=station_id)
                        list_datapoints.append(data_point)
                        tmax_data = 0
                        tmin_data = 0
    else:
        print(f"Error: File {file_path} not found.")

    return list_datapoints
