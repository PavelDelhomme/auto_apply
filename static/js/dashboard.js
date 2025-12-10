/**
 * JavaScript pour la page Dashboard
 */

let allPersonas = {};
let selectedPersonas = new Set();

// Charger les personas au démarrage
async function loadPersonas() {
    try {
        const response = await fetch('/api/personas');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        allPersonas = await response.json();
        return allPersonas;
    } catch (error) {
        console.error('Erreur chargement personas:', error);
        return {};
    }
}

// Variables pour la pagination des recherches actives
let activeSearchesPage = 1;
let activeSearchesPerPage = 5;
let allActiveSearches = {};

// Charger les recherches actives avec cache
async function loadActiveSearches() {
    const container = document.getElementById('activeSearchesContainer');
    if (!container) return;
    
    try {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">⏳ Chargement...</p>';
        
        // Utiliser le cache si disponible
        allActiveSearches = await CacheManager.cachedApiCall('/api/searches/enabled', {}, 'searches_enabled', 2 * 60 * 1000);
        
        // Filtrer les recherches invalides (sans query ou location)
        const validSearches = {};
        for (const [key, search] of Object.entries(allActiveSearches)) {
            // Garder seulement les recherches valides (avec au moins un nom ou une query)
            if (search && (search.query || search.name || search.location)) {
                validSearches[key] = search;
            }
        }
        allActiveSearches = validSearches;
        
        activeSearchesPage = 1;
        renderActiveSearches();
    } catch (error) {
        console.error('Erreur chargement recherches actives:', error);
        container.innerHTML = '<p style="color: var(--error);">Erreur lors du chargement</p>';
    }
}

