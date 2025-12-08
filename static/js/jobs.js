/**
 * JavaScript pour la page Jobs (Offres d'emploi)
 */

let allJobs = [];
let currentJobsFilter = 'all'; // 'all' ou 'unapplied'
let jobsPage = 1;
let jobsPerPage = 20;

// Charger les offres au démarrage
document.addEventListener('DOMContentLoaded', () => {
    loadAllJobs();
});

// Fonction pour afficher un loader
function showJobsLoader(message = 'Chargement des offres...') {
    const container = document.getElementById('jobsList');
    if (!container) return;
    
    container.innerHTML = `
        <div style="text-align: center; padding: 60px 20px; color: var(--text-secondary);">
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

// Charger toutes les offres
async function loadAllJobs() {
    try {
        showJobsLoader('Chargement de toutes les offres...');
        currentJobsFilter = 'all';
        jobsPage = 1;
        
        const response = await fetch('/api/jobs');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const jobs = await response.json();
        allJobs = Array.isArray(jobs) ? jobs : [];
        renderJobs();
        updateJobsCount();
    } catch (error) {
        console.error('Erreur chargement offres:', error);
        const container = document.getElementById('jobsList');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px; color: var(--error);">
                    <div style="font-size: 3em; margin-bottom: 15px;">❌</div>
                    <h3>Erreur lors du chargement</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary" onclick="loadAllJobs()" style="margin-top: 20px;">🔄 Réessayer</button>
                </div>
            `;
        }
    }
}

