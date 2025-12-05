"""
Scraper Deezer V6 - Approche par LABELS et GRAPHE D'ARTISTES
1. Partir d'artistes seed connus
2. Utiliser l'API "related artists" de Deezer
3. Explorer le graphe des artistes similaires
"""
import requests
import pandas as pd
from datetime import datetime
import time
import os

# Configuration
MIN_FANS = 1000
MAX_FANS = 100000

# ARTISTES SEED (connus, on part d'eux pour trouver les autres)
SEED_ARTISTS = [
    # Top rappeurs français (on les utilise comme point de départ)
    'ninho', 'jul', 'sch', 'booba', 'pnl', 'naps', 'soso maness',
    'niska', 'kaaris', 'freeze corleone', 'laylow', 'zola', 'rim k',
    'tiakola', 'leto', 'gazo', 'koba lad', 'soolking', 'heuss lenfoire',
    'maes', 'alonzo', 'gradur', 'lacrim', 'mhd', 'damso', 'hamza',
    'josman', 'kerchak', 'dinos', 'lomepal', 'nekfeu', 'orelsan','Hatik',
    'alpha wann', 'lefa', 'vald', 'columbine', 'eddy de pretto',
    'Tayc', 'Dadju', 'Vegedream','Maitres Gims','SDM','Black M',
    'sofiane','rsko', 'luther', 'zed', 'lyonzon',
    'elams','kofs', 'sat lherbier', 'moubarak', 'fahar',
    'guy2bezbar', 'moha la squale',
    'shotas', 'doria', 'kpri', 'cimer', 'pi\'erre bourne','Arsenik','Mafia K-1 Fry',
    'La Fouine','Sinik','Rohff','Sefyu','L\'Algérino','Soprano',
    'Medine','Youssoupha','Kery James','Nessbeal','Zoxea','NTM',
    'Pit Baccardi', 'Les Sages Poètes de la Rue', 'Sages Po',  # Ajout nouveaux
    
    # Top rappeuses/chanteuses françaises
    'chilla', 'lous and the yakuza', 'shay', 'djadja & dinaz', 'wejdene',
    'keny arkana', 'aya Nakamura', 'nora fatehi', 'lina',
    'Lala&ce', 'Meryl','Le Juiice','Imen Es','Doria','Vicky R','Eva Queen',
    'diam\'s','Lyna Mahyem','NEJ','Princess Aniès','Vitaa',
    'Zaho','Lady Laistee','Amel Bent'
]

# Blacklist
FORBIDDEN_NAMES = [
    'françois', 'francis', 'francois', 'compilation', 'various artists',
    'best of', 'greatest', 'lofi hip hop', 'chill beats', 'instrumental',
    'trap nation', 'rap nation', 'music factory', 'trap king', 'uk drill',
    'cut killer', 'dj', 'orchestra', 'orchestre', 'symphony',
    'k-trap', 'onf', 'hiphop tamizha', 'nikka costa', 'ryan paris',
    'nino ferrer', 'käärijä', 'hungria', 'comunidade', 'damaris',
    'trapped under ice', 'renee rapp', 'elyon',
    # Artistes connus non-rap ou hors genre
    'elsa esnoult', 'antilopa', 'antilopsa',
    'iliona',  # Pop, pas rap
    'julia beautx', 'beautx',  # Youtubeuse, pas française rap
    'babyhayabuse', 'baby hayabuse',  # Pas français
    'melissa m', 'mélissa m',  # Connue, R&B/Pop
]

def search_artist_by_name(name):
    """Recherche artiste par nom exact"""
    try:
        url = 'https://api.deezer.com/search/artist'
        params = {'q': name, 'limit': 1}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            artists = data.get('data', [])
            return artists[0] if artists else None
        
        return None
    except:
        return None

