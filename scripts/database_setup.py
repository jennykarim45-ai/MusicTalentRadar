import sqlite3
import pandas as pd
from datetime import datetime
import glob
import os

DB_NAME = 'jek2_records.db'

def create_database():
    """Cree la structure de la base de donnees"""
    print("Creation de la base de donnees JEK2 Records...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table principale des artistes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artistes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id TEXT UNIQUE,
            nom TEXT NOT NULL,
            plateforme TEXT NOT NULL,
            date_premiere_detection DATE NOT NULL,
            date_derniere_maj TIMESTAMP NOT NULL,
            url TEXT,
            image TEXT
        )
    ''')
    
    # Table historique des metriques
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metriques_historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id TEXT NOT NULL,
            plateforme TEXT NOT NULL,
            date_collecte TIMESTAMP NOT NULL,
            followers INTEGER,
            popularite INTEGER,
            score_potentiel REAL,
            genres TEXT,
            avg_track_popularity REAL,
            growth_indicator REAL,
            last_release_date TEXT,
            fans INTEGER,
            total_albums INTEGER,
            engagement_rate REAL,
            FOREIGN KEY (artist_id) REFERENCES artistes(artist_id)
        )
    ''')
    
    # Table des alertes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id TEXT NOT NULL,
            nom_artiste TEXT NOT NULL,
            type_alerte TEXT NOT NULL,
            message TEXT NOT NULL,
            date_alerte TIMESTAMP NOT NULL,
            vu BOOLEAN DEFAULT 0,
            FOREIGN KEY (artist_id) REFERENCES artistes(artist_id)
        )
    ''')
    
    # Index pour optimiser les requetes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_artist_id ON metriques_historique(artist_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date_collecte ON metriques_historique(date_collecte)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_plateforme ON metriques_historique(plateforme)')
    
    conn.commit()
    conn.close()
    
    print("Base de donnees creee avec succes !")
    print(f"  - Table 'artistes' : informations principales")
    print(f"  - Table 'metriques_historique' : evolution temporelle")
    print(f"  - Table 'alertes' : notifications")

def import_csv_data():
    """Importe les donnees existantes des CSV dans la base"""
    print("\nImportation des donnees CSV existantes...")
    
    conn = sqlite3.connect(DB_NAME)
    
    # Recherche des fichiers CSV Spotify
    spotify_files = glob.glob('data/spotify_emerging_artists_*.csv')
    deezer_files = glob.glob('data/deezer_emerging_artists_*.csv')
    
    if not spotify_files and not deezer_files:
        print("Aucun fichier CSV trouve dans le dossier 'data/'")
        print("Veuillez d'abord executer les scripts de collecte:")
        print("  python scripts/spotify_scraper.py")
        print("  python scripts/deezer_scraper.py")
        conn.close()
        return
    
    total_imported = 0
    
    # Import Spotify
    for file_path in spotify_files:
        print(f"\n  Import: {os.path.basename(file_path)}")
        try:
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                artist_id = row.get('id', f"spotify_{row['nom']}")
                
                # Insert ou update artiste
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO artistes (artist_id, nom, plateforme, date_premiere_detection, date_derniere_maj, url, image)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    artist_id,
                    row['nom'],
                    'Spotify',
                    datetime.now().strftime('%Y-%m-%d'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    row.get('url_spotify', ''),
                    row.get('image', '')
                ))
                
                # Insert metriques
                date_extraction = row.get('date_extraction', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                cursor.execute('''
                    INSERT INTO metriques_historique (
                        artist_id, plateforme, date_collecte, followers, popularite, 
                        score_potentiel, genres, avg_track_popularity, growth_indicator, last_release_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    artist_id,
                    'Spotify',
                    date_extraction,
                    row.get('followers', 0),
                    row.get('popularite', 0),
                    row.get('score_potentiel', 0),
                    row.get('genres', ''),
                    row.get('avg_track_popularity', 0),
                    row.get('growth_indicator', 0),
                    row.get('last_release_date', '')
                ))
                
                total_imported += 1
            
            conn.commit()
            print(f"    {len(df)} artistes Spotify importes")
            
        except Exception as e:
            print(f"    Erreur: {e}")
            continue
    
    # Import Deezer
    for file_path in deezer_files:
        print(f"\n  Import: {os.path.basename(file_path)}")
        try:
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                artist_id = row.get('artist_id', f"deezer_{row['nom']}")
                
                # Insert ou update artiste
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO artistes (artist_id, nom, plateforme, date_premiere_detection, date_derniere_maj, url, image)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    artist_id,
                    row['nom'],
                    'Deezer',
                    datetime.now().strftime('%Y-%m-%d'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    row.get('url_deezer', ''),
                    row.get('picture', '')
                ))
                
                # Insert metriques
                date_extraction = row.get('date_extraction', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                cursor.execute('''
                    INSERT INTO metriques_historique (
                        artist_id, plateforme, date_collecte, fans, 
                        total_albums, engagement_rate, score_potentiel
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    artist_id,
                    'Deezer',
                    date_extraction,
                    row.get('fans', 0),
                    row.get('total_albums', 0),
                    row.get('engagement_rate', 0),
                    row.get('score_potentiel', 0)
                ))
                
                total_imported += 1
            
            conn.commit()
            print(f"    {len(df)} artistes Deezer importes")
            
        except Exception as e:
            print(f"    Erreur: {e}")
            continue
    
    conn.close()
    
    print(f"\nTotal importe: {total_imported} entrees")
    print("Importation terminee !")

def show_database_stats():
    """Affiche les statistiques de la base de donnees"""
    print("\nStatistiques de la base de donnees:")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Nombre d'artistes
    cursor.execute("SELECT COUNT(*) FROM artistes")
    nb_artistes = cursor.fetchone()[0]
    print(f"Total artistes: {nb_artistes}")
    
    # Par plateforme
    cursor.execute("SELECT plateforme, COUNT(*) FROM artistes GROUP BY plateforme")
    for plateforme, count in cursor.fetchall():
        print(f"  - {plateforme}: {count}")
    
    # Nombre de points de donnees
    cursor.execute("SELECT COUNT(*) FROM metriques_historique")
    nb_metriques = cursor.fetchone()[0]
    print(f"\nPoints de donnees historiques: {nb_metriques}")
    
    # Alertes non lues
    cursor.execute("SELECT COUNT(*) FROM alertes WHERE vu = 0")
    nb_alertes = cursor.fetchone()[0]
    print(f"Alertes non lues: {nb_alertes}")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("JEK2 RECORDS - CONFIGURATION BASE DE DONNEES")
    print("=" * 60)
    
    create_database()
    import_csv_data()
    show_database_stats()
    
    print("\n" + "=" * 60)
    print("Configuration terminee !")
    print("Vous pouvez maintenant lancer:")
    print("  - python scripts/auto_scheduler.py : collecte automatique")
    print("  - streamlit run app/streamlit_dashboard.py : dashboard")
    print("=" * 60)