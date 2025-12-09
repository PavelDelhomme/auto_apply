/**
 * JavaScript pour la page Personas
 */

let allPersonas = {};
let selectedPersonas = new Set();
let currentPersonaKey = null;
let showingBaseOnly = false;
let personaSearchFilter = '';
let currentPersonasPage = 1;
let personasPerPage = 12;

// Cache pour les CVs et emails
let personasCVs = {};
let personasEmails = {};

// Charger les personas au démarrage
document.addEventListener('DOMContentLoaded', () => {
    loadAllPersonas();
});

// Fonction pour afficher un loader avec progression
function showPersonasLoader(message = 'Chargement des personas...', progress = 0, current = 0, total = 0) {
    const container = document.getElementById('personasList');
    if (!container) return;
    
    const percentage = total > 0 ? Math.round((current / total) * 100) : 0;
    const remaining = total > 0 ? total - current : 0;
    
    container.innerHTML = `
        <div style="text-align: center; padding: 60px 20px; color: var(--text-secondary);">
            <div style="font-size: 3em; margin-bottom: 15px; animation: pulse 2s infinite;">⏳</div>
            <p style="font-size: 1.1em; color: var(--text-primary); font-weight: 600; margin-bottom: 20px;">${message}</p>
            
            ${total > 0 ? `
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 0.9em; color: var(--text-secondary);">
                        <span>Progression</span>
                        <span style="font-weight: 700; color: var(--text-title);">${percentage}%</span>
                    </div>
                    <div style="width: 100%; max-width: 500px; margin: 0 auto; height: 24px; background: var(--border-color); border-radius: 12px; overflow: hidden; position: relative; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="
                            width: ${percentage}%;
                            height: 100%;
                            background: linear-gradient(90deg, var(--text-title) 0%, #5b21b6 100%);
                            border-radius: 12px;
                            transition: width 0.3s ease;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                        ">
                            ${percentage > 10 ? `<span style="color: white; font-size: 0.75em; font-weight: 700;">${percentage}%</span>` : ''}
                        </div>
                    </div>
                    <div style="margin-top: 12px; font-size: 0.85em; color: var(--text-secondary);">
                        <span style="color: var(--text-primary); font-weight: 600;">${current}</span> / <span style="color: var(--text-primary); font-weight: 600;">${total}</span> personas chargés
                        ${remaining > 0 ? `<span style="margin-left: 10px; color: var(--warning);">(${remaining} restant${remaining > 1 ? 's' : ''})</span>` : ''}
                    </div>
                </div>
            ` : ''}
            
            <div style="margin-top: 20px;">
                <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid var(--border-color); border-top-color: var(--text-title); border-radius: 50%; animation: spin 1s linear infinite;"></div>
            </div>
        </div>
    `;
}

// Ajouter les animations CSS si elles n'existent pas
if (!document.getElementById('loader-styles')) {
    const style = document.createElement('style');
    style.id = 'loader-styles';
    style.textContent = `
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}

async function loadPersonaCV(personaEmail) {
    if (personasCVs[personaEmail] !== undefined) {
        return personasCVs[personaEmail];
    }
    
    try {
        const response = await fetch(`/api/personas/cvs`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const allCVs = await response.json();
        if (!Array.isArray(allCVs)) {
            console.warn('La réponse de /api/personas/cvs n\'est pas un tableau:', allCVs);
            personasCVs[personaEmail] = null;
            return null;
        }
        const personaCV = allCVs.find(cv => cv.persona_email === personaEmail);
        personasCVs[personaEmail] = personaCV || null;
        return personasCVs[personaEmail];
    } catch (error) {
        console.error(`Erreur chargement CV pour ${personaEmail}:`, error);
        personasCVs[personaEmail] = null;
        return null;
    }
}

async function loadPersonaEmails(personaEmail) {
    if (personasEmails[personaEmail] !== undefined) {
        return personasEmails[personaEmail];
    }
    
    try {
        const response = await fetch(`/api/personas/${encodeURIComponent(personaEmail)}/emails/count`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        if (typeof data !== 'object' || data === null || typeof data.total !== 'number' || typeof data.unread !== 'number') {
            console.warn('La réponse de /api/personas/.../emails/count n\'a pas la structure attendue:', data);
            personasEmails[personaEmail] = { total: 0, unread: 0 };
            return personasEmails[personaEmail];
        }
        personasEmails[personaEmail] = data;
        return data;
    } catch (error) {
        console.error(`Erreur chargement emails pour ${personaEmail}:`, error);
        personasEmails[personaEmail] = { total: 0, unread: 0 };
        return personasEmails[personaEmail];
    }
}

function filterPersonas() {
    const searchInput = document.getElementById('personaSearchInput');
    if (searchInput) {
        personaSearchFilter = searchInput.value.toLowerCase().trim();
        currentPersonasPage = 1; // Réinitialiser à la page 1 lors d'une recherche
        renderPersonasList();
    }
}

async function renderPersonasList() {
    const container = document.getElementById('personasList');
    if (!container) return;
    
    let personasToShow = showingBaseOnly 
        ? Object.entries(allPersonas).filter(([k, p]) => !p.alias)
        : Object.entries(allPersonas);
    
    // Appliquer le filtre de recherche
    if (personaSearchFilter) {
        personasToShow = personasToShow.filter(([k, p]) => 
            p.name.toLowerCase().includes(personaSearchFilter) ||
            p.email.toLowerCase().includes(personaSearchFilter)
        );
    }
    
    // Trier par ordre alphabétique du nom
    personasToShow.sort((a, b) => {
        const nameA = (a[1].name || '').toLowerCase();
        const nameB = (b[1].name || '').toLowerCase();
        return nameA.localeCompare(nameB, 'fr');
    });
    
    const totalPersonas = personasToShow.length;
    
    if (totalPersonas === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 40px; color: var(--text-secondary);">Aucun persona trouvé</p>';
        return;
    }
    
    // Calcul de la pagination
    const totalPages = Math.ceil(totalPersonas / personasPerPage);
    const startIndex = (currentPersonasPage - 1) * personasPerPage;
    const endIndex = startIndex + personasPerPage;
    const paginatedPersonas = personasToShow.slice(startIndex, endIndex);
    
    // Ajuster la page courante si elle dépasse le nombre total de pages
    if (currentPersonasPage > totalPages && totalPages > 0) {
        currentPersonasPage = totalPages;
        return renderPersonasList(); // Re-rendre avec la page corrigée
    }
    
    showPersonasLoader('Chargement des personas...', 0, 0, paginatedPersonas.length);
    
    // Charger les CVs et emails uniquement pour les personas de la page courante
    let loadedCount = 0;
    const loadPromises = paginatedPersonas.map(async ([key, persona], index) => {
        await Promise.all([
            loadPersonaCV(persona.email),
            loadPersonaEmails(persona.email)
        ]);
        
        loadedCount++;
        const progress = (loadedCount / paginatedPersonas.length) * 100;
        showPersonasLoader(
            `Chargement des personas... (${loadedCount}/${paginatedPersonas.length})`,
            progress,
            loadedCount,
            paginatedPersonas.length
        );
    });
    
    await Promise.all(loadPromises);
    
    let html = '';
    
    for (const [key, persona] of paginatedPersonas) {
        const isSelected = selectedPersonas.has(persona.email);
        const variantCount = Object.values(allPersonas).filter(p => p.parent === persona.email).length;
        
        const cv = personasCVs[persona.email];
        const emails = personasEmails[persona.email] || { total: 0, unread: 0 };
        
        html += `
            <div class="persona-card ${isSelected ? 'selected' : ''}">
                <div class="persona-header">
                    <input type="checkbox" id="persona-${key}" ${isSelected ? 'checked' : ''} 
                           onchange="togglePersona('${persona.email}', ${isSelected})">
                    <div class="persona-info">
                        <div class="persona-name" title="${persona.name}">${persona.name}</div>
                        <div class="persona-email" title="${persona.email}">${persona.email}</div>
                        ${persona.parent ? `<small style="color: var(--text-secondary); display: block; margin-top: 5px;">Parent: ${persona.parent}</small>` : ''}
                    </div>
                </div>
                
                <div class="persona-section">
                    <div class="persona-section-title">
                        📄 CV
                        <div class="persona-badges-inline">
                            ${persona.alias ? '<span class="persona-badge" style="background: var(--info);">Alias</span>' : '<span class="persona-badge" style="background: var(--success);">Base</span>'}
                            ${!persona.alias && variantCount > 0 ? `<span class="persona-badge" style="background: var(--warning);">${variantCount} variante(s)</span>` : ''}
                        </div>
                    </div>
                    ${cv ? `
                        <div class="cv-info">
                            <span class="cv-status exists">✓ Disponible</span>
                            <span class="cv-filename" title="${cv.filename}">${cv.filename}</span>
                            <button class="btn-icon btn-view-cv" onclick="viewCV('${persona.email}')" title="Voir le CV">👁️</button>
                            <button class="btn-icon btn-download-cv" onclick="downloadCV('${persona.email}')" title="Télécharger">⬇️</button>
                        </div>
                    ` : `
                        <div class="cv-info">
                            <span class="cv-status missing">✗ Non généré</span>
                            <span style="flex: 1; color: var(--text-secondary);">Aucun CV disponible</span>
                        </div>
                    `}
                </div>
                
                <div class="persona-section">
                    <div class="persona-section-title">📧 Emails</div>
                    <div class="email-info">
                        <span class="email-count ${emails.unread > 0 ? 'unread' : ''}">${emails.total} email(s)</span>
                        ${emails.unread > 0 ? `<span class="email-count unread">${emails.unread} non lu(s)</span>` : ''}
                        <button class="btn-icon btn-view-emails" onclick="event.stopPropagation(); viewEmails('${persona.email}', '${persona.name}'); return false;" title="Voir les emails" style="margin-left: auto; cursor: pointer;">📬</button>
                    </div>
                </div>
                
                <div class="persona-actions">
                    <button class="btn-icon" onclick="showPersonaDetail('${key}')" title="Voir les détails" style="background: var(--text-title); color: white;">👁️ Détails</button>
                    <button class="btn-icon" onclick="editPersona('${key}')" title="Modifier" style="background: var(--info); color: white;">✏️ Modifier</button>
                    <button class="btn-icon" onclick="testPersona('${key}')" title="Tester" style="background: var(--warning); color: white;">🧪 Tester</button>
                    ${!persona.alias ? `<button class="btn-icon" onclick="showVariantsModal('${key}')" title="Créer variantes" style="background: var(--info); color: white;">🔄 Variantes</button>` : ''}
                    <button class="btn-icon" onclick="deletePersona('${key}')" title="Supprimer" style="background: var(--error); color: white;">🗑️ Supprimer</button>
                </div>
            </div>
        `;
    }
    
    // Ajouter la pagination
    if (totalPages > 1) {
        // Générer les numéros de page à afficher
        let pageNumbers = [];
        const maxVisiblePages = 5;
        
        if (totalPages <= maxVisiblePages) {
            // Afficher toutes les pages si moins de maxVisiblePages
            for (let i = 1; i <= totalPages; i++) {
                pageNumbers.push(i);
            }
        } else {
            // Afficher les pages autour de la page actuelle
            let startPage = Math.max(1, currentPersonasPage - Math.floor(maxVisiblePages / 2));
            let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
            
            if (endPage - startPage < maxVisiblePages - 1) {
                startPage = Math.max(1, endPage - maxVisiblePages + 1);
            }
            
            if (startPage > 1) {
                pageNumbers.push(1);
                if (startPage > 2) pageNumbers.push('...');
            }
            
            for (let i = startPage; i <= endPage; i++) {
                pageNumbers.push(i);
            }
            
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) pageNumbers.push('...');
                pageNumbers.push(totalPages);
            }
        }
        
        html += `
            <div class="pagination-container" style="grid-column: 1 / -1; margin-top: 30px;">
                <div class="pagination-wrapper">
                    <button class="pagination-btn" 
                            onclick="changePersonasPage(${currentPersonasPage - 1})" 
                            ${currentPersonasPage === 1 ? 'disabled' : ''}>
                        <span>←</span>
                        <span>Précédent</span>
                    </button>
                    
                    <div class="pagination-numbers">
                        ${pageNumbers.map(page => {
                            if (page === '...') {
                                return '<span class="pagination-ellipsis">...</span>';
                            }
                            const isActive = page === currentPersonasPage;
                            return `
                                <button class="pagination-btn-number ${isActive ? 'active' : ''}" 
                                        onclick="changePersonasPage(${page})"
                                        ${isActive ? 'aria-current="page"' : ''}>
                                    ${page}
                                </button>
                            `;
                        }).join('')}
                    </div>
                    
                    <button class="pagination-btn" 
                            onclick="changePersonasPage(${currentPersonasPage + 1})" 
                            ${currentPersonasPage === totalPages ? 'disabled' : ''}>
                        <span>Suivant</span>
                        <span>→</span>
                    </button>
                </div>
                
                <div class="pagination-info">
                    <span class="pagination-info-text">
                        Page <strong>${currentPersonasPage}</strong> sur <strong>${totalPages}</strong>
                    </span>
                    <span class="pagination-info-count">
                        (${totalPersonas} persona${totalPersonas > 1 ? 's' : ''})
                    </span>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html || '<p style="text-align: center; padding: 20px; color: var(--text-secondary);">Aucun persona trouvé</p>';
    updateSelectedCount();
}

function changePersonasPage(page) {
    const totalPersonas = showingBaseOnly 
        ? Object.entries(allPersonas).filter(([k, p]) => !p.alias).length
        : Object.entries(allPersonas).length;
    
    let filteredPersonas = showingBaseOnly 
        ? Object.entries(allPersonas).filter(([k, p]) => !p.alias)
        : Object.entries(allPersonas);
    
    if (personaSearchFilter) {
        filteredPersonas = filteredPersonas.filter(([k, p]) => 
            p.name.toLowerCase().includes(personaSearchFilter) ||
            p.email.toLowerCase().includes(personaSearchFilter)
        );
    }
    
    const totalPages = Math.ceil(filteredPersonas.length / personasPerPage);
    if (page < 1 || page > totalPages) return;
    
    currentPersonasPage = page;
    renderPersonasList();
    
    // Scroll vers la liste des personas en gardant la position relative
    const container = document.getElementById('personasList');
    if (container) {
        const card = container.closest('.card');
        if (card) {
            const offset = card.getBoundingClientRect().top + window.pageYOffset - 20;
            window.scrollTo({ top: offset, behavior: 'smooth' });
        }
    }
}

async function loadBasePersonas() {
    try {
        showPersonasLoader('Chargement des personas de base...', 0, 0, 0);
        currentPersonasPage = 1; // Réinitialiser à la page 1
        const response = await fetch('/api/personas/base');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        allPersonas = await response.json();
        showingBaseOnly = true;
        const totalCount = Object.keys(allPersonas).filter(([k, p]) => !p.alias).length;
        showPersonasLoader('Chargement des personas de base...', 50, totalCount, totalCount * 2);
        showingBaseOnly = true;
        await renderPersonasList();
    } catch (error) {
        console.error('Erreur chargement personas de base:', error);
        const container = document.getElementById('personasList');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px; color: var(--error);">
                    <div style="font-size: 3em; margin-bottom: 15px;">❌</div>
                    <h3>Erreur lors du chargement</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary" onclick="loadBasePersonas()" style="margin-top: 20px;">🔄 Réessayer</button>
                </div>
            `;
        }
    }
}

async function loadAllPersonas() {
    try {
        showPersonasLoader('Chargement de tous les personas...', 0, 0, 0);
        currentPersonasPage = 1; // Réinitialiser à la page 1
        const response = await fetch('/api/personas');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        allPersonas = await response.json();
        showingBaseOnly = false;
        const totalCount = Object.keys(allPersonas).length;
        showPersonasLoader('Chargement de tous les personas...', 50, totalCount, totalCount * 2);
        showingBaseOnly = false;
        await renderPersonasList();
    } catch (error) {
        console.error('Erreur chargement tous les personas:', error);
        const container = document.getElementById('personasList');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px; color: var(--error);">
                    <div style="font-size: 3em; margin-bottom: 15px;">❌</div>
                    <h3>Erreur lors du chargement</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary" onclick="loadAllPersonas()" style="margin-top: 20px;">🔄 Réessayer</button>
                </div>
            `;
        }
    }
}

