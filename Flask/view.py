from Flask import Flask, render_template
import os

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 4999))
    app.run(debug=True, host='0.0.0.0', port=port)

import mysql.connector
# from Altdaten import station

connection = mysql.connector.connect(
    user='root', password='root', host='mysql', port="3306", database='db')
print("DB connected")

cursor = connection.cursor()

# stations = station.load_stations_from_url("https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.csv")
cursor.execute('INSERT INTO students(FirstName, Surname)VALUES ("John", "Andersen"), ("Emma", "Smith")')
cursor.execute("SELECT * FROM students")
students = cursor.fetchall()
connection.close()