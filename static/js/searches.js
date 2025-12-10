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
    if (!search) return;
    
    const history = search.history || [];
    
    let historyHtml = '';
    if (history.length === 0) {
        historyHtml = '<p class="history-empty">Aucune exécution enregistrée</p>';
    } else {
        history.slice(-10).reverse().forEach((run, idx) => {
            historyHtml += `
                <div class="history-item">
                    <div class="history-item-header">
                        <strong class="history-item-title">Exécution #${history.length - idx}</strong>
                        <span class="history-item-date">${new Date(run.timestamp).toLocaleString('fr-FR')}</span>
                    </div>
                    ${run.stats ? `
                        <div style="margin-top: 10px; padding: 10px; background: var(--bg-card); border-radius: 5px;">
                            <strong style="color: var(--text-title);">Statistiques:</strong>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 8px;">
                                <div><span style="color: var(--text-secondary);">Offres trouvées:</span> <strong>${run.stats.jobs_found || 0}</strong></div>
                                <div><span style="color: var(--text-secondary);">Candidatures:</span> <strong>${run.stats.applications_sent || 0}</strong></div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        });
    }
    
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 900px; max-height: 90vh; overflow-y: auto;">
            <div class="modal-header">
                <h2 style="color: var(--text-title);">📊 Détails de la recherche: ${search.name}</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">✕</button>
            </div>
            <div style="padding: 20px;">
                <div style="margin-bottom: 20px;">
                    <h3 style="color: var(--text-title); margin-bottom: 10px;">Informations générales</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div><strong>Requête:</strong> ${search.query || 'N/A'}</div>
                        <div><strong>Localisation:</strong> ${search.location || 'N/A'}</div>
                        <div><strong>Type:</strong> ${search.job_type || 'Tous'}</div>
                        <div><strong>Statut:</strong> ${search.enabled !== false ? '<span style="color: var(--success);">✓ Activée</span>' : '<span style="color: var(--error);">✗ Désactivée</span>'}</div>
                    </div>
                </div>
                <div>
                    <h3 style="color: var(--text-title); margin-bottom: 10px;">Historique des exécutions</h3>
                    <div style="max-height: 400px; overflow-y: auto;">
                        ${historyHtml}
                    </div>
                </div>
            </div>
        </div>
    `;
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
