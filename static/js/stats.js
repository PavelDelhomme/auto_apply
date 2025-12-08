/**
 * JavaScript pour la page Stats
 */

let currentPage = 1;
let itemsPerPage = 20;

// Charger les statistiques au démarrage
document.addEventListener('DOMContentLoaded', () => {
    showLoader('statsContent', 'Chargement des statistiques...');
    loadStats();
});

// Fonction pour afficher un loader
function showLoader(containerId, message = 'Chargement...') {
    const container = document.getElementById(containerId);
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

async function loadStats() {
    try {
        showLoader('statsContent', 'Chargement des statistiques...');
        const response = await fetch('/api/stats');
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        const stats = await response.json();
        localStorage.setItem('lastStats', JSON.stringify(stats));
        currentPage = 1; // Réinitialiser la page
        renderStats(stats);
    } catch (error) {
        console.error('Erreur chargement statistiques:', error);
        const container = document.getElementById('statsContent');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px; color: var(--error);">
                    <div style="font-size: 3em; margin-bottom: 15px;">❌</div>
                    <h3>Erreur lors du chargement</h3>
                    <p>${error.message}</p>
                    <button class="btn btn-primary" onclick="loadStats()" style="margin-top: 20px;">🔄 Réessayer</button>
                </div>
            `;
        }
    }
}

function renderStats(stats) {
    const container = document.getElementById('statsContent');
    if (!container) {
        console.error('Élément statsContent non trouvé');
        return;
    }
    
    let html = `
        <div class="stats-detail-container">
            <h3 style="color: var(--text-title); margin-bottom: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 10px;">Statistiques par Persona</h3>
            <div class="stats-table-wrapper">
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>Persona</th>
                            <th>Total</th>
                            <th>Envoyées</th>
                            <th>Échouées</th>
                            <th>En attente</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    const personaStats = stats.persona_stats || {};
    const personasArray = Object.entries(personaStats);
    const totalPersonas = personasArray.length;
    
    if (totalPersonas === 0) {
        html += '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--text-secondary);">Aucune donnée disponible</td></tr>';
    } else {
        // Calcul de la pagination pour les personas
        const totalPages = Math.ceil(totalPersonas / itemsPerPage);
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const paginatedPersonas = personasArray.slice(startIndex, endIndex);
        
        for (const [persona, data] of paginatedPersonas) {
            const total = (data.sent || 0) + (data.failed || 0) + (data.pending || 0);
            html += `
                <tr>
                    <td>${persona}</td>
                    <td><strong>${total}</strong></td>
                    <td><span class="badge badge-success">${data.sent || 0}</span></td>
                    <td><span class="badge badge-error">${data.failed || 0}</span></td>
                    <td><span class="badge badge-warning">${data.pending || 0}</span></td>
                </tr>
            `;
        }
    }
    
    html += '</tbody></table></div>';
    
    // Ajouter la pagination pour les personas
    if (totalPersonas > itemsPerPage) {
        const totalPages = Math.ceil(totalPersonas / itemsPerPage);
        html += `
            <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 20px; padding: 20px; background: var(--bg-card); border-radius: 10px;">
                <button class="btn" onclick="changePersonaPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''} style="padding: 10px 20px;">
                    ← Précédent
                </button>
                <span style="color: var(--text-primary); font-weight: 600;">
                    Page ${currentPage} sur ${totalPages} (${totalPersonas} persona${totalPersonas > 1 ? 's' : ''})
                </span>
                <button class="btn" onclick="changePersonaPage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''} style="padding: 10px 20px;">
                    Suivant →
                </button>
            </div>
        `;
    }
    
    // Top jobs
    if (stats.top_jobs && stats.top_jobs.length > 0) {
        html += `
            <h3 style="margin-top: 40px; color: var(--text-title); margin-bottom: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 10px;">Top Offres Candidatées</h3>
            <div class="stats-table-wrapper">
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>Titre</th>
                            <th>Entreprise</th>
                            <th>Candidatures</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        const topJobs = stats.top_jobs.slice(0, 20); // Limiter à 20
        topJobs.forEach(job => {
            html += `
                <tr>
                    <td>${job.title || 'N/A'}</td>
                    <td>${job.company || 'N/A'}</td>
                    <td><strong>${job.count || 0}</strong></td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
    }
    
    // Statistiques globales
    html += `
        <div style="margin-top: 40px; padding: 20px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-radius: 12px; border-left: 4px solid var(--text-title);">
            <h3 style="color: var(--text-title); margin-bottom: 15px;">Statistiques Globales</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="text-align: center; padding: 15px; background: var(--bg-card); border-radius: 8px;">
                    <div style="font-size: 2em; margin-bottom: 5px;">💼</div>
                    <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 5px;">Offres totales</div>
                    <div style="color: var(--text-primary); font-size: 1.5em; font-weight: 700;">${stats.total_jobs || 0}</div>
                </div>
                <div style="text-align: center; padding: 15px; background: var(--bg-card); border-radius: 8px;">
                    <div style="font-size: 2em; margin-bottom: 5px;">📤</div>
                    <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 5px;">Candidatures totales</div>
                    <div style="color: var(--text-primary); font-size: 1.5em; font-weight: 700;">${stats.total_applications || 0}</div>
                </div>
                <div style="text-align: center; padding: 15px; background: var(--bg-card); border-radius: 8px;">
                    <div style="font-size: 2em; margin-bottom: 5px;">✅</div>
                    <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 5px;">Envoyées</div>
                    <div style="color: var(--success); font-size: 1.5em; font-weight: 700;">${stats.sent_applications || 0}</div>
                </div>
                <div style="text-align: center; padding: 15px; background: var(--bg-card); border-radius: 8px;">
                    <div style="font-size: 2em; margin-bottom: 5px;">❌</div>
                    <div style="color: var(--text-secondary); font-size: 0.85em; margin-bottom: 5px;">Échouées</div>
                    <div style="color: var(--error); font-size: 1.5em; font-weight: 700;">${stats.failed_applications || 0}</div>
                </div>
            </div>
        </div>
    `;
    
    html += '</div>';
    container.innerHTML = html;
}

function changePersonaPage(page) {
    const stats = JSON.parse(localStorage.getItem('lastStats') || '{}');
    const personaStats = stats.persona_stats || {};
    const totalPersonas = Object.keys(personaStats).length;
    const totalPages = Math.ceil(totalPersonas / itemsPerPage);
    
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    
    // Re-rendre avec la nouvelle page
    renderStats(stats);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
