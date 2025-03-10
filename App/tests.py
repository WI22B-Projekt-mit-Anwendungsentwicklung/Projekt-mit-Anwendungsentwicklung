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
    mock_cursor.fetchall.return_value = [
        ("ST123", "Station A", 48.0, 8.0),
        ("ST456", "Station B", 48.1, 8.1),
        ("ST789", "Station C", 49.0, 9.0),
    ]

    mock_conn = mocker.patch("data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    # Mock `haversine` um feste Entfernungen zurückzugeben
    mocker.patch("data_services.haversine", side_effect=[10.5, 5.0, 50.0])

    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 3)

    # 1. Test: Es sollten genau 3 Stationen gefunden werden
    assert len(stations) == 3, f"Fehler: Erwartet 3 Stationen, erhalten {len(stations)}"

    # 2. Test: Die Stationen sollten nach Entfernung sortiert sein
    expected_order = ["ST456", "ST123", "ST789"]  # Sortiert nach mockerten Distanzen
    actual_order = [station[0][0] for station in stations]  # Extrahiere die Station-IDs

    assert actual_order == expected_order, f"Fehler: Erwartete Reihenfolge {expected_order}, erhalten {actual_order}"

    print("Test erfolgreich bestanden!")

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
    line1 = "AO000066422195802TMIN  200  I  200  I  228  I  200  I  200  I  178  I  189  I  200  I  200  I  200  I  178  I  178  I  178  I  172  I  178  I  150  I  161  I  161  I  139  I  161  I  178  I  189  I  178  I  161  I  178  I  178  I  189  I  178  I-9999   -9999   -9999"
    assert extract_average_value(line1) == 18.143, f"Fehler: Erwartet 18.143, erhalten {extract_average_value(line1)}"

    # Testfall 2: Kein gültiger Wert
    line2 = "AO000066422195501TMAX-9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999"
    assert extract_average_value(line2) == 0, f"Fehler: Erwartet 0, erhalten {extract_average_value(line2)}"

    # Testfall 3: Nur ein gültiger Wert
    line3 = "AO000066422195501TMAX-9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999     278  I-9999   -9999   -9999"
    assert extract_average_value(line3) == 27.800, f"Fehler: Erwartet 27.800, erhalten {extract_average_value(line3)}"

    # Testfall 4: Mehrere gültige Werte
    line4 = "AO000066422195512TMAX-9999   -9999   -9999   -9999   -9999   -9999     278  I-9999   -9999   -9999   -9999   -9999   -9999   -9999   -9999     250  I  222  I-9999   -9999     239  I-9999     250  I-9999   -9999   -9999     250  I  222  I-9999     250  I  261  I  239  I"
    assert extract_average_value(line4) == 24.610, f"Fehler: Erwartet 24.610, erhalten {extract_average_value(line4)}"

    # Testfall 5: Negative Werte zulässig
    line5 = "AR000087860195608TMIN   -4  G  -16  G   -4  G   28  G   70  G   58  G   79  G   60  G   40  G   44  G   46  G  118  G  108  G   76  G   43  G    4  G   42  G  142  G  108  G   74  G   18  G    0  G    2  G   84  G   37  G   60  G   68  G   70  G   21  G   -7  G    4  G"
    assert extract_average_value(line5) == 4.423, f"Fehler: Erwartet 4.423, erhalten {extract_average_value(line5)}"

    print('Alle Tests erfolgreich bestanden!')


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

def test_get_stations_in_radius_invalid_radius(mocker):
    """Testet, ob negative Radiuswerte abgefangen werden"""
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [("ST123", "Station Name", 48.0, 8.0)]
    mock_conn = mocker.patch("data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    # Negativer Radius sollte zu einer Exception führen
    with pytest.raises(ValueError, match="Radius darf nicht negativ sein"):
        get_stations_in_radius(48.0, 8.0, -50, 2000, 2020, 5)

def test_get_stations_in_radius_max_radius(mocker):
    """Testet, ob Stationen über 100km entfernt ausgeschlossen werden"""
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [
        ("ST001", "Close Station", 48.0, 8.0),   # 50 km entfernt (soll erhalten bleiben)
        ("ST002", "Far Station", 49.5, 9.5)     # 150 km entfernt (soll ignoriert werden)
    ]
    mock_conn = mocker.patch("data_services.connection_pool.get_connection")
    mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    stations = get_stations_in_radius(48.0, 8.0, 100, 2000, 2020, 5)

    assert len(stations) == 1, f"Fehler: Erwartet 1 Station, erhalten {len(stations)}"
    assert stations[0][0][0] == "ST001", f"Fehler: Erwartet ST001, erhalten {stations[0][0][0]}"


