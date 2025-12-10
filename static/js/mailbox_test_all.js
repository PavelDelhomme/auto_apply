/**
 * JavaScript pour la page de test de connexions email pour tous les personas
 */

let allResults = [];
let currentFilter = 'all';

async function runAllTests() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const emptyState = document.getElementById('emptyState');
    const testResults = document.getElementById('testResults');
    const testStats = document.getElementById('testStats');
    
    if (loadingOverlay) loadingOverlay.style.display = 'flex';
    if (emptyState) emptyState.style.display = 'none';
    if (testResults) testResults.style.display = 'none';
    if (testStats) testStats.style.display = 'none';
    
    try {
        const response = await fetch('/api/personas/test-all-email-connections', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            allResults = data.results || [];
            displayResults(data);
        } else {
            alert(`Erreur: ${data.error || 'Erreur inconnue'}`);
        }
    } catch (error) {
        console.error('Erreur test connexions:', error);
        alert(`Erreur: ${error.message}`);
    } finally {
        if (loadingOverlay) loadingOverlay.style.display = 'none';
    }
}

function displayResults(data) {
    const testStats = document.getElementById('testStats');
    const testResults = document.getElementById('testResults');
    const resultsList = document.getElementById('resultsList');
    const emptyState = document.getElementById('emptyState');
    
    if (!testStats || !testResults || !resultsList) return;
    
    // Afficher les statistiques
    const statTotal = document.getElementById('statTotal');
    const statSuccess = document.getElementById('statSuccess');
    const statFailed = document.getElementById('statFailed');
    
    if (statTotal) statTotal.textContent = data.total || 0;
    if (statSuccess) statSuccess.textContent = data.successful || 0;
    if (statFailed) statFailed.textContent = data.failed || 0;
    
    testStats.style.display = 'flex';
    testResults.style.display = 'block';
    if (emptyState) emptyState.style.display = 'none';
    
    // Afficher les résultats
    renderResults();
}

function renderResults() {
    const resultsList = document.getElementById('resultsList');
    if (!resultsList) return;
    
    let filteredResults = allResults;
    
    if (currentFilter === 'success') {
        filteredResults = allResults.filter(r => r.success);
    } else if (currentFilter === 'failed') {
        filteredResults = allResults.filter(r => !r.success);
    }
    
    if (filteredResults.length === 0) {
        resultsList.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">Aucun résultat à afficher</div>';
        return;
    }
    
    let html = '';
    filteredResults.forEach(result => {
        const statusClass = result.success ? 'success' : 'failed';
        const statusBadge = result.success 
            ? '<span class="status-badge success">✅ OK</span>'
            : '<span class="status-badge failed">❌ Erreur</span>';
        
        const aliasInfo = result.is_alias 
            ? `<span class="alias-badge">Alias</span> ${result.parent ? `<br><small>Parent: ${result.parent}</small>` : ''}`
            : '<span style="color: var(--text-secondary);">Principal</span>';
        
        const details = result.success
            ? `<span class="success-text">${result.message || 'Connexion réussie'}</span><br><span class="server-info">${result.server}:${result.port}</span>`
            : `<span class="error-text">${escapeHtml(result.error || 'Erreur inconnue')}</span>${result.server ? `<br><span class="server-info">${result.server}:${result.port || 'N/A'}</span>` : ''}`;
        
        const responseTime = result.response_time ? `${result.response_time} ms` : 'N/A';
        
        html += `
            <div class="table-row ${statusClass}">
                <div>
                    <strong>${escapeHtml(result.name || 'N/A')}</strong>
                </div>
                <div>${escapeHtml(result.email || 'N/A')}</div>
                <div>${statusBadge}</div>
                <div>${aliasInfo}</div>
                <div>${responseTime}</div>
                <div>${details}</div>
            </div>
        `;
    });
    
    resultsList.innerHTML = html;
}

function filterResults(filter) {
    currentFilter = filter;
    
    // Mettre à jour les boutons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    renderResults();
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function testKeyPersonas() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const emptyState = document.getElementById('emptyState');
    const testResults = document.getElementById('testResults');
    const testStats = document.getElementById('testStats');
    
    if (loadingOverlay) loadingOverlay.style.display = 'flex';
    if (emptyState) emptyState.style.display = 'none';
    if (testResults) testResults.style.display = 'none';
    if (testStats) testStats.style.display = 'none';
    
    // Personas clés à tester
    const keyEmails = [
        'paul.delhomme@gmx.fr',
        'olivier.rousseau@gmx.com',
        'thomas.leroy@caramail.fr'
    ];
    
    try {
        const loadingProgress = document.getElementById('loadingProgress');
        if (loadingProgress) loadingProgress.textContent = 'Test des personas clés...';
        
        // Tester chaque persona individuellement
        const results = [];
        for (let i = 0; i < keyEmails.length; i++) {
            const email = keyEmails[i];
            if (loadingProgress) {
                loadingProgress.textContent = `Test ${i + 1}/${keyEmails.length}: ${email}`;
            }
            
            try {
                const response = await fetch(`/api/personas/${encodeURIComponent(email)}/emails/test-connection`, {
                    method: 'POST'
                });
                const result = await response.json();
                
                // Récupérer les infos du persona
                const allPersonasResponse = await fetch('/api/personas');
                let persona = null;
                if (allPersonasResponse.ok) {
                    const allPersonas = await allPersonasResponse.json();
                    // Trouver le persona par email
                    persona = Object.values(allPersonas).find(p => p.email === email);
                }
                
                results.push({
                    persona_key: email,
                    name: persona ? (persona.name || 'N/A') : 'N/A',
                    email: email,
                    success: result.success || false,
                    message: result.message,
                    error: result.error,
                    is_alias: persona ? (persona.alias || false) : false,
                    parent: persona ? (persona.parent || null) : null,
                    server: result.server,
                    port: result.port,
                    response_time: null
                });
            } catch (error) {
                results.push({
                    persona_key: email,
                    name: 'N/A',
                    email: email,
                    success: false,
                    error: error.message,
                    is_alias: false,
                    parent: null,
                    server: null,
                    port: null,
                    response_time: null
                });
            }
        }
        
        // Afficher les résultats
        allResults = results;
        displayResults({
            success: true,
            total: results.length,
            successful: results.filter(r => r.success).length,
            failed: results.filter(r => !r.success).length,
            results: results
        });
    } catch (error) {
        console.error('Erreur test personas clés:', error);
        alert(`Erreur: ${error.message}`);
    } finally {
        if (loadingOverlay) loadingOverlay.style.display = 'none';
    }
}

// Auto-lancer les tests au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    // Optionnel : auto-lancer les tests
    // runAllTests();
});

