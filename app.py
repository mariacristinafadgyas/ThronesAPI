from flask import Flask, jsonify, request
import random
from storage import read_data

app = Flask(__name__)


@app.route('/api/characters', methods=['GET'])
def get_characters():
    """Returns a JSON file containing the list of characters from a Game of Thrones."""

    characters = read_data('characters.json')

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

    if 'limit' not in request.args and 'skip' not in request.args:
        random_characters = random.sample(characters, min(20, len(characters)))
        return jsonify(random_characters), 200

    paginated_characters = characters[skip:skip + limit]

    return jsonify(paginated_characters), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
