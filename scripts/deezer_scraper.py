import requests
import pandas as pd
from datetime import datetime
import time
import os

# Configuration
MIN_FANS = 100
MAX_FANS = 100000

# Mots-cles de recherche
SEARCH_QUERIES = [
    'rap',
    'hip hop',
    'trap',
    'rnb',
    'r&b',
    'drill',
    'soul',
    'french rap',
    'french hip hop',
    'france',
    'paris',
    'marseille'
]

def search_deezer_artists(query, limit=100):
    """Recherche d'artistes sur Deezer"""
    try:
        print(f"  Recherche: '{query}'")
        
        url = 'https://api.deezer.com/search/artist'
        params = {
            'q': query,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            artists = data.get('data', [])
            print(f"    {len(artists)} artistes trouves")
            return artists
        else:
            print(f"    Erreur: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"  Erreur recherche: {e}")
        return []

def get_artist_details(artist_id):
    """Recupere les details d'un artiste"""
    try:
        url = f'https://api.deezer.com/artist/{artist_id}'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        return None

def get_artist_top_tracks(artist_id, limit=10):
    """Recupere les top tracks d'un artiste"""
    try:
        url = f'https://api.deezer.com/artist/{artist_id}/top'
        params = {'limit': limit}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            return []
            
    except Exception as e:
        return []

def get_artist_albums(artist_id, limit=10):
    """Recupere les albums d'un artiste"""
    try:
        url = f'https://api.deezer.com/artist/{artist_id}/albums'
        params = {'limit': limit}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            return []
            
    except Exception as e:
        return []

def calculate_engagement_rate(artist_data, top_tracks):
    """Calcule un taux d'engagement approximatif"""
    if not top_tracks:
        return 0
    
    avg_rank = sum([track.get('rank', 100000) for track in top_tracks]) / len(top_tracks)
    engagement = min(avg_rank / 100000 * 100, 100)
    
    return round(engagement, 2)

def is_recent_activity(albums):
    """Verifie si l'artiste a sorti quelque chose recemment"""
    if not albums:
        return False
    
    try:
        most_recent = albums[0]
        release_date = most_recent.get('release_date', '')
        
        if not release_date:
            return True
        
        from datetime import datetime
        try:
            release_datetime = datetime.strptime(release_date, '%Y-%m-%d')
        except:
            return True
        
        months_ago = (datetime.now() - release_datetime).days / 30
        
        return months_ago <= 24
        
    except:
        return True

def is_french_artist(artist_details):
    """Verifie si l'artiste est francais"""
    name = artist_details.get('name', '').lower()
    
    generic_keywords = ['rap francais', 'hip hop francais', 'france rap']
    if any(keyword in name for keyword in generic_keywords):
        return False
    
    return True

def calculate_potential_score(artist):
    """Calcule un score de potentiel STRICT pour Deezer (0-100)"""
    
    # 1. SCORE FANS (25 points max) - Plus strict
    fans = artist['fans']
    if 8000 <= fans <= 25000:  # Sweet spot plus étroit
        fans_score = 25
    elif 5000 <= fans < 8000:
        fans_score = 20
    elif 3000 <= fans < 5000:
        fans_score = 15
    elif 1000 <= fans < 3000:
        fans_score = 10
    else:
        # Au-delà de 25K, score décroissant (trop connu)
        if fans > 25000:
            fans_score = max(5, 25 - (fans - 25000) / 5000)
        else:
            fans_score = (fans / 3000) * 8
    
    # 2. ENGAGEMENT (25 points max) - Plus strict
    engagement = artist['engagement_rate']
    if engagement >= 80:
        engagement_score = 25
    elif engagement >= 60:
        engagement_score = 20
    elif engagement >= 40:
        engagement_score = 15
    elif engagement >= 20:
        engagement_score = 10
    else:
        engagement_score = (engagement / 20) * 8
    
    # 3. DISCOGRAPHIE (20 points max) - Récompense la régularité
    albums = artist['total_albums']
    if 3 <= albums <= 8:  # Sweet spot : actif mais pas surproduction
        albums_score = 20
    elif 2 <= albums < 3:
        albums_score = 15
    elif albums >= 9:
        albums_score = 15  # Trop d'albums = moins de "pépite"
    else:
        albums_score = albums * 8  # 1 album = 8 points
    
    # 4. RADIO (15 points max) - Réduit car trop courant
    radio_score = 15 if artist['radio'] else 8
    
    # 5. RATIO FANS/ALBUMS (15 points max) - Nouveau critère de qualité
    if albums > 0:
        ratio = fans / albums
        if 1000 <= ratio <= 8000:  # Bon équilibre popularité/production
            ratio_score = 15
        elif 500 <= ratio < 1000:
            ratio_score = 10
        else:
            ratio_score = min((ratio / 8000) * 12, 12)
    else:
        ratio_score = 0
    
    total = fans_score + engagement_score + albums_score + radio_score + ratio_score
    
    # Bonus/Malus final
    # Bonus pour les vrais émergents (5K-15K fans)
    if 5000 <= fans <= 15000:
        total = min(total + 5, 100)
    
    # Malus pour les très populaires (>40K = moins émergent)
    if fans > 40000:
        total = total * 0.85
    
    return round(min(total, 100), 2)

def main():
    """Fonction principale"""
    print("JEK2 RECORDS - TALENT SCOUTING DEEZER")
    print("Recherche d'artistes francais emergents")
    print("=" * 70)
    
    print("\nETAPE 1: Recherche d'artistes...")
    all_artists = []
    seen_ids = set()
    
    for query in SEARCH_QUERIES:
        artists = search_deezer_artists(query, limit=100)
        
        for artist in artists:
            artist_id = artist.get('id')
            if artist_id and artist_id not in seen_ids:
                seen_ids.add(artist_id)
                all_artists.append(artist)
        
        time.sleep(0.5)
    
    print(f"\n{len(all_artists)} artistes candidats")
    
    if len(all_artists) > 500:
        print(f"Limitation a 500 artistes")
        all_artists = all_artists[:500]
    
    print("\nETAPE 2: Analyse detaillee...")
    print("Cela peut prendre quelques minutes...")
    print("   Filtres actifs:")
    print(f"   • Fans: {MIN_FANS:,}-{MAX_FANS:,}")
    print(f"   • Activite recente: < 24 mois")
    print()
    
    artists_data = []
    all_artists_raw = []
    
    for i, artist in enumerate(all_artists, 1):
        if i % 20 == 0:
            print(f"  Progression: {i}/{len(all_artists)} | Valides: {len(artists_data)}")
        
        artist_id = artist.get('id')
        
        artist_details = get_artist_details(artist_id)
        
        if not artist_details:
            continue
        
        fans = artist_details.get('nb_fan', 0)
        
        albums = get_artist_albums(artist_id, limit=10)
        top_tracks = get_artist_top_tracks(artist_id, limit=10)
        
        raw_artist = {
            'nom': artist_details.get('name', ''),
            'fans': fans,
            'total_albums': artist_details.get('nb_album', 0),
            'url_deezer': artist_details.get('link', '')
        }
        
        all_artists_raw.append(raw_artist)
        
        if not is_french_artist(artist_details):
            continue
        
        if not (MIN_FANS <= fans <= MAX_FANS):
            continue
        
        if not is_recent_activity(albums):
            continue
        
        engagement_rate = calculate_engagement_rate(artist_details, top_tracks)
        
        artist_info = {
            'artist_id': artist_id,
            'nom': artist_details.get('name', ''),
            'fans': fans,
            'total_albums': artist_details.get('nb_album', 0),
            'engagement_rate': engagement_rate,
            'radio': artist_details.get('radio', False),
            'picture': artist_details.get('picture_medium', ''),
            'url_deezer': artist_details.get('link', ''),
            'date_extraction': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        artists_data.append(artist_info)
        time.sleep(0.3)
    
    print("\n" + "=" * 80)
    print("TOUS LES ARTISTES TROUVES (AVANT FILTRAGE)")
    print("=" * 80)
    
    # S'assurer que le dossier data existe
    os.makedirs('../data', exist_ok=True)
    
    if all_artists_raw:
        df_raw = pd.DataFrame(all_artists_raw)
        df_raw = df_raw.sort_values('fans', ascending=False)
        
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 40)
        
        print(df_raw.to_string(index=False))
        print(f"\nTotal: {len(df_raw)}")
        
        filename_raw = f'../data/deezer_all_artists_raw_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df_raw.to_csv(filename_raw, index=False, encoding='utf-8-sig')
        print(f"Donnees brutes: {filename_raw}")
    
    print("\n" + "=" * 80)
    print("ARTISTES VALIDES (FRANCAIS EMERGENTS)")
    print("=" * 80)
    print(f"{len(artists_data)} artistes valides")
    
    if len(artists_data) == 0:
        print("\nAucun artiste valide. Verifier les donnees brutes.")
        return
    
    for artist in artists_data:
        artist['score_potentiel'] = calculate_potential_score(artist)
    
    artists_data.sort(key=lambda x: x['score_potentiel'], reverse=True)
    
    df = pd.DataFrame(artists_data)
    
    column_order = [
        'nom', 'fans', 'total_albums', 'engagement_rate', 
        'score_potentiel', 'radio', 'url_deezer', 'date_extraction'
    ]
    df = df[column_order]
    
    filename = f'../data/deezer_emerging_artists_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"\nDonnees validees: {filename}")
    print(df.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("STATISTIQUES:")
    print(f"  • Total valides: {len(df)}")
    print(f"  • Moyenne fans: {df['fans'].mean():.0f}")
    print(f"  • Mediane fans: {df['fans'].median():.0f}")
    print(f"  • Albums moyens: {df['total_albums'].mean():.1f}")
    print(f"  • Engagement moyen: {df['engagement_rate'].mean():.2f}%")
    print(f"  • Score moyen: {df['score_potentiel'].mean():.1f}")
    print(f"  • Meilleur score: {df['score_potentiel'].max():.1f}")
    print(f"  • Presence radio: {df['radio'].sum()} artistes")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERREUR: {str(e)}")
        import traceback
        traceback.print_exc()