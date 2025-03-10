import pytest
from flask import Flask
import requests
from data_services import haversine, get_stations_in_radius, get_datapoints_for_station
from datapoint import DataPoint, extract_average_value, download_and_create_datapoints, download_and_create_datapoints_local
from routes import init_routes
from station import Station

# ----------------- Testing functions ----------------

# ----------------- data_services.py -----------------

def test_haversine():
    assert haversine(0, 0, 0, 0) == 0
    assert round(haversine(48.8566, 2.3522, 51.5074, -0.1278), 1) == 343.6

def test_get_stations_in_radius(mocker):
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [("ST123", "Station Name", 48.0, 8.0)]
    mock_conn = mocker.patch("data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 5)
    assert len(stations) > 0
    assert stations[0][0][0] == "ST123"

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
    # Testfall 1: Normalfall mit positiven Werten
    line1 = """01234567890123456789   250   300   -9999  """
    # Erwartetes Ergebnis: (250 + 300) / 2 / 10 = 27.5
    assert extract_average_value(line1) == 27.5, f"Fehler: Erwartet 27.5, erhalten {extract_average_value(line1)}"

    # Testfall 2: Nur ein gültiger Wert
    line2 = """01234567890123456789   100   -9999   -9999  """
    # Erwartetes Ergebnis: 100 / 10 = 10.0
    assert extract_average_value(line2) == 10.0, f"Fehler: Erwartet 10.0, erhalten {extract_average_value(line2)}"

    # Testfall 3: Kein gültiger Wert
    line3 = """01234567890123456789   -9999   -9999   -9999  """
    # Erwartetes Ergebnis: 0, da keine gültigen Werte
    assert extract_average_value(line3) == 0, f"Fehler: Erwartet 0, erhalten {extract_average_value(line3)}"

    # Testfall 4: Mehrere gültige Werte
    line4 = """01234567890123456789   500   600   700  """
    # Erwartetes Ergebnis: (500 + 600 + 700) / 3 / 10 = 60.0
    assert extract_average_value(line4) == 60.0, f"Fehler: Erwartet 60.0, erhalten {extract_average_value(line4)}"

    # Testfall 5: Negative Werte zulässig
    line5 = """01234567890123456789  -200   400   600  """
    # Erwartetes Ergebnis: (-200 + 400 + 600) / 3 / 10 = 26.67
    assert round(extract_average_value(line5), 2) == 26.67, f"Fehler: Erwartet 26.67, erhalten {extract_average_value(line5)}"

    print('Alle Tests erfolgreich bestanden!')


import requests
from unittest.mock import patch, mock_open, MagicMock

@patch("requests.get")
@patch("builtins.open", new_callable=mock_open, read_data=
"""
ACW00011604194901TMAX  289  X  289  X  283  X  283  X  289  X
ACW00011604194901TMIN  217  X  228  X  222  X  233  X  222  X
"""
       )
@patch("os.remove")  # Mock os.remove, damit keine Datei gelöscht wird
@patch("datapoint.extract_average_value")
def test_download_and_create_datapoints(mock_extract_avg, mock_os_remove, mock_open, mock_requests_get):
    # Mock die HTTP-Antwort mit Beispiel-Bytes für die Datei
    mock_requests_get.return_value = MagicMock(status_code=200, content=b"Dummy Data")

    # Mock den Return-Wert von extract_average_value für TMAX und TMIN
    mock_extract_avg.side_effect = [28.9, 21.7, 28.3, 22.8, 28.3, 22.2]

    # Führe die Funktion aus
    datapoints = download_and_create_datapoints("ACW00011604")

    # Prüfungen
    assert len(datapoints) == 3, f"Fehler: Erwartet 3 DataPoints, erhalten {len(datapoints)}"

    first_dp = datapoints[0]
    assert first_dp.date == 194901, f"Fehler: Erwartetes Datum 194901, erhalten {first_dp.date}"
    assert first_dp.tmax == 28.9, f"Fehler: Erwartetes TMAX 28.9, erhalten {first_dp.tmax}"
    assert first_dp.tmin == 21.7, f"Fehler: Erwartetes TMIN 21.7, erhalten {first_dp.tmin}"

    # Prüfen, ob die Datei geöffnet und gelöscht wurde
    mock_open.assert_called_with("ACW00011604.dly", 'wb')
    mock_os_remove.assert_called_with("ACW00011604.dly")

    print('Test erfolgreich bestanden!')


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


# ----------------- station.py -----------------

def test_station_init():
    station = Station("ID123", "TestStation", 48.0, 8.0, 2020, 2000, 2020, 2000)
    assert station.id == "ID123"
    assert station.name == "TestStation"
    assert station.latitude == 48.0
    assert station.longitude == 8.0


def test_station_repr():
    station = Station("ID123", "TestStation", 48.0, 8.0)
    assert "ID=ID123, Name=TestStation" in repr(station)

# Funktion, die getestet wird
def load_stations_from_url(url_inventory: str, url_stations: str):
    """
    Lädt und verarbeitet Stations- und Inventardaten von NOAA-URLs.
    """
    # Stationsdaten laden
    response = requests.get(url_stations)
    if response.status_code != 200:
        raise Exception(f"Fehler beim Laden der Stationsdaten: HTTP {response.status_code}")

    station_dict = {}
    for row in response.text.splitlines():
        station_id = row[:11]
        station_name = row[41:71].strip()
        station_dict[station_id] = station_name

    # Inventardaten laden
    response = requests.get(url_inventory)
    if response.status_code != 200:
        raise Exception(f"Fehler beim Laden der Inventardaten: HTTP {response.status_code}")

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
            stations.append(station)  # Füge die Station der Liste hinzu
            latest_station_id = station_id

    return stations


# Testfunktion für NOAA-Daten
def test_load_stations_with_real_noaa_data():
    """
    Testet die Funktion load_stations_from_url.
    """
    # NOAA-URLs
    url_stations = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
    url_inventory = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt"

    # Funktion testen
    stations = load_stations_from_url(url_inventory, url_stations)

    # Assertions: Sicherstellen, dass die Daten korrekt geladen wurden
    assert len(stations) > 0, "Es wurden keine Stationen geladen!"  # Es sollten Stationen vorhanden sein

    # Beispielprüfungen (Basis auf bekannten Stationen)
    first_station = stations[0]
    assert "id" in first_station, "Erste Station enthält keine ID"
    assert "name" in first_station, "Erste Station enthält keinen Namen"
    assert "latitude" in first_station, "Erste Station enthält keine Breitenkoordinaten"
    assert "longitude" in first_station, "Erste Station enthält keine Längenkoordinaten"

    # Beispielausgabe der ersten Station für Laufzeitprüfung (optional)
    print(f"Erste Station: {first_station}")


# ----------------- Additional Tests -----------------




