function loadAdmin() {
    return loadUser().then(user => {
        if (user.role !== 'admin') {
            window.location.href = '/index';
            return;
        }
        loadUsers();
    });
}

function loadUsers() {
    const list = document.getElementById('user-list');
    fetch('/api/usuarios')
        .then(response => response.json())
        .then(data => {
            list.innerHTML = data.users.map(user => `
                <li>
                    <div class="user-row">
                        <div>
                            <strong>${user.username}</strong>
                            <div class="robot-meta">Rol actual: ${user.role}</div>
                        </div>
                        <div class="user-actions">
                            <select id="role-${user.username}">
                                <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>admin</option>
                                <option value="tecnico" ${user.role === 'tecnico' ? 'selected' : ''}>tecnico</option>
                                <option value="operador" ${user.role === 'operador' ? 'selected' : ''}>operador</option>
                            </select>
                            <button type="button" onclick="updateRole('${user.username}')">Cambiar rol</button>
                            <button type="button" class="danger-button" onclick="deleteUser('${user.username}')">Eliminar</button>
                        </div>
                    </div>
                </li>
            `).join('');
        })
        .catch(error => {
            console.error(error);
            list.innerHTML = '<li class="error-text">No fue posible cargar usuarios.</li>';
        });
}

function createAdminUser() {
    const username = document.getElementById('new-username').value.trim();
    const password = document.getElementById('new-password').value.trim();
    const role = document.getElementById('new-role').value;
    const box = document.getElementById('admin-message');

    fetch('/api/usuarios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, role }),
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'No fue posible crear el usuario');
            }
            return data;
        })
        .then(data => {
            box.textContent = data.message;
            box.className = 'success-text';
            document.getElementById('new-username').value = '';
            document.getElementById('new-password').value = '';
            loadUsers();
        })
        .catch(error => {
            box.textContent = error.message;
            box.className = 'error-text';
        });
}

function updateRole(username) {
    const role = document.getElementById(`role-${username}`).value;
    fetch(`/api/usuarios/${username}/role`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role }),
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'No fue posible actualizar el rol');
            }
            return data;
        })
        .then(() => loadUsers())
        .catch(error => alert(error.message));
}

function deleteUser(username) {
    if (!confirm(`¿Eliminar a ${username}?`)) {
        return;
    }

    fetch(`/api/usuarios/${username}`, { method: 'DELETE' })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'No fue posible eliminar el usuario');
            }
            return data;
        })
        .then(() => loadUsers())
        .catch(error => alert(error.message));
}

window.createAdminUser = createAdminUser;
window.updateRole = updateRole;
window.deleteUser = deleteUser;

document.addEventListener('DOMContentLoaded', () => {
    loadAdmin();
});
