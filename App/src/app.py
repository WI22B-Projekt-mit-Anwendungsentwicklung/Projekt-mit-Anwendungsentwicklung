from flask import Flask
from flask_cors import CORS
from routes import init_routes
import data_services as ds
#from tests import run_all_tests
app = Flask(__name__)
CORS(app)
init_routes(app)
ds.save_data_to_db()
#run_all_tests()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
