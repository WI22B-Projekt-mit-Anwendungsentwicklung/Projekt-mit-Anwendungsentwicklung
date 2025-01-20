from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
import mysql.connector

app = Flask(__name__)
api = Api(app)

class UserInput(Resource):
    def post(self):
        # Nutzerdaten aus dem Request abrufen
        data = request.get_json()

        # Eingabedaten ausgeben (Zwischenspeichern in der Konsole)
        print("Nutzerinput empfangen:", data)

        # Erfolgs-Response zurückgeben
        return jsonify({"message": "Input received successfully", "data": data})

api.add_resource(UserInput, '/user-input')
@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)



connection = mysql.connector.connect(
    user='root', password='root', host='mysql', port="3306", database='db')
print("DB connected")

cursor = connection.cursor()
cursor.execute("SELECT * FROM students")
students = cursor.fetchall()
connection.close()
print(students)