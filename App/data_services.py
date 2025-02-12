from math import radians, sin, cos, atan2, sqrt
import station as st
import datapoint as dp
from mysql.connector import pooling

dbconfig = {
    "user": "root",
    "password": "root",
    "host": "mysql",
    "port": "3306",
    "database": "db"
}

# Initialisiere den Verbindungspool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    **dbconfig
)

# Stationen im Radius finden
def find_stations_within_radius(stations, latitude, longitude, radius, max_stations=0):
    """
    Findet alle Stationen innerhalb eines bestimmten Radius um eine gegebene Koordinate.

    :param stations: Liste der Stationen.
    :param latitude: Geografische Breite des Mittelpunkts (float).
    :param longitude: Geografische Länge des Mittelpunkts (float).
    :param radius: Radius in Kilometern (float).
    :param max_stations: Maximale Anzahl der Stationen.
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

def save_data_to_db():
    """
    Füllt die Tabellen "Station" und "Datapoint" in der Datenbank, falls sie leer sind,
    indem Daten von einer externen URL geladen und eingefügt werden.

    :return: Keine Rückgabe, führt Datenbankoperationen aus.
    """
    connection = connection_pool.get_connection()
    try:
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM Station;")
            inhalt_station = cursor.fetchall()
            if not inhalt_station:
                stations = st.load_stations_from_url("https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt")
                for station in stations:
                    cursor.execute(
                        """
                        INSERT INTO Station (station_name, latitude, longitude, first_tmax, latest_tmax, first_tmin, latest_tmin)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """,
                        (station.id, station.latitude, station.longitude, station.first_measure_tmax,
                         station.last_measure_tmax, station.first_measure_tmin, station.last_measure_tmin))
                connection.commit()
            else:
                print("Station bereits gefüllt")

            cursor.execute("SELECT * FROM Datapoint LIMIT 1;")
            inhalt_datapoint = cursor.fetchall()
            if not inhalt_datapoint:
                for station in inhalt_station:
                    datapoints = dp.download_and_create_datapoints_local(station[1])
                    foreign_key = station[0]
                    for datapoint in datapoints:
                        cursor.execute(
                            """
                            INSERT INTO Datapoint (SID, year, month, tmax, tmin)
                            VALUES (%s, %s, %s, %s, %s);
                            """,
                            (foreign_key, str(datapoint.date)[:4], str(datapoint.date)[-2:], datapoint.tmax, datapoint.tmin))
                connection.commit()
            else:
                print("Datapoint bereits gefüllt")
    finally:
        cursor.close()
        connection.close()

def get_stations_in_radius(latitude, longitude, radius, first_year, last_year, max_stations):
    """
    Ruft Stationen ab, die sich innerhalb eines bestimmten Radius um die angegebene Position befinden
    und Tmin/Tmax-Bedingungen für den Zeitraum erfüllen.

    :param latitude: Breitengrad der Suchposition.
    :param longitude: Längengrad der Suchposition.
    :param radius: Suchradius in Kilometern.
    :param first_year: Erstes Jahr des gesuchten Zeitraums.
    :param last_year: Letztes Jahr des gesuchten Zeitraums.
    :param max_stations: Maximale Anzahl zurückzugebender Stationen.

    :return: Liste von Stationen mit ihren Entfernungen im Radius (z. B. [(station, distance)]).
    """
    connection = connection_pool.get_connection()
    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT station_name, latitude, longitude 
                FROM Station 
                WHERE first_tmin <= %s 
                  AND latest_tmin >= %s 
                  AND first_tmax <= %s 
                  AND latest_tmax >= %s;
                """,
                (first_year, last_year, first_year, last_year))
            stations = cursor.fetchall()

            stations_in_radius = find_stations_within_radius(stations, latitude, longitude, radius, max_stations)
    finally:
        cursor.close()
        connection.close()

    return stations_in_radius  # (('GMM00010591', 50.933, 14.217), 66.85437995060985)

