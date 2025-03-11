import imaplib
import email

def connect_to_email(imap_server, username, password):
    """
    Connexion au serveur IMAP.
    """
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    return mail

def fetch_email(mail, persona_email):
    """
    Récupère les emails pour un persona spécifique.
    """
    mail.select("inbox")
    status, message = mail.search(None, 'UNSEEN') # Récupère automatiquement les emails non lus
    