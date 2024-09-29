import json


def read_data(file_path):
    """Reads the JSON file and returns the data."""
    with open(file_path, 'r') as fileobj:
        data = json.load(fileobj)
        return data
