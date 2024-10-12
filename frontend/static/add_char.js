document.getElementById('character-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    // Retrieve the token from localStorage
    const token = localStorage.getItem('token');

    // If no token is found, redirect to login page
    if (!token) {
        window.location.href = '/';  // Redirect to login if not authenticated
        return;
    }

    const formData = new FormData(this);
    const characterData = {};

    // Convert FormData to JSON and handle empty fields
    formData.forEach((value, key) => {
        characterData[key] = value.trim() === '' ? null : value; // Assign null if the field is empty
    });

    // Convert 'age' to an integer if provided
    if (characterData.age !== null) {
        characterData.age = parseInt(characterData.age, 10);
    }

    console.log('Character data being sent:', characterData); // Debugging

    // Send a POST request to the backend API
    fetch('http://localhost:5000/api/characters', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(characterData), // Convert the object to JSON
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log('Character added successfully:', data);
        alert('Character added successfully!');

        // Clear the form fields after successful submission
        document.getElementById('character-form').reset();
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        alert('Error adding character: ' + error.message);
    });
});
