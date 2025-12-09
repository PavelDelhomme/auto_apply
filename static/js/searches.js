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
        <div style="text-align: center; padding: 60px 20px; color: var(--text-secondary); grid-column: 1 / -1;">
            <div style="font-size: 3em; margin-bottom: 15px; animation: pulse 2s infinite;">⏳</div>
            <p style="font-size: 1.1em; color: var(--text-primary);">${message}</p>
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
                <div style="text-align: center; padding: 60px 20px; color: var(--error); grid-column: 1 / -1;">
                    <div style="font-size: 3em; margin-bottom: 15px;">❌</div>
                    <h3>Erreur lors du chargement</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary" onclick="loadAllSearches()" style="margin-top: 20px;">🔄 Réessayer</button>
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
                <div style="text-align: center; padding: 60px 20px; color: var(--error); grid-column: 1 / -1;">
                    <div style="font-size: 3em; margin-bottom: 15px;">❌</div>
                    <h3>Erreur lors du chargement</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary" onclick="loadEnabledSearches()" style="margin-top: 20px;">🔄 Réessayer</button>
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
            <div style="text-align: center; padding: 60px 20px; color: var(--text-secondary); grid-column: 1 / -1;">
                <div style="font-size: 4em; margin-bottom: 20px;">🔍</div>
                <h3 style="color: var(--text-primary); margin-bottom: 10px;">Aucune recherche trouvée</h3>
                <p>Créez votre première recherche pour commencer</p>
                <button class="btn btn-primary" onclick="showCreateSearchModal()" style="margin-top: 20px;">➕ Créer une recherche</button>
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
            <div class="search-card-ultra-modern ${isSelected ? 'selected' : ''}" style="
                background: ${isSelected ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)' : 'var(--bg-card)'};
                border: 2px solid ${isSelected ? 'var(--text-title)' : (isEnabled ? 'rgba(16, 185, 129, 0.3)' : 'var(--border-color)')};
                border-radius: 16px;
                padding: 0;
                margin-bottom: 20px;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: ${isSelected ? '0 8px 24px rgba(102, 126, 234, 0.25), 0 0 0 1px rgba(102, 126, 234, 0.1)' : '0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)'};
                position: relative;
                overflow: hidden;
                cursor: pointer;
            " onmouseenter="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 32px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.08)'" 
               onmouseleave="this.style.transform='translateY(0)'; this.style.boxShadow='${isSelected ? '0 8px 24px rgba(102, 126, 234, 0.25), 0 0 0 1px rgba(102, 126, 234, 0.1)' : '0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)'}'">
                
                <!-- Header avec gradient -->
                <div style="
                    background: ${gradientColor};
                    padding: 20px 24px;
                    color: white;
                    position: relative;
                    overflow: hidden;
                ">
                    <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); pointer-events: none;"></div>
                    
                    <div style="display: flex; align-items: center; justify-content: space-between; position: relative; z-index: 1;">
                        <div style="display: flex; align-items: center; gap: 15px; flex: 1;">
                            <input type="checkbox" id="search-${key}" ${isSelected ? 'checked' : ''} 
                                   onchange="event.stopPropagation(); toggleSearch('${key}', ${isSelected})"
                                   style="width: 22px; height: 22px; cursor: pointer; accent-color: white;"
                                   onclick="event.stopPropagation();">
                            
                            <div style="flex: 1; min-width: 0;">
                                <h3 style="margin: 0 0 8px 0; color: white; font-size: 1.4em; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                    ${search.name || 'Sans nom'}
                                </h3>
                                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                                    <span style="
                                        background: rgba(255,255,255,0.25);
                                        backdrop-filter: blur(10px);
                                        color: white;
                                        padding: 6px 14px;
                                        border-radius: 20px;
                                        font-size: 0.8em;
                                        font-weight: 600;
                                        border: 1px solid rgba(255,255,255,0.3);
                                    ">${isEnabled ? '✓ Activée' : '✗ Désactivée'}</span>
                                    ${search.standalone ? `
                                        <span style="
                                            background: rgba(255,255,255,0.2);
                                            backdrop-filter: blur(10px);
                                            color: white;
                                            padding: 6px 14px;
                                            border-radius: 20px;
                                            font-size: 0.8em;
                                            font-weight: 600;
                                            border: 1px solid rgba(255,255,255,0.3);
                                        ">🔍 Standalone</span>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Contenu principal -->
                <div style="padding: 24px;">
                    <!-- Requête et localisation -->
                    <div style="margin-bottom: 20px;">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; padding: 12px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%); border-radius: 12px; border-left: 4px solid var(--text-title);">
                            <div style="
                                width: 40px;
                                height: 40px;
                                background: var(--text-title);
                                border-radius: 10px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 1.2em;
                                flex-shrink: 0;
                            ">🔍</div>
                            <div style="flex: 1; min-width: 0;">
                                <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Recherche</div>
                                <div style="color: var(--text-primary); font-size: 1.1em; font-weight: 600;">${search.query || 'N/A'}</div>
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.08) 100%); border-radius: 12px; border-left: 4px solid var(--success);">
                            <div style="
                                width: 40px;
                                height: 40px;
                                background: var(--success);
                                border-radius: 10px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 1.2em;
                                flex-shrink: 0;
                            ">📍</div>
                            <div style="flex: 1; min-width: 0;">
                                <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Localisation</div>
                                <div style="color: var(--text-primary); font-size: 1.1em; font-weight: 600;">${search.location || 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Actions -->
                    <div style="
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                        gap: 10px;
                        padding-top: 20px;
                        border-top: 2px solid var(--border-color);
                    ">
                        <button onclick="event.stopPropagation(); showSearchDetails('${key}')" class="btn" style="background: linear-gradient(135deg, var(--info) 0%, #2563eb 100%); color: white;">
                            📊 Détails
                        </button>
                        <button onclick="event.stopPropagation(); editSearch('${key}')" class="btn" style="background: linear-gradient(135deg, var(--text-title) 0%, #5b21b6 100%); color: white;">
                            ✏️ Modifier
                        </button>
                        <button onclick="event.stopPropagation(); duplicateSearch('${key}')" class="btn" style="background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%); color: white;">
                            📋 Dupliquer
                        </button>
                        <button onclick="event.stopPropagation(); deleteSearch('${key}')" class="btn" style="background: linear-gradient(135deg, var(--error) 0%, #dc2626 100%); color: white;">
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
            <div class="pagination-container" style="grid-column: 1 / -1; margin-top: 30px;">
                <div class="pagination-wrapper">
                    <button class="pagination-btn pagination-btn-nav" 
                            onclick="changePage(${currentPage - 1})" 
                            ${currentPage === 1 ? 'disabled' : ''}
                            ${currentPage === 1 ? '' : `onmouseenter="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.4)'" onmouseleave="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(102, 126, 234, 0.3)'"`}>
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
                                <button class="pagination-btn pagination-btn-number ${isActive ? 'active' : ''}" 
                                        onclick="changePage(${page})"
                                        ${isActive ? 'aria-current="page"' : ''}>
                                    ${page}
                                </button>
                            `;
                        }).join('')}
                    </div>
                    
                    <button class="pagination-btn pagination-btn-nav" 
                            onclick="changePage(${currentPage + 1})" 
                            ${currentPage === totalPages ? 'disabled' : ''}
                            ${currentPage === totalPages ? '' : `onmouseenter="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.4)'" onmouseleave="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(102, 126, 234, 0.3)'"`}>
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
    
    // Scroll vers la liste des recherches au lieu du haut de la page
    setTimeout(() => {
        const searchesList = document.getElementById('searchesList');
        if (searchesList) {
            searchesList.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
        historyHtml = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">Aucune exécution enregistrée</p>';
    } else {
        history.slice(-10).reverse().forEach((run, idx) => {
            historyHtml += `
                <div style="padding: 15px; margin-bottom: 10px; background: var(--border-color); border-radius: 8px; border-left: 4px solid var(--text-title);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <strong style="color: var(--text-title);">Exécution #${history.length - idx}</strong>
                        <span style="color: var(--text-secondary); font-size: 0.85em;">${new Date(run.timestamp).toLocaleString('fr-FR')}</span>
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
