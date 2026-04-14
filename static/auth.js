function sendAuth(endpoint) {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const authMessage = document.getElementById('auth-message');

    if (!username || !password) {
        authMessage.innerText = 'Usuario y contraseña son obligatorios';
        authMessage.style.color = '#ffb4b4';
        return;
    }

    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Error en la autenticación');
            }
            return data;
        })
        .then(data => {
            authMessage.innerText = `${data.message}${data.role ? ` (${data.role})` : ''}`;
            authMessage.style.color = '#b8ffd1';
            if (endpoint === '/login') {
                setTimeout(() => {
                    window.location.href = '/index';
                }, 500);
            }
        })
        .catch(error => {
            authMessage.innerText = error.message;
            authMessage.style.color = '#ffb4b4';
        });
}

function login() {
    sendAuth('/login');
}

function registerUser() {
    sendAuth('/register');
}

window.login = login;
window.registerUser = registerUser;
