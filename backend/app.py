import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from functools import wraps
import json
import jwt
import os
import random
from storage import read_data, sync_data

# Loads and sets the environment variables
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
# This will enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=['Authorization', 'Content-Type'])

VALID_ATTRIBUTES = ['age', 'animal', 'death', 'house', 'name', 'nickname', 'role', 'strength', 'symbol']


def token_required(f):
    """ Middleware (decorator) to protect routes by requiring a valid JWT token.
    Ensures that an incoming request contains a valid JSON Web Token (JWT) in the
    'Authorization' header. It verifies the token's signature and checks if it is
    expired or invalid. If the token is missing or invalid, the request is denied
    with a 401 Unauthorized response. If the token is valid, the decoded payload
    (containing user information such as 'username' and 'role') is passed to the
    route handler as a parameter, but no role-based access control is enforced in
    this function. It takes f (which is the protected route function) as an argument."""
    @wraps(f)
    def decorated(*args, **kwargs):
        """The decorated function is the inner function that will actually wrap around
        the protected route. It receives the same arguments (*args, **kwargs) that the
        protected route would have received."""

        # Extracts the JWT from the Authorization header of the incoming request
        token = request.headers.get('Authorization')
        # print(f"Token received: {token}")

        if not token or not token.startswith('Bearer '):
            return jsonify({'message': 'Token is missing or invalid format'}), 401

        if token.startswith('Bearer '):
            token = token.split(' ')[1]  # Extract the token part only

        try:
            # Decode the JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        # Pass the payload to the route function
        return f(payload, *args, **kwargs)

    return decorated


@app.route('/api/register', methods=['POST'])
def register_user():
    """API to register a new user."""

    # Modified to be a local variable intead of a global variable
    users = read_data('users.json')

    new_user = request.get_json()

    username = new_user.get('username')
    password = new_user.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    if username in users:
        return jsonify({"message": "Username already exists."}), 400

    # Creates a new user entry with a default role
    # users[username] = {"password": password, "role": "user"}
    users.update({
        username: {
            "password": password,
            "role": "user"
        }
    })

    sync_data(os.path.join('backend', 'users.json'), users)
    return jsonify({"message": "User registered successfully."}), 200


@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint to authenticate users and return a JWT."""

    # Modified to be a local variable instead of a global variable
    users = read_data('users.json')

    auth_data = request.get_json()

    username = auth_data.get('username')
    password = auth_data.get('password')

    if username in users and users[username]['password'] == password:
        # JWT payload creation
        payload = {
            'username': username,
            'role': users[username]['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/api/characters', methods=['GET'])
@token_required
def get_characters(payload):
    """Returns a JSON file containing the list of characters from Game of Thrones,
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

    # Validates that all filter parameters are valid attributes
    for key in request.args:
        if (key not in VALID_ATTRIBUTES and
                key not in ['age_more_than', 'age_less_than', 'limit', 'skip', 'sort_asc', 'sort_desc']):
            return jsonify({"error": f"Invalid filter attribute: '{key}' is not a valid character attribute."}), 400

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

    if (sort_asc and sort_asc not in VALID_ATTRIBUTES) or (sort_desc and sort_desc not in VALID_ATTRIBUTES):
        return jsonify({"error": "To sort please select one of these attributes: 'age' / 'animal' /"
                                 " 'death' / 'house' / 'id' / 'name' / 'nickname' / 'role' "
                                 "/ 'strength' / 'symbol'"}), 400

    if sort_asc in VALID_ATTRIBUTES:
        sorted_characters = sorted(filtered_characters, key=lambda x: (x.get(sort_asc) is None, x.get(sort_asc)))
        # return jsonify(sorted_characters), 200

    elif sort_desc in VALID_ATTRIBUTES:
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
        return jsonify({"error": f"Skip is exceeding the length of the"
                                 f" characters database (Total characters: {len(sorted_characters)})"}), 400

    # if skip + limit > len(sorted_characters):
    #     return jsonify({"error": "Requested page exceeds available characters."}), 400

    if ('limit' not in request.args and 'skip' not in request.args and not sort_asc
            and not sort_desc and not any(filter_params.values())):
        random_characters = random.sample(characters, min(20, len(characters)))
        return jsonify(random_characters), 200

    paginated_characters = sorted_characters[skip:skip + limit]

    return jsonify(paginated_characters), 200


@app.route('/api/all_characters', methods=['GET'])
@token_required
def get_all_characters(payload):
    """Returns a JSON file containing the list of all characters from Game of Thrones."""

    characters = read_data('characters.json')

    return jsonify(characters), 200


@app.route('/api/characters/<int:character_id>', methods=['GET'])
@token_required
def get_character_by_id(payload, character_id):
    """Returns a JSON representation of the character whose 'id'
    matches the provided 'character_id'. If the character is not found,
    a 404 error is returned with an appropriate message."""

    characters = read_data('characters.json')

    for character in characters:
        if character['id'] == character_id:
            return jsonify(character), 200

    return jsonify({"error": f"Character with ID {character_id} not found."}), 400


@app.route('/api/characters', methods=['POST'])
@token_required
def add_character(payload):
    """Adds a new character to the character list, ensuring all required fields
    are filled and have the correct data types."""

    characters = read_data('characters.json')
    new_character = request.get_json()  # Retrieves data from the request

    # print("Received data:", new_character)  # Log the incoming request

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
    # For in-memory saving of a new character comment next line
    sync_data(os.path.join('backend', 'characters.json'), characters)
    return jsonify(new_character), 200


@app.route('/api/characters/<int:id>', methods=['DELETE'])
@token_required
def delete_character(payload, id):
    """Deletes a character based on the ID specified in the URL. If the character
     exists, it is deleted, if it does not exist, an error message is returned."""

    characters = read_data('characters.json')

    for character in characters:
        if character['id'] == id:
            characters.remove(character)
            sync_data(os.path.join('backend', 'characters.json'), characters)
            return jsonify({"message": f"Character with id {id} has been deleted"
                                       f" successfully."}), 200
    return jsonify({"message": f"Character with id {id} not found."}), 404


@app.route('/api/characters/<int:id>', methods=['PUT'])
@token_required
def update_character(payload, id):
    """Updates the attributes of an existing character by ID. If the character is
    found, it updates only the fields provided in the request body, leaving
    any unspecified fields unchanged. """

    characters = read_data('characters.json')
    data = request.get_json()

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
            character['animal'] = data.get('animal', character['animal'])
            character['death'] = data.get('death', character['death'])
            character['house'] = data.get('house', character['house'])
            character['nickname'] = data.get('nickname', character['nickname'])
            character['role'] = data.get('role', character['role'])
            character['strength'] = data.get('strength', character['strength'])
            character['symbol'] = data.get('symbol', character['symbol'])

            sync_data(os.path.join('backend', 'characters.json'), characters)

            return jsonify({"message": f"Character with id {id} has been updated "
                                       f"successfully.", "id": id}), 200
    return jsonify({"error": f"Character with id {id} not found!"}), 404


SWAGGER_URL = "/api/docs"  # swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL = "/static/swagger_data.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'ThronesAPI'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
