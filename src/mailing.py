import imaplib
import email
import smtplib
from email.message import EmailMessage

def forward_emails(imap_server, imap_port, imap_username, imap_password, smtp_server, smtp_port, smtp_username, smtp_password, recipient_email):
    # Connexion IMAP
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(imap_username, imap_password)
    mail.select('inbox')

    # Récupération des emails
    _, search_data = mail.search(None, 'ALL')
    my_messages = []
    for num in search_data[0].split():
        email_data = {}
        _, data = mail.fetch(num, '(RFC822)')
        raw_message = data[0][1]
        raw_message_string = raw_message.decode('utf-8')
        email_message = email.message_from_string(raw_message_string)
        my_messages.append(email_message)

    # Fermeture de la connexion IMAP
    mail.close()
    mail.logout()

    # Envoi des emails vers la nouvelle adresse
    for msg in my_messages:
        # Création d'un nouveau message pour l'envoi
        new_msg = EmailMessage()
        new_msg["Subject"] = msg['Subject']
        new_msg["From"] = msg["From"]
        new_msg['To'] = recipient_email
        new_msg.set_content(msg.as_string())

        try:
            # Connexion SMTP
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(new_msg)
            print("Email envoyé avec succès!")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")

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


# Utilisation d'exemple
imap_server = 'imap.gmx.com'
imap_port = 993
imap_username = 'christian.gaillard@gmx.com'
imap_password = 'FlSO0mkqv%c#bx'
smtp_server = 'smtp.gmx.com'
smtp_port = 465
smtp_username = 'christian.gaillard@gmx.com'
smtp_password = 'FlSO0mkqv%c#bx'
recipient_email = 'candidatures@delhomme.ovh'

forward_emails(imap_server, imap_port, imap_username, imap_password, smtp_server, smtp_port, smtp_username, smtp_password, recipient_email)


import json

def load_accounts(data_file="data.json"):
    with open(data_file, 'r') as file:
        data = json.load(file)
    
    accounts = []
    for key, value in data.items():
        if value['alias'] == False:
            accounts.append({
                'email': value['email'],
                'password': value['password']
            })
    
    return accounts

accounts = load_accounts()

for account in accounts:
    imap_server = 'imap.gmx.com'
    imap_port = 993
    imap_username = account['email']
    imap_password = account['password']
    smtp_server = 'smtp.gmx.com'
    smtp_port = 465
    smtp_username = account['email']
    smtp_password = account['password']
    recipient_email = 'candidatures@delhomme.ovh'
    
    forward_emails(imap_server, imap_port, imap_username, imap_password, smtp_server, smtp_port, smtp_username, smtp_password, recipient_email)



import schedule
import time

def job():
    # Appeler la fonction de récupération des emails ici
    print("Récupération des emails en cours...")

schedule.every(1).hours.do(job)  # Exécuter toutes les heures

while True:
    schedule.run_pending()
    time.sleep(1)
