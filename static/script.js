document.getElementById('submitBtn').addEventListener('click', async function() {
    var password1 = document.getElementById('password1').value;
    var password2 = document.getElementById('password2').value;

    if (password1 === password2) {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token'); // Отримання токену з URL

        try {
            const response = await fetch(`/password/reset?token=${token}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ password: password1 }) // Перевірте, чи це відповідає формату FastAPI-ендпоінту
            });

            const data = await response.json();
            console.log(data);
            // Обробка відповіді сервера
        } catch (error) {
            console.error('Помилка при скиданні пароля:', error);
        }
    } else {
        document.getElementById('message').textContent = 'Паролі не співпадають!';
    }
});
