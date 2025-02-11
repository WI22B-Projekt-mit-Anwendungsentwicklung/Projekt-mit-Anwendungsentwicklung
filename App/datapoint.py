import requests
import os

class DataPoint:
    def __init__(self, date: int, tmax: float, tmin: float, station=None):
        """
        Erstellt einen Datenpunkt mit Monat, Temperaturdaten und einer zugehörigen Station.

        :param date: Jahr+Monat im Format YYYYMM (z. B. 202401).
        :param station: Die Station (Instanz der Klasse Station), der dieser Datenpunkt zugeordnet ist.
        """

        self.date = date
        self.tmax = tmax
        self.tmin = tmin
        self.station = station  # Referenz einer Station

    def __repr__(self):
        """
        Repräsentation des Datenpunkts als String.

        :return: String-Repräsentation des Datenpunkts.
        """
        year = self.date // 100
        month = self.date % 100
        station_name = self.station if self.station else "None"
        return f"DataPoint(date={self.date}, station='{station_name}, tmax={self.tmax}, tmin={self.tmin}')"

def extract_average_value(line: str):
    """
    Extrahiert die VALUE-Werte aus dem gegebenen String und berechnet den Durchschnitt.

    :param line: Der gegebene String mit den Daten.
    :return: Der Durchschnitt der VALUE-Werte.
    """
    # Leere Liste für die VALUE-Werte
    value_werte = []

    # Schleife über die Startpositionen der VALUE-Felder (22, 30, 38, ..., 262)
    for start in range(21, len(line), 8):  # Start ist 21, da Python 0-basiert ist
        value_str = line[start:start + 5].strip()  # 5 Zeichen für die VALUE-Werte (z.B. ' 267')

        if value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit() and value_str != '-9999'):
            # Wenn es eine gültige Zahl ist, konvertiere sie in eine Ganzzahl
            value_werte.append(int(value_str))

    if len(value_werte) > 0:
        average_value = sum(value_werte) / len(value_werte) / 10
        return float(f"{average_value:.3f}")
    else:
        return 0

def download_and_create_datapoints(station_id: str):
    """
    Lädt die Datei einer gegebenen Station-ID herunter, extrahiert die relevanten Zeilen und erstellt DataPoint-Objekte.

    :param station_id: Die Station-ID, um die Datei herunterzuladen (z. B. 'ACW00011604').
    """
    url = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/{station_id}.dly"
    response = requests.get(url)
    list_datapoints = []

    if response.status_code == 200:
        file_name = f"{station_id}.dly"

        # Datei speichern
        with open(file_name, 'wb') as file:
            file.write(response.content)

        # Listen für Tmax und Tmin
        tmax_data = 0
        tmin_data = 0

        # Jede Zeile der Datei durchgehen
        with open(file_name, 'r') as file:
            for line in file:
                line_17 = line[17:21]
                if len(line) > 21 and (line_17 == "TMAX" or line_17 == "TMIN"):
                    # Extrahiere Datum (z.B. Jahr + Monat)
                    current_date = int(line[11:17])  # Jahr + Monat (YYYYMM)

                    # Wenn es eine TMAX Zeile ist, hole die Temperaturdaten
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


        # Datei nach der Verarbeitung löschen
        os.remove(file_name)
    else:
        print(f"Fehler beim Herunterladen: HTTP {response.status_code}")

    return list_datapoints

def download_and_create_datapoints_local(station_id: str):
    """
    Liest die Datei einer gegebenen Station-ID aus dem lokalen Verzeichnis,
    extrahiert die relevanten Zeilen und erstellt DataPoint-Objekte.

    :param station_id: Die Station-ID der Datei (z. B. 'ACW00011604').
    """
    file_path = f"/data/ghcnd_all/{station_id}.dly"
    list_datapoints = []

    if os.path.exists(file_path):
        # Listen für Tmax und Tmin
        tmax_data = 0
        tmin_data = 0

        # Datei auslesen
        with open(file_path, 'r') as file:
            for line in file:
                line_17 = line[17:21]
                if len(line) > 21 and (line_17 == "TMAX" or line_17 == "TMIN"):
                    # Extrahiere Datum (z.B. Jahr + Monat)
                    current_date = int(line[11:17])  # Jahr + Monat (YYYYMM)

                    # Wenn es eine TMAX Zeile ist, hole die Temperaturdaten
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
        print(f"Fehler: Datei {file_path} nicht gefunden.")

    return list_datapoints


if __name__ == "__main__":
    print(download_and_create_datapoints_local("AGE00147711"))
