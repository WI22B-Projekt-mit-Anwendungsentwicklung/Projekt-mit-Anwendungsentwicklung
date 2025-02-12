import data_services as ds
from flask import Flask
from flask_cors import CORS
from routes import init_routes

app = Flask(__name__)
CORS(app)

# Routen registrieren
init_routes(app)

# Initialisiere Datenbank, falls nötig
ds.save_data_to_db()

#print(ds.get_stations_in_radius(51.1, 13.3, 100, 1950, 2020, 20))
a = ds.get_datapoints_for_station("AE000041196", 1998, 2000)
print(a)
# [(1998, 20.573333342870075), (1999, 20.442583163579304), (2000, 20.360416650772095)], [(1998, 35.80766646067301), (1999, 35.89291683832804), (2000, 35.23483339945475)],
# [(1998, 20.62168768268742) , (1999, 20.457019009002266), (2000, 20.37627047398051)] , [(1998, 35.86117240174176), (1999, 35.91752619286106), (2000, 35.26121863901941)],

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
