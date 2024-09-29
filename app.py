from flask import Flask, jsonify
from storage import read_data

app = Flask(__name__)


@app.route('/api/characters', methods=['GET'])
def get_characters():
    """Returns a JSON file containing the list of characters from a Game of Thrones."""

    characters = read_data('characters.json')
    return jsonify(characters), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