function togglePersona(personaEmail, wasSelected) {
    if (wasSelected) {
        selectedPersonas.delete(personaEmail);
    } else {
        selectedPersonas.add(personaEmail);
    }
    renderPersonasList();
    updateSelectedCount();
}

function selectAllPersonas() {
    const personasToShow = showingBaseOnly 
        ? Object.entries(allPersonas).filter(([k, p]) => !p.alias)
        : Object.entries(allPersonas);
    
    personasToShow.forEach(([key, persona]) => {
        selectedPersonas.add(persona.email);
    });
    renderPersonasList();
    updateSelectedCount();
}

function deselectAllPersonas() {
    selectedPersonas.clear();
    renderPersonasList();
    updateSelectedCount();
}

function updateSelectedCount() {
    const count = selectedPersonas.size;
    const countElement = document.getElementById('selectedCount');
    if (countElement) {
        countElement.textContent = `${count} sélectionné(s)`;
    }
}

function viewCV(personaEmail) {
    window.open(`/api/personas/${encodeURIComponent(personaEmail)}/cv`, '_blank');
}

function downloadCV(personaEmail) {
    window.location.href = `/api/personas/${encodeURIComponent(personaEmail)}/cv/download`;
}

async function viewEmails(personaEmail, personaName) {
    if (!personaEmail) {
        console.error('viewEmails: personaEmail is required');
        alert('Erreur: Email du persona manquant');
        return;
    }
    
    // Supprimer le modal existant s'il y en a un
    const existingModal = document.getElementById('emailsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.id = 'emailsModal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 900px; max-height: 90vh; overflow-y: auto;">
            <div class="modal-header">
                <h2 style="color: var(--text-title); margin: 0;">📧 Emails de ${personaName || personaEmail}</h2>
                <button class="modal-close" onclick="closeEmailsModal()" style="background: transparent; border: none; font-size: 1.5em; cursor: pointer; color: var(--text-primary);">✕</button>
            </div>
            <div style="padding: 20px;">
                <div style="margin-bottom: 20px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <button class="btn" onclick="fetchEmailsForPersona('${personaEmail}')" style="background: var(--info); color: white;">🔄 Actualiser</button>
                    <button class="btn" onclick="testEmailConnection('${personaEmail}')" style="background: var(--warning); color: white;">🧪 Tester connexion</button>
                </div>
                <div id="emailsList" style="padding: 20px;">
                    <p style="text-align: center; color: var(--text-secondary);">Chargement des emails...</p>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Charger les emails
    await loadEmailsForPersona(personaEmail);
}

loadEmailsForPersona = async function(personaEmail) {
    const emailsList = document.getElementById('emailsList');
    if (!emailsList) return;
    
    try {
        const response = await fetch(`/api/personas/${encodeURIComponent(personaEmail)}/emails`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        let emails = await response.json();
        if (!Array.isArray(emails)) {
            emails = [];
        }
        
        let emailsHtml = '';
        if (emails.length === 0) {
            emailsHtml = `
                <div style="text-align: center; padding: 40px 20px; color: var(--text-secondary);">
                    <div style="font-size: 3em; margin-bottom: 15px;">📭</div>
                    <p style="font-size: 1.1em; margin-bottom: 10px;">Aucun email reçu</p>
                    <button class="btn" onclick="fetchEmailsForPersona('${personaEmail}')" style="background: var(--info); color: white; margin-top: 10px;">🔄 Récupérer depuis IMAP</button>
                </div>
            `;
        } else {
            emails.sort((a, b) => new Date(b.received_at) - new Date(a.received_at)); // Trier par date décroissante
            emails.forEach(email => {
                const date = new Date(email.received_at).toLocaleString('fr-FR');
                const emailType = email.email_type || 'inbox';
                emailsHtml += `
                    <div style="padding: 15px; margin-bottom: 15px; background: var(--bg-card); border: 2px solid var(--border-color); border-radius: 8px; border-left: 4px solid ${email.is_read ? 'var(--success)' : 'var(--warning)'}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; flex-wrap: wrap; gap: 10px;">
                            <strong style="color: var(--text-primary); font-size: 1.1em; flex: 1; min-width: 200px;">${email.subject || '(Sans objet)'}</strong>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                ${!email.is_read ? '<span style="background: var(--warning); color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600;">Non lu</span>' : ''}
                                <span style="background: var(--info); color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600;">${emailType}</span>
                            </div>
                        </div>
                        <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 8px;">
                            <strong>De:</strong> <span style="color: var(--text-primary);">${email.sender || 'Inconnu'}</span>
                        </div>
                        <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 12px;">
                            📅 ${date}
                        </div>
                        <div style="color: var(--text-primary); white-space: pre-wrap; max-height: 300px; overflow-y: auto; padding: 10px; background: var(--border-color); border-radius: 5px; margin-bottom: 10px; line-height: 1.5;">
                            ${(email.body || '(Aucun contenu)').substring(0, 500)}${email.body && email.body.length > 500 ? '...' : ''}
                        </div>
                        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                            ${!email.is_read ? `<button class="btn" onclick="markEmailRead('${personaEmail}', ${email.id})" style="background: var(--success); color: white;">✓ Marquer comme lu</button>` : ''}
                        </div>
                    </div>
                `;
            });
        }
        
        emailsList.innerHTML = emailsHtml;
    } catch (error) {
        console.error('Erreur chargement emails:', error);
        const emailsList = document.getElementById('emailsList');
        if (emailsList) {
            emailsList.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; color: var(--error);">
                    <div style="font-size: 3em; margin-bottom: 15px;">❌</div>
                    <p style="font-size: 1.1em; margin-bottom: 10px;">Erreur lors du chargement des emails</p>
                    <p style="font-size: 0.9em; color: var(--text-secondary);">${error.message}</p>
                    <button class="btn" onclick="loadEmailsForPersona('${personaEmail}')" style="background: var(--info); color: white; margin-top: 15px;">🔄 Réessayer</button>
                </div>
            `;
        }
    }
}

fetchEmailsForPersona = async function(personaEmail) {
    const emailsList = document.getElementById('emailsList');
    if (!emailsList) return;
    
    emailsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Récupération des emails depuis IMAP...</p>';
    
    try {
        const response = await fetch(`/api/personas/${encodeURIComponent(personaEmail)}/emails/fetch`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ ${result.message || 'Emails récupérés avec succès'}`);
            await loadEmailsForPersona(personaEmail);
        } else {
            alert(`❌ Erreur: ${result.error || 'Erreur inconnue'}`);
            await loadEmailsForPersona(personaEmail);
        }
    } catch (error) {
        console.error('Erreur fetch emails:', error);
        alert(`❌ Erreur: ${error.message}`);
        await loadEmailsForPersona(personaEmail);
    }
}

testEmailConnection = async function(personaEmail) {
    try {
        const response = await fetch(`/api/personas/${encodeURIComponent(personaEmail)}/emails/test-connection`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ Connexion réussie!\n\nServeur: ${result.server}:${result.port}`);
        } else {
            alert(`❌ Erreur de connexion: ${result.error}\n\nServeur: ${result.server || 'N/A'}:${result.port || 'N/A'}`);
        }
    } catch (error) {
        console.error('Erreur test connexion:', error);
        alert(`❌ Erreur: ${error.message}`);
    }
}

closeEmailsModal = function() {
    const modal = document.getElementById('emailsModal');
    if (modal) {
        modal.remove();
    }
}

markEmailRead = async function(personaEmail, emailId) {
    try {
        await fetch(`/api/personas/${encodeURIComponent(personaEmail)}/emails/${emailId}/read`, { method: 'POST' });
        await viewEmails(personaEmail, allPersonas[Object.keys(allPersonas).find(k => allPersonas[k].email === personaEmail)]?.name || personaEmail);
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// Fonctions pour les modals
function showCreatePersonaModal() {
    currentPersonaKey = null;
    // Créer le modal s'il n'existe pas
    let modal = document.getElementById('personaModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'personaModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h2 id="personaModalTitle" style="color: var(--text-title); margin: 0;">Créer un persona</h2>
                    <button class="modal-close" onclick="closePersonaModal()">✕</button>
                </div>
                <form id="personaForm" onsubmit="savePersona(event); return false;">
                    <div class="form-group">
                        <label>Nom</label>
                        <input type="text" id="personaName" required placeholder="Ex: Jean Dupont">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="personaEmail" required placeholder="Ex: jean.dupont@example.com">
                    </div>
                    <div class="form-group">
                        <label>Mot de passe</label>
                        <input type="password" id="personaPassword" placeholder="Mot de passe (optionnel)">
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="personaAlias" onchange="toggleAliasField()">
                            C'est un alias (variante d'un persona existant)
                        </label>
                    </div>
                    <div class="form-group" id="parentField" style="display: none;">
                        <label>Persona parent</label>
                        <select id="personaParent">
                            <option value="">Sélectionner un persona parent</option>
                        </select>
                    </div>
                    <div class="btn-group">
                        <button type="submit" class="btn btn-primary">Enregistrer</button>
                        <button type="button" class="btn" onclick="closePersonaModal()">Annuler</button>
                        <button type="button" class="btn btn-warning" id="testPersonaBtn" onclick="testCurrentPersona()" style="display: none;">🧪 Tester</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    const modalTitle = document.getElementById('personaModalTitle');
    const form = document.getElementById('personaForm');
    const aliasCheck = document.getElementById('personaAlias');
    const parentField = document.getElementById('parentField');
    const testBtn = document.getElementById('testPersonaBtn');
    
    if (modalTitle) modalTitle.textContent = 'Créer un persona';
    if (form) form.reset();
    if (aliasCheck) aliasCheck.checked = false;
    if (parentField) parentField.style.display = 'none';
    if (testBtn) testBtn.style.display = 'none';
    loadParentOptions();
    modal.classList.add('active');
}

function closePersonaModal() {
    const modal = document.getElementById('personaModal');
    if (modal) {
        modal.classList.remove('active');
    }
    currentPersonaKey = null;
}

function toggleAliasField() {
    const aliasCheck = document.getElementById('personaAlias');
    const parentField = document.getElementById('parentField');
    if (!aliasCheck || !parentField) return;
    
    if (aliasCheck.checked) {
        parentField.style.display = 'block';
        loadParentOptions();
    } else {
        parentField.style.display = 'none';
        const parentSelect = document.getElementById('personaParent');
        if (parentSelect) parentSelect.value = '';
    }
}

async function loadParentOptions() {
    const select = document.getElementById('personaParent');
    if (!select) return;
    
    try {
        const response = await fetch('/api/personas/base');
        if (!response.ok) return;
        const basePersonas = await response.json();
        select.innerHTML = '<option value="">Sélectionner un persona de base</option>';
        for (const [key, persona] of Object.entries(basePersonas)) {
            if (!currentPersonaKey || key !== currentPersonaKey) {
                select.innerHTML += `<option value="${persona.email}">${persona.name} (${persona.email})</option>`;
            }
        }
    } catch (error) {
        console.error('Erreur chargement parents:', error);
    }
}

async function savePersona(event) {
    event.preventDefault();
    
    const name = document.getElementById('personaName')?.value;
    const email = document.getElementById('personaEmail')?.value;
    const password = document.getElementById('personaPassword')?.value;
    const alias = document.getElementById('personaAlias')?.checked || false;
    const parent = document.getElementById('personaParent')?.value || null;
    
    if (!name || !email) {
        alert('Veuillez remplir au moins le nom et l\'email');
        return;
    }
    
    try {
        let response;
        if (currentPersonaKey) {
            response = await fetch(`/api/personas/${currentPersonaKey}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password, alias, parent })
            });
        } else {
            response = await fetch('/api/personas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password, alias, parent })
            });
        }
        
        const data = await response.json();
        if (data.success) {
            closePersonaModal();
            await loadAllPersonas();
        } else {
            alert(`Erreur: ${data.error || 'Erreur inconnue'}`);
        }
    } catch (error) {
        alert(`Erreur: ${error.message}`);
    }
}

