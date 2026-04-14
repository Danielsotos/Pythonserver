let currentUser = null;

function logout() {
    fetch('/logout', { method: 'POST' })
        .then(() => {
            window.location.href = '/login';
        })
        .catch(console.error);
}

function loadUser() {
    return fetch('/me')
        .then(response => {
            if (!response.ok) {
                throw new Error('No autenticado');
            }
            return response.json();
        })
        .then(user => {
            currentUser = user;
            const userBadge = document.getElementById('current-user');
            if (userBadge) {
                userBadge.textContent = `Sesión activa: ${user.username} (${user.role})`;
            }

            const adminLink = document.getElementById('admin-link');
            if (adminLink && user.role === 'admin') {
                adminLink.hidden = false;
            }

            const technicianLink = document.getElementById('incident-link');
            if (technicianLink) {
                technicianLink.hidden = false;
            }

            return user;
        })
        .catch(() => {
            window.location.href = '/login';
        });
}

window.logout = logout;
window.loadUser = loadUser;

document.addEventListener('DOMContentLoaded', () => {
    loadUser();
});
