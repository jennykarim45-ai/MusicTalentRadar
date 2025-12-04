import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
from PIL import Image

# Détection de l'environnement
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_POSTGRES = True
    DB_URL = st.secrets["DATABASE_URL"]
except:
    import sqlite3
    USE_POSTGRES = False
    DB_NAME = 'jek2_records.db'

st.set_page_config(
    page_title="JEK2 Records - Talent Radar",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLORS = {
    'primary': '#FF1B8D',
    'secondary': "#323A79",
    'accent1': '#FFD700',
    'accent2': "#4A0B7E",
    'accent3': "#D23934",
    'bg_dark': "#070707",
    'bg_card': "#000000",
    'text': "#E88F00"
}

st.markdown(f"""<style>
.stApp {{background: linear-gradient(135deg, {COLORS['bg_dark']} 0%, #1a0a2e 100%);}}
.main-header {{font-size: 3rem; font-weight: 900; background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']}, {COLORS['accent1']}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin: 1rem 0; text-transform: uppercase; letter-spacing: 3px;}}
.subtitle {{color: {COLORS['accent3']}; text-align: center; font-size: 1.2rem; margin-bottom: 2rem;}}
@media (max-width: 768px) {{.main-header {{font-size: 1.8rem !important;}} .subtitle {{font-size: 0.9rem !important;}}}}
.metric-card {{background: linear-gradient(135deg, {COLORS['bg_card']} 0%, #2a1a3e 100%); padding: 2rem; border-radius: 15px; border-left: 4px solid {COLORS['primary']}; box-shadow: 0 8px 16px rgba(255, 27, 141, 0.2); margin: 1rem 0;}}
h1, h2, h3 {{color: {COLORS['accent3']} !important; font-weight: 700 !important;}}
</style>""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data():
    """Charge les données"""
    try:
        if USE_POSTGRES:
            conn = psycopg2.connect(DB_URL)
        else:
            conn = sqlite3.connect(DB_NAME)
        
        artistes_df = pd.read_sql_query("SELECT * FROM artistes", conn)
        
        # Requête simplifiée sans sous-requête complexe
        metriques_df = pd.read_sql_query("""
            SELECT m.*, a.nom as nom_artiste, a.url, a.plateforme as platform
            FROM metriques_historique m
            LEFT JOIN artistes a ON m.artist_id = a.artist_id AND m.plateforme = a.plateforme
            ORDER BY m.date_collecte DESC
        """, conn)
        
        alertes_df = pd.read_sql_query(
            "SELECT * FROM alertes WHERE vu = FALSE ORDER BY date_alerte DESC" if USE_POSTGRES 
            else "SELECT * FROM alertes WHERE vu = 0 ORDER BY date_alerte DESC", 
            conn
        )
        
        conn.close()
        return artistes_df, metriques_df, alertes_df
    except Exception as e:
        st.error(f"Erreur chargement: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def get_latest_metrics(metriques_df):
    """Récupère les dernières métriques par artiste"""
    if metriques_df.empty:
        return pd.DataFrame()
    
    # Grouper par artist_id et plateforme, garder la plus récente
    metriques_df['date_collecte'] = pd.to_datetime(metriques_df['date_collecte'])
    latest = metriques_df.sort_values('date_collecte', ascending=False).groupby(['artist_id', 'plateforme']).first().reset_index()
    return latest

try:
    artistes_df, metriques_df, alertes_df = load_data()
    
    if artistes_df.empty or metriques_df.empty:
        st.error("❌ Base de données vide")
        st.info("Importez vos données avec `database_postgres.py`")
        st.stop()
    
    latest_metrics_df = get_latest_metrics(metriques_df)
    
    if latest_metrics_df.empty:
        st.error("❌ Aucune métrique trouvée")
        st.stop()
    
    latest_metrics_df['score_potentiel'] = pd.to_numeric(latest_metrics_df['score_potentiel'], errors='coerce')
    metriques_df['score_potentiel'] = pd.to_numeric(metriques_df['score_potentiel'], errors='coerce')
    
except Exception as e:
    st.error(f"Erreur: {e}")
    st.stop()

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    try:
        logo = Image.open('logo.png')
        st.image(logo, width=200)
    except:
        pass
with col2:
    st.markdown('<div class="main-header">JEK2 RECORDS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">🎤 TALENT RADAR 📡</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎛️ FILTRES")
    
    plateformes_disponibles = latest_metrics_df['plateforme'].unique().tolist() if 'plateforme' in latest_metrics_df.columns else []
    plateformes = ['Tous'] + plateformes_disponibles
    selected_plateforme = st.selectbox("🎵 Plateforme", plateformes)
    
    min_score = st.slider("⭐ Score minimum", 0, 100, 0, 5)
    followers_range = st.slider("👥 Followers/Fans", 0, 100000, (0, 100000), 1000)
    
    st.info("☁️ Mode Cloud" if USE_POSTGRES else "💻 Mode Local")
    st.write(f"**{len(latest_metrics_df)} artistes**")

# Filtres
filtered_df = latest_metrics_df.copy()
if selected_plateforme != 'Tous':
    filtered_df = filtered_df[filtered_df['plateforme'] == selected_plateforme]
filtered_df = filtered_df[filtered_df['score_potentiel'] >= min_score]
filtered_df['followers_total'] = filtered_df['followers'].fillna(0) + filtered_df['fans'].fillna(0)
filtered_df = filtered_df[
    (filtered_df['followers_total'] >= followers_range[0]) & 
    (filtered_df['followers_total'] <= followers_range[1])
]

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 VUE D'ENSEMBLE", 
    "🌟 TOP ARTISTES", 
    "📈 ÉVOLUTION", 
    "🔔 ALERTES",
    "ℹ️ À PROPOS"
])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("🎤 ARTISTES", len(artistes_df))
    with col2: st.metric("🟢 SPOTIFY", len(artistes_df[artistes_df['plateforme'] == 'Spotify']))
    with col3: st.metric("🔵 DEEZER", len(artistes_df[artistes_df['plateforme'] == 'Deezer']))
    with col4: st.metric("🔔 ALERTES", len(alertes_df))
    
    if len(filtered_df) > 0:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(filtered_df, x='score_potentiel', nbins=20, color='plateforme',
                              color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']})
            fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], font_color=COLORS['text'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            platform_counts = artistes_df['plateforme'].value_counts()
            fig = go.Figure(data=[go.Pie(labels=platform_counts.index, values=platform_counts.values, hole=0.4,
                                          marker=dict(colors=[COLORS['accent3'], COLORS['secondary']]))])
            fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], font_color=COLORS['text'])
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### 🌟 Top 20")
    if len(filtered_df) > 0:
        top_df = filtered_df.nlargest(min(20, len(filtered_df)), 'score_potentiel')
        fig = px.bar(top_df.sort_values('score_potentiel'), y='nom_artiste', x='score_potentiel', color='plateforme', 
                    orientation='h', text='score_potentiel',
                    color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']})
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], 
                         font_color=COLORS['text'], height=700)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 📈 Évolution")
    if len(metriques_df) > 0 and 'nom_artiste' in metriques_df.columns:
        artistes_list = sorted(metriques_df['nom_artiste'].dropna().unique())
        if len(artistes_list) > 0:
            selected_artist = st.selectbox("Artiste", artistes_list)
            if selected_artist:
                artist_data = metriques_df[metriques_df['nom_artiste'] == selected_artist].copy()
                if not artist_data.empty:
                    latest = artist_data.iloc[-1]
                    followers = latest['followers'] if pd.notna(latest.get('followers')) else latest.get('fans', 0)
                    col1, col2 = st.columns(2)
                    with col1: st.metric("👥 Followers", f"{int(followers):,}")
                    with col2: st.metric("⭐ Score", f"{latest['score_potentiel']:.1f}")

with tab4:
    st.markdown("### 🔔 Alertes")
    if len(alertes_df) == 0:
        st.info("Aucune alerte")

with tab5:
    st.markdown("## 🎤 JEK2 RECORDS - TALENT RADAR")
    st.markdown("Application de talent scouting pour artistes rap/hip-hop émergents")

