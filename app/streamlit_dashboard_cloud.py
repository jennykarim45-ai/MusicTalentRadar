import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
from PIL import Image

import auth  # ← AJOUT AUTHENTIFICATION

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
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============= AUTHENTIFICATION =============
if not auth.require_authentication():
    if st.session_state.get('show_login', False):
        auth.login_form()
    else:
        auth.public_page_about()
    st.stop()

auth.logout_button()
# ============================================

COLORS = {
    'primary': '#FF1B8D',
    'secondary': "#323A79",
    'accent1': "#336AAE",
    'accent2': "#4A0B7E",
    'accent3': "#21B178",
    'bg_dark': "#070707",
    'bg_card': "#000000",
    'text': "#B57714"
}
COLORS = {
    'primary': '#FF1B8D',
    'secondary': "#323A79",
    'accent1': "#495AB0",
    'accent2': "#4A0B7E",
    'accent3': "#21B178",
    'bg_dark': "#070707",
    'bg_card': "#000000",
    'text': "#B8770D"
}

st.markdown(f"""
    <style>
    /* Fond principal */
    .stApp {{
        background: linear-gradient(135deg, {COLORS['bg_dark']} 0%, #1a0a2e 100%);
    }}
    
    /* Header principal */
    .main-header {{
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']}, {COLORS['accent1']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 1rem 0;
        text-transform: uppercase;
        letter-spacing: 3px;
    }}
    
    .subtitle {{
        color: {COLORS['accent3']};
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }}
    
    /* RESPONSIVE MOBILE */
    @media (max-width: 768px) {{
        .main-header {{
            font-size: 1.8rem !important;
            letter-spacing: 1px !important;
        }}
        
        .subtitle {{
            font-size: 0.9rem !important;
        }}
        
        .metric-card {{
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }}
        
        .metric-card h3 {{
            font-size: 1.2rem !important;
        }}
        
        .metric-card h4 {{
            font-size: 1rem !important;
        }}
        
        .metric-card p, .metric-card li {{
            font-size: 0.9rem !important;
        }}
        
        .score-formula {{
            font-size: 0.85rem !important;
            padding: 0.5rem !important;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem !important;
            padding: 0.5rem !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            font-size: 0.85rem !important;
            padding: 0.3rem 0.5rem !important;
        }}
        
        .js-plotly-plot {{
            width: 100% !important;
        }}
        
        [data-testid="stSidebar"] {{
            width: 80% !important;
        }}
    }}
    
    /* Cartes métriques */
    .metric-card {{
        background: linear-gradient(135deg, {COLORS['bg_card']} 0%, #2a1a3e 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 4px solid {COLORS['primary']};
        box-shadow: 0 8px 16px rgba(255, 27, 141, 0.2);
        margin: 1rem 0;
    }}
    
    h1, h2, h3 {{
        color: {COLORS['accent3']} !important;
        font-weight: 700 !important;
    }}
    
    .css-1d391kg, [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['bg_card']} 0%, #1a0a2e 100%);
    }}
    
    .stMarkdown, p, li {{
        color: {COLORS['text']} !important;
    }}
    
    .stButton>button {{
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent2']});
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }}
    
    .info-box {{
        background: linear-gradient(135deg, #1a0a2e 0%, #2a1a3e 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {COLORS['accent1']};
        margin: 1rem 0;
    }}
    
    .score-formula {{
        background: {COLORS['bg_card']};
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid {COLORS['accent2']};
        font-family: monospace;
        color: {COLORS['accent1']};
        margin: 0.5rem 0;
    }}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data():
    """Charge les données depuis PostgreSQL ou SQLite"""
    try:
        if USE_POSTGRES:
            conn = psycopg2.connect(DB_URL)
        else:
            conn = sqlite3.connect(DB_NAME)
        
        artistes_df = pd.read_sql_query("SELECT * FROM artistes", conn)
        
        # Requête SQL simplifiée (compatible PostgreSQL et SQLite)
        metriques_df = pd.read_sql_query("""
            SELECT m.*, a.nom as nom_artiste, a.url, a.plateforme as platform
            FROM metriques_historique m
            LEFT JOIN artistes a ON m.artist_id = a.artist_id AND m.plateforme = a.plateforme
            ORDER BY m.date_collecte DESC
        """, conn)
        
        # Requête alertes adaptative
        if USE_POSTGRES:
            alertes_df = pd.read_sql_query(
                "SELECT * FROM alertes WHERE vu = FALSE ORDER BY date_alerte DESC", conn
            )
        else:
            alertes_df = pd.read_sql_query(
                "SELECT * FROM alertes WHERE vu = 0 ORDER BY date_alerte DESC", conn
            )
        
        conn.close()
        return artistes_df, metriques_df, alertes_df
        
    except Exception as e:
        st.error(f"❌ Erreur chargement données: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def get_latest_metrics(metriques_df):
    """Récupère les dernières métriques par artiste/plateforme"""
    if metriques_df.empty:
        return pd.DataFrame()
    
    try:
        # Conversion date
        metriques_df['date_collecte'] = pd.to_datetime(metriques_df['date_collecte'])
        
        # Grouper par artist_id et plateforme, garder la plus récente
        latest = metriques_df.sort_values('date_collecte', ascending=False) \
                             .groupby(['artist_id', 'plateforme']) \
                             .first() \
                             .reset_index()
        return latest
    except Exception as e:
        st.error(f"Erreur traitement métriques: {e}")
        return pd.DataFrame()

# ==================== CHARGEMENT DONNÉES ====================
try:
    artistes_df, metriques_df, alertes_df = load_data()
    
    # Vérifications robustes
    if artistes_df.empty or metriques_df.empty:
        st.error(" Base de données vide ou inaccessible")
        st.info(" Importez vos données avec le script `database_postgres.py`")
        st.stop()
    
    latest_metrics_df = get_latest_metrics(metriques_df)
    
    if latest_metrics_df.empty:
        st.error(" Aucune métrique trouvée")
        st.stop()
    
    # Conversion scores en numérique
    latest_metrics_df['score_potentiel'] = pd.to_numeric(latest_metrics_df['score_potentiel'], errors='coerce')
    metriques_df['score_potentiel'] = pd.to_numeric(metriques_df['score_potentiel'], errors='coerce')
    
except Exception as e:
    st.error(f" Erreur critique: {e}")
    st.stop()

# ==================== HEADER ====================
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    try:
        logo = Image.open('logo.png')
        st.image(logo, width=200)
    except:
        pass  # Logo optionnel

with col2:
    st.markdown('<div class="main-header">JEK2 RECORDS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">⭐ MUSIC TALENT RADAR ⭐</div>', unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## **🎛️ FILTRES**")
    
    # Liste des plateformes (gestion sécurisée)
    plateformes_disponibles = latest_metrics_df['plateforme'].unique().tolist() if 'plateforme' in latest_metrics_df.columns else []
    plateformes = ['Tous'] + plateformes_disponibles
    selected_plateforme = st.selectbox("🎵 Plateforme", plateformes)
    
    min_score = st.slider("⭐ Score minimum", 0, 100, 0, 5)
    followers_range = st.slider("👥 Followers/Fans", 0, 100000, (0, 100000), 1000)
    
    
# ==================== FILTRES ====================
filtered_df = latest_metrics_df.copy()

if selected_plateforme != 'Tous':
    filtered_df = filtered_df[filtered_df['plateforme'] == selected_plateforme]

filtered_df = filtered_df[filtered_df['score_potentiel'] >= min_score]

# Calcul followers total
filtered_df['followers_total'] = filtered_df['followers'].fillna(0) + filtered_df['fans'].fillna(0)
filtered_df = filtered_df[
    (filtered_df['followers_total'] >= followers_range[0]) & 
    (filtered_df['followers_total'] <= followers_range[1])
]

st.sidebar.write(f"**{len(filtered_df)} artistes** après filtrage")

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "**📊 VUE D'ENSEMBLE**", 
    "**🌟 TOP ARTISTES**", 
    "**📈 ÉVOLUTION**", 
    "**🔔 ALERTES**",
    "**ℹ️ À PROPOS**"
])

# ==================== TAB 1: VUE D'ENSEMBLE ====================
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎤 ARTISTES", len(artistes_df))
    with col2:
        st.metric("🟢 SPOTIFY", len(artistes_df[artistes_df['plateforme'] == 'Spotify']))
    with col3:
        st.metric("🔵 DEEZER", len(artistes_df[artistes_df['plateforme'] == 'Deezer']))
    with col4:
        st.metric("🔔 ALERTES", len(alertes_df))
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Distribution des scores")
        if len(filtered_df) > 0:
            fig = px.histogram(filtered_df, x='score_potentiel', nbins=20, color='plateforme',
                              color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']})
            fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], font_color=COLORS['text'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée avec ces filtres")
    
    with col2:
        st.markdown("### 👥 Répartition")
        platform_counts = artistes_df['plateforme'].value_counts()
        fig = go.Figure(data=[go.Pie(labels=platform_counts.index, values=platform_counts.values, hole=0.4,
                                      marker=dict(colors=[COLORS['accent3'], COLORS['secondary']]))])
        fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], font_color=COLORS['text'])
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🏆 Top 10")
    if len(filtered_df) > 0:
        top10 = filtered_df.nlargest(min(10, len(filtered_df)), 'score_potentiel')
        fig = px.bar(top10, x='score_potentiel', y='nom_artiste', orientation='h', color='plateforme', text='score_potentiel',
                    color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']})
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], 
                         font_color=COLORS['text'], yaxis={'categoryorder':'total ascending'}, height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée avec ces filtres")

# ==================== TAB 2: TOP ARTISTES ====================
with tab2:
    st.markdown("### 🌟 Top 20 Artistes")
    
    if len(filtered_df) > 0:
        top_df = filtered_df.nlargest(min(20, len(filtered_df)), 'score_potentiel')
        
        fig = px.bar(top_df.sort_values('score_potentiel'), y='nom_artiste', x='score_potentiel', color='plateforme', 
                    orientation='h', text='score_potentiel',
                    color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']})
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], 
                         font_color=COLORS['text'], height=700)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau des données
        display_df = top_df[['nom_artiste', 'plateforme', 'followers_total', 'score_potentiel', 'url']].copy()
        display_df.columns = ['Nom', 'Plateforme', 'Followers/Fans', 'Score', 'URL']
        display_df['Followers/Fans'] = display_df['Followers/Fans'].apply(lambda x: f"{int(x):,}")
        display_df['Score'] = display_df['Score'].round(1)
        st.dataframe(display_df, use_container_width=True, hide_index=True, 
                    column_config={"URL": st.column_config.LinkColumn("URL")})
    else:
        st.info("Aucune donnée avec ces filtres")

# ==================== TAB 3: EVOLUTION ====================
with tab3:
    st.markdown("### 📈 Évolution Temporelle")
    
    if len(metriques_df) > 0 and 'nom_artiste' in metriques_df.columns:
        artistes_list = sorted(metriques_df['nom_artiste'].dropna().unique())
        
        if len(artistes_list) > 0:
            selected_artist = st.selectbox("Artiste", artistes_list)
            
            if selected_artist:
                artist_data = metriques_df[metriques_df['nom_artiste'] == selected_artist].copy()
                
                if not artist_data.empty:
                    # Préparation des données
                    artist_data['date_collecte'] = pd.to_datetime(artist_data['date_collecte'])
                    artist_data = artist_data.sort_values('date_collecte')
                    
                    # Calcul followers (Spotify ou Deezer)
                    artist_data['followers_chart'] = artist_data.apply(
                        lambda row: row['followers'] if pd.notna(row.get('followers')) else row.get('fans', 0), axis=1
                    )
                    
                    latest = artist_data.iloc[-1]
                    followers = latest['followers_chart']
                    
                    # Métriques en haut
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("👥 Followers/Fans", f"{int(followers):,}")
                    with col2:
                        st.metric("⭐ Score Actuel", f"{latest['score_potentiel']:.1f}")
                    with col3:
                        if len(artist_data) > 1:
                            first_f = artist_data.iloc[0]['followers_chart']
                            if first_f > 0:
                                growth = ((followers - first_f) / first_f) * 100
                                st.metric("📈 Croissance", f"{growth:.1f}%")
                    
                    st.markdown("---")
                    
                    # Graphiques (2 colonnes)
                    if len(artist_data) > 1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 👥 Évolution des Followers/Fans")
                            chart_data = artist_data[artist_data['followers_chart'] > 0]
                            if len(chart_data) > 0:
                                fig = px.line(
                                    chart_data, 
                                    x='date_collecte', 
                                    y='followers_chart',
                                    markers=True,
                                    labels={'date_collecte': 'Date', 'followers_chart': 'Followers/Fans'}
                                )
                                fig.update_traces(
                                    line_color=COLORS['accent3'], 
                                    line_width=3, 
                                    marker=dict(size=10, color=COLORS['primary'])
                                )
                                fig.update_layout(
                                    plot_bgcolor=COLORS['bg_card'], 
                                    paper_bgcolor=COLORS['bg_card'], 
                                    font_color=COLORS['text'],
                                    xaxis_title="Date",
                                    yaxis_title="Followers/Fans",
                                    height=400
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Pas de données de followers")
                        
                        with col2:
                            st.markdown("#### ⭐ Évolution du Score")
                            fig = px.line(
                                artist_data, 
                                x='date_collecte', 
                                y='score_potentiel',
                                markers=True,
                                labels={'date_collecte': 'Date', 'score_potentiel': 'Score'}
                            )
                            fig.update_traces(
                                line_color=COLORS['secondary'], 
                                line_width=3, 
                                marker=dict(size=10, color=COLORS['accent1'])
                            )
                            fig.update_layout(
                                plot_bgcolor=COLORS['bg_card'], 
                                paper_bgcolor=COLORS['bg_card'], 
                                font_color=COLORS['text'],
                                xaxis_title="Date",
                                yaxis_title="Score de Potentiel",
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Pas assez de données historiques (minimum 2 collectes nécessaires)")
                else:
                    st.warning("Aucune donnée pour cet artiste")
        else:
            st.warning("Aucun artiste trouvé dans la base")
    else:
        st.info("Pas de données d'évolution disponibles")

# ==================== TAB 4: ALERTES ====================
with tab4:
    st.markdown("### 🔔 Alertes")
    if len(alertes_df) == 0:
        st.info("✅ Aucune alerte pour le moment")
    else:
        for _, alert in alertes_df.iterrows():
            st.markdown(f"""
                <div class="metric-card">
                    <h4>{alert['type_alerte']}</h4>
                    <p><strong>{alert['nom_artiste']}</strong></p>
                    <p>{alert['message']}</p>
                </div>
            """, unsafe_allow_html=True)

# ==================== TAB 5: À PROPOS ====================
with tab5:
    st.markdown("## 🎤 À PROPOS DE JEK2 RECORDS")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="color: {COLORS['primary']};">QUI SOMMES-NOUS ?</h3>
        <p style="font-size: 1.1rem; line-height: 1.8;">
        <strong>JEK2 Records</strong> est un label de musique urbaine français spécialisé dans 
        la découverte de nouveaux talents dans le <strong>rap, hip-hop, RnB et soul</strong>.
        </p>
        <p style="font-size: 1.1rem; line-height: 1.8;">
        Notre mission : identifier les artistes prometteurs <strong>avant</strong> qu'ils ne deviennent célèbres.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-box">
        <h4 style="color: {COLORS['accent3']};">NOS CRITÈRES</h4>
        <p><strong>👥 Communauté :</strong><br>
        1 000 - 50 000 followers</p>
        <p><strong>🎵 Genres :</strong><br>
        Rap, Hip-Hop, Trap, Drill, RnB, Soul</p>
        <p><strong>📍 Localisation :</strong><br>
        France</p>
        <p><strong>📅 Activité :</strong><br>
        Sortie récente (moins de 2 ans)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
    <h3 style="color: {COLORS['secondary']};"> MUSIC TALENT RADAR : NOTRE APPLICATION</h3>
    <p style="font-size: 1.1rem; line-height: 1.8;">
    <strong>MusicTalentRadar</strong> est une application qui analyse automatiquement 
    des milliers d'artistes sur Spotify et Deezer pour trouver les pépites de demain.
    </p>
    <h4 style="color: {COLORS['accent1']};">Comment ça marche ?</h4>
    <ul style="font-size: 1.05rem; line-height: 1.8;">
        <li>🤖 <strong>Collecte automatique</strong> : L'application scanne Spotify et Deezer tous les jours</li>
        <li>📊 <strong>Analyse intelligente</strong> : Chaque artiste reçoit un score sur 100 points</li>
        <li>📈 <strong>Suivi dans le temps</strong> : On surveille l'évolution de leur popularité</li>
        <li>🔔 <strong>Alertes</strong> : On vous prévient quand un artiste explose (+20% de followers)</li>
        <li>🎯 <strong>Recommandations</strong> : On vous propose les meilleurs talents à signer</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 🎯 COMMENT ON CALCULE LE SCORE DE POTENTIEL ?")
    
    st.markdown(f"""
    <div class="metric-card">
    <p style="font-size: 1.15rem; line-height: 1.8;">
    Chaque artiste reçoit un <strong>score sur 100 points</strong> qui mesure son potentiel de succès.
    Plus le score est élevé, plus l'artiste a du potentiel !
    </p>
    <p style="font-size: 1.05rem; line-height: 1.8;">
    💎 <strong>80-100 points</strong> : Pépites à signer en priorité absolue<br>
    📈 <strong>60-79 points</strong> : Artistes très prometteurs à surveiller de près<br>
    🌱 <strong>40-59 points</strong> : Talents émergents avec du potentiel<br>
    🔧 <strong>0-39 points</strong> : Potentiel à développer
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Détail du calcul par plateforme")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="color: {COLORS['primary']};">🟢 SPOTIFY (score sur 100)</h3>
        
        <h4 style="color: {COLORS['accent1']};">1️⃣ Popularité de l'artiste (30 points)</h4>
        <p style="font-size: 1rem; line-height: 1.6;">
        <strong>Ce qu'on mesure :</strong> L'indice de popularité Spotify (0-100)<br>
        <strong>Score maximum si :</strong> Popularité entre 30 et 50<br>
        <strong>Pourquoi ?</strong> C'est le sweet spot : assez connu pour avoir du momentum, 
        pas trop pour rester émergent.
        </p>
        <div class="score-formula">
        30-50 de popularité = 30 points (parfait)<br>
        20-29 de popularité = 25 points (très bien)<br>
        Autres = score proportionnel
        </div>
        
        <h4 style="color: {COLORS['accent1']};">2️⃣ Qualité des morceaux (20 points)</h4>
        <p style="font-size: 1rem; line-height: 1.6;">
        <strong>Ce qu'on mesure :</strong> La popularité moyenne des 10 meilleurs morceaux<br>
        <strong>Pourquoi ?</strong> Un artiste avec des tracks qui cartonnent = bon signe !
        </p>
        <div class="score-formula">
        Popularité moyenne des tracks ÷ 100 × 20<br>
        Exemple : Si moyenne = 50 → 10 points
        </div>
        
        <h4 style="color: {COLORS['accent1']};">3️⃣ Taille de la communauté (25 points)</h4>
        <p style="font-size: 1rem; line-height: 1.6;">
        <strong>Ce qu'on mesure :</strong> Le nombre de followers<br>
        <strong>Score maximum si :</strong> Entre 5 000 et 20 000 followers<br>
        <strong>Pourquoi ?</strong> C'est la zone parfaite : communauté engagée, 
        potentiel de croissance énorme.
        </p>
        <div class="score-formula">
        5 000 - 20 000 followers = 25 points<br>
        En dehors : score proportionnel
        </div>
        
        <h4 style="color: {COLORS['accent1']};">4️⃣ Indicateur de croissance (15 points)</h4>
        <p style="font-size: 1rem; line-height: 1.6;">
        <strong>Ce qu'on mesure :</strong> Popularité de l'artiste VS popularité de ses tracks<br>
        <strong>Pourquoi ?</strong> Si l'artiste est plus populaire que ses morceaux = buzz en cours !
        </p>
        <div class="score-formula">
        (Popularité artiste - Popularité tracks) × 0.5<br>
        Maximum : 15 points
        </div>
        
        <h4 style="color: {COLORS['accent1']};">5️⃣ Récence des sorties (10 points)</h4>
        <p style="font-size: 1rem; line-height: 1.6;">
        <strong>Ce qu'on mesure :</strong> Date de la dernière sortie<br>
        <strong>Pourquoi ?</strong> Un artiste actif = artiste sérieux !
        </p>
        <div class="score-formula">
        Sortie cette année = 10 points<br>
        Sortie l'année dernière = 7 points<br>
        Plus ancien = 4 points
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="color: {COLORS['secondary']};">🔵 DEEZER (score sur 100)</h3>
        
        <h4 style="color: {COLORS['accent1']};">1️⃣ Taille de la communauté (25 points)</h4>
        <p style="font-size: 1rem; line-height: 1.6;">
        <strong>Ce qu'on mesure :</strong> Le nombre de fans<br>
        <strong>Score maximum si :</strong> Entre 8 000 et 25 000 fans<br>
        <strong>Pourquoi ?</strong> Zone optimale pour un artiste émergent avec impact.
        </p>
        <div class="score-formula">
        8 000 - 25 000 fans = 25 points (parfait)<br>
        5 000 - 8 000 fans = 20 points (bien)<br>
        Plus de 40 000 = malus (trop connu)
        </div>
        
        <h4 style="color: {COLORS['accent1']};">2️⃣ Taux d'engagement (25 points)</h4>
        <p style="font-size: 1rem; line-height: 1.6;">
        <strong>Ce qu'on mesure :</strong> Le ratio entre popularité et nombre de fans<br>
        <strong>Pourquoi ?</strong> Mesure si la communauté est vraiment active et engagée.
        </p>
        <div class="score-formula">
        80% et + = 25 points (excellent)<br>
        60-80% = 20 points (très bien)<br>
        40-60% = 15 points (bien)<br>
        20-40% = 10 points (moyen)
        </div>
        
        <h4 style="color: {COLORS['accent1']};">3️⃣ Richesse de la discographie (20 points)</h4>
        <p style="font-size: 1rem; line-height: 1.6;">
        <strong>Ce qu'on mesure :</strong> Le nombre d'albums/EPs sortis<br>
        <strong>Score maximum si :</strong> Entre 3 et 8 projets<br>
        <strong>Pourquoi ?</strong> Assez de contenu pour prouver son talent, 
        pas trop pour éviter la surproduction.
        </p>
        <div class="score-formula">
        3-8 albums = 20 points (parfait)<br>
        2 albums = 15 points (bien)<br>
        Plus de 9 = 15 points (surproduction)
        </div>
        
        <h4 style="color: {COLORS['accent1']};">4️⃣ Présence radio (15 points)</h4>
        <p style="font-size: 1rem; line-height: 1.6;">
        <strong>Ce qu'on mesure :</strong> Si l'artiste est diffusé sur Deezer Radio<br>
        <strong>Pourquoi ?</strong> Signe de reconnaissance de l'industrie musicale.
        </p>
        <div class="score-formula">
        Diffusion radio = 15 points<br>
        Pas de diffusion = 8 points
        </div>
        
        <h4 style="color: {COLORS['accent1']};">5️⃣ Ratio Fans/Albums (15 points)</h4>
        <p style="font-size: 1rem; line-height: 1.6;">
        <strong>Ce qu'on mesure :</strong> Nombre de fans par album sorti<br>
        <strong>Score maximum si :</strong> Entre 1 000 et 8 000 fans par album<br>
        <strong>Pourquoi ?</strong> Mesure l'impact réel : chaque sortie attire-t-elle du monde ?
        </p>
        <div class="score-formula">
        1 000 - 8 000 fans/album = 15 points<br>
        500 - 1 000 fans/album = 10 points<br>
        Autres = score proportionnel
        </div>
        
        <h4 style="color: {COLORS['accent1']};">🎁 Bonus </h4>
        <div class="score-formula">
        ✅ BONUS +5 pts : Si 5 000-50 000 fans (zone pépite)<br>
        
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f"""
    <div class="info-box">
    <h3 style="color: {COLORS['accent3']};">💡 EN RÉSUMÉ</h3>
    <p style="font-size: 1.1rem; line-height: 1.8;">
    Notre algorithme cherche le <strong>"sweet spot"</strong> : des artistes qui ont déjà prouvé 
    leur talent (communauté engagée, morceaux de qualité, régularité), mais qui sont encore 
    <strong>sous le radar du grand public</strong>. C'est là qu'on peut les aider à exploser ! 🚀
    </p>
    <p style="font-size: 1.05rem; line-height: 1.8;">
    ⚠️ <strong>Important :</strong> Un score élevé ne garantit pas le succès, mais il identifie 
    les artistes qui ont toutes les cartes en main pour y arriver.
    </p>
    </div>
    """, unsafe_allow_html=True)