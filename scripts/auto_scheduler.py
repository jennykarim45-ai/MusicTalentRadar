import schedule
import time
import subprocess
import sqlite3
from datetime import datetime
import logging
import os

DB_NAME = 'jek2_records.db'

# Configuration du logging
os.makedirs('../logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/auto_collector.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def detect_growth_alerts():
    """Detecte les artistes en forte croissance et cree des alertes"""
    logger.info("Detection des alertes de croissance...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Requete pour detecter la croissance
    query = '''
        WITH latest_metrics AS (
            SELECT 
                artist_id,
                plateforme,
                followers,
                fans,
                score_potentiel,
                date_collecte,
                ROW_NUMBER() OVER (PARTITION BY artist_id, plateforme ORDER BY date_collecte DESC) as rn
            FROM metriques_historique
        ),
        previous_metrics AS (
            SELECT 
                artist_id,
                plateforme,
                followers,
                fans,
                score_potentiel,
                date_collecte,
                ROW_NUMBER() OVER (PARTITION BY artist_id, plateforme ORDER BY date_collecte DESC) as rn
            FROM metriques_historique
        )
        SELECT 
            l.artist_id,
            a.nom,
            l.plateforme,
            COALESCE(l.followers, l.fans) as latest_followers,
            COALESCE(p.followers, p.fans) as previous_followers,
            l.score_potentiel as latest_score,
            p.score_potentiel as previous_score
        FROM latest_metrics l
        JOIN previous_metrics p ON l.artist_id = p.artist_id AND l.plateforme = p.plateforme
        JOIN artistes a ON l.artist_id = a.artist_id
        WHERE l.rn = 1 AND p.rn = 2
    '''
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        alerts_created = 0
        
        for row in results:
            artist_id, nom, plateforme, latest_followers, previous_followers, latest_score, previous_score = row
            
            if latest_followers and previous_followers and previous_followers > 0:
                growth_pct = ((latest_followers - previous_followers) / previous_followers) * 100
                
                # Alerte si croissance > 20%
                if growth_pct >= 20:
                    message = f"Forte croissance de {growth_pct:.1f}% des followers sur {plateforme} ({previous_followers} -> {latest_followers})"
                    
                    cursor.execute('''
                        INSERT INTO alertes (artist_id, nom_artiste, type_alerte, message, date_alerte, vu)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (artist_id, nom, 'FORTE_CROISSANCE', message, datetime.now(), 0))
                    
                    alerts_created += 1
                    logger.info(f"Alerte creee: {nom} - {message}")
            
            # Alerte si score augmente significativement
            if latest_score and previous_score:
                score_increase = latest_score - previous_score
                if score_increase >= 10:
                    message = f"Score en hausse de {score_increase:.1f} points ({previous_score:.1f} -> {latest_score:.1f})"
                    
                    cursor.execute('''
                        INSERT INTO alertes (artist_id, nom_artiste, type_alerte, message, date_alerte, vu)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (artist_id, nom, 'AMELIORATION_SCORE', message, datetime.now(), 0))
                    
                    alerts_created += 1
                    logger.info(f"Alerte creee: {nom} - {message}")
        
        conn.commit()
        logger.info(f"{alerts_created} nouvelles alertes creees")
        
    except Exception as e:
        logger.error(f"Erreur detection alertes: {e}")
    
    finally:
        conn.close()

def run_spotify_scraper():
    """Execute le scraper Spotify"""
    logger.info("=" * 70)
    logger.info("Lancement collecte Spotify...")
    logger.info("=" * 70)
    
    try:
        result = subprocess.run(
            ['python', 'spotify_scraper.py'],
            cwd='../scripts',
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes max
        )
        
        if result.returncode == 0:
            logger.info("Collecte Spotify reussie")
            logger.info(result.stdout)
        else:
            logger.error(f"Erreur collecte Spotify: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout collecte Spotify (> 30 min)")
    except Exception as e:
        logger.error(f"Erreur execution Spotify: {e}")

def run_deezer_scraper():
    """Execute le scraper Deezer"""
    logger.info("=" * 70)
    logger.info("Lancement collecte Deezer...")
    logger.info("=" * 70)
    
    try:
        result = subprocess.run(
            ['python', 'deezer_scraper.py'],
            cwd='../scripts',
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes max
        )
        
        if result.returncode == 0:
            logger.info("Collecte Deezer reussie")
            logger.info(result.stdout)
        else:
            logger.error(f"Erreur collecte Deezer: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout collecte Deezer (> 30 min)")
    except Exception as e:
        logger.error(f"Erreur execution Deezer: {e}")

def update_database():
    """Met a jour la base de donnees avec les nouvelles donnees"""
    logger.info("Mise a jour de la base de donnees...")
    
    try:
        result = subprocess.run(
            ['python', 'database_setup.py'],
            cwd='../scripts',
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        if result.returncode == 0:
            logger.info("Base de donnees mise a jour")
        else:
            logger.error(f"Erreur MAJ database: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Erreur MAJ database: {e}")

def daily_collection_job():
    """Job de collecte quotidienne complete"""
    logger.info("\n" + "=" * 70)
    logger.info("DEBUT COLLECTE QUOTIDIENNE - " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("=" * 70)
    
    # 1. Collecte Spotify
    run_spotify_scraper()
    time.sleep(5)
    
    # 2. Collecte Deezer
    run_deezer_scraper()
    time.sleep(5)
    
    # 3. Mise a jour BDD
    update_database()
    time.sleep(2)
    
    # 4. Detection alertes
    detect_growth_alerts()
    
    logger.info("=" * 70)
    logger.info("FIN COLLECTE QUOTIDIENNE")
    logger.info("=" * 70 + "\n")

def main():
    """Programme principal du scheduler"""
    print("=" * 70)
    print("JEK2 RECORDS - COLLECTEUR AUTOMATIQUE")
    print("=" * 70)
    print("\nConfiguration:")
    print("  - Collecte quotidienne a 02:00")
    print("  - Spotify + Deezer + Detection alertes")
    print("  - Logs: logs/auto_collector.log")
    print("\nAppuyez sur Ctrl+C pour arreter")
    print("=" * 70 + "\n")
    
    # Planification quotidienne a 2h du matin
    schedule.every().day.at("02:00").do(daily_collection_job)
    
    # Option: collecte immediate au demarrage (decommenter si besoin)
    # logger.info("Collecte immediate au demarrage...")
    # daily_collection_job()
    
    logger.info("Scheduler demarre. En attente de la prochaine collecte...")
    logger.info(f"Prochaine execution: {schedule.next_run()}")
    
    # Boucle principale
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifie toutes les minutes
            
    except KeyboardInterrupt:
        logger.info("\nArret du scheduler demande par l'utilisateur")
        print("\nScheduler arrete proprement.")

if __name__ == "__main__":
    main()