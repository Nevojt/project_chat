document.getElementById('submitBtn').addEventListener('click', async function() {
    var password1 = document.getElementById('password1').value;
    var password2 = document.getElementById('password2').value;
    if (!isValidPassword(password1)) {
        document.getElementById('message').textContent = 'The password must be between 4 and 8 characters long, contain at least one uppercase letter, one number, and one special character.';
        return;
    }
    if (password1 !== password2) {
        document.getElementById('message').textContent = 'Passwords do not match!';
        return;
    }
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token'); // Отримання токену з URL
    try {
        const response = await fetch(`/password/reset?token=${token}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password: password1 })
        });
        const data = await response.json();
        if (response.ok) {
            // Успішне скидання пароля
            window.location.href = '/success-page'; // Перенаправлення на сторінку успіху
        } else {
            console.error('Error resetting password:', data);
            document.getElementById('message').textContent = 'Error resetting password';
        }
    } catch (error) {
        console.error('Error resetting password:', error);
        document.getElementById('message').textContent = 'Error resetting password';
    }
});
function isValidPassword(password) {
    var passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=!?]).{4,8}$/;
    return passwordRegex.test(password);
}

function togglePassword(inputId) {
    var passwordInput = document.getElementById(inputId);
    var toggleIcon = document.querySelector('.toggle-' + inputId);
    var toggleIconSlash = document.querySelector('.toggle-' + inputId + '-slash');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        if (toggleIcon) toggleIcon.style.display = 'none';
        if (toggleIconSlash) toggleIconSlash.style.display = 'block';
    } else {
        passwordInput.type = 'password';
        if (toggleIcon) toggleIcon.style.display = 'block';
        if (toggleIconSlash) toggleIconSlash.style.display = 'none';
    }
}