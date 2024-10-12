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

    // Fetch character details (age, animal, etc.) from the /api/characters - backend endpoint
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
                ageElement.innerHTML = `<b>Age:</b> ${details.age}`;

                // Create and set role
                const roleElement = document.createElement('p');
                roleElement.innerHTML = `<b>Role:</b> ${details.role}`;

                // Create and set house
                const houseElement = document.createElement('p');
                houseElement.innerHTML = `<b>House:</b> ${details.house}`;

                // Append the elements to the card
                characterCard.appendChild(img);
                characterCard.appendChild(name);
                characterCard.appendChild(ageElement);
                characterCard.appendChild(roleElement);
                characterCard.appendChild(houseElement);

                // Append the character card to the grid
                charactersGrid.appendChild(characterCard);
            });
        })
        .catch(error => {
            console.error('Error fetching characters:', error);
            charactersGrid.textContent = 'Error loading characters. Please try again later.';
        });
});
