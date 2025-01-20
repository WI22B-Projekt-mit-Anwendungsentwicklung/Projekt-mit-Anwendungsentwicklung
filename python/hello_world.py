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

