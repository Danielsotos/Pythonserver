let idInput = null;
let commentInput = null;
let resultado = null;
let currentUser = null;

function initializeElements() {
    idInput = document.getElementById('id');
    commentInput = document.getElementById('comment');
    resultado = document.getElementById('resultado');
}

function cargarUsuario() {
    fetch('/me')
    .then(r => {
        if (!r.ok) {
            throw new Error('No autenticado');
        }
        return r.json();
    })
    .then(data => {
        currentUser = data.username;
        const userBadge = document.getElementById('current-user');
        if (userBadge) {
            userBadge.innerText = `Sesión activa: ${currentUser}`;
        }
    })
    .catch(() => {
        window.location.href = '/login';
    });
}

function guardarID() {
    const ultimoIdElement = document.getElementById('ultimo-id');
    if (!ultimoIdElement) {
        return;
    }

    fetch('/datos')
    .then(r => r.json())
    .then(d => {
        const rutas = {
            '/FLR': 'robotsFLR',
            '/SBS': 'robotsSBS',
            '/ABC': 'robotsABC'
        };

        const path = location.pathname.replace(/\/$/, '');
        const key = rutas[path] || 'robotsFLR';
        const lista = d[key];

        if (lista && lista.length) {
            ultimoIdElement.innerText = 'Último ID: ' + lista[lista.length - 1].id;
            console.log('Último ID actualizado:', lista[lista.length - 1].id);
        } else {
            ultimoIdElement.innerText = 'No hay IDs registrados aún';
        }
    })
    .catch(error => {
        console.error('Error al cargar datos:', error);
        ultimoIdElement.innerText = 'Error al cargar datos';
    });
}

function enviarID() {
    if (!idInput || !resultado) {
        return;
    }

    const id = idInput.value.trim();
    const comment = commentInput ? commentInput.value.trim() : '';
    if (!id) return alert('ID requerido');

    fetch(location.pathname, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id, comment: comment })
    })
    .then(r => r.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
        if (data.message) {
            resultado.innerHTML = `<p style="color: green;">✓ ${data.message}. Registrado por ${data.created_by}</p>`;
            idInput.value = '';
            if (commentInput) {
                commentInput.value = '';
            }
            setTimeout(() => {
                resultado.innerHTML = '';
            }, 3000);
        } else if (data.error) {
            resultado.innerHTML = '<p style="color: red;">✗ Error: ' + data.error + '</p>';
        }
        guardarID();
    })
    .catch(console.error);
}

function volver() {
    location.href = '/index';
}

function logout() {
    fetch('/logout', { method: 'POST' })
    .then(() => {
        window.location.href = '/login';
    })
    .catch(console.error);
}

function mostrarLista() {
    const listaDiv = document.getElementById('lista-robots');
    
    // Si la lista ya está visible, ocultarla
    if (listaDiv.style.display === 'block') {
        listaDiv.style.display = 'none';
        return;
    }
    
    fetch('/datos')
    .then(r => r.json())
    .then(d => {
        const rutas = {
            '/FLR': 'robotsFLR',
            '/SBS': 'robotsSBS',
            '/ABC': 'robotsABC'
        };

        const path = location.pathname.replace(/\/$/, '');
        const key = rutas[path] || 'robotsFLR';
        const robots = d[key] || [];
        const tipoRobot = path === '/FLR' ? 'FLR' : path === '/SBS' ? 'SBS' : 'FLR';
        
        if (robots.length === 0) {
            listaDiv.innerHTML = `<p style="color: #666;">No hay robots ${tipoRobot} registrados aún.</p>`;
        } else {
            let html = `<h3>Lista de Robots ${tipoRobot}:</h3><ul style="text-align: left; display: inline-block;">`;
            robots.forEach((robot, index) => {
                const fecha = new Date(robot.timestamp).toLocaleString();
                const comment = robot.comment ? ` - <strong>Comentario:</strong> ${robot.comment}` : '';
                html += `<li><strong>ID:</strong> ${robot.id} - <strong>Usuario:</strong> ${robot.created_by} - <strong>Fecha:</strong> ${fecha}${comment}</li>`;
            });
            html += '</ul>';
            listaDiv.innerHTML = html;
        }
        
        listaDiv.style.display = 'block';
        console.log(`Lista de robots ${tipoRobot} mostrada:`, robots.length, 'robots');
    })
    .catch(error => {
        console.error('Error al cargar lista:', error);
        listaDiv.innerHTML = '<p style="color: red;">Error al cargar la lista de robots.</p>';
        listaDiv.style.display = 'block';
    });
}

window.enviarID = enviarID;
window.volver = volver;
window.mostrarLista = mostrarLista;
window.logout = logout;

document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    cargarUsuario();
    if (document.getElementById('ultimo-id')) {
        guardarID();
    }
});
