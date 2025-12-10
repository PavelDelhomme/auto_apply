/**
 * JavaScript pour la page Mailbox
 */

let allPersonas = {};
let selectedPersonaEmail = null;
let allEmails = [];
let filteredEmails = [];
let selectedEmailId = null;
let filteredPersonasForMailbox = [];
let currentDropdownIndex = -1;

// Charger les personas au démarrage
document.addEventListener('DOMContentLoaded', () => {
    loadPersonas();
    
    // Gérer les touches clavier pour la recherche
    const searchInput = document.getElementById('personaSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keydown', handlePersonaSearchKeydown);
    }
});

async function loadPersonas() {
    try {
        const response = await fetch('/api/personas');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        allPersonas = await response.json();
        filteredPersonasForMailbox = Object.values(allPersonas);
    } catch (error) {
        console.error('Erreur chargement personas:', error);
    }
}

function filterPersonasForMailbox(searchTerm) {
    const searchInput = document.getElementById('personaSearchInput');
    const dropdown = document.getElementById('personaDropdown');
    
    if (!searchInput || !dropdown) return;
    
    const term = searchTerm.toLowerCase().trim();
    currentDropdownIndex = -1;
    
    if (term === '') {
        // Afficher tous les personas triés
        filteredPersonasForMailbox = Object.values(allPersonas).sort((a, b) => {
            const nameA = (a.name || a.email || '').toLowerCase();
            const nameB = (b.name || b.email || '').toLowerCase();
            return nameA.localeCompare(nameB);
        });
    } else {
        // Filtrer les personas
        filteredPersonasForMailbox = Object.values(allPersonas).filter(persona => {
            const name = (persona.name || '').toLowerCase();
            const email = (persona.email || '').toLowerCase();
            return name.includes(term) || email.includes(term);
        }).sort((a, b) => {
            const nameA = (a.name || a.email || '').toLowerCase();
            const nameB = (b.name || b.email || '').toLowerCase();
            return nameA.localeCompare(nameB);
        });
    }
    
    renderPersonaDropdown();
}

function renderPersonaDropdown() {
    const dropdown = document.getElementById('personaDropdown');
    if (!dropdown) return;
    
    if (filteredPersonasForMailbox.length === 0) {
        dropdown.innerHTML = '<div class="persona-dropdown-empty">Aucun persona trouvé</div>';
        dropdown.style.display = 'block';
        return;
    }
    
    let html = '';
    filteredPersonasForMailbox.forEach((persona, index) => {
        const isSelected = persona.email === selectedPersonaEmail;
        const isAlias = persona.alias || false;
        const parentInfo = isAlias && persona.parent ? ` (Alias de ${persona.parent})` : '';
        
        html += `
            <div 
                class="persona-dropdown-item ${isSelected ? 'selected' : ''}" 
                data-email="${escapeHtml(persona.email)}"
                data-index="${index}"
                onmouseenter="highlightPersonaDropdownItem(${index})"
                onclick="selectPersonaFromDropdown('${escapeHtml(persona.email)}')"
            >
                <div class="persona-dropdown-item-name">${escapeHtml(persona.name || persona.email)}</div>
                <div class="persona-dropdown-item-email">${escapeHtml(persona.email)}</div>
                ${isAlias ? `<div class="persona-dropdown-item-alias">${escapeHtml(parentInfo)}</div>` : ''}
            </div>
        `;
    });
    
    dropdown.innerHTML = html;
    dropdown.style.display = 'block';
}

function highlightPersonaDropdownItem(index) {
    currentDropdownIndex = index;
    const items = document.querySelectorAll('.persona-dropdown-item');
    items.forEach((item, i) => {
        item.classList.toggle('selected', i === index);
    });
}

function selectPersonaFromDropdown(email) {
    const searchInput = document.getElementById('personaSearchInput');
    if (searchInput) {
        const persona = Object.values(allPersonas).find(p => p.email === email);
        if (persona) {
            searchInput.value = `${persona.name || persona.email} (${persona.email})`;
        }
    }
    hidePersonaDropdown();
    loadPersonaMailbox(email);
}

