from flask import Flask, render_template, jsonify, url_for, request
import requests

app = Flask(__name__, static_folder='static', template_folder='templates')

# ThronesAPI URL for character information
THRONES_API_URL = 'https://thronesapi.com/api/v2/Characters'


@app.route('/', methods=['GET'])
def login():
    """Renders the homepage."""
    return render_template("login.html")


@app.route('/registration', methods=['GET'])
def register():
    """Renders the registration page."""
    return render_template("register.html")


@app.route('/characters', methods=['GET'])
def characters():
    """Renders the characters page."""
    return render_template("characters.html")


# API route to fetch Game of Thrones characters with their pictures
@app.route('/api/characters/pictures', methods=['GET'])
def get_characters_pictures():
    """API route to fetch Game of Thrones characters images."""
    try:
        # Retrieve the token from the Authorization header of the frontend request
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        # Set up headers with the token for the backend API call
        headers = {
            'Authorization': token  # Pass token in the backend API request
        }

        # Fetch characters from local backend (characters.json)
        # local_characters = read_data(os.path.join('..', 'backend', 'characters.json'))  -> works with localhost
        res = requests.get('https://thronesapi-backend.onrender.com/api/all_characters', headers=headers)
        if res.status_code != 200:
            return jsonify({'message': 'Failed to fetch characters from backend.'}), res.status_code

        local_characters = res.json()

        # Fetch character images from external ThronesAPI
        response = requests.get(THRONES_API_URL)
        response.raise_for_status()  # Raises an error if the request fails
        external_characters = response.json()

        # Create a dictionary of external characters for quick lookup by name
        external_characters_dict = {char['fullName']: char['imageUrl'] for char in external_characters}

        # Define a default image URL for characters without an external image
        default_image_url = url_for('static', filename='GoT.jpg')

        # Combine local characters with their images from external API
        combined_characters = []
        for character in local_characters:
            character_name = character.get('name')
            # Fallback to local image if not found
            image_url = external_characters_dict.get(character_name, default_image_url)

            combined_characters.append({
                'name': character_name,
                'imageUrl': image_url
            })

        return jsonify(combined_characters), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/add_character_view', methods=['GET', 'POST'])
def add_character_view():
    return render_template('add_character_view.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)