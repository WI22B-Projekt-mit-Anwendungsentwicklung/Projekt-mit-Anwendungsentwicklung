import data_services as ds
from flask import Flask
from flask_cors import CORS
from routes import init_routes
import pytest

app = Flask(__name__)
CORS(app)

# Register routes
init_routes(app)

# Initialize database, if needed
ds.save_data_to_db()


# Run tests with coverage
def run_tests():
    print("Running tests with coverage...")

    pytest_args = [
        "-q",  # Quiet mode (reduziert die Ausgabe)
        "--cov=data_services",  # Coverage für data_services.py
        "--cov=datapoint",  # Coverage für datapoint.py
        "--cov=routes",  # Coverage für routes.py
        "--cov=station",  # Coverage für station.py
        "--cov-report=term",  # Zeigt die Coverage in der Konsole an
        "tests.py"  # Testdatei
    ]

    pytest_exit_code = pytest.main(pytest_args)

    if pytest_exit_code != 0:
        print("\nTests failed! Exiting the application...")
        exit(1)
    else:
        print("\nAll tests passed! Coverage report displayed above.")


# Run the test function
run_tests()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
