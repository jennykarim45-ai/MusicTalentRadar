"""
Détection des alertes de croissance pour JEK2 Records
Analyse les variations de followers/fans et génère des alertes
"""
import psycopg2
from datetime import datetime, timedelta
import os

def get_connection():
    """Connexion à la base PostgreSQL"""
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        raise Exception("DATABASE_URL non configurée")
    return psycopg2.connect(db_url)

def detect_growth_alerts():
    """Détecte les hausses importantes de followers/fans"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Récupérer les artistes avec historique
    cursor.execute("""
        WITH latest AS (
            SELECT DISTINCT ON (artist_id, plateforme)
                artist_id, plateforme, followers, fans, date_collecte,
                COALESCE(followers, fans) as metric_value
            FROM metriques_historique
            ORDER BY artist_id, plateforme, date_collecte DESC
        ),
        previous AS (
            SELECT DISTINCT ON (artist_id, plateforme)
                artist_id, plateforme, 
                COALESCE(followers, fans) as metric_value
            FROM metriques_historique
            WHERE date_collecte < NOW() - INTERVAL '1 day'
            ORDER BY artist_id, plateforme, date_collecte DESC
        )
        SELECT 
            a.nom as nom_artiste,
            l.artist_id,
            l.plateforme,
            l.metric_value as current_value,
            p.metric_value as previous_value,
            ((l.metric_value - p.metric_value) * 100.0 / NULLIF(p.metric_value, 0)) as growth_percent
        FROM latest l
        JOIN previous p ON l.artist_id = p.artist_id AND l.plateforme = p.plateforme
        JOIN artistes a ON l.artist_id = a.artist_id AND l.plateforme = a.plateforme
        WHERE l.metric_value > p.metric_value
        AND ((l.metric_value - p.metric_value) * 100.0 / NULLIF(p.metric_value, 0)) > 10
        ORDER BY growth_percent DESC
        LIMIT 20
    """)
    
    results = cursor.fetchall()
    
    if not results:
        print("✅ Aucune alerte de croissance détectée")
        cursor.close()
        conn.close()
        return
    
    print(f"\n🔔 {len(results)} alertes de croissance détectées :")
    
    # Insérer les alertes
    for row in results:
        nom, artist_id, plateforme, current, previous, growth = row
        
        message = f"📈 Croissance de {growth:.1f}% ({int(previous):,} → {int(current):,})"
        
        cursor.execute("""
            INSERT INTO alertes (artist_id, nom_artiste, type_alerte, message, vu)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            artist_id,
            nom,
            'croissance_followers',
            message,
            False
        ))
        
        print(f"  • {nom} ({plateforme}): {message}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ {len(results)} alertes enregistrées")

if __name__ == "__main__":
    try:
        print("="*60)
        print("🔍 DÉTECTION D'ALERTES DE CROISSANCE")
        print("="*60)
        detect_growth_alerts()
        print("\n✅ Détection terminée")
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        exit(1)