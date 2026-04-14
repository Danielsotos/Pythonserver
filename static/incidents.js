let currentIncidentUser = null;

function loadIncidentUser() {
    return loadUser().then(user => {
        currentIncidentUser = user;
        renderIncidentActionsInfo();
        return user;
    });
}

function renderIncidentActionsInfo() {
    const info = document.getElementById('incident-role-info');
    if (!info || !currentIncidentUser) {
        return;
    }

    if (currentIncidentUser.role === 'admin' || currentIncidentUser.role === 'tecnico') {
        info.textContent = 'Puedes comentar incidencias y marcarlas como resueltas.';
    } else {
        info.textContent = 'Puedes revisar incidencias, pero solo técnicos y administradores pueden resolverlas.';
    }
}

function renderIncidentList() {
    const list = document.getElementById('incident-list');
    fetch('/api/incidencias')
        .then(response => response.json())
        .then(incidents => {
            if (!incidents.length) {
                list.innerHTML = '<p class="muted-text">No hay incidencias registradas.</p>';
                return;
            }

            list.innerHTML = incidents.map(incident => {
                const comments = incident.comments.length
                    ? `<div class="incident-comments">${incident.comments.map(comment => `
                        <div class="comment-item">
                            <strong>${comment.author}</strong> <span>${new Date(comment.created_at).toLocaleString()}</span>
                            <p>${comment.comment}</p>
                        </div>
                    `).join('')}</div>`
                    : '<p class="muted-text">Sin comentarios técnicos.</p>';

                const canManage = currentIncidentUser && (currentIncidentUser.role === 'admin' || currentIncidentUser.role === 'tecnico');
                const actions = canManage && incident.status === 'abierto' ? `
                    <div class="incident-actions">
                        <textarea id="comment-${incident.id}" placeholder="Comentario técnico"></textarea>
                        <div class="hero-actions left-actions">
                            <button type="button" onclick="sendIncidentComment(${incident.id})">Guardar comentario</button>
                            <button type="button" onclick="resolveIncident(${incident.id})">Marcar resuelto</button>
                        </div>
                    </div>
                ` : '';

                const resolvedInfo = incident.status === 'resuelto'
                    ? `<p class="resolved-text">Resuelto por ${incident.resolved_by || 'sin dato'}${incident.resolved_at ? ` el ${new Date(incident.resolved_at).toLocaleString()}` : ''}</p>`
                    : '';

                return `
                    <article class="incident-card">
                        <div class="incident-header">
                            <div>
                                <p class="eyebrow">${incident.section}</p>
                                <h3>Robot ${incident.robot_id}</h3>
                            </div>
                            <div class="priority-badge priority-${incident.priority}">
                                Prioridad ${incident.priority}
                            </div>
                        </div>
                        <p><strong>Error:</strong> ${incident.error_type}</p>
                        <p><strong>Reportado por:</strong> ${incident.created_by}</p>
                        <p><strong>Estado:</strong> ${incident.status}</p>
                        <p><strong>Detalle:</strong> ${incident.description || 'Sin descripción adicional'}</p>
                        ${resolvedInfo}
                        ${comments}
                        ${actions}
                    </article>
                `;
            }).join('');
        })
        .catch(error => {
            console.error(error);
            list.innerHTML = '<p class="error-text">No se pudieron cargar las incidencias.</p>';
        });
}

function sendIncidentComment(incidentId) {
    const field = document.getElementById(`comment-${incidentId}`);
    const comment = field.value.trim();
    if (!comment) {
        alert('Debes escribir un comentario');
        return;
    }

    fetch(`/api/incidencias/${incidentId}/comentarios`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment }),
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'No se pudo guardar el comentario');
            }
            return data;
        })
        .then(() => {
            renderIncidentList();
        })
        .catch(error => alert(error.message));
}

function resolveIncident(incidentId) {
    const field = document.getElementById(`comment-${incidentId}`);
    const comment = field ? field.value.trim() : '';

    fetch(`/api/incidencias/${incidentId}/resolver`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment }),
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'No se pudo resolver la incidencia');
            }
            return data;
        })
        .then(() => {
            renderIncidentList();
        })
        .catch(error => alert(error.message));
}

window.sendIncidentComment = sendIncidentComment;
window.resolveIncident = resolveIncident;

document.addEventListener('DOMContentLoaded', () => {
    loadIncidentUser().then(renderIncidentList);
});
