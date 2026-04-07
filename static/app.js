let idInput = null;
let resultado = null;

function initializeElements() {
    idInput = document.getElementById('id');
    resultado = document.getElementById('resultado');
}

function guardarID() {
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

        const ultimoIdElement = document.getElementById('ultimo-id');
        if (lista && lista.length) {
            ultimoIdElement.innerText = 'Último ID: ' + lista[lista.length - 1].id;
            console.log('Último ID actualizado:', lista[lista.length - 1].id);
        } else {
            ultimoIdElement.innerText = 'No hay IDs registrados aún';
        }
    })
    .catch(error => {
        console.error('Error al cargar datos:', error);
        document.getElementById('ultimo-id').innerText = 'Error al cargar datos';
    });
}

function enviarID() {
    const id = idInput.value.trim();
    if (!id) return alert('ID requerido');

    fetch(location.pathname, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    })
    .then(r => r.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
        if (data.message) {
            resultado.innerHTML = '<p style="color: green;">✓ ' + data.message + '</p>';
            idInput.value = ''; // Limpiar el input
            setTimeout(() => {
                resultado.innerHTML = '';
            }, 3000); // Limpiar mensaje después de 3 segundos
        } else if (data.error) {
            resultado.innerHTML = '<p style="color: red;">✗ Error: ' + data.error + '</p>';
        }
        guardarID(); // Actualizar la lista después de guardar
    })
    .catch(console.error);
}

function volver() {
    location.href = '/';
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
                html += `<li><strong>ID:</strong> ${robot.id} - <strong>Fecha:</strong> ${fecha}</li>`;
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

document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    guardarID();
});