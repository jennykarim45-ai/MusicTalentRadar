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
    import os
    
    # Déterminer le bon chemin
    if os.path.exists('../data'):
        data_path = '../data'
    elif os.path.exists('data'):
        data_path = 'data'
    else:
        print("❌ Dossier 'data' introuvable")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Import Spotify
    spotify_files = glob.glob(f'{data_path}/spotify_emerging_artists_*.csv')
    print(f"Fichiers Spotify trouvés: {len(spotify_files)}")
    
    for file in spotify_files:
        print(f"Import {file}...")
        df = pd.read_csv(file)
        print(f"  → {len(df)} artistes dans le fichier")
        
        for _, row in df.iterrows():
            # Insert artiste
            cursor.execute("""
                INSERT INTO artistes (artist_id, nom, plateforme, url, image_url)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (artist_id, plateforme) DO NOTHING
            """, (
                str(row.get('id', '')),
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
                str(row.get('id', '')),
                'Spotify',
                int(row.get('followers', 0)) if pd.notna(row.get('followers')) else 0,
                int(row.get('popularite', 0)) if pd.notna(row.get('popularite')) else 0,
                float(row.get('score_potentiel', 0)) if pd.notna(row.get('score_potentiel')) else 0,
                row.get('date_extraction', datetime.now())
            ))
        
        print(f"  ✅ Importé")
    
    # Import Deezer
    deezer_files = glob.glob(f'{data_path}/deezer_emerging_artists_*.csv')
    print(f"Fichiers Deezer trouvés: {len(deezer_files)}")
    
    for file in deezer_files:
        print(f"Import {file}...")
        df = pd.read_csv(file)
        print(f"  → {len(df)} artistes dans le fichier")
        
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
                int(row.get('fans', 0)) if pd.notna(row.get('fans')) else 0,
                float(row.get('score_potentiel', 0)) if pd.notna(row.get('score_potentiel')) else 0,
                float(row.get('engagement_rate', 0)) if pd.notna(row.get('engagement_rate')) else 0,
                int(row.get('total_albums', 0)) if pd.notna(row.get('total_albums')) else 0,
                row.get('date_extraction', datetime.now())
            ))
        
        print(f"  ✅ Importé")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    total_files = len(spotify_files) + len(deezer_files)
    if total_files == 0:
        print("⚠️ Aucun fichier CSV trouvé")
    else:
        print(f"\n✅ Import terminé ({total_files} fichiers)")

if __name__ == "__main__":
    print("Initialisation de la base PostgreSQL...")
    init_database()
    
    print("\nImport des données CSV...")
    import_csv_to_postgres()
    
    print("\n✅ Configuration terminée !")
