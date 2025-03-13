from flask import request, jsonify, render_template
import data_services as ds

def init_routes(app):

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/submit', methods=['POST'])
    def receive_data():
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius')
        year_start = data.get('yearStart')
        year_end = data.get('yearEnd')
        stations = data.get('stations')

        stations_in_radius = ds.get_stations_in_radius(latitude, longitude, radius, year_start, year_end, stations)
        data["stationsInRadius"] = stations_in_radius

        return jsonify(data["stationsInRadius"]), 200

    @app.route('/get_weather_data', methods=['POST'])
    def get_weather_data():
        data = request.json
        station_name = data.get('stationName')
        year_start = data.get('yearStart')
        year_end = data.get('yearEnd')

        if not station_name or not year_start or not year_end:
            return jsonify({"message": "Fehlende Parameter"}), 400

        weather_data = ds.get_datapoints_for_station(station_name, year_start, year_end)
        data["weatherData"] = weather_data

        return jsonify(data["weatherData"]), 200
