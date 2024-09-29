from flask import Flask, jsonify, request
import random
from storage import read_data

app = Flask(__name__)


@app.route('/api/characters', methods=['GET'])
def get_characters():
    """Returns a JSON file containing the list of characters from a Game of Thrones,
    supporting pagination through the 'limit' and 'skip' query parameters. If these
    parameters are not provided, a random selection of 20 characters is returned by default."""

    characters = read_data('characters.json')

    # Sort by any of the character's attributes
    sort_asc = request.args.get('sort_asc')
    sort_desc = request.args.get('sort_desc')
    attributes = ['age', 'animal', 'death', 'house', 'id', 'name', 'nickname', 'role', 'strength', 'symbol']

    if (sort_asc and sort_asc not in attributes) or (sort_desc and sort_desc not in attributes):
        return jsonify({"error": "To sort please select one of these attributes: 'age' / 'animal' /"
                                 " 'death' / 'house' / 'id' / 'name' / 'nickname' / 'role' "
                                 "/ 'strength' / 'symbol'"}), 400

    if sort_asc in attributes:
        sorted_characters = sorted(characters, key=lambda x: (x.get(sort_asc) is None, x.get(sort_asc)))
        return jsonify(sorted_characters), 200

    if sort_desc in attributes:
        sorted_characters = sorted(characters, key=lambda x: (x.get(sort_desc) is None, x.get(sort_desc)), reverse=True)
        return jsonify(sorted_characters), 200

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

    if skip >= len(characters):
        return jsonify({"message": f"Skip is exceeding the length of the"
                                   f" characters database (Total characters: {len(characters)})"}), 400

    if 'limit' not in request.args and 'skip' not in request.args and not sort_asc and not sort_desc:
        random_characters = random.sample(characters, min(20, len(characters)))
        return jsonify(random_characters), 200

    paginated_characters = characters[skip:skip + limit]

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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
