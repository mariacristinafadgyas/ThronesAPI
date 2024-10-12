document.addEventListener('DOMContentLoaded', () => {
    const charactersGrid = document.getElementById('charactersGrid');

    // Retrieve the token from localStorage
    const token = localStorage.getItem('token');

    // If no token is found, redirect to login page
    if (!token) {
        window.location.href = '/';  // Redirect to login if not authenticated
        return;
    }

    // Set up the headers with the Authorization token
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };

    // Function to handle unauthorized access and redirect to login
    const handleUnauthorized = (response) => {
        if (response.status === 401) {
            // Token is expired, missing, or invalid, redirect to login
            localStorage.removeItem('token');  // Remove the token from localStorage
            window.location.href = '/';  // Redirect to the login page
            throw new Error('Unauthorized - Token is invalid or expired');
        }
        return response;  // Return the response if it’s not unauthorized
    };

    // Fetch character pictures from the /api/characters/pictures endpoint
    const fetchCharacterPictures = fetch('http://localhost:5001/api/characters/pictures')
    .then(handleUnauthorized)  // Handle expired/invalid token
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    });

    // Fetch character details (age, animal, etc.) from the /api/all_characters - backend endpoint
    const fetchCharacterDetails = fetch('http://localhost:5000/api/all_characters', {
        headers: headers  // Include the token in the request headers
    })
    .then(handleUnauthorized)  // Handle expired/invalid token
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    });

    // Combine the data from both APIs
    Promise.all([fetchCharacterPictures, fetchCharacterDetails])
        .then(([picturesData, detailsData]) => {
            // Create a dictionary from the character details for quick lookup by name
            const detailsDict = detailsData.reduce((acc, character) => {
                acc[character.name] = {
                    id: character.id,  // Include character ID for deletion
                    age: character.age,
                    role: character.role,
                    house: character.house
                };
                return acc;
            }, {});

            // For each character in the pictures data, create an element to display their details
            picturesData.forEach(character => {
                const characterCard = document.createElement('div');
                characterCard.classList.add('character-card');

                // Create and set image
                const img = document.createElement('img');
                img.src = character.imageUrl || 'static/default.jpg';
                img.alt = `${character.name}'s Image`;
                img.classList.add('character-image');

                // Create and set name
                const name = document.createElement('p');
                name.innerHTML = `<b>Name:</b> <span>${character.name}</span>`;

                // Get character details (age, role, house, etc.) from the dictionary, fallback to 'Unknown' or 'None' if not available
                const details = detailsDict[character.name] || {};

                // Create and set age
                const ageElement = document.createElement('p');
                ageElement.innerHTML = `<b>Age:</b> ${details.age || 'Unknown'}`;

                // Create and set role
                const roleElement = document.createElement('p');
                roleElement.innerHTML = `<b>Role:</b> ${details.role || 'Unknown'}`;

                // Create and set house
                const houseElement = document.createElement('p');
                houseElement.innerHTML = `<b>House:</b> ${details.house || 'Unknown'}`;

                // Create edit button form
                const editForm = document.createElement('form');
                editForm.classList.add('edit-form');

                const editButton = document.createElement('button');
                editButton.classList.add('btn', 'btn-primary');
                editButton.innerHTML = `<i class="fa fa-pencil" aria-hidden="true"></i>`;

                editButton.onclick = () => {
                    const newName = prompt('Enter new name:', character.name);
                    const newAge = prompt('Enter new age:', details.age);
                    const newRole = prompt('Enter new role:', details.role);
                    const newHouse = prompt('Enter new house:', details.house);

                    const updatedCharacter = {
                        name: newName || character.name,
                        age: parseInt(newAge) || details.age,
                        role: newRole || details.role,
                        house: newHouse || details.house
                    };

                    fetch(`http://localhost:5000/api/characters/${details.id}`, {
                        method: 'PUT',
                        headers: headers,
                        body: JSON.stringify(updatedCharacter)
                    })
                        .then(handleUnauthorized)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`Failed to update character. Status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            alert(data.message);
                            name.innerHTML = `<b>Name:</b> <span>${updatedCharacter.name}</span>`;
                            ageElement.innerHTML = `<b>Age:</b> ${updatedCharacter.age}`;
                            roleElement.innerHTML = `<b>Role:</b> ${updatedCharacter.role}`;
                            houseElement.innerHTML = `<b>House:</b> ${updatedCharacter.house}`;
                        })
                        .catch(error => {
                            console.error('Error updating character:', error);
                            alert('Failed to update character. Please try again.');
                        });
                };

                // Create delete button form
                const deleteForm = document.createElement('form');
                deleteForm.setAttribute('action', `http://localhost:5000/api/characters/${details.id}`);
                deleteForm.setAttribute('method', 'DELETE');
                deleteForm.classList.add('delete-form');

                const deleteButton = document.createElement('button');
                deleteButton.classList.add('btn', 'btn-danger');
                deleteButton.innerHTML = `<i class="fa fa-trash" aria-hidden="true"></i>`;

                deleteButton.onclick = (event) => {
                    event.preventDefault();  // Prevent default form submission
                    const confirmed = confirm('Are you sure you want to delete this character?');
                    if (confirmed) {
                        fetch(deleteForm.action, {
                            method: 'DELETE',
                            headers: headers  // Pass token in headers
                        })
                        .then(handleUnauthorized)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`Failed to delete character. Status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            alert(data.message);  // Show success message
                            characterCard.remove();  // Remove card from grid
                        })
                        .catch(error => {
                            console.error('Error deleting character:', error);
                            alert('Failed to delete character. Please try again.');
                        });
                    }
                };

                // Create a button group container for edit and delete buttons
                const buttonGroup = document.createElement('div');
                buttonGroup.classList.add('button-group');

                // Append delete and edit button to the group
                buttonGroup.appendChild(editButton);
                buttonGroup.appendChild(deleteButton);

                // Append the elements to the card
                characterCard.appendChild(img);
                characterCard.appendChild(name);
                characterCard.appendChild(ageElement);
                characterCard.appendChild(roleElement);
                characterCard.appendChild(houseElement);
                characterCard.appendChild(buttonGroup);

                // Append the character card to the grid
                charactersGrid.appendChild(characterCard);
            });
        })
        .catch(error => {
            console.error('Error fetching characters:', error);
            charactersGrid.textContent = 'Error loading characters. Please try again later.';
        });
});
