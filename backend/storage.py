import json


def read_data(file_path):
    """Reads the JSON file and returns the data.Handles errors if the file
     doesn't exist or contains invalid JSON."""
    try:
        with open(file_path, 'r') as fileobj:
            data = json.load(fileobj)
            return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} contains invalid JSON.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []


def sync_data(file_path, characters):
    """Writes data to the JSON file. Handles errors that might occur during
    the write process."""
    updated_characters = json.dumps(characters)
    try:
        with open(file_path, 'w') as fileobj:
            fileobj.write(updated_characters)
    except IOError:
        print(f"Error: Unable to write to file {file_path}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    characters = read_data('backend/characters.json')
    new_character = {
        "name": "Jon Snow",
        "age": 25,
        "animal": None,
        "death": None,
        "house": "Stark",
        "id": 51,
        "nickname": None,
        "role": "King in the North",
        "strength": 80,
        "symbol": "Wolf"
        }
    characters.append(new_character)
    sync_data('backend/characters.json', characters)


if __name__ == "__main__":
    main()
