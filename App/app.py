from flask import Flask, render_template, request, jsonify
import mysql.connector
import station as st
import datapoint as dp
app = Flask(__name__)

def save_data_to_db():
    cursor.execute("SELECT * FROM Station;")
    inhalt_station = cursor.fetchall()
    if not inhalt_station:
        stations = st.load_stations_from_url("https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt")
        for station in stations:
            cursor.execute(
                "INSERT INTO Station (id, latitude, longitude, first_tmax, latest_tmax, first_tmin, latest_tmin) "
                f"VALUES ('{station.id}', {station.latitude}, {station.longitude}, {station.first_measure_tmax},"
                f" {station.last_measure_tmax}, {station.first_measure_tmin}, {station.last_measure_tmin});")
        connection.commit()
    else:
        print("Station bereits gefüllt")

    cursor.execute("SELECT * FROM Datapoint LIMIT 1;")
    inhalt_datapoint = cursor.fetchall()
    if not inhalt_datapoint:
        for station in inhalt_station:
            datapoints = dp.download_and_create_datapoints(station[0])
            for datapoint in datapoints:
                cursor.execute(
                    f"INSERT INTO Datapoint (station_id, year, month, tmax, tmin) VALUES ('{datapoint.station}', {str(datapoint.date)[:4]}, {str(datapoint.date)[-2:]},{datapoint.tmax},{datapoint.tmin});")
        connection.commit()
    else:
        print("Datapoint bereits gefüllt")

def get_stations():
    cursor.execute("SELECT * FROM Station;")
    return cursor.fetchall()

def get_stations_in_radius(latitude, longitude, radius, first_year, last_year):
    cursor.execute(f"SELECT id, latitude, longitude FROM Station "
                   f"WHERE first_tmin >= {first_year} "
                   f"AND latest_tmin <= {last_year} "
                   f"AND first_tmax >= {first_year} "
                   f"AND latest_tmax <= {last_year} ;")
    stations = cursor.fetchall()

    stations_in_radius = st.find_stations_within_radius(stations, latitude, longitude, radius)
    return stations_in_radius  # (('GMM00010591', 50.933, 14.217), 66.85437995060985)

def get_datapoints_for_station(station_id, first_year, last_year):
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

    # 1. Jährlicher Mittelwert der Temperaturminima
    cursor.execute(f"SELECT year, AVG(tmin) FROM Datapoint "
                   f"WHERE station_id = '{station_id}' AND year BETWEEN {first_year} AND {last_year} "
                   f"GROUP BY year ORDER BY year;")
    ten_datasets.append(cursor.fetchall())

    # 2. Jährlicher Mittelwert der Temperaturmaxima
    cursor.execute(f"SELECT year, AVG(tmax) FROM Datapoint "
                   f"WHERE station_id = '{station_id}' AND year BETWEEN {first_year} AND {last_year} "
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
                       f"WHERE station_id = '{station_id}' AND month BETWEEN {start_month} AND {end_month} "
                       f"AND year BETWEEN {first_year} AND {last_year} "
                       f"GROUP BY year ORDER BY year;")
        ten_datasets.append(cursor.fetchall())

        cursor.execute(f"SELECT year, AVG(tmax) FROM Datapoint "
                       f"WHERE station_id = '{station_id}' AND month BETWEEN {start_month} AND {end_month} "
                       f"AND year BETWEEN {first_year} AND {last_year} "
                       f"GROUP BY year ORDER BY year;")
        ten_datasets.append(cursor.fetchall())

    # 9. Jährlicher Mittelwert der Temperaturminima im Winter (Dez-Vorjahr + Jan+Feb)
    cursor.execute(f"SELECT CASE WHEN month = 12 THEN year + 1 ELSE year END AS winter_year, "
                   f"AVG(tmin) FROM Datapoint "
                   f"WHERE station_id = '{station_id}' AND (month = 12 OR month BETWEEN 1 AND 2) "
                   f"AND (CASE WHEN month = 12 THEN year + 1 ELSE year END) BETWEEN {first_year} AND {last_year} "
                   f"GROUP BY winter_year ORDER BY winter_year;")
    ten_datasets.append(cursor.fetchall())

    # 10. Jährlicher Mittelwert der Temperaturmaxima im Winter (Dez-Vorjahr + Jan+Feb)
    cursor.execute(f"SELECT CASE WHEN month = 12 THEN year + 1 ELSE year END AS winter_year, "
                   f"AVG(tmax) FROM Datapoint "
                   f"WHERE station_id = '{station_id}' AND (month = 12 OR month BETWEEN 1 AND 2) "
                   f"AND (CASE WHEN month = 12 THEN year + 1 ELSE year END) BETWEEN {first_year} AND {last_year} "
                   f"GROUP BY winter_year ORDER BY winter_year;")
    ten_datasets.append(cursor.fetchall())

    return ten_datasets

@app.route('/')
def home():
    return render_template('index.html')

connection = mysql.connector.connect(
    user='root', password='root', host='mysql', port="3306", database='db')
print("DB connected")

cursor = connection.cursor()
# -----

save_data_to_db()

print(get_stations_in_radius(51.1, 13.3, 100, 1950, 2020))
a = get_datapoints_for_station("AE000041196", 1990, 2000)

b = 1
for i in a:
    print(f"Dataset {b}:--------------------------------")
    b += 1
    for j in i:
        print(j)
    print("--------------------------------")



cursor.execute("SELECT * FROM Datapoint LIMIT 5;")
result = cursor.fetchall()
print(result)
print(type(result))
connection.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)



