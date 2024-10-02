from flask import Flask, jsonify, request
import random
from storage import read_data, sync_data

app = Flask(__name__)


@app.route('/api/characters', methods=['GET'])
def get_characters():
    """Returns a JSON file containing the list of characters from a Game of Thrones,
    supporting pagination through the 'limit' and 'skip' query parameters. If these
    parameters are not provided, a random selection of 20 characters is returned by default.
    Filtering by attributes such as age, house, and role is supported, allowing multiple
    filters to be applied simultaneously. Additionally, characters can be sorted in
    ascending or descending order by any specified attribute."""

    characters = read_data('characters.json')

    # Filtering
    filter_params = {
        'age': request.args.get('age'),
        'animal': request.args.get('animal'),
        'death': request.args.get('death'),
        'house': request.args.get('house'),
        'name': request.args.get('name'),
        'nickname': request.args.get('nickname'),
        'role': request.args.get('role'),
        'strength': request.args.get('strength'),
        'symbol': request.args.get('symbol'),
        'age_more_than': request.args.get('age_more_than'),
        'age_less_than': request.args.get('age_less_than')
    }

    filtered_characters = characters
    for key, value in filter_params.items():
        if value:
            if key in ['age', 'age_more_than', 'age_less_than']:
                try:
                    value = int(value)
                except ValueError:
                    return jsonify({"error": f"Invalid {key} parameter. Age must be an integer."}), 400

                if key == 'age_more_than':
                    filtered_characters = [character for character in filtered_characters
                                           if character['age'] is not None and character['age'] >= value]
                elif key == 'age_less_than':
                    filtered_characters = [character for character in filtered_characters
                                           if character['age'] is not None and character['age'] <= value]
                elif key == 'age':
                    filtered_characters = [character for character in filtered_characters
                                           if character['age'] is not None and character['age'] == value]
            else:
                filtered_characters = [character for character in filtered_characters
                                       if character.get(key) is not None
                                       and value.lower() in character[key].lower()]

    # Sort by any of the character's attributes
    sort_asc = request.args.get('sort_asc')
    sort_desc = request.args.get('sort_desc')
    attributes = ['age', 'animal', 'death', 'house', 'id', 'name', 'nickname', 'role', 'strength', 'symbol']

    if (sort_asc and sort_asc not in attributes) or (sort_desc and sort_desc not in attributes):
        return jsonify({"error": "To sort please select one of these attributes: 'age' / 'animal' /"
                                 " 'death' / 'house' / 'id' / 'name' / 'nickname' / 'role' "
                                 "/ 'strength' / 'symbol'"}), 400

    if sort_asc in attributes:
        sorted_characters = sorted(filtered_characters, key=lambda x: (x.get(sort_asc) is None, x.get(sort_asc)))
        # return jsonify(sorted_characters), 200

    elif sort_desc in attributes:
        sorted_characters = sorted(filtered_characters,
                                   key=lambda x: (x.get(sort_desc) is None, x.get(sort_desc)), reverse=True)
        # return jsonify(sorted_characters), 200
    else:
        sorted_characters = filtered_characters

    # Pagination
    limit = 20
    skip = 0

    if 'limit' in request.args:
        try:
            limit = int(request.args.get('limit'))
            if limit <= 0:
                return jsonify({"error": "Limit must be greater than 0."}), 400
        except ValueError:
            return jsonify({"error": "Invalid limit parameter. Must be an integer."}), 400

    if 'skip' in request.args:
        try:
            skip = int(request.args.get('skip'))
            if skip < 0:
                return jsonify({"error": "Skip must be a non-negative integer."}), 400
        except ValueError:
            return jsonify({"error": "Invalid skip parameter. Must be an integer."}), 400

    if skip >= len(sorted_characters):
        return jsonify({"message": f"Skip is exceeding the length of the"
                                   f" characters database (Total characters: {len(sorted_characters)})"}), 400

    if ('limit' not in request.args and 'skip' not in request.args and not sort_asc
            and not sort_desc and not any(filter_params.values())):
        random_characters = random.sample(characters, min(20, len(characters)))
        return jsonify(random_characters), 200

    paginated_characters = sorted_characters[skip:skip + limit]

    return jsonify(paginated_characters), 200


@app.route('/api/characters/<int:character_id>', methods=['GET'])
def get_character_by_id(character_id):
    """Returns a JSON representation of the character whose 'id'
    matches the provided 'character_id'. If the character is not found,
    a 404 error is returned with an appropriate message."""

    characters = read_data('characters.json')

    for character in characters:
        if character['id'] == character_id:
            return jsonify(character), 200

    return jsonify({"error": f"Character with ID {character_id} not found."}), 400


@app.route('/api/characters', methods=['POST'])
def add_character():
    """Adds a new character to the character list, ensuring all required fields
    are filled and have the correct data types."""

    characters = read_data('characters.json')

    new_character = request.get_json()  # Retrieves data from the request

    required_fields = {
        'name': str,
        'age': int,
        'animal': str,
        'death': str,
        'house': str,
        'nickname': str,
        'role': str,
        'strength': str,
        'symbol': str
    }

    for field, field_type in required_fields.items():
        if field not in new_character:
            new_character[field] = None

        if new_character[field] is not None and not isinstance(new_character[field], field_type):
            return jsonify({"error": f"'{field}' must be of type {field_type.__name__} or null."}), 400

    new_character['id'] = max([char['id'] for char in characters]) + 1 if characters else 1
    characters.append(new_character)
    sync_data('characters.json', characters)  # For in-memory saving of a new character comment this line
    return jsonify(new_character), 200


@app.route('/api/characters/<int:id>', methods=['DELETE'])
def delete_character(id):
    """Deletes a character based on the ID specified in the URL. If the character
     exists, it is deleted, if it does not exist, an error message is returned."""

    characters = read_data('characters.json')

    for character in characters:
        if character['id'] == id:
            characters.remove(character)
            sync_data('characters.json', characters)
            return jsonify({"message": f"Character with id {id} has been deleted"
                                       f" successfully."}), 200
    return jsonify({"message": f"Character with id {id} not found."}), 404


@app.route('/api/characters/<int:id>', methods=['PUT'])
def update_character(id):
    """Updates the attributes of an existing character. If the character is
    found, it updates only the fields provided in the request body, leaving
    any unspecified fields unchanged. """

    characters = read_data('characters.json')
    data = request.get_json()

    required_fields = {
        'name': str,
        'age': int,
        'death': str,
        'house': str,
        'nickname': str,
        'role': str,
        'strength': str,
        'symbol': str
    }

    for field, expected_type in required_fields.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                return jsonify({"error": f"'{field}' must be of type {expected_type.__name__}."}), 400
        elif field in data and data[field] is None:
            data[field] = None   # Allow null values if explicitly sent

    for character in characters:
        if character['id'] == id:
            character['name'] = data.get('name', character['name'])
            character['age'] = data.get('age', character['age'])
            character['death'] = data.get('death', character['death'])
            character['house'] = data.get('house', character['house'])
            character['nickname'] = data.get('nickname', character['nickname'])
            character['role'] = data.get('role', character['role'])
            character['strength'] = data.get('strength', character['strength'])
            character['symbol'] = data.get('symbol', character['symbol'])

            sync_data('characters.json', characters)

            return jsonify({"message": f"Character with id {id} has been updated "
                                       f"successfully.", "id": id}), 200
    return jsonify({"error": f"Character with id {id} not found!"}), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