function editPersona(key) {
    currentPersonaKey = key;
    const persona = allPersonas[key];
    if (!persona) return;
    
    // Créer le modal s'il n'existe pas
    let modal = document.getElementById('personaModal');
    if (!modal) {
        showCreatePersonaModal();
        modal = document.getElementById('personaModal');
    }
    
    const modalTitle = document.getElementById('personaModalTitle');
    const nameInput = document.getElementById('personaName');
    const emailInput = document.getElementById('personaEmail');
    const passwordInput = document.getElementById('personaPassword');
    const aliasCheck = document.getElementById('personaAlias');
    const parentField = document.getElementById('parentField');
    const parentSelect = document.getElementById('personaParent');
    const testBtn = document.getElementById('testPersonaBtn');
    
    if (modalTitle) modalTitle.textContent = 'Modifier le persona';
    if (nameInput) nameInput.value = persona.name || '';
    if (emailInput) emailInput.value = persona.email || '';
    if (passwordInput) passwordInput.value = persona.password || '';
    if (aliasCheck) aliasCheck.checked = persona.alias || false;
    if (testBtn) testBtn.style.display = 'inline-block';
    
    toggleAliasField();
    if (persona.parent && parentSelect) {
        parentSelect.value = persona.parent;
    }
    
    loadParentOptions();
    if (modal) modal.classList.add('active');
}

