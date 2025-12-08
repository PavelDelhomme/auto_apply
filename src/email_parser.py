"""
Parser pour analyser les emails de candidatures et extraire les informations
"""
import re
from typing import Dict, Optional, List
from datetime import datetime

def parse_application_email(email_body: str, email_subject: str, sender: str) -> Dict:
    """
    Parse un email de réponse à une candidature pour extraire les informations.
    
    :param email_body: Corps de l'email
    :param email_subject: Sujet de l'email
    :param sender: Expéditeur de l'email
    :return: Dictionnaire avec les informations extraites
    """
    result = {
        'type': 'unknown',
        'status': 'unknown',
        'company': None,
        'job_title': None,
        'next_step': None,
        'date': None,
        'confidence': 0
    }
    
    # Normaliser le texte
    text = (email_subject + ' ' + email_body).lower()
    
    # Détecter le type d'email
    if any(word in text for word in ['refus', 'refusé', 'refused', 'désolé', 'désolée', 'malheureusement', 'unfortunately']):
        result['type'] = 'rejection'
        result['status'] = 'rejected'
        result['confidence'] += 0.8
    elif any(word in text for word in ['entretien', 'interview', 'rdv', 'rendez-vous', 'appel', 'call', 'visio', 'zoom']):
        result['type'] = 'interview'
        result['status'] = 'interview_scheduled'
        result['confidence'] += 0.9
        
        # Extraire la date de l'entretien
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+(\d{1,2})[/-](\d{1,2})',
            r'le\s+(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['date'] = match.group(0)
                break
        
        # Extraire l'heure
        time_pattern = r'(\d{1,2})[h:](\d{2})'
        time_match = re.search(time_pattern, text)
        if time_match:
            result['next_step'] = f"Entretien prévu {time_match.group(0)}"
    elif any(word in text for word in ['accepté', 'acceptée', 'accepted', 'félicitations', 'congratulations', 'bienvenue', 'welcome']):
        result['type'] = 'acceptance'
        result['status'] = 'accepted'
        result['confidence'] += 0.9
    elif any(word in text for word in ['candidature', 'application', 'postulation', 'reçu', 'received']):
        result['type'] = 'acknowledgment'
        result['status'] = 'acknowledged'
        result['confidence'] += 0.7
    elif any(word in text for word in ['relance', 'follow-up', 'suivi', 'update']):
        result['type'] = 'follow_up'
        result['status'] = 'in_progress'
        result['confidence'] += 0.6
    
    # Extraire le nom de l'entreprise
    company_patterns = [
        r'chez\s+([A-Z][a-zA-Z\s&]+)',
        r'de\s+([A-Z][a-zA-Z\s&]+)',
        r'([A-Z][a-zA-Z\s&]+)\s+vous',
    ]
    for pattern in company_patterns:
        match = re.search(pattern, text)
        if match:
            result['company'] = match.group(1).strip()
            break
    
    # Extraire le titre du poste
    job_patterns = [
        r'poste\s+de\s+([a-zA-Z\s]+)',
        r'offre\s+([a-zA-Z\s]+)',
        r'candidature\s+pour\s+([a-zA-Z\s]+)',
    ]
    for pattern in job_patterns:
        match = re.search(pattern, text)
        if match:
            result['job_title'] = match.group(1).strip()
            break
    
    # Extraire les prochaines étapes
    if result['type'] == 'interview':
        if 'visio' in text or 'zoom' in text or 'teams' in text:
            result['next_step'] = 'Entretien en visioconférence'
        elif 'téléphone' in text or 'phone' in text or 'appel' in text:
            result['next_step'] = 'Entretien téléphonique'
        elif 'présentiel' in text or 'sur site' in text:
            result['next_step'] = 'Entretien en présentiel'
    
    return result

def parse_all_emails(emails: List[Dict]) -> Dict:
    """
    Parse une liste d'emails et retourne des statistiques.
    
    :param emails: Liste de dictionnaires d'emails
    :return: Dictionnaire avec statistiques
    """
    stats = {
        'total': len(emails),
        'rejections': 0,
        'interviews': 0,
        'acceptances': 0,
        'acknowledgments': 0,
        'follow_ups': 0,
        'unknown': 0,
        'companies': {},
        'by_type': {}
    }
    
    for email in emails:
        parsed = parse_application_email(
            email.get('body', ''),
            email.get('subject', ''),
            email.get('sender', '')
        )
        
        stats['by_type'][parsed['type']] = stats['by_type'].get(parsed['type'], 0) + 1
        
        if parsed['type'] == 'rejection':
            stats['rejections'] += 1
        elif parsed['type'] == 'interview':
            stats['interviews'] += 1
        elif parsed['type'] == 'acceptance':
            stats['acceptances'] += 1
        elif parsed['type'] == 'acknowledgment':
            stats['acknowledgments'] += 1
        elif parsed['type'] == 'follow_up':
            stats['follow_ups'] += 1
        else:
            stats['unknown'] += 1
        
        if parsed['company']:
            stats['companies'][parsed['company']] = stats['companies'].get(parsed['company'], 0) + 1
    
    return stats

