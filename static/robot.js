let idInput = null;
let commentInput = null;
let resultBox = null;
let robotListBox = null;
let lastIdBox = null;
let modal = null;
let modalRobotId = null;
let incidentType = null;
let incidentPriority = null;
let incidentDescription = null;
let currentPath = '';

function sectionKey() {
    return currentPath === '/SBS' ? 'robotsSBS' : 'robotsFLR';
}

function sectionName() {
    return currentPath === '/SBS' ? 'robotsSBS' : 'robotsFLR';
}

function bindRobotElements() {
    currentPath = location.pathname.replace(/\/$/, '');
    idInput = document.getElementById('id');
    commentInput = document.getElementById('comment');
    resultBox = document.getElementById('resultado');
    robotListBox = document.getElementById('lista-robots');
    lastIdBox = document.getElementById('ultimo-id');
    modal = document.getElementById('incident-modal');
    modalRobotId = document.getElementById('incident-robot-id');
    incidentType = document.getElementById('incident-type');
    incidentPriority = document.getElementById('incident-priority');
    incidentDescription = document.getElementById('incident-description');
}

function updatePriorityByType() {
    if (!incidentType || !incidentPriority) {
        return;
    }

    const fixed = {
        'LIDAR': 1,
        'Choque': 1,
        'Parada de emergencia': 3,
    };

    if (fixed[incidentType.value]) {
        incidentPriority.value = fixed[incidentType.value];
        incidentPriority.disabled = true;
    } else {
        incidentPriority.disabled = false;
    }
}

function fetchRobots() {
    return fetch('/datos')
        .then(response => response.json())
        .then(data => data[sectionKey()] || []);
}

function refreshLastRobot() {
    if (!lastIdBox) {
        return;
    }

    fetchRobots()
        .then(robots => {
            if (!robots.length) {
                lastIdBox.innerText = 'No hay IDs registrados aún';
                return;
            }
            lastIdBox.innerText = `Último ID: ${robots[0].id}`;
        })
        .catch(error => {
            console.error(error);
            lastIdBox.innerText = 'Error al cargar datos';
        });
}

function submitRobot() {
    const id = idInput.value.trim();
    const comment = commentInput.value.trim();

    if (!id) {
        alert('ID requerido');
        return;
    }

    fetch(currentPath, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, comment }),
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'No se pudo guardar el robot');
            }
            return data;
        })
        .then(data => {
            resultBox.innerHTML = `<p class="success-text">Registro guardado por ${data.created_by}</p>`;
            idInput.value = '';
            commentInput.value = '';
            refreshLastRobot();
            renderRobotList();
        })
        .catch(error => {
            resultBox.innerHTML = `<p class="error-text">${error.message}</p>`;
        });
}

function renderRobotList() {
    if (!robotListBox) {
        return;
    }

    fetchRobots()
        .then(robots => {
            if (!robots.length) {
                robotListBox.style.display = 'block';
                robotListBox.innerHTML = '<p class="muted-text">No hay robots registrados aún.</p>';
                return;
            }

            const items = robots.map(robot => {
                const date = new Date(robot.timestamp).toLocaleString();
                const comment = robot.comment ? `<div class="robot-meta"><strong>Comentario:</strong> ${robot.comment}</div>` : '';
                return `
                    <li>
                        <div class="robot-row">
                            <div>
                                <div><strong>ID:</strong> ${robot.id}</div>
                                <div class="robot-meta"><strong>Usuario:</strong> ${robot.created_by}</div>
                                <div class="robot-meta"><strong>Fecha:</strong> ${date}</div>
                                ${comment}
                            </div>
                            <button type="button" onclick="openIncidentModal('${robot.id}')">Reportar error</button>
                        </div>
                    </li>
                `;
            }).join('');

            robotListBox.innerHTML = `<h3>Robots registrados</h3><ul>${items}</ul>`;
            robotListBox.style.display = 'block';
        })
        .catch(error => {
            console.error(error);
            robotListBox.style.display = 'block';
            robotListBox.innerHTML = '<p class="error-text">No fue posible cargar la lista.</p>';
        });
}

function toggleRobotList() {
    if (robotListBox.style.display === 'block') {
        robotListBox.style.display = 'none';
        return;
    }
    renderRobotList();
}

function openIncidentModal(robotId) {
    modalRobotId.value = robotId;
    incidentType.value = 'LIDAR';
    incidentDescription.value = '';
    updatePriorityByType();
    modal.hidden = false;
}

function closeIncidentModal() {
    modal.hidden = true;
}

function submitIncident() {
    const payload = {
        section: sectionName(),
        robot_id: modalRobotId.value.trim(),
        error_type: incidentType.value,
        priority: Number(incidentPriority.value),
        description: incidentDescription.value.trim(),
    };

    fetch('/api/incidencias', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'No fue posible registrar la incidencia');
            }
            return data;
        })
        .then(() => {
            resultBox.innerHTML = '<p class="success-text">Incidencia registrada correctamente</p>';
            closeIncidentModal();
        })
        .catch(error => {
            resultBox.innerHTML = `<p class="error-text">${error.message}</p>`;
        });
}

window.submitRobot = submitRobot;
window.toggleRobotList = toggleRobotList;
window.openIncidentModal = openIncidentModal;
window.closeIncidentModal = closeIncidentModal;
window.submitIncident = submitIncident;
window.updatePriorityByType = updatePriorityByType;

document.addEventListener('DOMContentLoaded', () => {
    bindRobotElements();
    loadUser();
    refreshLastRobot();
    updatePriorityByType();
});
