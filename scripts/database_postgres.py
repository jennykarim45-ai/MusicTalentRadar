import psycopg2
from psycopg2.extras import RealDictCursor
import os
import streamlit as st

def get_database_url():
    """Récupère l'URL de la base de données depuis les secrets Streamlit"""
    try:
        # En production (Streamlit Cloud)
        return st.secrets["DATABASE_URL"]
    except:
        # En local (pour tests)
        return os.getenv("DATABASE_URL", "")

def get_connection():
    """Crée une connexion à la base PostgreSQL"""
    db_url = get_database_url()
    if not db_url:
        raise Exception("DATABASE_URL non configurée")
    return psycopg2.connect(db_url)

def init_database():
    """Initialise les tables PostgreSQL"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table artistes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artistes (
            id SERIAL PRIMARY KEY,
            artist_id VARCHAR(255) NOT NULL,
            nom VARCHAR(255) NOT NULL,
            plateforme VARCHAR(50) NOT NULL,
            url TEXT,
            image_url TEXT,
            date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(artist_id, plateforme)
        )
    """)
    
    # Index sur artist_id pour performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_artist_id ON artistes(artist_id)
    """)
    
    # Table métriques historique (SANS foreign key)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metriques_historique (
            id SERIAL PRIMARY KEY,
            artist_id VARCHAR(255) NOT NULL,
            plateforme VARCHAR(50) NOT NULL,
            date_collecte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            followers INTEGER,
            fans INTEGER,
            popularite INTEGER,
            score_potentiel DECIMAL(5,2),
            engagement_rate DECIMAL(5,2),
            total_albums INTEGER
        )
    """)
    
    # Index pour performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_metrics_artist_platform 
        ON metriques_historique(artist_id, plateforme)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_date_collecte 
        ON metriques_historique(date_collecte DESC)
    """)
    
    # Table alertes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertes (
            id SERIAL PRIMARY KEY,
            artist_id VARCHAR(255) NOT NULL,
            nom_artiste VARCHAR(255),
            type_alerte VARCHAR(100),
            message TEXT,
            date_alerte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vu BOOLEAN DEFAULT FALSE
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_alertes_artist ON alertes(artist_id)
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Base de données PostgreSQL initialisée")

def import_csv_to_postgres():
    """Importe les données CSV existantes vers PostgreSQL"""
    import pandas as pd
    import glob
    from datetime import datetime
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Import Spotify
    spotify_files = glob.glob('data/spotify_emerging_artists_*.csv')
    for file in spotify_files:
        print(f"Import {file}...")
        df = pd.read_csv(file)
        
        for _, row in df.iterrows():
            # Insert artiste
            cursor.execute("""
                INSERT INTO artistes (artist_id, nom, plateforme, url, image_url)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (artist_id, plateforme) DO NOTHING
            """, (
                row.get('id', ''),
                row['nom'],
                'Spotify',
                row.get('url_spotify', ''),
                row.get('image', '')
            ))
            
            # Insert métriques
            cursor.execute("""
                INSERT INTO metriques_historique 
                (artist_id, plateforme, followers, popularite, score_potentiel, date_collecte)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                row.get('id', ''),
                'Spotify',
                row.get('followers', 0),
                row.get('popularite', 0),
                row.get('score_potentiel', 0),
                row.get('date_extraction', datetime.now())
            ))
    
    # Import Deezer
    deezer_files = glob.glob('data/deezer_emerging_artists_*.csv')
    for file in deezer_files:
        print(f"Import {file}...")
        df = pd.read_csv(file)
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO artistes (artist_id, nom, plateforme, url, image_url)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (artist_id, plateforme) DO NOTHING
            """, (
                str(row.get('artist_id', '')),
                row['nom'],
                'Deezer',
                row.get('url_deezer', ''),
                row.get('picture', '')
            ))
            
            cursor.execute("""
                INSERT INTO metriques_historique 
                (artist_id, plateforme, fans, score_potentiel, engagement_rate, 
                 total_albums, date_collecte)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                str(row.get('artist_id', '')),
                'Deezer',
                row.get('fans', 0),
                row.get('score_potentiel', 0),
                row.get('engagement_rate', 0),
                row.get('total_albums', 0),
                row.get('date_extraction', datetime.now())
            ))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Import terminé")

if __name__ == "__main__":
    print("Initialisation de la base PostgreSQL...")
    init_database()
    
    print("\nImport des données CSV...")
    import_csv_to_postgres()
    
    print("\n✅ Configuration terminée !")