function renderActiveSearches() {
    const container = document.getElementById('activeSearchesContainer');
    if (!container) return;
    
    if (!allActiveSearches || Object.keys(allActiveSearches).length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">Aucune recherche active</p>';
        return;
    }
    
    const searchesArray = Object.entries(allActiveSearches);
    const totalItems = searchesArray.length;
    const totalPages = Math.ceil(totalItems / activeSearchesPerPage);
    const startIndex = (activeSearchesPage - 1) * activeSearchesPerPage;
    const endIndex = startIndex + activeSearchesPerPage;
    const paginatedSearches = searchesArray.slice(startIndex, endIndex);
    
    let html = '';
    for (const [key, search] of paginatedSearches) {
        const personasAssigned = search.personas_assigned || [];
        const personasExcluded = search.personas_excluded || [];
        const history = search.history || [];
        const lastRun = history.length > 0 ? history[history.length - 1] : null;
        const runCount = search.run_count || 0;
        
        // Calculer les statistiques de la dernière exécution
        let lastRunStats = {
            jobs_found: 0,
            applications_sent: 0,
            applications_failed: 0,
            successful: 0
        };
        
        if (lastRun && lastRun.stats) {
            lastRunStats = {
                jobs_found: lastRun.stats.jobs_found || 0,
                applications_sent: lastRun.stats.applications_sent || 0,
                applications_failed: lastRun.stats.failed || 0,
                successful: lastRun.stats.successful || 0
            };
        }
        
        html += `
            <div class="active-search-card">
                <div class="active-search-header">
                    <div class="active-search-info">
                        <h3 class="active-search-title">${search.name || 'Sans nom'}</h3>
                        <p class="active-search-meta">
                            🔍 <strong>${search.query || (search.name || 'Non spécifié')}</strong> | 📍 <strong>${search.location || 'Non spécifié'}</strong>
                        </p>
                        <small class="active-search-id">ID: ${key}</small>
                        ${search.description ? `<p class="active-search-description">${search.description}</p>` : ''}
                    </div>
                    <div class="active-search-toggle-container">
                        <button onclick="toggleSearchActive('${key}')" class="toggle-search-btn ${search.is_active !== false ? 'active' : 'inactive'}">
                            ${search.is_active !== false ? '✅ Active' : '⏸️ Inactive'}
                        </button>
                    </div>
                </div>
                
                <!-- Statistiques de la dernière exécution -->
                ${lastRun ? `
                    <div class="last-execution-stats">
                        <div class="last-execution-header">
                            <strong class="last-execution-title">📊 Dernière exécution</strong>
                            <span class="last-execution-date">${new Date(lastRun.timestamp).toLocaleString('fr-FR', {day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'})}</span>
                        </div>
                        <div class="stats-grid">
                            <div class="stat-box">
                                <div class="stat-icon">💼</div>
                                <div class="stat-label">Offres</div>
                                <div class="stat-value">${lastRunStats.jobs_found}</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-icon">📤</div>
                                <div class="stat-label">Candidatures</div>
                                <div class="stat-value">${lastRunStats.applications_sent}</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-icon">✅</div>
                                <div class="stat-label">Réussies</div>
                                <div class="stat-value success">${lastRunStats.successful}</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-icon">❌</div>
                                <div class="stat-label">Échouées</div>
                                <div class="stat-value error">${lastRunStats.applications_failed}</div>
                            </div>
                        </div>
                    </div>
                ` : `
                    <div class="no-execution-message">
                        <p>⏳ Aucune exécution enregistrée</p>
                    </div>
                `}
                
                <!-- Informations générales -->
                <div class="search-general-info">
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">🔄 Exécutions:</span>
                            <strong class="info-value">${runCount}</strong>
                        </div>
                        <div class="info-item">
                            <span class="info-label">💼 Type:</span>
                            <strong class="info-value">${search.job_type || 'Tous'}</strong>
                        </div>
                        <div class="info-item">
                            <span class="info-label">📊 Max résultats:</span>
                            <strong class="info-value">${search.max_results || 50}</strong>
                        </div>
                        ${search.standalone ? `
                            <div class="info-item">
                                <span class="info-label">🔍 Mode:</span>
                                <strong class="info-value info">Standalone</strong>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Personas -->
                ${personasAssigned.length > 0 || personasExcluded.length > 0 ? `
                    <div class="personas-section">
                        ${personasAssigned.length > 0 ? `
                            <div class="personas-group">
                                <strong class="personas-group-title assigned">✓ Personas assignés (${personasAssigned.length}):</strong>
                                <div class="personas-tags">
                                    ${personasAssigned.slice(0, 5).map(email => {
                                        const persona = allPersonas[Object.keys(allPersonas).find(k => allPersonas[k].email === email)];
                                        const name = persona ? persona.name : email;
                                        return `<span class="persona-tag assigned">${name}</span>`;
                                    }).join('')}
                                    ${personasAssigned.length > 5 ? `<span class="personas-more">+${personasAssigned.length - 5}</span>` : ''}
                                </div>
                            </div>
                        ` : ''}
                        ${personasExcluded.length > 0 ? `
                            <div class="personas-group">
                                <strong class="personas-group-title excluded">✗ Personas exclus (${personasExcluded.length}):</strong>
                                <div class="personas-tags">
                                    ${personasExcluded.slice(0, 5).map(email => {
                                        const persona = allPersonas[Object.keys(allPersonas).find(k => allPersonas[k].email === email)];
                                        const name = persona ? persona.name : email;
                                        return `<span class="persona-tag excluded">${name}</span>`;
                                    }).join('')}
                                    ${personasExcluded.length > 5 ? `<span class="personas-more">+${personasExcluded.length - 5}</span>` : ''}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                ` : ''}
                
                <!-- Bouton pour voir les détails complets -->
                <div class="view-details-section">
                    <button onclick="showSearchDetailsFromDashboard('${key}')" class="view-details-btn">
                        📊 Voir les détails complets
                    </button>
                </div>
            </div>
        `;
    }
    
    // Ajouter la pagination avec layout amélioré : Précédent (gauche) | Info (centre) | Suivant (droite), nombre total en dessous
    if (totalPages > 1) {
        html += `
            <div class="pagination-container-dashboard">
                <div class="pagination-row">
                    <button class="pagination-btn-nav pagination-btn-prev" onclick="changeActiveSearchesPage(${activeSearchesPage - 1})" ${activeSearchesPage === 1 ? 'disabled' : ''}>
                        <span class="pagination-icon">←</span>
                        <span class="pagination-text">Précédent</span>
                    </button>
                    <div class="pagination-info-center">
                        <div class="pagination-page-info">
                            Page <strong>${activeSearchesPage}</strong> sur <strong>${totalPages}</strong>
                        </div>
                    </div>
                    <button class="pagination-btn-nav pagination-btn-next" onclick="changeActiveSearchesPage(${activeSearchesPage + 1})" ${activeSearchesPage === totalPages ? 'disabled' : ''}>
                        <span class="pagination-text">Suivant</span>
                        <span class="pagination-icon">→</span>
                    </button>
                </div>
                <div class="pagination-count">
                    ${totalItems} recherche${totalItems > 1 ? 's' : ''}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Fonction pour afficher les détails complets d'une recherche depuis le dashboard
async function showSearchDetailsFromDashboard(searchKey) {
    const search = allActiveSearches[searchKey];
    if (!search) {
        // Recharger les recherches si nécessaire
        await loadActiveSearches();
        const updatedSearch = allActiveSearches[searchKey];
        if (!updatedSearch) {
            alert('Recherche non trouvée');
            return;
        }
        showSearchDetailsModal(updatedSearch, searchKey);
    } else {
        showSearchDetailsModal(search, searchKey);
    }
}

// Fonction pour afficher un modal avec tous les détails de la recherche
function showSearchDetailsModal(search, searchKey) {
    const history = search.history || [];
    const personasAssigned = search.personas_assigned || [];
    const personasExcluded = search.personas_excluded || [];
    
    let historyHtml = '';
    if (history.length === 0) {
        historyHtml = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">Aucune exécution enregistrée</p>';
    } else {
        history.slice(-10).reverse().forEach((run, idx) => {
            const runStats = run.stats || {};
            historyHtml += `
                <div style="padding: 15px; margin-bottom: 15px; background: var(--border-color); border-radius: 8px; border-left: 4px solid var(--text-title);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <strong style="color: var(--text-title); font-size: 1em;">Exécution #${history.length - idx}</strong>
                        <span style="color: var(--text-secondary); font-size: 0.85em;">${new Date(run.timestamp).toLocaleString('fr-FR')}</span>
                    </div>
                    ${run.steps ? `
                        <div style="margin-bottom: 10px;">
                            <strong style="color: var(--text-title); font-size: 0.9em; display: block; margin-bottom: 8px;">Étapes:</strong>
                            ${run.steps.map(step => `
                                <div style="margin: 5px 0; padding: 8px; background: var(--bg-card); border-radius: 5px; font-size: 0.85em;">
                                    <span style="color: var(--text-primary);">${step.step}</span>
                                    ${step.status ? `<span style="color: ${step.status === 'success' ? 'var(--success)' : 'var(--error)'}; margin-left: 10px; font-weight: 600;">${step.status === 'success' ? '✓' : '✗'}</span>` : ''}
                                    ${step.message ? `<div style="color: var(--text-secondary); font-size: 0.8em; margin-top: 3px;">${step.message}</div>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    ${runStats ? `
                        <div style="padding: 12px; background: var(--bg-card); border-radius: 6px; margin-top: 10px;">
                            <strong style="color: var(--text-title); font-size: 0.9em; display: block; margin-bottom: 8px;">📊 Statistiques:</strong>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;">
                                <div><span style="color: var(--text-secondary); font-size: 0.85em;">Offres trouvées:</span> <strong style="color: var(--text-primary);">${runStats.jobs_found || 0}</strong></div>
                                <div><span style="color: var(--text-secondary); font-size: 0.85em;">Candidatures:</span> <strong style="color: var(--text-primary);">${runStats.applications_sent || 0}</strong></div>
                                <div><span style="color: var(--text-secondary); font-size: 0.85em;">Réussies:</span> <strong style="color: var(--success);">${runStats.successful || 0}</strong></div>
                                <div><span style="color: var(--text-secondary); font-size: 0.85em;">Échouées:</span> <strong style="color: var(--error);">${runStats.failed || 0}</strong></div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        });
    }
    
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.style.zIndex = '3000';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 1000px; max-height: 90vh; overflow-y: auto;">
            <div class="modal-header">
                <h2 style="color: var(--text-title); margin: 0;">📊 Détails complets: ${search.name || 'Sans nom'}</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()" style="background: transparent; border: none; font-size: 1.5em; cursor: pointer; color: var(--text-primary);">✕</button>
            </div>
            
            <div style="padding: 20px;">
                <!-- Informations générales -->
                <div style="margin-bottom: 25px;">
                    <h3 style="color: var(--text-title); margin-bottom: 15px; border-bottom: 2px solid var(--border-color); padding-bottom: 8px;">Informations générales</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div><strong style="color: var(--text-secondary);">Requête:</strong> <span style="color: var(--text-primary);">${search.query || 'N/A'}</span></div>
                        <div><strong style="color: var(--text-secondary);">Localisation:</strong> <span style="color: var(--text-primary);">${search.location || 'N/A'}</span></div>
                        <div><strong style="color: var(--text-secondary);">Type:</strong> <span style="color: var(--text-primary);">${search.job_type || 'Tous'}</span></div>
                        <div><strong style="color: var(--text-secondary);">Max résultats:</strong> <span style="color: var(--text-primary);">${search.max_results || 50}</span></div>
                        <div><strong style="color: var(--text-secondary);">Exécutions:</strong> <span style="color: var(--text-primary);">${search.run_count || 0}</span></div>
                        <div><strong style="color: var(--text-secondary);">Statut:</strong> ${search.enabled !== false ? '<span style="color: var(--success);">✓ Activée</span>' : '<span style="color: var(--error);">✗ Désactivée</span>'}</div>
                        <div><strong style="color: var(--text-secondary);">Standalone:</strong> <span style="color: var(--text-primary);">${search.standalone ? 'Oui' : 'Non'}</span></div>
                        <div><strong style="color: var(--text-secondary);">ID:</strong> <span style="color: var(--text-primary); font-family: monospace; font-size: 0.9em;">${searchKey}</span></div>
                    </div>
                    ${search.description ? `
                        <div style="margin-top: 15px; padding: 12px; background: var(--border-color); border-radius: 6px;">
                            <strong style="color: var(--text-secondary); display: block; margin-bottom: 5px;">Description:</strong>
                            <p style="color: var(--text-primary); margin: 0; line-height: 1.5;">${search.description}</p>
                        </div>
                    ` : ''}
                </div>
                
                <!-- Personas -->
                ${personasAssigned.length > 0 || personasExcluded.length > 0 ? `
                    <div style="margin-bottom: 25px;">
                        <h3 style="color: var(--text-title); margin-bottom: 15px; border-bottom: 2px solid var(--border-color); padding-bottom: 8px;">Personas</h3>
                        ${personasAssigned.length > 0 ? `
                            <div style="margin-bottom: 15px;">
                                <strong style="color: var(--success); font-size: 0.9em; display: block; margin-bottom: 8px;">✓ Assignés (${personasAssigned.length}):</strong>
                                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                    ${personasAssigned.map(email => {
                                        const persona = allPersonas[Object.keys(allPersonas).find(k => allPersonas[k].email === email)];
                                        const name = persona ? persona.name : email;
                                        return `<span style="background: var(--success); color: white; padding: 6px 12px; border-radius: 12px; font-size: 0.85em; font-weight: 600;">${name}</span>`;
                                    }).join('')}
                                </div>
                            </div>
                        ` : ''}
                        ${personasExcluded.length > 0 ? `
                            <div>
                                <strong style="color: var(--error); font-size: 0.9em; display: block; margin-bottom: 8px;">✗ Exclus (${personasExcluded.length}):</strong>
                                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                    ${personasExcluded.map(email => {
                                        const persona = allPersonas[Object.keys(allPersonas).find(k => allPersonas[k].email === email)];
                                        const name = persona ? persona.name : email;
                                        return `<span style="background: var(--error); color: white; padding: 6px 12px; border-radius: 12px; font-size: 0.85em; font-weight: 600;">${name}</span>`;
                                    }).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                ` : ''}
                
                <!-- Historique des exécutions -->
                <div>
                    <h3 style="color: var(--text-title); margin-bottom: 15px; border-bottom: 2px solid var(--border-color); padding-bottom: 8px;">Historique des exécutions (${history.length})</h3>
                    <div style="max-height: 500px; overflow-y: auto; padding-right: 10px;">
                        ${historyHtml}
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Fermer le modal en cliquant en dehors
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Exporter la fonction globalement pour qu'elle soit accessible depuis onclick
window.changeActiveSearchesPage = function(page) {
    const totalPages = Math.ceil(Object.keys(allActiveSearches).length / activeSearchesPerPage);
    if (page < 1 || page > totalPages) return;
    
    // Sauvegarder la position actuelle du scroll
    const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    
    activeSearchesPage = page;
    renderActiveSearches();
    
    // Scroll vers la section "Recherches Actives" en gardant la position relative
    setTimeout(() => {
        const activeSearchesSection = document.getElementById('activeSearchesContainer');
        if (activeSearchesSection) {
            // Trouver le conteneur parent (la card)
            const card = activeSearchesSection.closest('.card');
            if (card) {
                const cardTop = card.getBoundingClientRect().top + window.pageYOffset;
                // Scroll vers la card en gardant un peu d'espace en haut
                window.scrollTo({ top: cardTop - 20, behavior: 'smooth' });
            } else {
                // Fallback: scroll vers le conteneur avec block: 'nearest' pour éviter de remonter trop haut
                activeSearchesSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }
    }, 100);
};

// Variables pour la pagination des logs
let logsPage = 1;
let logsPerPage = 50;
let allLogs = [];

// Fonction pour ajouter un log
function addLog(message, level = 'info', timestamp = null) {
    const logsContainer = document.getElementById('logsContainer');
    if (!logsContainer) return;
    
    const time = timestamp || new Date().toLocaleTimeString('fr-FR');
    const logEntry = {
        time,
        level,
        message
    };
    
    // Ajouter au début du tableau
    allLogs.unshift(logEntry);
    
    // Garder seulement les 1000 derniers logs en mémoire
    if (allLogs.length > 1000) {
        allLogs = allLogs.slice(0, 1000);
    }
    
    // Re-rendre les logs avec pagination
    renderLogs();
}

function renderLogs() {
    const logsContainer = document.getElementById('logsContainer');
    if (!logsContainer) return;
    
    if (allLogs.length === 0) {
        logsContainer.innerHTML = `
            <div class="log-entry">
                <span class="log-timestamp">--:--:--</span>
                <span class="log-level info">INFO</span>
                <span>Aucun log disponible</span>
            </div>
        `;
        return;
    }
    
    const totalPages = Math.ceil(allLogs.length / logsPerPage);
    const startIndex = (logsPage - 1) * logsPerPage;
    const endIndex = startIndex + logsPerPage;
    const paginatedLogs = allLogs.slice(startIndex, endIndex);
    
    let html = '';
    for (const log of paginatedLogs) {
        html += `
            <div class="log-entry">
                <span class="log-timestamp">${log.time}</span>
                <span class="log-level ${log.level}">${log.level.toUpperCase()}</span>
                <span>${log.message}</span>
            </div>
        `;
    }
    
    // Ajouter la pagination avec layout amélioré : Précédent (gauche) | Info (centre) | Suivant (droite), nombre total en dessous
    if (totalPages > 1) {
        html += `
            <div class="pagination-container-dashboard">
                <div class="pagination-row">
                    <button class="pagination-btn-nav pagination-btn-prev" onclick="changeLogsPage(${logsPage - 1})" ${logsPage === 1 ? 'disabled' : ''}>
                        <span class="pagination-icon">←</span>
                        <span class="pagination-text">Précédent</span>
                    </button>
                    <div class="pagination-info-center">
                        <div class="pagination-page-info">
                            Page <strong>${logsPage}</strong> sur <strong>${totalPages}</strong>
                        </div>
                    </div>
                    <button class="pagination-btn-nav pagination-btn-next" onclick="changeLogsPage(${logsPage + 1})" ${logsPage === totalPages ? 'disabled' : ''}>
                        <span class="pagination-text">Suivant</span>
                        <span class="pagination-icon">→</span>
                    </button>
                </div>
                <div class="pagination-count">
                    ${totalItems} log${totalItems !== 1 ? 's' : ''}
                </div>
            </div>
        `;
    }
    
    logsContainer.innerHTML = html;
}

// Exporter la fonction globalement pour qu'elle soit accessible depuis onclick
window.changeLogsPage = function(page) {
    const totalPages = Math.ceil(allLogs.length / logsPerPage);
    if (page < 1 || page > totalPages) return;
    
    logsPage = page;
    renderLogs();
    
    // Scroll vers la section "Logs" en gardant la position relative
    setTimeout(() => {
        const logsSection = document.getElementById('logsContainer');
        if (logsSection) {
            // Trouver le conteneur parent (la card)
            const card = logsSection.closest('.card');
            if (card) {
                const cardTop = card.getBoundingClientRect().top + window.pageYOffset;
                // Scroll vers la card en gardant un peu d'espace en haut
                window.scrollTo({ top: cardTop - 20, behavior: 'smooth' });
            } else {
                // Fallback: scroll vers le conteneur avec block: 'nearest' pour éviter de remonter trop haut
                logsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }
    }, 100);
};

// Mettre à jour les statistiques
function updateStats(stats) {
    if (!stats) return;
    
    const totalJobs = document.getElementById('totalJobs');
    const totalApplications = document.getElementById('totalApplications');
    const sentApplications = document.getElementById('sentApplications');
    const failedApplications = document.getElementById('failedApplications');
    const jobsFound = document.getElementById('jobsFound');
    const applicationsSent = document.getElementById('applicationsSent');
    const applicationsFailed = document.getElementById('applicationsFailed');
    
    // Statistiques globales (depuis la base de données)
    if (totalJobs) totalJobs.textContent = stats.total_jobs || 0;
    if (totalApplications) totalApplications.textContent = stats.total_applications || 0;
    if (sentApplications) sentApplications.textContent = stats.sent_applications || 0;
    if (failedApplications) failedApplications.textContent = stats.failed_applications || 0;
    
    // Statistiques de session actuelle (depuis app_state)
    if (jobsFound) jobsFound.textContent = stats.jobs_found || 0;
    if (applicationsSent) applicationsSent.textContent = stats.applications_sent || 0;
    if (applicationsFailed) applicationsFailed.textContent = stats.applications_failed || 0;
}

// Charger les statistiques initiales
async function loadInitialStats() {
    try {
        const response = await fetch('/api/stats');
        if (response.ok) {
            const stats = await response.json();
            updateStats(stats);
        }
    } catch (error) {
        console.error('Erreur chargement stats:', error);
    }
}

// Générer les CVs
async function generateCVs() {
    try {
        addLog('📄 Génération des CVs en cours...', 'info');
        const response = await fetch('/api/generate_cvs', { method: 'POST' });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success) {
            addLog(`✅ ${data.count} CV(s) généré(s) avec succès`, 'success');
            if (typeof showToast === 'function') {
                showToast(`${data.count} CV(s) généré(s)`, 'success');
            }
        } else {
            throw new Error(data.error || 'Erreur lors de la génération');
        }
    } catch (error) {
        addLog(`❌ Erreur lors de la génération des CVs: ${error.message}`, 'error');
        if (typeof showToast === 'function') {
            showToast(`Erreur: ${error.message}`, 'error');
        } else {
            alert(`Erreur: ${error.message}`);
        }
    }
}

// Rechercher des offres
async function scrapeJobs() {
    // Vérifier si on est sur la page jobs, si oui utiliser les champs existants
    const jobsQuery = document.getElementById('jobsSearchQuery');
    const jobsLocation = document.getElementById('jobsSearchLocation');
    
    let query, location;
    
    if (jobsQuery && jobsLocation) {
        query = jobsQuery.value.trim();
        location = jobsLocation.value.trim();
    } else {
        // Sinon, ouvrir un modal ou utiliser des valeurs par défaut
        query = prompt('Mots-clés de recherche:', 'développeur python');
        if (!query) return;
        
        location = prompt('Localisation:', 'Rennes');
        if (!location) return;
    }
    
    if (!query || !location) {
        if (typeof showToast === 'function') {
            showToast('Veuillez remplir les champs de recherche', 'warning');
        } else {
            alert('Veuillez remplir les champs de recherche');
        }
        return;
    }
    
    try {
        addLog(`🔍 Démarrage de la recherche: "${query}" à ${location}...`, 'info');
        const response = await fetch('/api/scrape_jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, location, max_results: 50 })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success) {
            addLog('✅ Recherche d\'offres démarrée avec succès', 'success');
            if (typeof showToast === 'function') {
                showToast('Recherche d\'offres démarrée', 'success');
            }
        } else {
            throw new Error(data.error || 'Erreur inconnue');
        }
    } catch (error) {
        addLog(`❌ Erreur lors de la recherche: ${error.message}`, 'error');
        if (typeof showToast === 'function') {
            showToast(`Erreur: ${error.message}`, 'error');
        } else {
            alert(`Erreur: ${error.message}`);
        }
    }
}

// Modal Auto Apply
function showAutoApplyModal() {
    const modal = document.getElementById('autoApplyModal');
    if (modal) {
        modal.classList.add('active');
        renderModalPersonas();
    }
}

function closeAutoApplyModal() {
    const modal = document.getElementById('autoApplyModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

async function renderModalPersonas() {
    const container = document.getElementById('modalPersonasList');
    if (!container) return;
    
    await loadPersonas();
    let html = '';
    
    for (const [key, persona] of Object.entries(allPersonas)) {
        if (persona.alias) continue;
        const isSelected = selectedPersonas.has(persona.email);
        html += `
            <div style="padding: 8px; margin: 5px 0; background: var(--border-color); border-radius: 5px;">
                <input type="checkbox" id="modal-persona-${key}" ${isSelected ? 'checked' : ''} 
                       onchange="toggleModalPersona('${persona.email}', ${isSelected})">
                <label for="modal-persona-${key}" style="margin-left: 8px; cursor: pointer;">
                    <strong>${persona.name}</strong> (${persona.email})
                </label>
            </div>
        `;
    }
    
    container.innerHTML = html || '<p>Aucun persona disponible</p>';
    updateModalPersonasCount();
}

function toggleModalPersona(email, wasSelected) {
    if (wasSelected) {
        selectedPersonas.delete(email);
    } else {
        selectedPersonas.add(email);
    }
    updateModalPersonasCount();
}

function updateModalPersonasCount() {
    const count = selectedPersonas.size;
    const countElement = document.getElementById('modalPersonasCount');
    if (countElement) {
        countElement.textContent = count;
    }
}

async function startAutoApplyFromModal() {
    const query = document.getElementById('modalQuery')?.value || '';
    const location = document.getElementById('modalLocation')?.value || '';
    
    if (!query || !location) {
        if (typeof showToast === 'function') {
            showToast('Veuillez remplir tous les champs', 'warning');
        } else {
            alert('Veuillez remplir tous les champs');
        }
        return;
    }
    
    if (selectedPersonas.size === 0) {
        if (typeof showToast === 'function') {
            showToast('Veuillez sélectionner au moins un persona', 'warning');
        } else {
            alert('Veuillez sélectionner au moins un persona');
        }
        return;
    }
    
    try {
        addLog('🚀 Démarrage de Auto Apply...', 'info');
        const response = await fetch('/api/start_auto_apply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                location,
                personas: Array.from(selectedPersonas)
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success) {
            addLog('✅ Auto Apply démarré avec succès', 'success');
            if (typeof showToast === 'function') {
                showToast('Auto Apply démarré', 'success');
            }
            closeAutoApplyModal();
            // Mettre à jour l'état
            if (typeof updateStatusUI === 'function') {
                updateStatusUI('running', true);
            }
        } else {
            throw new Error(data.error || 'Erreur lors du démarrage');
        }
    } catch (error) {
        addLog(`❌ Erreur lors du démarrage: ${error.message}`, 'error');
        if (typeof showToast === 'function') {
            showToast(`Erreur: ${error.message}`, 'error');
        } else {
            alert(`Erreur: ${error.message}`);
        }
    }
}

async function stopAutoApply() {
    if (!confirm('Êtes-vous sûr de vouloir arrêter le processus Auto Apply ?')) {
        return;
    }
    
    try {
        addLog('⏹️ Arrêt du processus Auto Apply...', 'warning');
        const response = await fetch('/api/stop_auto_apply', { method: 'POST' });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success) {
            addLog('✅ Auto Apply arrêté avec succès', 'success');
            if (typeof showToast === 'function') {
                showToast('Auto Apply arrêté', 'success');
            }
            // Mettre à jour l'état
            if (typeof updateStatusUI === 'function') {
                updateStatusUI('ready', false);
            }
        } else {
            throw new Error(data.error || 'Erreur lors de l\'arrêt');
        }
    } catch (error) {
        addLog(`❌ Erreur lors de l'arrêt: ${error.message}`, 'error');
        if (typeof showToast === 'function') {
            showToast(`Erreur: ${error.message}`, 'error');
        } else {
            alert(`Erreur: ${error.message}`);
        }
    }
}

// Variables pour le test de candidature
let selectedTestJob = null;
let allJobsForTest = [];

// Modal Test Application
function showTestApplicationModal() {
    const modal = document.getElementById('testApplicationModal');
    if (modal) {
        modal.classList.add('active');
        // Charger les personas dans le select
        loadTestPersonas();
        // Charger les offres existantes
        loadExistingJobsForTest();
        // Réinitialiser
        selectedTestJob = null;
        document.getElementById('testMode').value = 'url';
        toggleTestMode();
    } else {
        alert('Modal de test de candidature non trouvé. Veuillez recharger la page.');
    }
}

function closeTestApplicationModal() {
    const modal = document.getElementById('testApplicationModal');
    if (modal) {
        modal.classList.remove('active');
    }
    selectedTestJob = null;
}

function toggleTestMode() {
    const mode = document.getElementById('testMode')?.value;
    const urlSection = document.getElementById('testModeUrl');
    const searchSection = document.getElementById('testModeSearch');
    const existingSection = document.getElementById('testModeExisting');
    
    // Masquer toutes les sections
    if (urlSection) urlSection.style.display = 'none';
    if (searchSection) searchSection.style.display = 'none';
    if (existingSection) existingSection.style.display = 'none';
    
    // Afficher la section correspondante
    if (mode === 'url' && urlSection) {
        urlSection.style.display = 'block';
    } else if (mode === 'search' && searchSection) {
        searchSection.style.display = 'block';
    } else if (mode === 'existing' && existingSection) {
        existingSection.style.display = 'block';
        loadExistingJobsForTest();
    }
}

async function loadTestPersonas() {
    const select = document.getElementById('testPersona');
    if (!select) return;
    
    try {
        await loadPersonas();
        select.innerHTML = '<option value="">Sélectionner un persona</option>';
        for (const [key, persona] of Object.entries(allPersonas)) {
            if (!persona.alias) {
                select.innerHTML += `<option value="${persona.email}">${persona.name} (${persona.email})</option>`;
            }
        }
    } catch (error) {
        console.error('Erreur chargement personas:', error);
        select.innerHTML = '<option value="">Erreur de chargement</option>';
    }
}

async function loadExistingJobsForTest() {
    const container = document.getElementById('testExistingJobsList');
    if (!container) return;
    
    try {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">⏳ Chargement des offres...</p>';
        
        const response = await fetch('/api/jobs?limit=100');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const jobs = await response.json();
        allJobsForTest = Array.isArray(jobs) ? jobs : [];
        
        renderExistingJobsForTest();
    } catch (error) {
        console.error('Erreur chargement offres:', error);
        container.innerHTML = `<p style="text-align: center; color: var(--error);">Erreur: ${error.message}</p>`;
    }
}

function renderExistingJobsForTest(filter = '') {
    const container = document.getElementById('testExistingJobsList');
    if (!container) return;
    
    let jobsToShow = allJobsForTest;
    if (filter) {
        const filterLower = filter.toLowerCase();
        jobsToShow = allJobsForTest.filter(job => 
            (job.title && job.title.toLowerCase().includes(filterLower)) ||
            (job.company && job.company.toLowerCase().includes(filterLower)) ||
            (job.location && job.location.toLowerCase().includes(filterLower))
        );
    }
    
    if (jobsToShow.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Aucune offre trouvée</p>';
        return;
    }
    
    let html = '';
    jobsToShow.slice(0, 20).forEach(job => {
        const isSelected = selectedTestJob && selectedTestJob.id === job.id;
        html += `
            <div class="job-item-test" onclick="selectJobForTest(${job.id})" style="
                padding: 15px;
                margin-bottom: 10px;
                border: 2px solid ${isSelected ? 'var(--text-title)' : 'var(--border-color)'};
                border-radius: 10px;
                background: ${isSelected ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)' : 'var(--bg-card)'};
                cursor: pointer;
                transition: all 0.3s ease;
            " onmouseenter="this.style.borderColor='var(--text-title)'; this.style.transform='translateX(5px)'" 
               onmouseleave="if (!${isSelected}) { this.style.borderColor='var(--border-color)'; this.style.transform='translateX(0)' }">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <div style="flex: 1;">
                        <strong style="color: var(--text-primary); font-size: 1.05em; display: block; margin-bottom: 5px;">${job.title || 'Sans titre'}</strong>
                        <div style="color: var(--text-secondary); font-size: 0.9em;">
                            <span>🏢 ${job.company || 'N/A'}</span> | 
                            <span>📍 ${job.location || 'N/A'}</span>
                        </div>
                    </div>
                    ${isSelected ? '<span style="color: var(--success); font-size: 1.5em;">✓</span>' : ''}
                </div>
                ${job.url ? `<a href="${job.url}" target="_blank" style="color: var(--text-title); font-size: 0.85em; text-decoration: none;">🔗 Voir l'offre</a>` : ''}
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function filterExistingJobsForTest() {
    const filter = document.getElementById('testExistingSearch')?.value || '';
    renderExistingJobsForTest(filter);
}

function selectJobForTest(jobId) {
    selectedTestJob = allJobsForTest.find(job => job.id === jobId);
    renderExistingJobsForTest(document.getElementById('testExistingSearch')?.value || '');
}

async function searchJobForTest() {
    const query = document.getElementById('testSearchQuery')?.value;
    const location = document.getElementById('testSearchLocation')?.value;
    const platform = document.getElementById('testSearchPlatform')?.value;
    const resultsContainer = document.getElementById('testSearchResults');
    
    if (!query || !location) {
        alert('Veuillez remplir les mots-clés et la localisation');
        return;
    }
    
    if (!resultsContainer) return;
    
    try {
        resultsContainer.style.display = 'block';
        resultsContainer.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">⏳ Recherche en cours...</p>';
        
        const response = await fetch('/api/scrape_jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                query, 
                location, 
                max_results: 10,
                platform: platform || 'indeed'
            })
        });
        
        const data = await response.json();
        if (data.success) {
            // Attendre un peu pour que les offres soient enregistrées
            setTimeout(async () => {
                const jobsResponse = await fetch('/api/jobs?limit=50');
                const jobs = await jobsResponse.json();
                const recentJobs = Array.isArray(jobs) ? jobs.slice(0, 10) : [];
                
                if (recentJobs.length === 0) {
                    resultsContainer.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Aucune offre trouvée. Réessayez dans quelques secondes.</p>';
                    return;
                }
                
                let html = '<p style="margin-bottom: 10px; font-weight: 600; color: var(--text-title);">Sélectionnez une offre :</p>';
                recentJobs.forEach(job => {
                    html += `
                        <div onclick="selectJobFromSearch(${job.id})" style="
                            padding: 12px;
                            margin-bottom: 8px;
                            border: 2px solid var(--border-color);
                            border-radius: 8px;
                            background: var(--bg-card);
                            cursor: pointer;
                            transition: all 0.3s ease;
                        " onmouseenter="this.style.borderColor='var(--text-title)'; this.style.transform='translateX(5px)'" 
                           onmouseleave="this.style.borderColor='var(--border-color)'; this.style.transform='translateX(0)'">
                            <strong style="color: var(--text-primary);">${job.title || 'Sans titre'}</strong><br>
                            <small style="color: var(--text-secondary);">${job.company || 'N/A'} - ${job.location || 'N/A'}</small>
                        </div>
                    `;
                });
                
                resultsContainer.innerHTML = html;
            }, 2000);
        } else {
            resultsContainer.innerHTML = `<p style="text-align: center; color: var(--error);">Erreur: ${data.error || 'Erreur inconnue'}</p>`;
        }
    } catch (error) {
        resultsContainer.innerHTML = `<p style="text-align: center; color: var(--error);">Erreur: ${error.message}</p>`;
    }
}

function selectJobFromSearch(jobId) {
    selectedTestJob = allJobsForTest.find(job => job.id === jobId);
    if (!selectedTestJob) {
        // Charger depuis l'API
        fetch(`/api/jobs`)
            .then(r => r.json())
            .then(jobs => {
                selectedTestJob = jobs.find(job => job.id === jobId);
                if (selectedTestJob) {
                    document.getElementById('testMode').value = 'existing';
                    toggleTestMode();
                    loadExistingJobsForTest();
                }
            });
    } else {
        document.getElementById('testMode').value = 'existing';
        toggleTestMode();
        loadExistingJobsForTest();
    }
}

async function startTestApplication() {
    const mode = document.getElementById('testMode')?.value;
    const personaEmail = document.getElementById('testPersona')?.value;
    const useCoverLetter = document.getElementById('testUseCoverLetter')?.checked;
    const dryRun = document.getElementById('testDryRun')?.checked;
    
    if (!personaEmail) {
        alert('Veuillez sélectionner un persona');
        return;
    }
    
    let platform = '';
    let jobUrl = '';
    
    if (mode === 'url') {
        platform = document.getElementById('testPlatform')?.value;
        jobUrl = document.getElementById('testJobUrl')?.value;
        
        if (!platform || !jobUrl) {
            alert('Veuillez remplir la plateforme et l\'URL');
            return;
        }
    } else if (mode === 'search' || mode === 'existing') {
        if (!selectedTestJob || !selectedTestJob.url) {
            alert('Veuillez sélectionner une offre d\'emploi');
            return;
        }
        jobUrl = selectedTestJob.url;
        platform = selectedTestJob.platform || 'indeed';
    }
    
    try {
        const response = await fetch('/api/test_application', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                platform,
                job_url: jobUrl,
                persona_email: personaEmail,
                use_cover_letter: useCoverLetter,
                dry_run: dryRun
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success) {
            const modeText = dryRun ? '(Mode test - dry run) ' : '';
            addLog(`✅ Test de candidature ${modeText}démarré avec succès`, 'success');
            if (typeof showToast === 'function') {
                showToast(`Test de candidature ${modeText}démarré`, 'success');
            }
            closeTestApplicationModal();
        } else {
            throw new Error(data.error || 'Erreur inconnue');
        }
    } catch (error) {
        addLog(`❌ Erreur lors du test: ${error.message}`, 'error');
        if (typeof showToast === 'function') {
            showToast(`Erreur: ${error.message}`, 'error');
        } else {
            alert(`Erreur: ${error.message}`);
        }
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    loadInitialStats();
    loadActiveSearches();
    addLog('Page chargée', 'success');
    
    // Écouter les événements WebSocket pour les logs
    if (typeof socket !== 'undefined') {
        socket.on('log', (data) => {
            addLog(data.message, data.level, data.timestamp);
        });
        
        socket.on('stats_update', (stats) => {
            updateStats(stats);
        });
    }
});

