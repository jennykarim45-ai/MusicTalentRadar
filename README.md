# JEK2 Records - Music Talent Radar

site: https://musictalentradar-ats9ctct3i3mxbhms7q6x3.streamlit.app/
Application de détection d'artistes émergents de musiques urbaines en France utilisant l'analyse de données.

## Objectif

Identifier des artistes rap/hip-hop français émergents avant qu'ils ne deviennent connus, en analysant leurs métriques sur Spotify et Deezer.

##  Installation
```bash
# Cloner le repo
git clone https://github.com/jennykarim45-ai/MusicTalentRadar.git
cd MusicTalentRadar

# Créer et activer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Installer les dépendances
pip install -r requirements.txt

# Configurer les clés API
# Créer config.py avec vos clés Spotify/YouTube
```

##  Utilisation
```bash
# 1. Collecter les données
python scripts/spotify_scraper.py
python scripts/deezer_scraper.py

# 2. Créer la base de données
python scripts/database_setup.py

# 3. Lancer le dashboard
streamlit run app/streamlit_dashboard.py
```

## Fonctionnalités

- ✅ Collecte automatique quotidienne
- ✅ Base de données avec historique
- ✅ Dashboard interactif
- ✅ Suivi d'évolution temporelle
- ✅ Système d'alertes intelligent
- ✅ Segmentation des artistes

## Structure
```
MusicTalentRadar/
├── scripts/          # Scripts de collecte et analyse
├── app/              # Dashboard Streamlit
├── data/             # Données CSV
├── logs/             # Logs de collecte
└── visualizations/   # Graphiques générés
```

## Technologies

- Python 3.11.9
- Streamlit (Dashboard)
- Pandas, Numpy (Analyse)
- Plotly (Visualisation)
- SQLite (Base de données)
- Spotify & Deezer APIs

