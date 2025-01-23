from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
import mysql.connector

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

connection = mysql.connector.connect(
    user='root', password='root', host='mysql', port="3306", database='db')
print("DB connected")

cursor = connection.cursor()
cursor.execute("SELECT * FROM students")
students = cursor.fetchall()
connection.close()
print(students)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)