function showPersonaDropdown() {
    const dropdown = document.getElementById('personaDropdown');
    const searchInput = document.getElementById('personaSearchInput');
    
    if (dropdown && searchInput) {
        if (searchInput.value.trim() === '') {
            filterPersonasForMailbox('');
        }
        renderPersonaDropdown();
    }
}

function hidePersonaDropdown() {
    // Délai pour permettre le clic sur un élément
    setTimeout(() => {
        const dropdown = document.getElementById('personaDropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }, 200);
}

function handlePersonaSearchKeydown(event) {
    const dropdown = document.getElementById('personaDropdown');
    if (!dropdown || dropdown.style.display === 'none') return;
    
    const items = document.querySelectorAll('.persona-dropdown-item');
    if (items.length === 0) return;
    
    switch (event.key) {
        case 'ArrowDown':
            event.preventDefault();
            currentDropdownIndex = Math.min(currentDropdownIndex + 1, items.length - 1);
            highlightPersonaDropdownItem(currentDropdownIndex);
            items[currentDropdownIndex].scrollIntoView({ block: 'nearest' });
            break;
        case 'ArrowUp':
            event.preventDefault();
            currentDropdownIndex = Math.max(currentDropdownIndex - 1, -1);
            if (currentDropdownIndex >= 0) {
                highlightPersonaDropdownItem(currentDropdownIndex);
                items[currentDropdownIndex].scrollIntoView({ block: 'nearest' });
            }
            break;
        case 'Enter':
            event.preventDefault();
            if (currentDropdownIndex >= 0 && currentDropdownIndex < items.length) {
                const email = items[currentDropdownIndex].dataset.email;
                selectPersonaFromDropdown(email);
            }
            break;
        case 'Escape':
            hidePersonaDropdown();
            break;
    }
}

async function loadPersonaMailbox(personaEmail) {
    if (!personaEmail) {
        hideMailboxContent();
        return;
    }
    
    selectedPersonaEmail = personaEmail;
    const persona = Object.values(allPersonas).find(p => p.email === personaEmail);
    
    if (!persona) {
        alert('Persona non trouvé');
        return;
    }
    
    // Afficher les informations du persona
    showPersonaInfo(persona);
    
    // Charger les emails
    await loadEmails(personaEmail);
    
    // Afficher le contenu
    showMailboxContent();
}

function showPersonaInfo(persona) {
    const personaInfo = document.getElementById('personaInfo');
    const personaName = document.getElementById('selectedPersonaName');
    const personaEmail = document.getElementById('selectedPersonaEmail');
    
    if (personaInfo) personaInfo.style.display = 'block';
    if (personaName) personaName.textContent = persona.name || persona.email;
    if (personaEmail) personaEmail.textContent = persona.email;
    
    // Charger les statistiques
    loadEmailStats(persona.email);
}

function hidePersonaInfo() {
    const personaInfo = document.getElementById('personaInfo');
    if (personaInfo) personaInfo.style.display = 'none';
}

async function loadEmailStats(personaEmail) {
    try {
        const response = await fetch(`/api/personas/${encodeURIComponent(personaEmail)}/emails/count`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const stats = await response.json();
        
        const receivedEl = document.getElementById('emailsReceived');
        const unreadEl = document.getElementById('emailsUnread');
        
        if (receivedEl) receivedEl.textContent = stats.total || 0;
        if (unreadEl) unreadEl.textContent = stats.unread || 0;
        
        // TODO: Ajouter le compteur d'emails envoyés si disponible
        const sentEl = document.getElementById('emailsSent');
        if (sentEl) sentEl.textContent = '0'; // À implémenter
    } catch (error) {
        console.error('Erreur chargement stats emails:', error);
    }
}

async function loadEmails(personaEmail) {
    const emailsList = document.getElementById('emailsList');
    if (!emailsList) return;
    
    try {
        emailsList.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">⏳ Chargement des emails...</div>';
        
        const response = await fetch(`/api/personas/${encodeURIComponent(personaEmail)}/emails`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        allEmails = await response.json();
        filteredEmails = [...allEmails];
        
        renderEmails();
    } catch (error) {
        console.error('Erreur chargement emails:', error);
        emailsList.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--error);">❌ Erreur lors du chargement: ${error.message}</div>`;
    }
}

function renderEmails() {
    const emailsList = document.getElementById('emailsList');
    if (!emailsList) return;
    
    if (filteredEmails.length === 0) {
        emailsList.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">📭 Aucun email trouvé</div>';
        return;
    }
    
    let html = '';
    filteredEmails.forEach(email => {
        const date = new Date(email.received_at);
        const dateStr = date.toLocaleString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const preview = email.body ? email.body.substring(0, 100).replace(/\n/g, ' ') + '...' : '(Aucun contenu)';
        
        html += `
            <div class="email-item ${!email.is_read ? 'unread' : ''}" onclick="openEmail(${email.id})">
                <div class="email-item-content">
                    <div class="email-item-header">
                        <span class="email-sender">${escapeHtml(email.sender || 'Expéditeur inconnu')}</span>
                        <span class="email-date">${dateStr}</span>
                    </div>
                    <div class="email-subject">${escapeHtml(email.subject || '(Sans objet)')}</div>
                    <div class="email-preview">${escapeHtml(preview)}</div>
                </div>
            </div>
        `;
    });
    
    emailsList.innerHTML = html;
}

function openEmail(emailId) {
    const email = allEmails.find(e => e.id === emailId);
    if (!email) return;
    
    selectedEmailId = emailId;
    
    // Marquer comme lu
    if (!email.is_read) {
        markEmailAsRead(emailId);
    }
    
    // Afficher le modal
    const modal = document.getElementById('readEmailModal');
    if (!modal) return;
    
    const subjectEl = document.getElementById('emailSubject');
    const fromEl = document.getElementById('emailFrom');
    const toEl = document.getElementById('emailTo');
    const dateEl = document.getElementById('emailDate');
    const contentEl = document.getElementById('emailContent');
    
    if (subjectEl) subjectEl.textContent = email.subject || '(Sans objet)';
    if (fromEl) fromEl.textContent = email.sender || 'Expéditeur inconnu';
    if (toEl) toEl.textContent = selectedPersonaEmail;
    
    const date = new Date(email.received_at);
    if (dateEl) {
        dateEl.textContent = date.toLocaleString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    if (contentEl) {
        contentEl.textContent = email.body || '(Aucun contenu)';
    }
    
    modal.classList.add('active');
}

function closeReadEmailModal() {
    const modal = document.getElementById('readEmailModal');
    if (modal) modal.classList.remove('active');
    selectedEmailId = null;
    
    // Recharger les emails pour mettre à jour le statut "lu"
    if (selectedPersonaEmail) {
        loadEmails(selectedPersonaEmail);
        loadEmailStats(selectedPersonaEmail);
    }
}

async function markEmailAsRead(emailId) {
    if (!selectedPersonaEmail) return;
    
    try {
        await fetch(`/api/personas/${encodeURIComponent(selectedPersonaEmail)}/emails/${emailId}/read`, {
            method: 'POST'
        });
    } catch (error) {
        console.error('Erreur marquage email comme lu:', error);
    }
}

async function markAllAsRead() {
    if (!selectedPersonaEmail || !confirm('Marquer tous les emails comme lus ?')) return;
    
    const unreadEmails = allEmails.filter(e => !e.is_read);
    for (const email of unreadEmails) {
        await markEmailAsRead(email.id);
    }
    
    await loadEmails(selectedPersonaEmail);
    await loadEmailStats(selectedPersonaEmail);
}

function filterEmails() {
    const filter = document.getElementById('emailFilter')?.value || 'all';
    
    if (filter === 'all') {
        filteredEmails = [...allEmails];
    } else if (filter === 'unread') {
        filteredEmails = allEmails.filter(e => !e.is_read);
    } else if (filter === 'read') {
        filteredEmails = allEmails.filter(e => e.is_read);
    }
    
    renderEmails();
}

function searchEmails() {
    const search = document.getElementById('emailSearch')?.value.toLowerCase() || '';
    const filter = document.getElementById('emailFilter')?.value || 'all';
    
    let emails = allEmails;
    
    // Appliquer le filtre
    if (filter === 'unread') {
        emails = emails.filter(e => !e.is_read);
    } else if (filter === 'read') {
        emails = emails.filter(e => e.is_read);
    }
    
    // Appliquer la recherche
    if (search) {
        emails = emails.filter(e => {
            const subject = (e.subject || '').toLowerCase();
            const sender = (e.sender || '').toLowerCase();
            const body = (e.body || '').toLowerCase();
            return subject.includes(search) || sender.includes(search) || body.includes(search);
        });
    }
    
    filteredEmails = emails;
    renderEmails();
}

function showMailboxContent() {
    const empty = document.getElementById('mailboxEmpty');
    const content = document.getElementById('mailboxContent');
    
    if (empty) empty.style.display = 'none';
    if (content) content.style.display = 'flex';
}

function hideMailboxContent() {
    const empty = document.getElementById('mailboxEmpty');
    const content = document.getElementById('mailboxContent');
    
    if (empty) empty.style.display = 'flex';
    if (content) content.style.display = 'none';
    hidePersonaInfo();
}

async function refreshMailbox() {
    if (!selectedPersonaEmail) return;
    
    await loadEmails(selectedPersonaEmail);
    await loadEmailStats(selectedPersonaEmail);
}

async function refreshAllMailboxes() {
    if (selectedPersonaEmail) {
        await refreshMailbox();
    }
}

async function fetchEmailsFromIMAP() {
    if (!selectedPersonaEmail) {
        alert('Veuillez sélectionner un persona');
        return;
    }
    
    if (!confirm('Récupérer les nouveaux emails depuis le serveur IMAP ?')) return;
    
    try {
        const response = await fetch(`/api/personas/${encodeURIComponent(selectedPersonaEmail)}/emails/fetch`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ ${result.fetched_count || 0} email(s) récupéré(s)`);
            await refreshMailbox();
        } else {
            let errorMsg = `❌ Erreur: ${result.error || 'Erreur inconnue'}`;
            if (result.hint) {
                errorMsg += `\n\n💡 ${result.hint}`;
            }
            if (response.status === 401 && result.is_alias && result.parent) {
                errorMsg += `\n\n⚠️ Ce persona est un alias. ${result.parent ? `Parent: ${result.parent}` : ''}`;
            }
            alert(errorMsg);
        }
    } catch (error) {
        console.error('Erreur récupération emails:', error);
        alert(`❌ Erreur: ${error.message}`);
    }
}

function showComposeEmailModal() {
    if (!selectedPersonaEmail) {
        alert('Veuillez sélectionner un persona');
        return;
    }
    
    const modal = document.getElementById('composeEmailModal');
    const fromInput = document.getElementById('composeFrom');
    
    if (modal) modal.classList.add('active');
    if (fromInput) fromInput.value = selectedPersonaEmail;
}

function closeComposeEmailModal() {
    const modal = document.getElementById('composeEmailModal');
    if (modal) modal.classList.remove('active');
    
    // Réinitialiser le formulaire
    const form = document.getElementById('composeEmailForm');
    if (form) form.reset();
    if (document.getElementById('composeFrom')) {
        document.getElementById('composeFrom').value = selectedPersonaEmail || '';
    }
}

async function sendEmail(event) {
    event.preventDefault();
    
    if (!selectedPersonaEmail) {
        alert('Veuillez sélectionner un persona');
        return;
    }
    
    const to = document.getElementById('composeTo')?.value;
    const subject = document.getElementById('composeSubject')?.value;
    const body = document.getElementById('composeBody')?.value;
    
    if (!to || !subject || !body) {
        alert('Veuillez remplir tous les champs');
        return;
    }
    
    try {
        const response = await fetch('/api/personas/test-email-send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from_email: selectedPersonaEmail,
                to_email: to,
                subject: subject,
                body: body
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Email envoyé avec succès !');
            closeComposeEmailModal();
        } else {
            alert(`❌ Erreur: ${result.error || 'Erreur inconnue'}`);
        }
    } catch (error) {
        console.error('Erreur envoi email:', error);
        alert(`❌ Erreur: ${error.message}`);
    }
}

async function testEmailConnection() {
    if (!selectedPersonaEmail) {
        alert('Veuillez sélectionner un persona');
        return;
    }
    
    try {
        const response = await fetch(`/api/personas/${encodeURIComponent(selectedPersonaEmail)}/emails/test-connection`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ Connexion réussie !\nServeur: ${result.server}:${result.port}`);
        } else {
            let errorMsg = `❌ Erreur: ${result.error || 'Erreur inconnue'}`;
            if (result.hint) {
                errorMsg += `\n\n💡 ${result.hint}`;
            }
            if (response.status === 401) {
                errorMsg += `\n\n🔍 Informations de diagnostic:`;
                errorMsg += `\n   - Serveur: ${result.server || 'N/A'}:${result.port || 'N/A'}`;
                if (result.password_source) {
                    errorMsg += `\n   - Source du mot de passe: ${result.password_source}`;
                }
                if (result.is_alias && result.parent) {
                    errorMsg += `\n   - Type: Alias`;
                    errorMsg += `\n   - Parent: ${result.parent}`;
                    if (selectedPersonaEmail.includes('@gmx.') || selectedPersonaEmail.includes('@caramail.')) {
                        errorMsg += `\n\n📌 Pour les alias GMX/CaraMail, le mot de passe doit être celui du compte principal.`;
                        if (result.password_source && result.password_source.includes('recherche automatique')) {
                            errorMsg += `\n   Le système a cherché automatiquement un persona principal.`;
                            errorMsg += `\n   Vérifiez que ce persona principal a le bon mot de passe.`;
                        }
                    }
                } else {
                    errorMsg += `\n   - Type: Persona principal`;
                    errorMsg += `\n   - Le mot de passe vient directement de personas.json`;
                }
                
                // Message spécial pour GMX/CaraMail
                if (result.requires_imap_activation) {
                    errorMsg += `\n\n⚠️ ATTENTION - GMX/CaraMail:`;
                    errorMsg += `\n   Les protocoles IMAP/POP3/SMTP sont DÉSACTIVÉS par défaut !`;
                    errorMsg += `\n\n📋 Pour activer l'accès IMAP:`;
                    errorMsg += `\n   1. Connectez-vous à https://www.gmx.fr ou https://www.caramail.com`;
                    errorMsg += `\n   2. Allez dans Paramètres / Réglages de votre boîte mail`;
                    errorMsg += `\n   3. Cherchez "Accès par programme" ou "IMAP/POP3"`;
                    errorMsg += `\n   4. Activez l'accès IMAP et SMTP`;
                    errorMsg += `\n   5. Réessayez la connexion`;
                    errorMsg += `\n\n💡 Note: GMX envoie un email de confirmation quand vous activez IMAP.`;
                } else {
                    errorMsg += `\n\n🔧 Solutions possibles:`;
                    errorMsg += `\n   1. Vérifiez que le mot de passe est correct dans personas.json`;
                    errorMsg += `\n   2. Utilisez le bouton "Mettre à jour mot de passe" pour le corriger`;
                    errorMsg += `\n   3. Vérifiez que l'accès IMAP est activé pour ce compte email`;
                    errorMsg += `\n   4. Vérifiez que les caractères spéciaux dans le mot de passe sont correctement encodés`;
                }
            }
            alert(errorMsg);
        }
    } catch (error) {
        console.error('Erreur test connexion:', error);
        alert(`❌ Erreur: ${error.message}`);
    }
}

function replyToEmail() {
    if (!selectedEmailId) return;
    
    const email = allEmails.find(e => e.id === selectedEmailId);
    if (!email) return;
    
    showComposeEmailModal();
    
    const toInput = document.getElementById('composeTo');
    const subjectInput = document.getElementById('composeSubject');
    const bodyInput = document.getElementById('composeBody');
    
    if (toInput) toInput.value = email.sender || '';
    if (subjectInput) subjectInput.value = `Re: ${email.subject || ''}`;
    if (bodyInput) {
        bodyInput.value = `\n\n--- Message original ---\nDe: ${email.sender}\nDate: ${new Date(email.received_at).toLocaleString('fr-FR')}\n\n${email.body || ''}`;
    }
    
    closeReadEmailModal();
}

function forwardEmail() {
    if (!selectedEmailId) return;
    
    const email = allEmails.find(e => e.id === selectedEmailId);
    if (!email) return;
    
    showComposeEmailModal();
    
    const subjectInput = document.getElementById('composeSubject');
    const bodyInput = document.getElementById('composeBody');
    
    if (subjectInput) subjectInput.value = `Fwd: ${email.subject || ''}`;
    if (bodyInput) {
        bodyInput.value = `\n\n--- Message transféré ---\nDe: ${email.sender}\nDate: ${new Date(email.received_at).toLocaleString('fr-FR')}\nSujet: ${email.subject || ''}\n\n${email.body || ''}`;
    }
    
    closeReadEmailModal();
}

function deleteEmail() {
    if (!selectedEmailId || !confirm('Supprimer cet email ?')) return;
    
    // TODO: Implémenter la suppression d'email
    alert('Fonctionnalité de suppression à implémenter');
}

function showUpdatePasswordModal() {
    if (!selectedPersonaEmail) {
        alert('Veuillez sélectionner un persona');
        return;
    }
    
    const modal = document.getElementById('updatePasswordModal');
    const emailInput = document.getElementById('updatePasswordEmail');
    
    if (modal) modal.classList.add('active');
    if (emailInput) emailInput.value = selectedPersonaEmail;
}

function closeUpdatePasswordModal() {
    const modal = document.getElementById('updatePasswordModal');
    if (modal) modal.classList.remove('active');
    
    // Réinitialiser le formulaire
    const form = document.getElementById('updatePasswordForm');
    if (form) form.reset();
    if (document.getElementById('updatePasswordEmail')) {
        document.getElementById('updatePasswordEmail').value = selectedPersonaEmail || '';
    }
}

async function updatePassword(event) {
    event.preventDefault();
    
    if (!selectedPersonaEmail) {
        alert('Veuillez sélectionner un persona');
        return;
    }
    
    const password = document.getElementById('updatePasswordValue')?.value;
    
    if (!password) {
        alert('Veuillez entrer un mot de passe');
        return;
    }
    
    try {
        const response = await fetch(`/api/personas/${encodeURIComponent(selectedPersonaEmail)}/password`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: password })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Mot de passe mis à jour avec succès !');
            closeUpdatePasswordModal();
            // Recharger les stats pour mettre à jour l'affichage
            await loadEmailStats(selectedPersonaEmail);
        } else {
            alert(`❌ Erreur: ${result.error || 'Erreur inconnue'}`);
        }
    } catch (error) {
        console.error('Erreur mise à jour mot de passe:', error);
        alert(`❌ Erreur: ${error.message}`);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Exporter les fonctions pour les rendre accessibles globalement
window.showUpdatePasswordModal = showUpdatePasswordModal;
window.closeUpdatePasswordModal = closeUpdatePasswordModal;
window.updatePassword = updatePassword;
window.filterPersonasForMailbox = filterPersonasForMailbox;
window.showPersonaDropdown = showPersonaDropdown;
window.hidePersonaDropdown = hidePersonaDropdown;
window.selectPersonaFromDropdown = selectPersonaFromDropdown;
window.highlightPersonaDropdownItem = highlightPersonaDropdownItem;

// Fermer les modals en cliquant en dehors
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

