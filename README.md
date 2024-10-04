# ThronesAPI

This project is a Flask-based **REST API** for managing a collection of characters from the Game of Thrones universe. The API allows users to create, retrieve, update, and delete (**CRUD**) character records while supporting filtering, sorting, and pagination for more efficient data handling. The API also implements **JWT-based authentication**, ensuring that only authenticated users can interact with the data.

## Features
1. **JWT Authentication**:

- Protected routes require a valid JWT token in the request header.
- Tokens are generated during login and are valid for 1 hour.
- 
2. **CRUD Operations**:

- **Create**: Add new characters to the database.
- **Read**: Retrieve characters with optional filtering, sorting, and pagination.
- **Update**: Modify existing character details.
- **Delete**: Remove characters by their ID.

3. **Filtering and Sorting**: 

- You can filter characters based on various attributes like age, house, and role.
- Sorting can be done on multiple fields, both in ascending and descending order.

4. **Pagination**:

- Control the number of characters returned using the limit and skip query parameters.

## Installation and Setup
1. *Clone the repository*
```
git clone https://github.com/mariacristinafadgyas/ThronesAPI
```
```
cd ThronesAPI
```
2. *Install dependencies*
```
pip install -r requirements.txt
```
3. *Set up the environment variables* <br>
Create a `.env` file in the root directory and add the following:
```
SECRET_KEY="your_secret_key_here"
```
> 🛎️ **NOTE** 🛎️ <br>
> - The environment variable, SECRET_KEY, is used for signing JWT tokens. This key must be set in the `.env` file.<br>
> - Tokens expire after 1 hour, after which the user must log in again
4. *Run the application*
```
python app.py
```
> 🛎️ **IMPORTANT** 🛎️ <br>
> The API will run on http://localhost:5000.
5. *Run tests*  <br>
Unit tests are included in this project to verify that the API works as expected.
```
pytest test_api.py 
```
or 
```
python -m unittest discover
```

## API Endpoints
1. **Login**
- Endpoint: **/login**
- Method: **POST**
- Description: Authenticates a user and returns a JWT token.
- Postman example:
```
localhost:5000/login
```
- Request Body:
```
{
  "username": "jane",
  "password": "pass456#"
}
```
- Response: 
```
{
  "token": "your_jwt_token_here"
}
```
2. **Get All Characters**
- Endpoint: **/api/characters**
- Method: **GET**
- Description: Retrieves all characters with optional filtering, sorting, and pagination.
- Query Parameters (optional):
    - `limit`: Limits the number of results (default is 20).
    - `skip`: Skips a number of records (for pagination).
    - `name, age, animal, death, house, nickname, role, strength, symbol`: Filters based on character attributes. 
    - `sort_asc`: Sort results in ascending order by a specified attribute.
    - `sort_desc`: Sort results in descending order by a specified attribute.
- Postman example:<br>
*Headers*:
*Authorization*: `Bearer your_jwt_token_here`<br>
You can replace your_jwt_token_here with the actual JWT token you receive from the /login endpoint.
```
localhost:5000/api/characters?limit=5&skip=10&sort_asc=age&house=Stark
```
3. **Get Character by ID**
- Endpoint: **/api/characters/<int:character_id>**
- Method: **GET**
- Description: Retrieves a character by their ID.
- Postman example: 
- *Headers*:
*Authorization*: `Bearer your_jwt_token_here`<br>
```
localhost:5000/api/characters/50
```
4. **Add a New Character**
- Endpoint: **/api/characters**
- Method: **POST**
- Description: Adds a new character to the list.
- - Postman example:
```
localhost:5000/api/characters
```
- Request Body:
```
{
  "name": "Arya Stark",
  "age": 18,
  "animal": "Direwolf",
  "house": "Stark",
  "nickname": "No One",
  "role": "Assassin",
  "strength": "Bravery",
  "symbol": "Sword"
}
```
- Response: 
```
{
  "id": 51,
  "name": "Arya Stark",
  "age": 18,
  ...
}
```
5. **Update a Character**
- Endpoint: /api/characters/<int:id>
- Method: **PUT**
- Description: Adds a new character to the list.
- - Postman example:
```
localhost:5000/api/characters/51
```
- Request Body:
```
{
  "name": "Jon Snow Updated",
  "age": 30
}
```
- Response: 
```
{
  "message": "Character with id 51 has been updated successfully.",
  "id": 1
}
```
6. **Delete a Character**
- Endpoint: **/api/characters/<int:id>**
- Method: **DELETE**
- Description: Deletes a character by their ID.
- - Postman example:
```
localhost:5000/api/characters/51
```
- Response: 
```
{
  "message": "Character with id 51 has been deleted successfully."
}
```
## API Documentation with Swagger
This project employs **Swagger** to offer interactive API documentation, facilitating easy visualization and testing of the API endpoints.

### Accessing the Swagger UI
- Once the application is running, you can access the Swagger UI at the following URL:
```
localhost:5000/api/docs/#
```
- **Login Requirement**: Before accessing most of the endpoints, you must first log in to obtain a JWT token.
  - To log in, expand the User Login endpoint.
  - Provide your username and password, then click the `Try it out` button to execute the request. If successful, you will receive a JWT token in the response.
- **Using the Token**: 
  - After obtaining the token, copy the token provided in the response. 
  - For subsequent API requests, paste the token into the **Authorization** header in the format: `Bearer {your_token}`
- Click on an endpoint to expand its details, fill in the required parameters, and click the `Try it out` button to execute the request.

## Data Storage
- `users.json`: Stores user data (username, password, and roles).
- `characters.json`: Stores character data from Game of Thrones (id, name, age, house, etc.).
Both files are read from and written to using read_data() and sync_data() helper functions.

> 🧸️ **NOTE** 🧸 <br>
> Contributions are welcome! Feel free to submit issues or pull requests.