import unittest
import json
from app import app
import jwt
import os
from datetime import datetime, timedelta

SECRET_KEY = os.getenv('SECRET_KEY')


def generate_token(username, role='user', secret_key=SECRET_KEY, exp_hours=1):
    """Helper function to generate JWT tokens for testing"""
    payload = {
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=exp_hours)
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')


class APITestCases(unittest.TestCase):
    def setUp(self):
        """Set up the test client and other necessary data before each test"""
        self.app = app.test_client()  # Creates a test client for the Flask app
        self.app.testing = True  # Enables testing mode for debugging info
        # Uses the generate_token function to create a JWT token for a user named 'testuser'
        self.token = generate_token('testuser')
        # Sets the authorization headers required for API requests
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def test_login_success(self):
        """Test login success with correct credentials"""
        response = self.app.post('/login', json={'username': 'maria', 'password': 'pass123#'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', data)

    def test_login_failure(self):
        """Test login failure with wrong credentials"""
        response = self.app.post('/login', json={'username': 'admin', 'password': 'wrongpassword'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['message'], 'Invalid username or password')

    def test_get_characters_no_auth(self):
        """Test unauthorized access to the get_characters endpoint"""
        response = self.app.get('/api/characters')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token is missing or invalid format', str(response.data))

    def test_get_characters_success(self):
        """Test fetching characters with valid token"""
        response = self.app.get('/api/characters', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_character_by_id_success(self):
        """Test fetching a single character by ID"""
        response = self.app.get('/api/characters/11', headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_character_by_id_not_found(self):
        """Test fetching a character by non-existent ID"""
        response = self.app.get('/api/characters/999', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Character with ID 999 not found.")

    def test_add_and_delete_character_success(self):
        """Test adding a new character with valid data"""
        new_character = {
            'name': 'John Snow',
            'age': 25,
            'animal': 'Wolf',
            'death': 'Alive',
            'house': 'Stark',
            'nickname': 'King in the North',
            'role': 'Leader',
            'strength': 'Swordsmanship',
            'symbol': 'Wolf'
        }
        response = self.app.post('/api/characters', json=new_character, headers=self.headers)
        self.assertEqual(response.status_code, 200)

        # In order not to modify the database the newly created character is deleted
        created_character = json.loads(response.data)
        character_id = created_character['id']  # Dynamically extract the id
        response = self.app.delete(f'/api/characters/{character_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], f'Character with id {character_id} has been deleted successfully.')

    def test_add_character_missing_field(self):
        """Test adding a character with missing required fields, expecting None values."""
        new_character = {
            'name': 'John Snow',
            'nickname': 'King in the North',
            'role': 'Leader',
        }
        response = self.app.post('/api/characters', json=new_character, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        # Check that the missing fields are set to None
        self.assertIsNone(data.get('age'))
        self.assertIsNone(data.get('animal'))
        self.assertIsNone(data.get('death'))
        self.assertIsNone(data.get('house'))
        self.assertIsNone(data.get('strength'))
        self.assertIsNone(data.get('symbol'))

        # In order not to modify the database the newly created character is deleted
        character_id = data['id']  # Dynamically extract the id
        response = self.app.delete(f'/api/characters/{character_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], f'Character with id {character_id} has been deleted successfully.')

    def test_add_character_invalid_data_type(self):
        """Test adding a character with invalid data type"""
        new_character = {
            'name': 'Arya Stark',
            'age': 'invalid_age',  # Invalid age data type
            'animal': 'Wolf',
            'death': 'Alive',
            'house': 'Stark',
            'nickname': 'No One',
            'role': 'Assassin',
            'strength': 'Stealth',
            'symbol': 'Direwolf'
        }
        response = self.app.post('/api/characters', json=new_character, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("must be of type int", data['error'])

    def test_update_character_success(self):
        """Test updating a character's details"""

        # Create a character
        new_character = {
            'name': 'Jon Snow',
            'age': 29,
            'death': 'Alive',
            'house': 'Stark',
            'nickname': 'King in the North',
            'role': 'Leader',
            'strength': 'Bravery',
            'symbol': 'Wolf'
        }
        create_response = self.app.post('/api/characters', json=new_character, headers=self.headers)
        self.assertEqual(create_response.status_code, 200)

        created_character = json.loads(create_response.data)
        character_id = created_character['id']  # Dynamically extract the id

        # Update the newly created character
        update_data = {
            'name': 'Jon Snow Updated',
            'age': 30
        }

        response = self.app.put(f'/api/characters/{character_id}', json=update_data, headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn(f"Character with id {character_id} has been updated successfully", data['message'])

        # In order not to modify the database the newly created character is deleted
        response = self.app.delete(f'/api/characters/{character_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], f'Character with id {character_id} has been deleted successfully.')

    def test_delete_character_not_found(self):
        """Test deleting a character that does not exist"""
        response = self.app.delete('/api/characters/999', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Character with id 999 not found.')

    def test_pagination_success(self):
        """Test paginated character fetching"""
        response = self.app.get('/api/characters?limit=5&skip=0', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 5)  # Expecting 5 characters in the response

    def test_sort_ascending(self):
        """Test sorting characters in ascending order by age"""
        response = self.app.get('/api/characters?sort_asc=age', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data[0]['age'] <= data[1]['age'])

    def test_invalid_sort_attribute(self):
        """Test sorting by an invalid attribute"""
        response = self.app.get('/api/characters?sort_asc=invalid_field', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("To sort please select one of these attributes: 'age' / "
                      "'animal' / 'death' / 'house' / 'id' / 'name' / 'nickname' / 'role' "
                      "/ 'strength' / 'symbol'", data['error'])


if __name__ == '__main__':
    unittest.main()
