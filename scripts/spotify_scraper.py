import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from datetime import datetime, timedelta

# Configuration
try:
    from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
    CLIENT_ID = SPOTIFY_CLIENT_ID
    CLIENT_SECRET = SPOTIFY_CLIENT_SECRET
except ImportError:
    CLIENT_ID = 'b0db9b64906d4b85be2b4fad1fd55298'
    CLIENT_SECRET = '99b48bf848d44b80b070c92f7c87eb64'

# Filtres stricts pour artistes émergents
MIN_FOLLOWERS = 1000
MAX_FOLLOWERS = 50000
MIN_POPULARITY = 10
MAX_POPULARITY = 60
MIN_RECENT_RELEASE_MONTHS = 24

# Mots à exclure
EXCLUDE_KEYWORDS = [
    'official', 'records', 'music', 'label', 'compilation', 
    'various artists', 'soundtrack', 'ost', 'tribute'
]

# Authentification
auth_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
sp = spotipy.Spotify(auth_manager=auth_manager)

def is_valid_artist(artist_name):
    """Vérifie si le nom de l'artiste n'est pas une compilation ou un label"""
    name_lower = artist_name.lower()
    return not any(keyword in name_lower for keyword in EXCLUDE_KEYWORDS)

def search_emerging_artists_from_playlists(genres, queries):
    """Recherche ciblée dans des playlists de découverte"""
    all_artists = []
    seen_ids = set()
    
    for query in queries:
        print(f"\nRecherche: '{query}'")
        
        try:
            playlists = sp.search(q=query, type='playlist', limit=15, market='FR')
            
            for playlist in playlists['playlists']['items']:
                if not playlist:
                    continue
                
                playlist_name = playlist['name'].lower()
                playlist_id = playlist['id']
                
                if any(word in playlist_name for word in ['nouveauté', 'découverte', 'émergent', 'underground', 'indé', 'nouveau', 'fresh', 'upcoming']):
                    print(f"  Playlist: {playlist['name']} ({playlist.get('tracks', {}).get('total', 0)} tracks)")
                    
                    try:
                        tracks = sp.playlist_tracks(playlist_id, limit=100)
                        
                        for item in tracks['items']:
                            if not item.get('track') or not item['track'].get('artists'):
                                continue
                            
                            for artist in item['track']['artists']:
                                artist_id = artist['id']
                                artist_name = artist['name']
                                
                                if artist_id and artist_id not in seen_ids and is_valid_artist(artist_name):
                                    seen_ids.add(artist_id)
                                    all_artists.append({'id': artist_id, 'name': artist_name})
                        
                        time.sleep(0.5)
                    
                    except Exception as e:
                        print(f"    Erreur playlist: {str(e)}")
                        continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"  Erreur recherche '{query}': {str(e)}")
            continue
    
    return all_artists

def get_artist_recent_albums(artist_id):
    """Vérifie les sorties récentes de l'artiste"""
    try:
        albums = sp.artist_albums(artist_id, limit=10, album_type='album,single')
        
        if not albums['items']:
            return False, None
        
        most_recent = albums['items'][0]
        release_date = most_recent.get('release_date', '')
        
        if not release_date:
            return False, None
        
        try:
            if len(release_date) == 4:
                release_date += '-01-01'
            
            release_datetime = datetime.strptime(release_date, '%Y-%m-%d')
            months_ago = (datetime.now() - release_datetime).days / 30
            
            is_recent = months_ago <= MIN_RECENT_RELEASE_MONTHS
            
            return is_recent, release_date
            
        except:
            return False, None
            
    except Exception as e:
        return False, None