def get_artist_details(artist_id):
    """Détails complets artiste"""
    try:
        response = requests.get(f'https://api.deezer.com/artist/{artist_id}', timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_related_artists(artist_id):
    """CLEF : Récupère les artistes similaires !"""
    try:
        url = f'https://api.deezer.com/artist/{artist_id}/related'
        params = {'limit': 50}  # Max 50 artistes similaires
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        
        return []
    except:
        return []

def get_artist_top_tracks(artist_id, limit=10):
    try:
        response = requests.get(f'https://api.deezer.com/artist/{artist_id}/top', 
                               params={'limit': limit}, timeout=10)
        return response.json().get('data', []) if response.status_code == 200 else []
    except:
        return []

def get_artist_albums(artist_id, limit=10):
    try:
        response = requests.get(f'https://api.deezer.com/artist/{artist_id}/albums',
                               params={'limit': limit}, timeout=10)
        return response.json().get('data', []) if response.status_code == 200 else []
    except:
        return []

def is_forbidden(name):
    """Check blacklist"""
    name_lower = name.lower().strip()
    
    for forbidden in FORBIDDEN_NAMES:
        if forbidden in name_lower:
            return True
    
    # Patterns génériques
    generic = ['beats', 'instrumental', 'playlist', 'channel', 
               'nation', 'united', 'official', 'music', 'factory']
    if sum(1 for g in generic if g in name_lower) >= 2:
        return True
    
    return False

def is_recent_activity(albums):
    """Activité < 24 mois"""
    if not albums:
        return True
    
    try:
        release_date = albums[0].get('release_date', '')
        if not release_date:
            return True
        
        release_dt = datetime.strptime(release_date, '%Y-%m-%d')
        months_ago = (datetime.now() - release_dt).days / 30
        return months_ago <= 24
    except:
        return True

def calculate_engagement(artist_data, top_tracks):
    if not top_tracks:
        return 0
    avg_rank = sum([t.get('rank', 100000) for t in top_tracks]) / len(top_tracks)
    return round(min(avg_rank / 100000 * 100, 100), 2)

def calculate_score(artist):
    """Calcule le score de potentiel (0-100) - VERSION RÉALISTE"""
    fans = artist['fans']
    engagement = artist['engagement_rate']
    albums = artist['total_albums']
    
    # 1. SCORE FANS (30 points max) - Courbe réaliste
    if fans < 1000:
        fans_score = 0
    elif 1000 <= fans < 5000:
        # Croissance progressive 0-15 pts
        fans_score = (fans - 1000) / 4000 * 15
    elif 5000 <= fans < 15000:
        # Zone intéressante 15-25 pts
        fans_score = 15 + ((fans - 5000) / 10000 * 10)
    elif 15000 <= fans <= 30000:
        # Zone optimale 25-30 pts
        fans_score = 25 + ((fans - 15000) / 15000 * 5)
    else:
        # Décroissance après 30K (déjà connus)
        fans_score = max(20, 30 - ((fans - 30000) / 20000 * 10))
    
    # 2. ENGAGEMENT (30 points max) - Plus strict
    # Engagement parfait = 30 pts, mais rare d'avoir 100%
    if engagement >= 90:
        engagement_score = 25 + ((engagement - 90) / 10 * 5)
    elif engagement >= 70:
        engagement_score = 20 + ((engagement - 70) / 20 * 5)
    elif engagement >= 50:
        engagement_score = 15 + ((engagement - 50) / 20 * 5)
    elif engagement >= 30:
        engagement_score = 10 + ((engagement - 30) / 20 * 5)
    else:
        engagement_score = (engagement / 30) * 10
    
    # 3. DISCOGRAPHIE (25 points max) - Courbe en cloche
    if albums == 0:
        albums_score = 0
    elif albums == 1:
        albums_score = 8
    elif albums == 2:
        albums_score = 15
    elif 3 <= albums <= 8:
        # Zone optimale
        albums_score = 20 + ((8 - abs(albums - 5)) / 3 * 5)
    elif 9 <= albums <= 15:
        # Bon mais moins optimal
        albums_score = 18 - ((albums - 9) / 6 * 3)
    elif 16 <= albums <= 30:
        # Beaucoup d'albums
        albums_score = 15 - ((albums - 16) / 14 * 5)
    else:
        # Trop d'albums
        albums_score = max(5, 10 - ((albums - 30) / 20 * 5))
    
    # 4. RATIO FANS/ALBUMS (15 points max) - Efficacité
    if albums > 0:
        ratio = fans / albums
        if 2000 <= ratio <= 8000:
            # Ratio optimal
            ratio_score = 15
        elif 1000 <= ratio < 2000:
            ratio_score = 10 + ((ratio - 1000) / 1000 * 5)
        elif 8000 < ratio <= 15000:
            ratio_score = 15 - ((ratio - 8000) / 7000 * 5)
        elif ratio < 1000:
            ratio_score = (ratio / 1000) * 10
        else:
            ratio_score = max(5, 10 - ((ratio - 15000) / 10000 * 5))
    else:
        ratio_score = 0
    
    # TOTAL (sans bonus ni malus)
    total = fans_score + engagement_score + albums_score + ratio_score
    
    return round(min(total, 100), 2)

def main():
    print("=" * 80)
    print("🎤 JEK2 RECORDS - DEEZER V6 : EXPLORATION PAR GRAPHE")
    print("🔍 Stratégie : Partir d'artistes connus → Explorer artistes similaires")
    print("=" * 80)
    
    print(f"\n📋 CONFIG:")
    print(f"   • Fans: {MIN_FANS:,} - {MAX_FANS:,}")
    print(f"   • Artistes seed: {len(SEED_ARTISTS)}")
    print(f"   • Méthode: API 'related artists'")
    
    print(f"\n🌱 ÉTAPE 1: Trouver les artistes SEED sur Deezer...")
    
    seed_ids = []
    seed_found = []
    
    for seed_name in SEED_ARTISTS:
        artist = search_artist_by_name(seed_name)
        if artist:
            artist_id = artist.get('id')
            artist_name = artist.get('name')
            seed_ids.append(artist_id)
            seed_found.append(artist_name)
            print(f"  ✅ {artist_name} (ID: {artist_id})")
        time.sleep(0.1)
    
    print(f"\n✅ {len(seed_ids)} artistes seed trouvés sur Deezer")
    
    print(f"\n🕸️ ÉTAPE 2: Explorer les artistes SIMILAIRES (graphe)...")
    
    all_candidates = {}  # {artist_id: artist_data}
    
    for i, seed_id in enumerate(seed_ids, 1):
        if i % 10 == 0:
            print(f"   {i}/{len(seed_ids)} seeds explorés | {len(all_candidates)} candidats uniques")
        
        # Récupérer artistes similaires
        related = get_related_artists(seed_id)
        
        for artist in related:
            artist_id = artist.get('id')
            
            if artist_id not in all_candidates:
                all_candidates[artist_id] = artist
        
        time.sleep(0.2)
    
    print(f"\n✅ {len(all_candidates)} artistes candidats uniques trouvés")
    
    print(f"\n🔎 ÉTAPE 3: Filtrage et validation...")
    
    artists_data = []
    rejected = {'blacklist': 0, 'fans': 0, 'activite': 0, 'albums': 0, 'seed_artist': 0}
    
    # Créer un set des IDs seed pour exclusion rapide
    seed_ids_set = set(seed_ids)
    
    for i, (artist_id, artist) in enumerate(all_candidates.items(), 1):
        if i % 100 == 0:
            print(f"   {i}/{len(all_candidates)} | ✅ {len(artists_data)} validés")
        
        # NOUVEAU FILTRE : Exclure les artistes SEED (trop connus)
        if artist_id in seed_ids_set:
            rejected['seed_artist'] += 1
            continue
        
        # Récupérer détails complets
        details = get_artist_details(artist_id)
        
        if not details:
            continue
        
        name = details.get('name', '')
        fans = details.get('nb_fan', 0)
        nb_albums = details.get('nb_album', 0)
        
        # Filtres
        if is_forbidden(name):
            rejected['blacklist'] += 1
            continue
        
        if not (MIN_FANS <= fans <= MAX_FANS):
            rejected['fans'] += 1
            continue
        
        if nb_albums > 150:
            rejected['albums'] += 1
            continue
        
        albums = get_artist_albums(artist_id)
        
        if not is_recent_activity(albums):
            rejected['activite'] += 1
            continue
        
        # Validé !
        top_tracks = get_artist_top_tracks(artist_id)
        engagement = calculate_engagement(details, top_tracks)
        
        artist_info = {
            'artist_id': artist_id,
            'nom': name,
            'fans': fans,
            'total_albums': nb_albums,
            'engagement_rate': engagement,
            'radio': details.get('radio', False),
            'url_deezer': details.get('link', ''),
            'date_extraction': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        artists_data.append(artist_info)
        
        time.sleep(0.15)
    
    print(f"\n{'='*80}")
    print(f"📊 RÉSULTATS")
    print(f"{'='*80}")
    print(f"✅ Validés: {len(artists_data)}")
    print(f"❌ Rejetés:")
    print(f"   • Artistes SEED (trop connus): {rejected['seed_artist']}")
    print(f"   • Blacklist: {rejected['blacklist']}")
    print(f"   • Fans hors limite: {rejected['fans']}")
    print(f"   • Trop d'albums: {rejected['albums']}")
    print(f"   • Pas actif: {rejected['activite']}")
    
    if len(artists_data) == 0:
        print("\n⚠️ Aucun artiste validé")
        return
    
    # Calculer scores
    for artist in artists_data:
        artist['score_potentiel'] = calculate_score(artist)
    
    artists_data.sort(key=lambda x: x['score_potentiel'], reverse=True)
    
    df = pd.DataFrame(artists_data)
    
    # Sauvegarder
    os.makedirs('../data', exist_ok=True)
    filename = f'../data/deezer_emerging_artists_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 {filename}")
    
    # TOP 30 AVEC SCORES BIEN VISIBLES
    print(f"\n🏆 TOP 30 PAR SCORE DE POTENTIEL")
    print("="*80)
    for idx, row in df.head(30).iterrows():
        print(f"{row['nom']:<40} {int(row['fans']):>8,} fans | Score: {row['score_potentiel']:>5.1f}")
    
    # TABLEAU COMPLET
    print(f"\n" + "="*80)
    print("📋 TABLEAU COMPLET (tous les artistes triés par score)")
    print("="*80)
    
    column_order = [
        'nom', 'fans', 'total_albums', 'engagement_rate', 
        'score_potentiel', 'radio', 'url_deezer', 'date_extraction'
    ]
    df_display = df[column_order]
    
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    
    print(df_display.to_string(index=False))
    
    print(f"\n📊 STATS:")
    print(f"   Total: {len(df)}")
    print(f"   Fans moyen: {df['fans'].mean():,.0f}")
    print(f"   Score moyen: {df['score_potentiel'].mean():.1f}")
    print(f"   Avec radio: {df['radio'].sum()}")
    
    # Vérifier quelques noms connus
    test_names = ['Raplume', 'Guy2Bezbar', 'Luther', 'Zed', 'Lyonzon']
    found_known = []
    
    for test_name in test_names:
        if test_name.lower() in df['nom'].str.lower().values:
            found_known.append(test_name)
    
    if found_known:
        print(f"\n✅ Artistes émergents connus trouvés: {', '.join(found_known)}")
    
    print(f"\n💡 TIP: Ce scraper peut être relancé plusieurs fois pour")
    print(f"   explorer plus profondément le graphe d'artistes similaires")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
