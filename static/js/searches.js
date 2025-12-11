/**
 * JavaScript pour la page Searches
 */

let allSearches = {};
let selectedSearches = new Set();
let currentSearchKey = null;
let searchAssignedPersonas = new Set();
let searchExcludedPersonas = new Set();
let allPersonas = {};
let currentPage = 1;
let itemsPerPage = 10;

// Charger les recherches au démarrage
document.addEventListener('DOMContentLoaded', () => {
    showLoader('searchesList', 'Chargement des recherches...');
    loadAllSearches();
});

// Fonction pour afficher un loader
function showLoader(containerId, message = 'Chargement...') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="searches-loading">
            <div class="loading-icon">⏳</div>
            <p class="loading-message">${message}</p>
            <div style="margin-top: 20px;">
                <div class="loading-spinner"></div>
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

async function loadAllSearches() {
    try {
        showLoader('searchesList', 'Chargement des recherches...');
        const response = await fetch('/api/searches');
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        allSearches = await response.json();
        currentPage = 1;
        renderSearchesList();
    } catch (error) {
        console.error('Erreur chargement recherches:', error);
        const container = document.getElementById('searchesList');
        if (container) {
            container.innerHTML = `
                <div class="error-container">
                    <div class="error-icon">❌</div>
                    <h3>Erreur lors du chargement</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary error-message" onclick="loadAllSearches()">🔄 Réessayer</button>
                </div>
            `;
        }
    }
}

async function loadEnabledSearches() {
    try {
        showLoader('searchesList', 'Chargement des recherches activées...');
        const response = await fetch('/api/searches/enabled');
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        allSearches = await response.json();
        currentPage = 1;
        renderSearchesList();
    } catch (error) {
        console.error('Erreur chargement recherches activées:', error);
        const container = document.getElementById('searchesList');
        if (container) {
            container.innerHTML = `
                <div class="error-container">
                    <div class="error-icon">❌</div>
                    <h3>Erreur lors du chargement</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary error-message" onclick="loadEnabledSearches()">🔄 Réessayer</button>
                </div>
            `;
        }
    }
}

