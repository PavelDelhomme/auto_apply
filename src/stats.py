import sqlite3
import os
from collections import defaultdict

def get_db_path():
    """Retourne le chemin de la base de données."""
    db_dir = 'data'
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'jobs.db')

def get_statistics():
    """
    Génère des statistiques sur les candidatures.
    :return: Dictionnaire contenant les statistiques.
    """
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    # Statistiques générales
    total_jobs = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    total_applications = c.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    sent_applications = c.execute("SELECT COUNT(*) FROM applications WHERE status = 'sent'").fetchone()[0]
    failed_applications = c.execute("SELECT COUNT(*) FROM applications WHERE status = 'failed'").fetchone()[0]
    pending_applications = c.execute("SELECT COUNT(*) FROM applications WHERE status = 'pending'").fetchone()[0]
    
    # Statistiques par persona
    c.execute("""SELECT persona_name, persona_email, COUNT(*) as count, status
                 FROM applications
                 GROUP BY persona_email, status""")
    persona_stats = defaultdict(lambda: {'sent': 0, 'failed': 0, 'pending': 0})
    for row in c.fetchall():
        persona_name, persona_email, count, status = row
        persona_stats[persona_name][status] = count
    
    # Offres avec le plus de candidatures
    c.execute("""SELECT j.title, j.company, COUNT(a.id) as application_count
                 FROM jobs j
                 LEFT JOIN applications a ON j.id = a.job_id
                 GROUP BY j.id
                 ORDER BY application_count DESC
                 LIMIT 10""")
    top_jobs = [{'title': row[0], 'company': row[1], 'count': row[2]} for row in c.fetchall()]
    
    conn.close()
    
    return {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "sent_applications": sent_applications,
        "failed_applications": failed_applications,
        "pending_applications": pending_applications,
        "persona_stats": dict(persona_stats),
        "top_jobs": top_jobs
    }

def print_statistics():
    """Affiche les statistiques de manière formatée."""
    stats = get_statistics()
    
    print("\n" + "="*60)
    print("📊 STATISTIQUES DES CANDIDATURES")
    print("="*60)
    print(f"\n📋 Offres d'emploi:")
    print(f"   Total d'offres trouvées: {stats['total_jobs']}")
    
    print(f"\n📨 Candidatures:")
    print(f"   Total: {stats['total_applications']}")
    print(f"   ✅ Envoyées: {stats['sent_applications']}")
    print(f"   ❌ Échouées: {stats['failed_applications']}")
    print(f"   ⏳ En attente: {stats['pending_applications']}")
    
    if stats['persona_stats']:
        print(f"\n👥 Statistiques par persona:")
        for persona_name, persona_data in stats['persona_stats'].items():
            total = sum(persona_data.values())
            print(f"   {persona_name}:")
            print(f"      Total: {total}")
            print(f"      ✅ Envoyées: {persona_data['sent']}")
            print(f"      ❌ Échouées: {persona_data['failed']}")
    
    if stats['top_jobs']:
        print(f"\n🏆 Top 10 des offres les plus candidatées:")
        for i, job in enumerate(stats['top_jobs'], 1):
            print(f"   {i}. {job['title']} chez {job['company']} ({job['count']} candidatures)")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print_statistics()
