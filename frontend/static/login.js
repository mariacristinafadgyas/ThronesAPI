// Handle login
document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    // Send request to the correct backend URL (localhost:5000)
    fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }), // Send login credentials
    })
    .then(response => {
        // Check if the response is not OK (e.g., 404 or 500) and handle the error
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text); });
        }
        return response.json(); // Parse the response as JSON
    })
    .then(data => {
        if (data.token) {
            localStorage.setItem('token', data.token);  // Store token in localStorage
            // alert('Login successful! Redirecting to characters page...');
            window.location.href = '/characters'; // Redirect after successful login
        } else {
            alert(data.message);  // Show error message if login fails
        }
    })
    .catch(error => console.error('Error logging in:', error));  // Handle any errors
});
