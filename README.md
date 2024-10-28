# ThronesAPI

This project is a Flask-based **REST API** for managing a collection of characters from the Game of Thrones universe. The API allows users to create, retrieve, update, and delete (**CRUD**) character records while supporting filtering, sorting, and pagination for more efficient data handling. The API also implements **JWT-based authentication**, ensuring that only authenticated users can interact with the data.

## Features
1. **JWT Authentication**:

- Protected routes require a valid JWT token in the request header.
- Tokens are generated during login and are valid for 1 hour.

2. **CRUD Operations**:

- **Create**: Add new characters to the database.
- **Read**: Retrieve characters with optional filtering, sorting, and pagination.
- **Update**: Modify existing character details by their ID.
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
1. **Register a New User**
- Endpoint: **/api/register**
- Method: **POST**
- Description:  Registers a new user by adding their username and password to the `users.json` file. Each new user is assigned the default role of "user."
- Postman example:
```
localhost:5000/api/register
```
- Request Body:
```
{
  "username": "new_user",
  "password": "password123"
}
```
- Response:
  - If successful:
```
{
  "message": "User registered successfully."
}
```
  - If the username already exists:
```
{
   "message": "Username already exists."
}
```
  - If username or password is missing:
```
{
   "message": "Username and password are required."
}
```
2. **Login**
- Endpoint: **/api/login**
- Method: **POST**
- Description: Authenticates a user and returns a JWT token.
- Postman example:
```
localhost:5000/api/login
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
3. **Get Characters**
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
4. **Get Character by ID**
- Endpoint: **/api/characters/<int:character_id>**
- Method: **GET**
- Description: Retrieves a character by their ID.
- Postman example: 
- *Headers*:
*Authorization*: `Bearer your_jwt_token_here`<br>
```
localhost:5000/api/characters/50
```
5. **Add a New Character**
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
6. **Update a Character**
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
7. **Delete a Character**
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

### Accessing Swagger UI Without Running the App
You can view the Swagger documentation directly, without needing to run the app, by visiting:
```
https://thronesapi-backend.onrender.com/api/docs/#/
```
> 🛎️ **NOTE** 🛎️ <br>
> The app is hosted on a free Render account, so it may experience delays of up to 50 seconds or more due to spin-down after periods of inactivity.
## Data Storage
- `users.json`: Stores user data (username, password, and roles).
- `characters.json`: Stores character data from Game of Thrones (id, name, age, house, etc.).
Both files are read from and written to using read_data() and sync_data() helper functions.

## Frontend Features

### User Registration 
Users can create an account by providing a username and password. Upon successful registration, users can log in to access character management features.

### User Login 
The application allows users to log in using their credentials. Upon successful login, a JWT token is generated, enabling access to protected API routes.

### Character Management
- **Display Characters**: All characters are displayed on the characters page, showcasing their details and associated images.
- **Add Character**: Users can add new characters to the database through the add character view, with input validation handled via JavaScript.
- **Edit Character**: Logged-in users can edit existing character cards directly from the character management page. Changes are saved to the database (JSON file) upon submission.
- **Delete Character**: Users have the ability to delete characters from the database. This action removes the character record from the JSON file, ensuring data consistency.

### Installation and Running the Frontend
1. Ensure that the backend is running on [http://localhost:5000](http://localhost:5000).
2. Navigate to the `/frontend` directory.
3. Start the Flask server by running:
```
python frontend_app.py
```
### User Access
Access the frontend application in your browser at:
```
http://localhost:5001/
```
## Live Deployments
The application has been deployed on `Render`, with separate services for the backend and frontend. You can access both live sites at the following URLs:

- **Frontend** (Character Management UI): <br>
https://thronesapi-frontend.onrender.com/ <br>
This is where users can register, log in, view, edit, and delete Game of Thrones characters.

- **Backend** (API for Characters and Users): <br>
https://thronesapi-backend.onrender.com/api/all_characters <br>
This serves the API routes, including character management and authentication.
> 🧸️ **NOTE** 🧸 <br>
> Contributions are welcome! Feel free to submit issues or pull requests.