function renderSearchesList() {
    const container = document.getElementById('searchesList');
    if (!container) {
        console.error('Élément searchesList non trouvé');
        return;
    }
    
    const searchesArray = Object.entries(allSearches);
    const totalItems = searchesArray.length;
    
    if (totalItems === 0) {
        container.innerHTML = `
            <div class="empty-container">
                <div class="empty-icon">🔍</div>
                <h3 class="empty-title">Aucune recherche trouvée</h3>
                <p>Créez votre première recherche pour commencer</p>
                <button class="btn btn-primary empty-action" onclick="showCreateSearchModal()">➕ Créer une recherche</button>
            </div>
        `;
        return;
    }
    
    // Calcul de la pagination
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedSearches = searchesArray.slice(startIndex, endIndex);
    
    let html = '';
    
    for (const [key, search] of paginatedSearches) {
        const isSelected = selectedSearches.has(key);
        const isEnabled = search.enabled !== false;
        const personasAssigned = search.personas_assigned || [];
        const personasExcluded = search.personas_excluded || [];
        const history = search.history || [];
        const lastRun = history.length > 0 ? history[history.length - 1] : null;
        const gradientColor = isEnabled ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)';
        
        html += `
            <div class="search-card-ultra-modern ${isSelected ? 'selected' : ''} ${isEnabled ? 'search-card-enabled' : ''}">
                <!-- Header avec gradient -->
                <div class="search-card-header ${isEnabled ? 'search-card-header-enabled' : 'search-card-header-disabled'}">
                    <div class="search-card-header-overlay"></div>
                    <div class="search-card-header-content">
                        <div class="search-card-header-left">
                            <input type="checkbox" id="search-${key}" ${isSelected ? 'checked' : ''} 
                                   onchange="event.stopPropagation(); toggleSearch('${key}', ${isSelected})"
                                   class="search-card-checkbox"
                                   onclick="event.stopPropagation();">
                            <div class="search-card-title-wrapper">
                                <h3 class="search-card-title">${search.name || 'Sans nom'}</h3>
                                <div class="search-card-badges">
                                    <span class="search-card-badge">${isEnabled ? '✓ Activée' : '✗ Désactivée'}</span>
                                    ${search.standalone ? `<span class="search-card-badge">🔍 Standalone</span>` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Contenu principal -->
                <div class="search-card-body">
                    <!-- Requête et localisation -->
                    <div class="search-card-info-section">
                        <div class="search-card-info-item search-card-info-item-query">
                            <div class="search-card-info-icon">🔍</div>
                            <div class="search-card-info-content">
                                <div class="search-card-info-label">Recherche</div>
                                <div class="search-card-info-value">${search.query || 'N/A'}</div>
                            </div>
                        </div>
                        <div class="search-card-info-item search-card-info-item-location">
                            <div class="search-card-info-icon search-card-info-icon-location">📍</div>
                            <div class="search-card-info-content">
                                <div class="search-card-info-label">Localisation</div>
                                <div class="search-card-info-value">${search.location || 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Actions -->
                    <div class="search-card-actions">
                        <button onclick="event.stopPropagation(); showSearchDetails('${key}')" class="search-card-action-btn">
                            📊 Détails
                        </button>
                        <button onclick="event.stopPropagation(); editSearch('${key}')" class="search-card-action-btn search-card-action-btn-edit">
                            ✏️ Modifier
                        </button>
                        <button onclick="event.stopPropagation(); duplicateSearch('${key}')" class="search-card-action-btn search-card-action-btn-duplicate">
                            📋 Dupliquer
                        </button>
                        <button onclick="event.stopPropagation(); deleteSearch('${key}')" class="search-card-action-btn search-card-action-btn-delete">
                            🗑️ Supprimer
                        </button>
                    </div>
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
            let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
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
            <div class="pagination-container">
                <div class="pagination-wrapper">
                    <button class="pagination-btn-nav" 
                            onclick="changePage(${currentPage - 1})" 
                            ${currentPage === 1 ? 'disabled' : ''}>
                        <span class="pagination-icon">←</span>
                        <span class="pagination-text">Précédent</span>
                    </button>
                    
                    <div class="pagination-numbers">
                        ${pageNumbers.map(page => {
                            if (page === '...') {
                                return '<span class="pagination-ellipsis">...</span>';
                            }
                            const isActive = page === currentPage;
                            return `
                                <button class="pagination-btn-number ${isActive ? 'active' : ''}" 
                                        onclick="changePage(${page})"
                                        ${isActive ? 'aria-current="page"' : ''}>
                                    ${page}
                                </button>
                            `;
                        }).join('')}
                    </div>
                    
                    <button class="pagination-btn-nav" 
                            onclick="changePage(${currentPage + 1})" 
                            ${currentPage === totalPages ? 'disabled' : ''}>
                        <span class="pagination-text">Suivant</span>
                        <span class="pagination-icon">→</span>
                    </button>
                </div>
                
                <div class="pagination-info">
                    <span class="pagination-info-text">
                        Page <strong>${currentPage}</strong> sur <strong>${totalPages}</strong>
                    </span>
                    <span class="pagination-info-count">
                        (${totalItems} recherche${totalItems > 1 ? 's' : ''})
                    </span>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
    updateSelectedSearchesCount();
}

function changePage(page) {
    const totalPages = Math.ceil(Object.keys(allSearches).length / itemsPerPage);
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    renderSearchesList();
    
    // Scroll vers la liste des recherches en gardant la position relative
    setTimeout(() => {
        const searchesList = document.getElementById('searchesList');
        if (searchesList) {
            // Trouver le conteneur parent (la card ou le conteneur principal)
            const container = searchesList.closest('.card') || searchesList.closest('.main-content');
            if (container) {
                const containerTop = container.getBoundingClientRect().top + window.pageYOffset;
                // Scroll vers le conteneur en gardant un peu d'espace en haut
                window.scrollTo({ top: containerTop - 20, behavior: 'smooth' });
            } else {
                // Fallback: scroll vers la liste avec block: 'nearest' pour éviter de remonter trop haut
                searchesList.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }
    }, 100);
}

function toggleSearch(searchKey, wasSelected) {
    if (wasSelected) {
        selectedSearches.delete(searchKey);
    } else {
        selectedSearches.add(searchKey);
    }
    renderSearchesList();
    updateSelectedSearchesCount();
}

function selectAllSearches() {
    Object.keys(allSearches).forEach(key => {
        selectedSearches.add(key);
    });
    renderSearchesList();
    updateSelectedSearchesCount();
}

function deselectAllSearches() {
    selectedSearches.clear();
    renderSearchesList();
    updateSelectedSearchesCount();
}

function toggleAllSearchesEnabled() {
    const allSelected = Object.keys(allSearches).length === selectedSearches.size && selectedSearches.size > 0;
    if (allSelected) {
        Array.from(selectedSearches).forEach(async (key) => {
            try {
                const search = allSearches[key];
                await fetch(`/api/searches/${key}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ...search, enabled: false })
                });
            } catch (error) {
                console.error(`Erreur désactivation recherche ${key}:`, error);
            }
        });
        loadAllSearches();
    } else {
        Array.from(selectedSearches).forEach(async (key) => {
            try {
                const search = allSearches[key];
                await fetch(`/api/searches/${key}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ...search, enabled: true })
                });
            } catch (error) {
                console.error(`Erreur activation recherche ${key}:`, error);
            }
        });
        loadAllSearches();
    }
}

function updateSelectedSearchesCount() {
    const count = selectedSearches.size;
    const countElement = document.getElementById('selectedSearchesCount');
    if (countElement) {
        countElement.textContent = `${count} sélectionnée(s)`;
    }
}

async function showSearchDetails(searchKey) {
    const search = allSearches[searchKey];
    if (!search) {
        console.error('Recherche non trouvée:', searchKey);
        return;
    }
    
    // Récupérer l'historique complet depuis l'API
    let history = [];
    try {
        const historyResponse = await fetch(`/api/searches/${searchKey}/history`);
        if (historyResponse.ok) {
            const historyData = await historyResponse.json();
            history = historyData.history || [];
        }
    } catch (error) {
        console.error('Erreur récupération historique:', error);
        history = search.history || [];
    }
    
    let historyHtml = '';
    if (history.length === 0) {
        historyHtml = `
            <div style="padding: 40px; text-align: center; color: var(--text-secondary);">
                <div style="font-size: 3em; margin-bottom: 15px;">📋</div>
                <p style="font-size: 1.1em; margin-bottom: 10px;">Aucune exécution enregistrée</p>
                <p style="font-size: 0.9em; opacity: 0.7;">L'historique apparaîtra ici après la première exécution de cette recherche</p>
            </div>
        `;
    } else {
        history.slice(-10).reverse().forEach((run, idx) => {
            const runDate = run.timestamp ? new Date(run.timestamp).toLocaleString('fr-FR') : 'Date inconnue';
            const jobsFound = run.jobs_found || 0;
            const jobsFiltered = run.jobs_filtered || 0;
            const applicationsSent = run.applications_sent || 0;
            const applicationsFailed = run.applications_failed || 0;
            const duration = run.duration_seconds ? `${Math.round(run.duration_seconds)}s` : 'N/A';
            const personasUsed = run.personas_used || [];
            const errors = run.errors || [];
            const steps = run.steps || [];
            
            historyHtml += `
                <div style="padding: 20px; margin-bottom: 15px; background: var(--bg-card); border-radius: 12px; border-left: 5px solid var(--primary); box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 2px solid var(--border-color);">
                        <div>
                            <strong style="color: var(--text-title); font-size: 1.1em;">Exécution #${history.length - idx}</strong>
                            <div style="color: var(--text-secondary); font-size: 0.85em; margin-top: 5px;">⏱️ Durée: ${duration}</div>
                        </div>
                        <span style="color: var(--text-secondary); font-size: 0.9em;">${runDate}</span>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 15px;">
                        <div style="padding: 12px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%); border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.2);">
                            <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 5px;">🔍 Offres trouvées</div>
                            <div style="color: var(--text-title); font-size: 1.5em; font-weight: 700;">${jobsFound}</div>
                        </div>
                        ${jobsFiltered > 0 ? `
                        <div style="padding: 12px; background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%); border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.2);">
                            <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 5px;">🔎 Offres filtrées</div>
                            <div style="color: var(--text-title); font-size: 1.5em; font-weight: 700;">${jobsFiltered}</div>
                        </div>
                        ` : ''}
                        <div style="padding: 12px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%); border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
                            <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 5px;">✅ Candidatures envoyées</div>
                            <div style="color: var(--success); font-size: 1.5em; font-weight: 700;">${applicationsSent}</div>
                        </div>
                        ${applicationsFailed > 0 ? `
                        <div style="padding: 12px; background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%); border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.2);">
                            <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 5px;">❌ Candidatures échouées</div>
                            <div style="color: var(--error); font-size: 1.5em; font-weight: 700;">${applicationsFailed}</div>
                        </div>
                        ` : ''}
                    </div>
                    
                    ${personasUsed.length > 0 ? `
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border-color);">
                        <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 8px;">👤 Personas utilisés (${personasUsed.length}):</div>
                        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                            ${personasUsed.map(email => `<span style="padding: 4px 10px; background: var(--primary); color: white; border-radius: 6px; font-size: 0.85em;">${email}</span>`).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${errors.length > 0 ? `
                    <div style="margin-top: 15px; padding: 12px; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border-left: 3px solid var(--error);">
                        <div style="color: var(--error); font-weight: 600; margin-bottom: 8px;">⚠️ Erreurs (${errors.length}):</div>
                        <div style="color: var(--text-body); font-size: 0.9em;">
                            ${errors.slice(0, 3).map(err => `<div style="margin: 4px 0;">• ${typeof err === 'string' ? err : JSON.stringify(err)}</div>`).join('')}
                            ${errors.length > 3 ? `<div style="margin-top: 5px; color: var(--text-secondary); font-size: 0.85em;">... et ${errors.length - 3} autre(s)</div>` : ''}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${steps.length > 0 ? `
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border-color);">
                        <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 8px;">📝 Étapes:</div>
                        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                            ${steps.map(step => `<span style="padding: 4px 10px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 6px; font-size: 0.85em; color: var(--text-body);">${typeof step === 'string' ? step : JSON.stringify(step)}</span>`).join('')}
                        </div>
                    </div>
                    ` : ''}
                </div>
            `;
        });
    }
    
    // Utiliser les bons noms de champs
    const isActive = search.is_active !== false && search.enabled !== false;
    const searchType = search.search_type || search.job_type || 'Tous';
    const personasAssigned = search.personas_assigned || [];
    const personasExcluded = search.personas_excluded || [];
    const tags = search.tags || [];
    const contractTypes = search.contract_type || [];
    
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 900px; max-height: 90vh; overflow-y: auto;">
            <div class="modal-header">
                <h2 style="color: var(--text-title); margin: 0;">📊 Détails de la recherche: ${search.name || 'Sans nom'}</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">✕</button>
            </div>
            <div style="padding: 20px;">
                <!-- Informations générales -->
                <div style="margin-bottom: 30px;">
                    <h3 style="color: var(--text-title); margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid var(--border-color);">📋 Informations générales</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 5px;">Requête</div>
                            <div style="color: var(--text-title); font-weight: 500;">${search.query || 'N/A'}</div>
                        </div>
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 5px;">Localisation</div>
                            <div style="color: var(--text-title); font-weight: 500;">${search.location || 'N/A'}</div>
                        </div>
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 5px;">Type de recherche</div>
                            <div style="color: var(--text-title); font-weight: 500;">${searchType}</div>
                        </div>
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 5px;">Statut</div>
                            <div style="color: ${isActive ? 'var(--success)' : 'var(--error)'}; font-weight: 500;">
                                ${isActive ? '✓ Activée' : '✗ Désactivée'}
                            </div>
                        </div>
                        ${search.max_results ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 5px;">Résultats max</div>
                            <div style="color: var(--text-title); font-weight: 500;">${search.max_results}</div>
                        </div>
                        ` : ''}
                        ${search.standalone ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 5px;">Mode</div>
                            <div style="color: var(--text-title); font-weight: 500;">🔍 Standalone</div>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Description -->
                ${search.description ? `
                <div style="margin-bottom: 30px;">
                    <h3 style="color: var(--text-title); margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid var(--border-color);">📝 Description</h3>
                    <div style="padding: 15px; background: var(--bg-card); border-radius: 8px; color: var(--text-body);">
                        ${search.description}
                    </div>
                </div>
                ` : ''}
                
                <!-- Mots-clés -->
                ${(search.title_keywords && search.title_keywords.length > 0) || (search.exclude_keywords && search.exclude_keywords.length > 0) ? `
                <div style="margin-bottom: 30px;">
                    <h3 style="color: var(--text-title); margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid var(--border-color);">🔑 Mots-clés</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">
                        ${search.title_keywords && search.title_keywords.length > 0 ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 8px;">Mots-clés titre</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                                ${search.title_keywords.map(kw => `<span style="padding: 4px 8px; background: var(--primary); color: white; border-radius: 4px; font-size: 0.85em;">${kw}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        ${search.exclude_keywords && search.exclude_keywords.length > 0 ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 8px;">Mots-clés exclus</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                                ${search.exclude_keywords.map(kw => `<span style="padding: 4px 8px; background: var(--error); color: white; border-radius: 4px; font-size: 0.85em;">${kw}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
                ` : ''}
                
                <!-- Personas -->
                ${personasAssigned.length > 0 || personasExcluded.length > 0 ? `
                <div style="margin-bottom: 30px;">
                    <h3 style="color: var(--text-title); margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid var(--border-color);">👤 Personas</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">
                        ${personasAssigned.length > 0 ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 8px;">Personas assignés</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                                ${personasAssigned.map(email => `<span style="padding: 4px 8px; background: var(--success); color: white; border-radius: 4px; font-size: 0.85em;">${email}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        ${personasExcluded.length > 0 ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 8px;">Personas exclus</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                                ${personasExcluded.map(email => `<span style="padding: 4px 8px; background: var(--error); color: white; border-radius: 4px; font-size: 0.85em;">${email}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
                ` : ''}
                
                <!-- Tags et autres détails -->
                ${tags.length > 0 || contractTypes.length > 0 || search.experience_level || search.remote !== undefined || search.full_time !== undefined ? `
                <div style="margin-bottom: 30px;">
                    <h3 style="color: var(--text-title); margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid var(--border-color);">🏷️ Détails supplémentaires</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        ${tags.length > 0 ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 8px;">Tags</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                                ${tags.map(tag => `<span style="padding: 4px 8px; background: var(--primary); color: white; border-radius: 4px; font-size: 0.85em;">${tag}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        ${contractTypes.length > 0 ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 8px;">Types de contrat</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                                ${contractTypes.map(ct => `<span style="padding: 4px 8px; background: var(--primary); color: white; border-radius: 4px; font-size: 0.85em;">${ct}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        ${search.experience_level ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 5px;">Niveau d'expérience</div>
                            <div style="color: var(--text-title); font-weight: 500;">${search.experience_level}</div>
                        </div>
                        ` : ''}
                        ${search.remote !== undefined ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 5px;">Télétravail</div>
                            <div style="color: var(--text-title); font-weight: 500;">${search.remote ? '✓ Oui' : '✗ Non'}</div>
                        </div>
                        ` : ''}
                        ${search.full_time !== undefined ? `
                        <div style="padding: 10px; background: var(--bg-card); border-radius: 8px;">
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 5px;">Temps plein</div>
                            <div style="color: var(--text-title); font-weight: 500;">${search.full_time ? '✓ Oui' : '✗ Non'}</div>
                        </div>
                        ` : ''}
                    </div>
                </div>
                ` : ''}
                
                <!-- Historique -->
                <div>
                    <h3 style="color: var(--text-title); margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid var(--border-color);">📜 Historique des exécutions</h3>
                    <div style="max-height: 400px; overflow-y: auto;">
                        ${historyHtml}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Gérer la fermeture du modal
    const closeModal = () => {
        modal.remove();
    };
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    const closeBtn = modal.querySelector('.modal-close');
    if (closeBtn) {
        closeBtn.onclick = closeModal;
    }
    
    document.body.appendChild(modal);
}

// Fonctions pour les modals (à compléter selon les besoins)
function showCreateSearchModal() {
    alert('Fonction à implémenter');
}

function editSearch(key) {
    alert('Fonction à implémenter');
}

function duplicateSearch(key) {
    alert('Fonction à implémenter');
}

async function deleteSearch(key) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette recherche ?')) return;
    
    try {
        const response = await fetch(`/api/searches/${key}`, { method: 'DELETE' });
        if (response.ok) {
            loadAllSearches();
        } else {
            alert('Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur suppression:', error);
        alert('Erreur lors de la suppression');
    }
}