// Charger uniquement les offres non candidatées
async function loadUnappliedJobs() {
    try {
        showJobsLoader('Chargement des offres non candidatées...');
        currentJobsFilter = 'unapplied';
        jobsPage = 1;
        
        const response = await fetch('/api/jobs?unapplied=true');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const jobs = await response.json();
        allJobs = Array.isArray(jobs) ? jobs : [];
        renderJobs();
        updateJobsCount();
    } catch (error) {
        console.error('Erreur chargement offres non candidatées:', error);
        const container = document.getElementById('jobsList');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px; color: var(--error);">
                    <div style="font-size: 3em; margin-bottom: 15px;">❌</div>
                    <h3>Erreur lors du chargement</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary" onclick="loadUnappliedJobs()" style="margin-top: 20px;">🔄 Réessayer</button>
                </div>
            `;
        }
    }
}

// Afficher les offres
function renderJobs() {
    const container = document.getElementById('jobsList');
    if (!container) return;
    
    if (allJobs.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 20px; color: var(--text-secondary);">
                <div style="font-size: 3em; margin-bottom: 15px;">📭</div>
                <h3>Aucune offre disponible</h3>
                <p>Utilisez le bouton "🔍 Rechercher" pour trouver des offres d'emploi.</p>
            </div>
        `;
        return;
    }
    
    // Pagination
    const totalPages = Math.ceil(allJobs.length / jobsPerPage);
    const startIndex = (jobsPage - 1) * jobsPerPage;
    const endIndex = startIndex + jobsPerPage;
    const paginatedJobs = allJobs.slice(startIndex, endIndex);
    
    let html = `
        <div style="overflow-x: auto;">
            <table class="stats-table" style="width: 100%; min-width: 800px;">
                <thead>
                    <tr>
                        <th>Titre</th>
                        <th>Entreprise</th>
                        <th>Localisation</th>
                        <th>Plateforme</th>
                        <th>Date</th>
                        <th>Statut</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    paginatedJobs.forEach(job => {
        const date = job.created_at ? new Date(job.created_at).toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }) : 'N/A';
        
        const status = job.applied ? 
            '<span style="background: var(--success); color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.85em; font-weight: 600;">✅ Candidaté</span>' :
            '<span style="background: var(--warning); color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.85em; font-weight: 600;">⏳ Non candidaté</span>';
        
        html += `
            <tr style="transition: background 0.2s ease;">
                <td style="font-weight: 600; color: var(--text-primary);">${job.title || 'N/A'}</td>
                <td style="color: var(--text-secondary);">${job.company || 'N/A'}</td>
                <td style="color: var(--text-secondary);">${job.location || 'N/A'}</td>
                <td style="color: var(--text-secondary);">
                    ${job.platform ? `<span style="background: var(--info); color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.8em;">${job.platform}</span>` : 'N/A'}
                </td>
                <td style="color: var(--text-secondary); font-size: 0.9em;">${date}</td>
                <td>${status}</td>
                <td>
                    ${job.url ? `
                        <a href="${job.url}" target="_blank" style="
                            color: var(--text-title);
                            text-decoration: none;
                            padding: 6px 12px;
                            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                            border-radius: 6px;
                            font-weight: 600;
                            font-size: 0.9em;
                            display: inline-block;
                            transition: all 0.3s ease;
                        " onmouseenter="this.style.background='linear-gradient(135deg, var(--text-title) 0%, #5b21b6 100%)'; this.style.color='white';" 
                           onmouseleave="this.style.background='linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)'; this.style.color='var(--text-title)'">
                            🔗 Voir l'offre
                        </a>
                    ` : ''}
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    // Ajouter la pagination
    if (totalPages > 1) {
        html += `
            <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 25px; padding: 20px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%); border-radius: 12px; border: 2px solid var(--border-color);">
                <button class="btn" onclick="changeJobsPage(${jobsPage - 1})" ${jobsPage === 1 ? 'disabled' : ''} style="
                    background: ${jobsPage === 1 ? 'var(--border-color)' : 'linear-gradient(135deg, var(--text-title) 0%, #5b21b6 100%)'};
                    color: ${jobsPage === 1 ? 'var(--text-secondary)' : 'white'};
                    padding: 10px 20px;
                    border-radius: 10px;
                    font-weight: 600;
                    border: none;
                    cursor: ${jobsPage === 1 ? 'not-allowed' : 'pointer'};
                ">
                    ← Précédent
                </button>
                <span style="color: var(--text-primary); font-weight: 700; font-size: 1em; padding: 10px 20px; background: var(--bg-card); border-radius: 10px; border: 2px solid var(--text-title);">
                    Page ${jobsPage} sur ${totalPages} (${allJobs.length} offre${allJobs.length > 1 ? 's' : ''})
                </span>
                <button class="btn" onclick="changeJobsPage(${jobsPage + 1})" ${jobsPage === totalPages ? 'disabled' : ''} style="
                    background: ${jobsPage === totalPages ? 'var(--border-color)' : 'linear-gradient(135deg, var(--text-title) 0%, #5b21b6 100%)'};
                    color: ${jobsPage === totalPages ? 'var(--text-secondary)' : 'white'};
                    padding: 10px 20px;
                    border-radius: 10px;
                    font-weight: 600;
                    border: none;
                    cursor: ${jobsPage === totalPages ? 'not-allowed' : 'pointer'};
                ">
                    Suivant →
                </button>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Changer de page
function changeJobsPage(page) {
    const totalPages = Math.ceil(allJobs.length / jobsPerPage);
    if (page < 1 || page > totalPages) return;
    jobsPage = page;
    renderJobs();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Mettre à jour le compteur
function updateJobsCount() {
    const countElement = document.getElementById('jobsCount');
    if (countElement) {
        countElement.textContent = allJobs.length;
    }
}

// Rechercher des offres
async function scrapeJobs() {
    const queryInput = document.getElementById('jobsSearchQuery');
    const locationInput = document.getElementById('jobsSearchLocation');
    
    if (!queryInput || !locationInput) {
        alert('Champs de recherche non trouvés');
        return;
    }
    
    const query = queryInput.value.trim();
    const location = locationInput.value.trim();
    
    if (!query || !location) {
        alert('Veuillez remplir les champs de recherche et de localisation');
        return;
    }
    
    try {
        showJobsLoader(`Recherche d'offres: "${query}" à ${location}...`);
        
        const response = await fetch('/api/scrape_jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                query, 
                location, 
                max_results: 50 
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Recharger les offres après la recherche
            setTimeout(() => {
                loadAllJobs();
            }, 1000);
        } else {
            throw new Error(data.error || 'Erreur lors de la recherche');
        }
    } catch (error) {
        console.error('Erreur recherche offres:', error);
        const container = document.getElementById('jobsList');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px; color: var(--error);">
                    <div style="font-size: 3em; margin-bottom: 15px;">❌</div>
                    <h3>Erreur lors de la recherche</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary" onclick="scrapeJobs()" style="margin-top: 20px;">🔄 Réessayer</button>
                </div>
            `;
        }
    }
}

// Variables pour l'historique des recherches
let searchHistoryPage = 1;
let searchHistoryPerPage = 20;

// Afficher l'historique des recherches
async function showSearchHistory() {
    const modal = document.getElementById('searchHistoryModal');
    if (modal) {
        modal.classList.add('active');
        await loadSearchHistory();
    }
}

function closeSearchHistoryModal() {
    const modal = document.getElementById('searchHistoryModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

async function loadSearchHistory(page = 1) {
    const container = document.getElementById('searchHistoryList');
    const pagination = document.getElementById('searchHistoryPagination');
    
    if (!container) return;
    
    try {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">⏳ Chargement de l\'historique...</p>';
        
        const response = await fetch(`/api/job-searches?page=${page}&per_page=${searchHistoryPerPage}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        if (!data.success) throw new Error(data.error || 'Erreur inconnue');
        
        const searches = data.searches || [];
        const paginationInfo = data.pagination || {};
        
        if (searches.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Aucune recherche enregistrée</p>';
            if (pagination) pagination.innerHTML = '';
            return;
        }
        
        let html = '<div style="display: grid; gap: 15px;">';
        searches.forEach(search => {
            const date = new Date(search.created_at);
            const dateStr = date.toLocaleString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            html += `
                <div style="
                    padding: 15px;
                    border: 2px solid var(--border-color);
                    border-radius: 10px;
                    background: var(--bg-card);
                    transition: all 0.3s ease;
                    cursor: pointer;
                " onmouseenter="this.style.borderColor='var(--text-title)'; this.style.transform='translateY(-2px)'" 
                   onmouseleave="this.style.borderColor='var(--border-color)'; this.style.transform='translateY(0)'"
                   onclick="relaunchSearch('${search.query}', '${search.location}', ${search.max_results})">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <div style="flex: 1;">
                            <strong style="color: var(--text-primary); font-size: 1.1em; display: block; margin-bottom: 5px;">
                                🔍 ${search.query || 'Sans mots-clés'}
                            </strong>
                            <div style="color: var(--text-secondary); font-size: 0.9em;">
                                📍 ${search.location || 'N/A'} | 
                                📊 ${search.jobs_found || 0} offre(s) trouvée(s) | 
                                🎯 Max: ${search.max_results || 50}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: var(--text-secondary); font-size: 0.85em;">${dateStr}</div>
                            <div style="color: var(--text-secondary); font-size: 0.8em; margin-top: 5px;">
                                ${search.platform || 'indeed'}
                            </div>
                        </div>
                    </div>
                    <button class="btn btn-primary" style="width: 100%; margin-top: 10px;" 
                            onclick="event.stopPropagation(); relaunchSearch('${search.query}', '${search.location}', ${search.max_results})">
                        🔄 Relancer cette recherche
                    </button>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
        
        // Pagination
        if (pagination && paginationInfo.pages > 1) {
            let paginationHtml = '';
            if (paginationInfo.page > 1) {
                paginationHtml += `<button class="btn" onclick="loadSearchHistory(${paginationInfo.page - 1})">◀ Précédent</button>`;
            }
            paginationHtml += `<span style="padding: 10px 15px; color: var(--text-secondary);">
                Page ${paginationInfo.page} / ${paginationInfo.pages} (${paginationInfo.total} recherches)
            </span>`;
            if (paginationInfo.page < paginationInfo.pages) {
                paginationHtml += `<button class="btn" onclick="loadSearchHistory(${paginationInfo.page + 1})">Suivant ▶</button>`;
            }
            pagination.innerHTML = paginationHtml;
        } else if (pagination) {
            pagination.innerHTML = '';
        }
        
        searchHistoryPage = page;
    } catch (error) {
        console.error('Erreur chargement historique:', error);
        container.innerHTML = `<p style="text-align: center; color: var(--error);">Erreur: ${error.message}</p>`;
    }
}

function relaunchSearch(query, location, maxResults) {
    // Remplir les champs de recherche
    const queryInput = document.getElementById('jobsSearchQuery');
    const locationInput = document.getElementById('jobsSearchLocation');
    
    if (queryInput) queryInput.value = query;
    if (locationInput) locationInput.value = location;
    
    // Fermer le modal
    closeSearchHistoryModal();
    
    // Lancer la recherche
    setTimeout(() => {
        scrapeJobs();
    }, 300);
}
