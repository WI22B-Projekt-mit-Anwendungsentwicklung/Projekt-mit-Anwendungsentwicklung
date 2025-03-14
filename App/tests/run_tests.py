
# =========================================================
# Run All Tests
# =========================================================


def run_backend_tests():
    """
    Runs the Python tests (Pytest) with coverage.
    """
    import sys
    import pytest
    print("Running Python backend tests with coverage...")
    pytest_args = [
        "-q",
        "--cov=src.data_services",
        "--cov=src.datapoint",
        "--cov=src.routes",
        "--cov=src.calculations",
        "--cov=src.station",
        "--cov-report=term",
        "tests"
    ]

    exit_code = pytest.main(pytest_args)
    if exit_code != 0:
        print("\nPython tests failed! Exiting...")
        sys.exit(1)
    else:
        print("\nPython tests passed successfully.")


def run_frontend_tests():
    """
    Runs the frontend (JS) tests by calling 'npm test'.
    """
    import sys
    import os

    print("Running frontend tests with 'npm test'...")
    exit_code = os.system("npm test")
    if exit_code != 0:
        print("\nFrontend tests failed! Exiting...")
        sys.exit(1)
    else:
        print("\nFrontend tests passed successfully.")


def run_all_tests():
    """
    Runs both backend and frontend tests in sequence.
    This is the single function we will call from app.py.
    """
    run_frontend_tests()
    run_backend_tests()