from flask import Flask, render_template, request, jsonify
import mysql.connector
import station as st
import datapoint as dp
from flask_cors import CORS
from mysql.connector import pooling
app = Flask(__name__)
CORS(app)


def save_data_to_db():
    cursor.execute("SELECT * FROM Station;")
    inhalt_station = cursor.fetchall()
    if not inhalt_station:
        stations = st.load_stations_from_url("https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt")
        for station in stations:
            cursor.execute(
                "INSERT INTO Station (station_name, latitude, longitude, first_tmax, latest_tmax, first_tmin, latest_tmin) "
                f"VALUES ('{station.id}', {station.latitude}, {station.longitude}, {station.first_measure_tmax},"
                f" {station.last_measure_tmax}, {station.first_measure_tmin}, {station.last_measure_tmin});")
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
                    f"INSERT INTO Datapoint (SID, year, month, tmax, tmin) VALUES ('{foreign_key}', {str(datapoint.date)[:4]}, {str(datapoint.date)[-2:]},{datapoint.tmax},{datapoint.tmin});")
        connection.commit()
    else:
        print("Datapoint bereits gefüllt")

def get_stations():
    cursor.execute("SELECT * FROM Station;")
    return cursor.fetchall()

def get_stations_in_radius(latitude, longitude, radius, first_year, last_year, max_stations):
    cursor.execute(f"SELECT station_name, latitude, longitude FROM Station "
                   f"WHERE first_tmin <= {first_year} "
                   f"AND latest_tmin >= {last_year} "
                   f"AND first_tmax <= {first_year} "
                   f"AND latest_tmax >= {last_year} ;")
    stations = cursor.fetchall()

    stations_in_radius = st.find_stations_within_radius(stations, latitude, longitude, radius, max_stations)
    return stations_in_radius  # (('GMM00010591', 50.933, 14.217), 66.85437995060985)

def get_datapoints_for_station(station_name, first_year, last_year):
    # 1. Jahresdurchschnitt Tmin
    # 2. Jahresdurchschnitt Tmax
    # 3. Frühling Tmin
    # 4. Frühling Tmax
    # 5. Sommer Tmin
    # 6. Sommer Tmax
    # 7. Herbst Tmin
    # 8. Herbst Tmax
    # 9. Winter Tmin
    # 10. Winter Tmax

    ten_datasets = []

    cursor.execute(f"SELECT SID FROM Datapoint WHERE station_name = '{station_name}';")
    sid = cursor.fetchall()
    station_id = sid[0]

    # 1. Jährlicher Mittelwert der Temperaturminima
    cursor.execute(f"SELECT year, AVG(tmin) FROM Datapoint "
                   f"WHERE SID = {station_id} AND year BETWEEN {first_year} AND {last_year} "
                   f"GROUP BY year ORDER BY year;")
    ten_datasets.append(cursor.fetchall())

    # 2. Jährlicher Mittelwert der Temperaturmaxima
    cursor.execute(f"SELECT year, AVG(tmax) FROM Datapoint "
                   f"WHERE SID = {station_id} AND year BETWEEN {first_year} AND {last_year} "
                   f"GROUP BY year ORDER BY year;")
    ten_datasets.append(cursor.fetchall())

    # 3-8. Jährliche Mittelwerte für Tmin und Tmax in den Jahreszeiten Frühling, Sommer, Herbst
    seasons = {
        "spring": (3, 5),
        "summer": (6, 8),
        "autumn": (9, 11),
    }

    for season, (start_month, end_month) in seasons.items():
        cursor.execute(f"SELECT year, AVG(tmin) FROM Datapoint "
                       f"WHERE SID = {station_id} AND month BETWEEN {start_month} AND {end_month} "
                       f"AND year BETWEEN {first_year} AND {last_year} "
                       f"GROUP BY year ORDER BY year;")
        ten_datasets.append(cursor.fetchall())

        cursor.execute(f"SELECT year, AVG(tmax) FROM Datapoint "
                       f"WHERE SID = {station_id} AND month BETWEEN {start_month} AND {end_month} "
                       f"AND year BETWEEN {first_year} AND {last_year} "
                       f"GROUP BY year ORDER BY year;")
        ten_datasets.append(cursor.fetchall())

    # 9. Jährlicher Mittelwert der Temperaturminima im Winter (Dez-Vorjahr + Jan+Feb)
    cursor.execute(f"SELECT CASE WHEN month = 12 THEN year + 1 ELSE year END AS winter_year, "
                   f"AVG(tmin) FROM Datapoint "
                   f"WHERE SID = {station_id} AND (month = 12 OR month BETWEEN 1 AND 2) "
                   f"AND (CASE WHEN month = 12 THEN year + 1 ELSE year END) BETWEEN {first_year} AND {last_year} "
                   f"GROUP BY winter_year ORDER BY winter_year;")
    ten_datasets.append(cursor.fetchall())

    # 10. Jährlicher Mittelwert der Temperaturmaxima im Winter (Dez-Vorjahr + Jan+Feb)
    cursor.execute(f"SELECT CASE WHEN month = 12 THEN year + 1 ELSE year END AS winter_year, "
                   f"AVG(tmax) FROM Datapoint "
                   f"WHERE SID = {station_id} AND (month = 12 OR month BETWEEN 1 AND 2) "
                   f"AND (CASE WHEN month = 12 THEN year + 1 ELSE year END) BETWEEN {first_year} AND {last_year} "
                   f"GROUP BY winter_year ORDER BY winter_year;")
    ten_datasets.append(cursor.fetchall())

    return ten_datasets

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
connection = connection_pool.get_connection()

cursor = connection.cursor()
# -----
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def receive_data():
    data = request.json  # Holt die JSON-Daten aus der Anfrage
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius = data.get('radius')
    year_start = data.get('yearStart')
    year_end = data.get('yearEnd')
    stations = data.get('stations')

    # Verbindung zur Datenbank
    try:
        connection = mysql.connector.connect(
            user='root', password='root', host='mysql', port="3306", database='db'
        )
        cursor = connection.cursor()

        # Stationsdaten abrufen
        stations_in_radius = get_stations_in_radius(latitude, longitude, radius, year_start, year_end, stations)

        # Füge die Ergebnisse zur Antwort hinzu
        data["stationsInRadius"] = stations_in_radius

    except mysql.connector.Error as err:
        return jsonify({"error": f"Fehler bei der Datenbankverbindung: {err}"}), 500
    finally:
        # Schließen der Verbindung und des Cursors
        cursor.close()
        connection.close()

    return jsonify({"message": f"{data} erfolgreich empfangen!"}), 200


save_data_to_db()

print(get_stations_in_radius(51.1, 13.3, 100, 1950, 2020, 20))
#a = get_datapoints_for_station("AE000041196", 1990, 2000)



cursor.execute("SELECT * FROM Datapoint LIMIT 5;")
result = cursor.fetchall()
print(result)
print(type(result))
connection.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)



