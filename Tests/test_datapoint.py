import pytest
from App.datapoint import DataPoint, extract_average_value, download_and_create_datapoints, download_and_create_datapoints_local

def test_datapoint_init():
    dp = DataPoint(202401, 25.5, 10.3, "ST123")
    assert dp.date == 202401
    assert dp.tmax == 25.5
    assert dp.tmin == 10.3

def test_datapoint_repr():
    dp = DataPoint(202401, 25.5, 10.3, "ST123")
    assert "DataPoint(date=202401" in repr(dp)

def test_extract_average_value():
    line = """01234567890123456789   250   300   -9999  """
    assert extract_average_value(line) == 27.5
