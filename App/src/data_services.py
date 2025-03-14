import station as st
import datapoint as dp
import calculations as calc
import time
from mysql.connector import pooling

# Wait to make sure MYSQL DB is running
time.sleep(10)

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

                cursor.execute("SELECT * FROM Station;")
                inhalt_station = cursor.fetchall()

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

    :return: List of stations with their distances within the radius.
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

            stations_in_radius = calc.find_stations_within_radius(stations, latitude, longitude, radius, max_stations)
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
                    SELECT CASE WHEN month = 12 THEN year + 1 ELSE year END AS winter_year,
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

            cursor.execute(
                """
                SELECT winter_year,
                       SUM(tmax * days_in_month) / SUM(days_in_month) AS avg_tmax
                FROM (
                    SELECT CASE WHEN month = 12 THEN year + 1 ELSE year END AS winter_year,
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
