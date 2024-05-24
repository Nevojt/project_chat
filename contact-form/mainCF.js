
document.getElementById('contactForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let valid = true;

    // Clear previous error messages
    document.querySelectorAll('.error-message').forEach(function(error) {
        error.textContent = '';
    });

    // Form validation
    if (!document.getElementById('name').value.trim()) {
        document.getElementById('name-error').textContent = 'Name is required.';
        valid = false;
    }

    if (!document.getElementById('email').value.trim()) {
        document.getElementById('email-error').textContent = 'Email is required.';
        valid = false;
    }

    if (!document.getElementById('subject').value.trim()) {
        document.getElementById('subject-error').textContent = 'Subject is required.';
        valid = false;
    }

    if (!document.getElementById('message').value.trim()) {
        document.getElementById('message-error').textContent = 'Message is required.';
        valid = false;
    }

    // Submit form data if valid
    if (valid) {
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            subject: document.getElementById('subject').value,
            message: document.getElementById('message').value
        };

        fetch('/submit-form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.text())
        .then(data => {
            alert(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});



