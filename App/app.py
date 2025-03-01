import data_services as ds
from flask import Flask
from flask_cors import CORS
from routes import init_routes

app = Flask(__name__)
CORS(app)

# Register routes
init_routes(app)

# Initialize database, if needed
ds.save_data_to_db()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