async function deletePersona(key) {
    const persona = allPersonas[key];
    if (!persona) return;
    
    if (!confirm(`Êtes-vous sûr de vouloir supprimer ${persona.name} (${persona.email}) ?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/personas/${key}`, { method: 'DELETE' });
        const data = await response.json();
        if (data.success) {
            await loadAllPersonas();
        } else {
            alert(`Erreur: ${data.error || 'Erreur inconnue'}`);
        }
    } catch (error) {
        alert(`Erreur: ${error.message}`);
    }
}

function showPersonaDetail(key) {
    const persona = allPersonas[key];
    if (!persona) return;
    
    const variants = Object.values(allPersonas).filter(p => p.parent === persona.email);
    const cv = personasCVs[persona.email];
    const emails = personasEmails[persona.email] || { total: 0, unread: 0 };
    
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
            <div class="modal-header">
                <h2 style="color: var(--text-title); margin: 0;">👤 ${persona.name}</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">✕</button>
            </div>
            <div style="padding: 20px;">
                <div style="margin-bottom: 20px; padding-bottom: 20px; border-bottom: 2px solid var(--border-color);">
                    <h3 style="color: var(--text-title); margin-bottom: 10px;">Informations générales</h3>
                    <div style="display: grid; gap: 10px;">
                        <div><strong>Email:</strong> <span style="color: var(--text-secondary);">${persona.email}</span></div>
                        <div><strong>Type:</strong> <span style="background: ${persona.alias ? 'var(--info)' : 'var(--success)'}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.85em;">${persona.alias ? 'Alias' : 'Base'}</span></div>
                        ${persona.parent ? `<div><strong>Parent:</strong> <span style="color: var(--text-secondary);">${persona.parent}</span></div>` : ''}
                    </div>
                </div>
                
                <div style="margin-bottom: 20px; padding-bottom: 20px; border-bottom: 2px solid var(--border-color);">
                    <h3 style="color: var(--text-title); margin-bottom: 10px;">📄 CV</h3>
                    ${cv ? `
                        <div style="padding: 10px; background: var(--border-color); border-radius: 5px;">
                            <div><strong>Fichier:</strong> ${cv.filename}</div>
                            <div style="margin-top: 10px;">
                                <button class="btn" onclick="viewCV('${persona.email}')" style="background: var(--info); color: white; margin-right: 10px;">👁️ Voir</button>
                                <button class="btn" onclick="downloadCV('${persona.email}')" style="background: var(--success); color: white;">⬇️ Télécharger</button>
                            </div>
                        </div>
                    ` : '<p style="color: var(--text-secondary);">Aucun CV généré</p>'}
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: var(--text-title); margin-bottom: 10px;">📧 Emails</h3>
                    <div style="padding: 10px; background: var(--border-color); border-radius: 5px;">
                        <div><strong>Total:</strong> ${emails.total} email(s)</div>
                        <div><strong>Non lus:</strong> <span style="color: ${emails.unread > 0 ? 'var(--warning)' : 'var(--text-secondary)'};">${emails.unread}</span></div>
                        <button class="btn" onclick="viewEmails('${persona.email}', '${persona.name}'); this.closest('.modal').remove();" style="margin-top: 10px; background: var(--text-title); color: white;">📬 Voir les emails</button>
                    </div>
                </div>
                
                ${!persona.alias && variants.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: var(--text-title); margin-bottom: 10px;">🔄 Variantes (${variants.length})</h3>
                        <div style="max-height: 200px; overflow-y: auto;">
                            ${variants.map(v => `
                                <div style="padding: 8px; margin-bottom: 5px; background: var(--border-color); border-radius: 5px;">
                                    <strong>${v.name}</strong><br>
                                    <small style="color: var(--text-secondary);">${v.email}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div class="btn-group" style="margin-top: 20px;">
                    <button class="btn" onclick="editPersona('${key}'); this.closest('.modal').remove();" style="background: var(--info); color: white;">✏️ Modifier</button>
                    <button class="btn" onclick="testPersona('${key}'); this.closest('.modal').remove();" style="background: var(--warning); color: white;">🧪 Tester</button>
                    <button class="btn" onclick="showTestEmailModal('${persona.email}', '${persona.name}'); this.closest('.modal').remove();" style="background: var(--success); color: white;">📧 Tester Email</button>
                    ${!persona.alias ? `<button class="btn" onclick="showVariantsModal('${key}'); this.closest('.modal').remove();" style="background: var(--info); color: white;">🔄 Variantes</button>` : ''}
                    <button class="btn" onclick="deletePersona('${key}'); this.closest('.modal').remove();" style="background: var(--error); color: white;">🗑️ Supprimer</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function testEmailSend(fromEmail, toEmail) {
    if (!fromEmail || !toEmail) {
        alert('Veuillez sélectionner un expéditeur et un destinataire.');
        return;
    }
    
    if (fromEmail === toEmail) {
        alert('L\'expéditeur et le destinataire doivent être différents.');
        return;
    }
    
    const subject = prompt('Sujet de l\'email de test:', 'Test d\'envoi de mail entre personas');
    if (!subject) return;
    
    const body = prompt('Corps de l\'email de test:', 'Ceci est un test d\'envoi de mail entre personas.');
    if (body === null) return;
    
    try {
        const response = await fetch('/api/personas/test-email-send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from_email: fromEmail,
                to_email: toEmail,
                subject: subject,
                body: body || 'Ceci est un test d\'envoi de mail entre personas.'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ ${result.message}\n\nServeur: ${result.server}:${result.port}`);
        } else {
            alert(`❌ Erreur: ${result.error}\n\nServeur: ${result.server || 'N/A'}:${result.port || 'N/A'}`);
        }
    } catch (error) {
        alert(`❌ Erreur: ${error.message}`);
    }
}

