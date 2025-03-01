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

# Initialize connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    **dbconfig
)

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

def save_data_to_db():
    """
    Populates the "Station" and "Datapoint" tables in the database if they are empty
    by loading and inserting data from an external URL.

    :return: No return value, performs database operations.
    """

    connection = connection_pool.get_connection()
    try:
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM Station;")
            inhalt_station = cursor.fetchall()
            if not inhalt_station:
                stations = st.load_stations_from_url(
                    "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt",
                    "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt")
                for station in stations:
                    cursor.execute(
                        """
                        INSERT INTO Station (station_id, station_name, latitude, longitude, first_tmax, latest_tmax, 
                        first_tmin, latest_tmin)
                        VALUES (%s,%s, %s, %s, %s, %s, %s, %s);
                        """,
                        (station.id, station.name, station.latitude, station.longitude, station.first_measure_tmax,
                         station.last_measure_tmax, station.first_measure_tmin, station.last_measure_tmin))
                connection.commit()
            else:
                print("Station already filled.")

            cursor.execute("SELECT * FROM Datapoint LIMIT 1;")
            inhalt_datapoint = cursor.fetchall()
            if not inhalt_datapoint:
                for station in inhalt_station:
                    datapoints = dp.download_and_create_datapoints(station[1])
                    foreign_key = station[0]
                    for datapoint in datapoints:
                        cursor.execute(
                            """
                            INSERT INTO Datapoint (SID, year, month, tmax, tmin)
                            VALUES (%s, %s, %s, %s, %s);
                            """,
                            (foreign_key, str(datapoint.date)[:4], str(datapoint.date)[-2:],
                             datapoint.tmax, datapoint.tmin))
                connection.commit()
            else:
                print("Datapoint already filled.")
    finally:
        cursor.close()
        connection.close()

def get_stations_in_radius(latitude, longitude, radius, first_year, last_year, max_stations):
    """
    Retrieves stations located within a specified radius around the given position
    that meet Tmin/Tmax conditions for the specified time period.

    :param latitude: Latitude of the search position.
    :param longitude: Longitude of the search position.
    :param radius: Search radius in kilometers.
    :param first_year: First year of the desired time period.
    :param last_year: Last year of the desired time period.
    :param max_stations: Maximum number of stations to return.

    :return: List of stations with their distances within the radius (e.g., [(station, distance)]).
    """

    connection = connection_pool.get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT station_id, station_name, latitude, longitude 
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

def get_datapoints_for_station(station_id, first_year, last_year):
    """
    Retrieves temperature average records (Tmin and Tmax) for a station,
    grouped by year and seasons.

    :param station_id: Name of the station.
    :param first_year: First year of the time period.
    :param last_year: Last year of the time period.

    :return: List with 10 records (Northern hemisphere):
             1. Annual average Tmin
             2. Annual average Tmax
             3. Spring Tmin
             4. Spring Tmax
             5. Summer Tmin
             6. Summer Tmax
             7. Autumn Tmin
             8. Autumn Tmax
             9. Winter Tmin
            10. Winter Tmax
    """
    connection = connection_pool.get_connection()
    try:
        with (connection.cursor() as cursor):

            ten_datasets = []

            cursor.execute("SELECT SID FROM Station WHERE station_id = %s;", (station_id,))
            sid = cursor.fetchall()
            station_id = sid[0][0]

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

            seasons = {
                "spring": (3, 5),
                "summer": (6, 8),
                "autumn": (9, 11),
            }

            for season, (start_month, end_month) in seasons.items():

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

            cursor.execute(
                """
                SELECT winter_year,
                       SUM(tmin * days_in_month) / SUM(days_in_month) AS avg_tmin
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
                      AND (CASE WHEN month IN (1,2) THEN year - 1 ELSE year END) BETWEEN %s AND %s
                    GROUP BY year, month
                ) AS subquery
                GROUP BY winter_year
                ORDER BY winter_year;
                """,
                (station_id, first_year, last_year))
            ten_datasets.append(cursor.fetchall())

            cursor.execute(
                """
                SELECT winter_year,
                       SUM(tmax * days_in_month) / SUM(days_in_month) AS avg_tmax
                FROM (
                    SELECT CASE WHEN month IN (1, 2) THEN year - 1 ELSE year END AS winter_year,
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
                      AND (CASE WHEN month IN (1,2) THEN year - 1 ELSE year END) BETWEEN %s AND %s
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
