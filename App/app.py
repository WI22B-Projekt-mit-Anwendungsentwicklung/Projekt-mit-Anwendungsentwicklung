from flask import Flask, render_template, request, jsonify
import mysql.connector
import station
import datapoint as dp
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

connection = mysql.connector.connect(
    user='root', password='root', host='mysql', port="3306", database='db')
print("DB connected")

stations = []
cursor = connection.cursor()
cursor.execute("SELECT * FROM Station;")
inhalt_station = cursor.fetchall()
if not inhalt_station:
    print("Tabelle leer")
    stations = station.load_stations_from_url("https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt")
    for station in stations:
        cursor.execute("INSERT INTO Station (id, latitude, longitude, first_tmax, latest_tmax, first_tmin, latest_tmin) "
                     f"VALUES ('{station.id}', {station.latitude}, {station.longitude}, {station.first_measure_tmax},"
                       f" {station.last_measure_tmax}, {station.first_measure_tmin}, {station.last_measure_tmin});")
    connection.commit()
else:
    print("Tabelle bereits gefüllt")

cursor.execute("SELECT * FROM Datapoint;")
inhalt_datapoint = cursor.fetchall()
if not inhalt_datapoint and inhalt_station:
    print("Tabelle Datapoint leer")
    for station in inhalt_station:
        datapoints = dp.download_and_create_datapoints_local(station[0])
        for datapoint in datapoints:
            cursor.execute(f"INSERT INTO Datapoint (station_id, year, month, tmax, tmin) VALUES ('{datapoint.station}', {str(datapoint.date)[:4]}, {str(datapoint.date)[-2:]},{datapoint.tmax},{datapoint.tmin});")
else:
    print("Tabelle bereits gefüllt")


cursor.execute("SELECT * FROM Datapoint LIMIT 10;")
rows = cursor.fetchall()
connection.close()

print(rows)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)