async function testPersona(key) {
    const persona = allPersonas[key];
    if (!persona) return;
    
    try {
        const response = await fetch(`/api/personas/${key}/test`, { method: 'POST' });
        const result = await response.json();
        
        if (result.valid) {
            let message = `✅ Persona valide`;
            if (result.warnings && result.warnings.length > 0) {
                message += `\n⚠️ Avertissements: ${result.warnings.join(', ')}`;
            }
            alert(`Persona valide!\n\n${result.warnings && result.warnings.length > 0 ? 'Avertissements:\n' + result.warnings.join('\n') : 'Aucun problème détecté.'}`);
        } else {
            alert(`Persona invalide!\n\nErreurs:\n${result.errors.join('\n')}\n\n${result.warnings && result.warnings.length > 0 ? 'Avertissements:\n' + result.warnings.join('\n') : ''}`);
        }
    } catch (error) {
        alert(`Erreur test: ${error.message}`);
    }
}

function testCurrentPersona() {
    if (currentPersonaKey) {
        testPersona(currentPersonaKey);
    }
}

function showTestEmailModal(fromEmail, fromName) {
    // Créer une liste de tous les personas pour le destinataire
    const personasList = Object.entries(allPersonas)
        .map(([key, p]) => `<option value="${p.email}">${p.name} (${p.email})</option>`)
        .join('');
    
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h2 style="color: var(--text-title); margin: 0;">📧 Tester l'envoi d'email</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">✕</button>
            </div>
            <div style="padding: 20px;">
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Expéditeur:</label>
                    <input type="text" id="testEmailFrom" value="${fromEmail}" readonly style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 5px; background: var(--bg-card); color: var(--text-primary);">
                    <small style="color: var(--text-secondary);">${fromName}</small>
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Destinataire:</label>
                    <select id="testEmailTo" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 5px; background: var(--bg-card); color: var(--text-primary);">
                        ${personasList}
                    </select>
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Sujet:</label>
                    <input type="text" id="testEmailSubject" value="Test d'envoi de mail entre personas" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 5px; background: var(--bg-card); color: var(--text-primary);">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">Message:</label>
                    <textarea id="testEmailBody" rows="5" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 5px; background: var(--bg-card); color: var(--text-primary);">Ceci est un test d'envoi de mail entre personas.</textarea>
                </div>
                <div style="display: flex; gap: 10px; justify-content: flex-end;">
                    <button class="btn" onclick="this.closest('.modal').remove()" style="background: var(--text-secondary); color: white;">Annuler</button>
                    <button class="btn" onclick="sendTestEmail()" style="background: var(--success); color: white;">📧 Envoyer</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function sendTestEmail() {
    const fromEmail = document.getElementById('testEmailFrom')?.value;
    const toEmail = document.getElementById('testEmailTo')?.value;
    const subject = document.getElementById('testEmailSubject')?.value;
    const body = document.getElementById('testEmailBody')?.value;
    
    if (!fromEmail || !toEmail) {
        alert('Veuillez sélectionner un expéditeur et un destinataire.');
        return;
    }
    
    if (fromEmail === toEmail) {
        alert('L\'expéditeur et le destinataire doivent être différents.');
        return;
    }
    
    try {
        const response = await fetch('/api/personas/test-email-send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from_email: fromEmail,
                to_email: toEmail,
                subject: subject || 'Test d\'envoi de mail entre personas',
                body: body || 'Ceci est un test d\'envoi de mail entre personas.'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ ${result.message}\n\nServeur: ${result.server}:${result.port}`);
            document.querySelector('.modal.active')?.remove();
        } else {
            alert(`❌ Erreur: ${result.error}\n\nServeur: ${result.server || 'N/A'}:${result.port || 'N/A'}`);
        }
    } catch (error) {
        alert(`❌ Erreur: ${error.message}`);
    }
}

function showVariantsModal(key) {
    const persona = allPersonas[key];
    if (!persona) return;
    
    let modal = document.getElementById('variantsModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'variantsModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h2 style="color: var(--text-title); margin: 0;">🔄 Créer des variantes</h2>
                    <button class="modal-close" onclick="closeVariantsModal()">✕</button>
                </div>
                <div class="form-group">
                    <label>Persona de base</label>
                    <div id="variantBasePersona" style="padding: 10px; background: var(--border-color); border-radius: 5px;">
                        -
                    </div>
                </div>
                <div class="form-group">
                    <label>Nombre de variantes</label>
                    <input type="number" id="variantCount" min="1" max="20" value="3">
                </div>
                <div class="form-group">
                    <label>Modèle de nom (optionnel)</label>
                    <input type="text" id="variantNamePattern" placeholder="Ex: {name} Variant {n}">
                    <small style="color: var(--text-secondary);">Utilisez {name} pour le nom original et {n} pour le numéro</small>
                </div>
                <div class="btn-group">
                    <button class="btn btn-primary" onclick="createVariants()">Créer</button>
                    <button class="btn" onclick="closeVariantsModal()">Annuler</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    const basePersonaDiv = document.getElementById('variantBasePersona');
    const countInput = document.getElementById('variantCount');
    const patternInput = document.getElementById('variantNamePattern');
    
    if (basePersonaDiv) {
        basePersonaDiv.innerHTML = `
            <strong>${persona.name}</strong><br>
            <small style="color: var(--text-secondary);">${persona.email}</small>
        `;
    }
    if (countInput) countInput.value = 3;
    if (patternInput) patternInput.value = '';
    
    variantBaseKey = key;
    modal.classList.add('active');
}

let variantBaseKey = null;

function closeVariantsModal() {
    const modal = document.getElementById('variantsModal');
    if (modal) {
        modal.classList.remove('active');
    }
    variantBaseKey = null;
}

async function createVariants() {
    if (!variantBaseKey) return;
    
    const count = parseInt(document.getElementById('variantCount')?.value || 3);
    const namePattern = document.getElementById('variantNamePattern')?.value || null;
    
    try {
        const response = await fetch(`/api/personas/${variantBaseKey}/variants`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count, name_pattern: namePattern })
        });
        
        const data = await response.json();
        if (data.success) {
            closeVariantsModal();
            await loadAllPersonas();
        } else {
            alert(`Erreur: ${data.error || 'Erreur inconnue'}`);
        }
    } catch (error) {
        alert(`Erreur: ${error.message}`);
    }
}

// Exporter les fonctions globalement pour qu'elles soient accessibles depuis onclick
// Ces fonctions doivent être disponibles après leur définition
(function() {
    // Attendre que le DOM soit prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            // Ré-exporter après le chargement
            if (typeof viewEmails === 'function') {
                window.viewEmails = viewEmails;
                window.closeEmailsModal = closeEmailsModal;
                window.fetchEmailsForPersona = fetchEmailsForPersona;
                window.testEmailConnection = testEmailConnection;
                window.markEmailRead = markEmailRead;
                window.loadEmailsForPersona = loadEmailsForPersona;
            }
        });
    } else {
        // DOM déjà chargé
        if (typeof viewEmails === 'function') {
            window.viewEmails = viewEmails;
            window.closeEmailsModal = closeEmailsModal;
            window.fetchEmailsForPersona = fetchEmailsForPersona;
            window.testEmailConnection = testEmailConnection;
            window.markEmailRead = markEmailRead;
            window.loadEmailsForPersona = loadEmailsForPersona;
        }
    }
})();