def get_datapoints_for_station(station_name, first_year, last_year):
    """
    Ruft Datensätze zu Temperaturmittelwerten (Tmin und Tmax) einer Station ab,
    gruppiert nach Jahr und Jahreszeiten.

    :param station_name: Name der Station.
    :param first_year: Erstes Jahr des Zeitraums.
    :param last_year: Letztes Jahr des Zeitraums.

    :return: Liste mit 10 Datensätzen:
             1. Jahresdurchschnitt Tmin
             2. Jahresdurchschnitt Tmax
             3. Frühling Tmin
             4. Frühling Tmax
             5. Sommer Tmin
             6. Sommer Tmax
             7. Herbst Tmin
             8. Herbst Tmax
             9. Winter Tmin
            10. Winter Tmax
    """
    connection = connection_pool.get_connection()
    try:
        with (connection.cursor() as cursor):

            ten_datasets = []

            cursor.execute("SELECT SID FROM Station WHERE station_name = %s;", (station_name,))
            sid = cursor.fetchall()
            station_id = sid[0][0]

            # 1. Jahresdurchschnitt Tmin
            cursor.execute(
                """
                SELECT year,
                       SUM(tmin * days_in_month) / SUM(days_in_month)
                FROM (
                    SELECT year,
                           month,
                           AVG(tmin) AS tmin,
                           CASE
                               WHEN month = 2 THEN
                                   CASE
                                       WHEN (year % 4 = 0 AND (year % 100 != 0 OR year % 400 = 0)) THEN 29
                                       ELSE 28
                                   END
                               WHEN month IN (4, 6, 9, 11) THEN 30
                               ELSE 31
                           END AS days_in_month
                    FROM Datapoint
                    WHERE SID = %s
                      AND year BETWEEN %s AND %s
                    GROUP BY year, month
                ) AS subquery
                GROUP BY year
                ORDER BY year;
                """,
                (station_id, first_year, last_year))
            ten_datasets.append(cursor.fetchall())

            # Jahresdurchschnitt Tmax
            cursor.execute(
                """
                SELECT year,
                       SUM(tmax * days_in_month) / SUM(days_in_month)
                FROM (
                    SELECT year,
                           month,
                           AVG(tmax) AS tmax,
                           CASE
                               WHEN month = 2 THEN
                                   CASE
                                       WHEN (year % 4 = 0 AND (year % 100 != 0 OR year % 400 = 0)) THEN 29
                                       ELSE 28
                                   END
                               WHEN month IN (4, 6, 9, 11) THEN 30
                               ELSE 31
                           END AS days_in_month
                    FROM Datapoint
                    WHERE SID = %s
                      AND year BETWEEN %s AND %s
                    GROUP BY year, month
                ) AS subquery
                GROUP BY year
                ORDER BY year;
                """,
                (station_id, first_year, last_year))
            ten_datasets.append(cursor.fetchall())

            # 3-8. Jährliche Mittelwerte für Tmin und Tmax in den Jahreszeiten Frühling, Sommer, Herbst
            seasons = {
                "spring": (3, 5),
                "summer": (6, 8),
                "autumn": (9, 11),
            }

            for season, (start_month, end_month) in seasons.items():
                # Tmin
                cursor.execute(
                    """
                    SELECT year,
                           SUM(tmin * days_in_month) / SUM(days_in_month)
                    FROM (
                        SELECT year,
                               month,
                               AVG(tmin) AS tmin,
                               CASE
                                   WHEN month = 2 THEN
                                       CASE
                                           WHEN (year % 4 = 0 AND (year % 100 != 0 OR year % 400 = 0)) THEN 29
                                           ELSE 28
                                       END
                                   WHEN month IN (4, 6, 9, 11) THEN 30
                                   ELSE 31
                               END AS days_in_month
                        FROM Datapoint
                        WHERE SID = %s
                          AND month BETWEEN %s AND %s
                          AND year BETWEEN %s AND %s
                        GROUP BY year, month
                    ) AS subquery
                    GROUP BY year
                    ORDER BY year;
                    """,
                    (station_id, start_month, end_month, first_year, last_year))
                ten_datasets.append(cursor.fetchall())

                # Tmax
                cursor.execute(
                    """
                    SELECT year,
                           SUM(tmax * days_in_month) / SUM(days_in_month)
                    FROM (
                        SELECT year,
                               month,
                               AVG(tmax) AS tmax,
                               CASE
                                   WHEN month = 2 THEN
                                       CASE
                                           WHEN (year % 4 = 0 AND (year % 100 != 0 OR year % 400 = 0)) THEN 29
                                           ELSE 28
                                       END
                                   WHEN month IN (4, 6, 9, 11) THEN 30
                                   ELSE 31
                               END AS days_in_month
                        FROM Datapoint
                        WHERE SID = %s
                          AND month BETWEEN %s AND %s
                          AND year BETWEEN %s AND %s
                        GROUP BY year, month
                    ) AS subquery
                    GROUP BY year
                    ORDER BY year;
                    """,
                    (station_id, start_month, end_month, first_year, last_year))
                ten_datasets.append(cursor.fetchall())

            # 9. Jährlicher Mittelwert der Temperaturminima im Winter (Dez-Vorjahr + Jan+Feb)
            cursor.execute(
                """
                SELECT winter_year,
                       SUM(tmin * days_in_month) / SUM(days_in_month)
                FROM (
                    SELECT CASE WHEN month IN (1, 2) THEN year - 1 ELSE year END AS winter_year,
                           month,
                           AVG(tmin) AS tmin,
                           CASE
                               WHEN month = 2 THEN
                                   CASE
                                       WHEN (year % 4 = 0 AND (year % 100 != 0 OR year % 400 = 0)) THEN 29
                                       ELSE 28
                                   END
                               WHEN month = 12 THEN 31
                               WHEN month = 1 THEN 31
                               ELSE 30
                           END AS days_in_month
                    FROM Datapoint
                    WHERE SID = %s
                      AND (month = 12 OR month BETWEEN 1 AND 2)
                      AND (CASE WHEN month = 12 THEN year + 1 ELSE year END) BETWEEN %s AND %s
                    GROUP BY year, month
                ) AS subquery
                GROUP BY winter_year
                ORDER BY winter_year;
                """,
                (station_id, first_year, last_year))
            ten_datasets.append(cursor.fetchall())

            # 10. Jährlicher Mittelwert der Temperaturmaxima im Winter (Dez-Vorjahr + Jan+Feb)
            cursor.execute(
                """
                SELECT winter_year,
                       SUM(tmax * days_in_month) / SUM(days_in_month)
                FROM (
                    SELECT CASE WHEN month IN (1, 2) THEN year -1  ELSE year END AS winter_year,
                           month,
                           AVG(tmax) AS tmax,
                           CASE
                               WHEN month = 2 THEN
                                   CASE
                                       WHEN (year % 4 = 0 AND (year % 100 != 0 OR year % 400 = 0)) THEN 29
                                       ELSE 28
                                   END
                               WHEN month = 12 THEN 31
                               WHEN month = 1 THEN 31
                               ELSE 30
                           END AS days_in_month
                    FROM Datapoint
                    WHERE SID = %s
                      AND (month = 12 OR month BETWEEN 1 AND 2)
                      AND (CASE WHEN month = 12 THEN year + 1 ELSE year END) BETWEEN %s AND %s
                    GROUP BY year, month
                ) AS subquery
                GROUP BY winter_year
                ORDER BY winter_year;
                """,
                (station_id, first_year, last_year))
            ten_datasets.append(cursor.fetchall())

    finally:
        cursor.close()
        connection.close()

    return ten_datasets