def get_artist_details(artist_id):
    """Récupère les détails complets d'un artiste avec filtres stricts"""
    try:
        artist = sp.artist(artist_id)
        
        popularity = artist['popularity']
        if not (MIN_POPULARITY <= popularity <= MAX_POPULARITY):
            return None
        
        followers = artist['followers']['total']
        if not (MIN_FOLLOWERS <= followers <= MAX_FOLLOWERS):
            return None
        
        is_recent, last_release = get_artist_recent_albums(artist_id)
        if not is_recent:
            return None
        
        genres = artist['genres']
        genre_keywords = ['rap', 'hip hop', 'hip-hop', 'rnb', 'r&b', 'soul', 'trap', 'drill']
        has_relevant_genre = any(
            any(keyword in genre.lower() for keyword in genre_keywords) 
            for genre in genres
        ) if genres else False
        
        top_tracks = sp.artist_top_tracks(artist_id, country='FR')
        
        if not top_tracks['tracks']:
            return None
        
        avg_popularity = sum([track['popularity'] for track in top_tracks['tracks']]) / len(top_tracks['tracks'])
        
        growth_indicator = popularity - avg_popularity
        
        artist_data = {
            'id': artist['id'],
            'nom': artist['name'],
            'followers': followers,
            'genres': ', '.join(genres) if genres else 'Non spécifié',
            'popularite': popularity,
            'avg_track_popularity': round(avg_popularity, 2),
            'growth_indicator': round(growth_indicator, 2),
            'last_release_date': last_release,
            'url_spotify': artist['external_urls']['spotify'],
            'image': artist['images'][0]['url'] if artist['images'] else None,
            'date_extraction': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return artist_data
        
    except Exception as e:
        print(f"  Erreur artiste {artist_id}: {str(e)}")
        return None

def calculate_potential_score(artist):
    """Calcule un score de potentiel avec des critères affinés"""
    if 30 <= artist['popularite'] <= 60:
        popularity_score = 30
    elif 20 <= artist['popularite'] < 30:
        popularity_score = 25
    else:
        popularity_score = (artist['popularite'] / MAX_POPULARITY) * 20
    
    track_score = (artist['avg_track_popularity'] / 100) * 20
    
    if 5000 <= artist['followers'] <= 20000:
        followers_score = 25
    else:
        followers_score = (artist['followers'] / MAX_FOLLOWERS) * 20
    
    growth_score = max(0, min(artist['growth_indicator'] * 0.5, 15))
    
    try:
        if artist['last_release_date']:
            release_year = int(artist['last_release_date'][:4])
            current_year = datetime.now().year
            
            if release_year == current_year:
                recency_score = 10
            elif release_year == current_year - 1:
                recency_score = 7
            else:
                recency_score = 4
        else:
            recency_score = 0
    except:
        recency_score = 0
    
    total_score = popularity_score + track_score + followers_score + growth_score + recency_score
    
    return round(total_score, 2)

# Programme principal
print("JEK2 RECORDS - TALENT SCOUTING SPOTIFY V2")
print("Recherche ciblée d'artistes émergents (< 50K followers)")
print("=" * 70)

search_queries = [
    'rap français nouveauté découverte',
    'hip hop français émergent',
    'rap français underground indépendant',
    'nouveauté rap france',
    'découverte hip hop français',
    'artiste émergent rap français',
    'nouveau rappeur français',
    'rap français indé',
    'rnb français nouveauté',
    'soul français émergent'
]

genres = ['rap français', 'hip hop français', 'rnb français']

print("\nETAPE 1: Recherche d'artistes émergents...")
artists_list = search_emerging_artists_from_playlists(genres, search_queries)
print(f"\n{len(artists_list)} artistes candidats trouvés")

print("\nETAPE 2: Analyse détaillée et filtrage strict...")
print("Cela peut prendre plusieurs minutes...")
print("   Filtres actifs:")
print(f"   • Popularité: {MIN_POPULARITY}-{MAX_POPULARITY}")
print(f"   • Followers: {MIN_FOLLOWERS:,}-{MAX_FOLLOWERS:,}")
print(f"   • Activité récente: < {MIN_RECENT_RELEASE_MONTHS} mois")
print()

artists_details = []
rejected_count = {
    'popularity': 0,
    'followers': 0,
    'no_recent_release': 0,
    'other': 0
}

for i, artist in enumerate(artists_list[:1000], 1):
    if i % 25 == 0:
        print(f"  Progression: {i}/{min(1000, len(artists_list))} | Validés: {len(artists_details)}")
    
    details = get_artist_details(artist['id'])
    if details:
        artists_details.append(details)
    
    time.sleep(0.3)

print(f"\n{len(artists_details)} artistes émergents validés après filtrage")

if len(artists_details) == 0:
    print("\nAucun artiste ne correspond aux critères stricts.")
    print("Suggestions:")
    print("  - Élargir la fourchette de popularité")
    print("  - Élargir la fourchette de followers")
    print("  - Augmenter le délai de sortie récente")
    exit()

print("\nETAPE 3: Calcul du score de potentiel...")
for artist in artists_details:
    artist['score_potentiel'] = calculate_potential_score(artist)

artists_details.sort(key=lambda x: x['score_potentiel'], reverse=True)

df = pd.DataFrame(artists_details)

column_order = [
    'nom', 'followers', 'popularite', 'avg_track_popularity', 
    'growth_indicator', 'score_potentiel', 'last_release_date',
    'genres', 'url_spotify', 'date_extraction'
]
df = df[column_order]

filename = f'../data/spotify_emerging_artists_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
df.to_csv(filename, index=False, encoding='utf-8-sig')

print(f"\nDonnées exportées dans: {filename}")
print(f"\n{len(df)} ARTISTES ÉMERGENTS TROUVÉS (classés par potentiel)")
print("=" * 80)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 40)

print(df.to_string(index=False))

print("\n" + "=" * 80)
print("STATISTIQUES:")
print(f"  • Total d'artistes émergents: {len(df)}")
print(f"  • Moyenne followers: {df['followers'].mean():.0f}")
print(f"  • Médiane followers: {df['followers'].median():.0f}")
print(f"  • Moyenne popularité: {df['popularite'].mean():.1f}")
print(f"  • Score potentiel moyen: {df['score_potentiel'].mean():.1f}")
print(f"  • Meilleur score: {df['score_potentiel'].max():.1f}")
print(f"  • Score le plus bas: {df['score_potentiel'].min():.1f}")
print(f"\nTop 3 artistes les plus prometteurs:")
for i, row in df.head(3).iterrows():
    print(f"   {i+1}. {row['nom']} - Score: {row['score_potentiel']} | {row['followers']:,} followers")