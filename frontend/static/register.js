// Handle registration

document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;

    fetch('http://localhost:5000/api/register', {  // Backend URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    })
    .then(response => response.json())
    .then(data => {
        // Remove any existing messages
        const existingMessage = document.querySelector('.success-message, .error-message');
        if (existingMessage) existingMessage.remove();

        if (data.message === "User registered successfully.") {
            // Create and display success message
            const successMessage = document.createElement('p');
            successMessage.textContent = "Registration successful! Redirecting to login...";
            successMessage.classList.add('success-message');  // Add class for success styling
            document.body.appendChild(successMessage);

            // Redirect to login page after a brief delay (e.g., 2 seconds)
            setTimeout(function() {
                window.location.href = '/';
            }, 2000);
        } else {
            // Create and display error message
            const errorMessage = document.createElement('p');
            errorMessage.textContent = data.message;
            errorMessage.classList.add('error-message');  // Add class for error styling
            document.body.appendChild(errorMessage);
        }
    })
    .catch(error => console.error('Error registering:', error));
});
