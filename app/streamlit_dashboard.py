import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime
import sys
import os
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_NAME = 'jek2_records.db'

st.set_page_config(
    page_title="JEK2 Records - Talent Radar",
    layout="wide",
    initial_sidebar_state="expanded"
)



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
        
        /* Tabs plus compacts sur mobile */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem !important;
            padding: 0.5rem !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            font-size: 0.85rem !important;
            padding: 0.3rem 0.5rem !important;
        }}
        
        /* Graphiques responsive */
        .js-plotly-plot {{
            width: 100% !important;
        }}
        
        /* Sidebar plus étroite sur mobile */
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
    conn = sqlite3.connect(DB_NAME)
    artistes_df = pd.read_sql_query("SELECT * FROM artistes", conn)
    metriques_df = pd.read_sql_query("""
        SELECT m.*, a.nom as nom_artiste
        FROM metriques_historique m
        JOIN artistes a ON m.artist_id = a.artist_id
        ORDER BY date_collecte DESC
    """, conn)
    alertes_df = pd.read_sql_query("SELECT * FROM alertes WHERE vu = 0 ORDER BY date_alerte DESC", conn)
    conn.close()
    return artistes_df, metriques_df, alertes_df

def get_latest_metrics():
    conn = sqlite3.connect(DB_NAME)
    query = """
        WITH ranked_metrics AS (
            SELECT m.*, a.nom, a.url, a.plateforme,
                   ROW_NUMBER() OVER (PARTITION BY m.artist_id, m.plateforme ORDER BY m.date_collecte DESC) as rn
            FROM metriques_historique m
            JOIN artistes a ON m.artist_id = a.artist_id
        )
        SELECT * FROM ranked_metrics WHERE rn = 1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

try:
    artistes_df, metriques_df, alertes_df = load_data()
    latest_metrics_df = get_latest_metrics()
    
    # Conversion des scores en numérique
    latest_metrics_df['score_potentiel'] = pd.to_numeric(latest_metrics_df['score_potentiel'], errors='coerce')
    metriques_df['score_potentiel'] = pd.to_numeric(metriques_df['score_potentiel'], errors='coerce')
    
        
except Exception as e:
    st.error(f"Erreur: {e}")
    st.stop()

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    try:
        logo = Image.open('logo.png')
        st.image(logo, width=200)
    except Exception as e:
        st.warning(f"Logo non trouvé: {e}")
        st.write("Placez logo.png à la racine du projet")
        
with col2:
    st.markdown('<div class="main-header">JEK2 RECORDS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle"> ⭐ MUSIC TALENT RADAR ⭐ </div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎛️ FILTRES")
    
    # Liste des plateformes
    plateformes_uniques = latest_metrics_df['plateforme'].unique().tolist()
    plateformes = ['Tous'] + plateformes_uniques
    selected_plateforme = st.selectbox("🎵 Plateforme", plateformes)
    
    min_score = st.slider("⭐ Score minimum", 0, 100, 0, 5)
    followers_range = st.slider("👥 Followers/Fans", 0, 100000, (0, 100000), 1000)

# Application des filtres
filtered_df = latest_metrics_df.copy()

if selected_plateforme != 'Tous':
    filtered_df = filtered_df[filtered_df['plateforme'] == selected_plateforme]

filtered_df = filtered_df[filtered_df['score_potentiel'] >= min_score]

filtered_df['followers_total'] = filtered_df['followers'].fillna(0) + filtered_df['fans'].fillna(0)
filtered_df = filtered_df[
    (filtered_df['followers_total'] >= followers_range[0]) & 
    (filtered_df['followers_total'] <= followers_range[1])
]

st.sidebar.write(f"**{len(filtered_df)} artistes** après filtrage")

# TABS DANS LE BON ORDRE
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 VUE D'ENSEMBLE", 
    "🌟 TOP ARTISTES", 
    "📈 ÉVOLUTION", 
    "🔔 ALERTES",
    "ℹ️ À PROPOS"
])

# TAB 1: VUE D'ENSEMBLE
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
        fig = px.bar(top10, x='score_potentiel', y='nom', orientation='h', color='plateforme', text='score_potentiel',
                    color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']})
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], 
                         font_color=COLORS['text'], yaxis={'categoryorder':'total ascending'}, height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée avec ces filtres")

# TAB 2: TOP ARTISTES
with tab2:
    st.markdown("### 🌟 Top 20 Artistes")
    
    if len(filtered_df) > 0:
        top_df = filtered_df.nlargest(min(20, len(filtered_df)), 'score_potentiel')
        
        fig = px.bar(top_df.sort_values('score_potentiel'), y='nom', x='score_potentiel', color='plateforme', 
                    orientation='h', text='score_potentiel',
                    color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']})
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], 
                         font_color=COLORS['text'], height=700)
        st.plotly_chart(fig, use_container_width=True)
        
        display_df = top_df[['nom', 'plateforme', 'followers_total', 'score_potentiel', 'url']].copy()
        display_df.columns = ['Nom', 'Plateforme', 'Followers/Fans', 'Score', 'URL']
        display_df['Followers/Fans'] = display_df['Followers/Fans'].apply(lambda x: f"{int(x):,}")
        display_df['Score'] = display_df['Score'].round(1)
        st.dataframe(display_df, use_container_width=True, hide_index=True, 
                    column_config={"URL": st.column_config.LinkColumn("URL")})
    else:
        st.info("Aucune donnée avec ces filtres")

# TAB 3: EVOLUTION
with tab3:
    st.markdown("### 📈 Évolution Temporelle")
    
    if len(metriques_df) > 0:
        selected_artist = st.selectbox("Artiste", sorted(metriques_df['nom_artiste'].unique()))
        
        if selected_artist:
            artist_data = metriques_df[metriques_df['nom_artiste'] == selected_artist].copy()
            artist_data['date_collecte'] = pd.to_datetime(artist_data['date_collecte'])
            artist_data = artist_data.sort_values('date_collecte')
            
            latest = artist_data.iloc[-1]
            followers = latest['followers'] if pd.notna(latest['followers']) else latest.get('fans', 0)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👥 Followers", f"{int(followers):,}")
            with col2:
                st.metric("⭐ Score", f"{latest['score_potentiel']:.1f}")
            with col3:
                if len(artist_data) > 1:
                    first_f = artist_data.iloc[0]['followers'] if pd.notna(artist_data.iloc[0]['followers']) else artist_data.iloc[0].get('fans', 0)
                    if first_f > 0:
                        growth = ((followers - first_f) / first_f) * 100
                        st.metric("📈 Croissance", f"{growth:.1f}%")
            
            if len(artist_data) > 1:
                col1, col2 = st.columns(2)
                with col1:
                    artist_data['followers_chart'] = artist_data.apply(
                        lambda row: row['followers'] if pd.notna(row['followers']) else row.get('fans', 0), axis=1)
                    chart_data = artist_data[artist_data['followers_chart'] > 0]
                    if len(chart_data) > 0:
                        fig = px.line(chart_data, x='date_collecte', y='followers_chart', 
                                     title='Followers/Fans', markers=True)
                        fig.update_traces(line_color=COLORS['accent3'], line_width=3, marker=dict(size=8))
                        fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], font_color=COLORS['text'])
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig = px.line(artist_data, x='date_collecte', y='score_potentiel', 
                                 title='Score', markers=True)
                    fig.update_traces(line_color=COLORS['secondary'], line_width=3, marker=dict(size=8))
                    fig.update_layout(plot_bgcolor=COLORS['bg_card'], paper_bgcolor=COLORS['bg_card'], font_color=COLORS['text'])
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pas de données d'évolution")

# TAB 4: ALERTES
with tab4:
    st.markdown("### 🔔 Alertes")
    if len(alertes_df) == 0:
        st.info("Aucune alerte")
    else:
        for _, alert in alertes_df.iterrows():
            st.markdown(f"""
                <div class="metric-card">
                    <h4>{alert['type_alerte']}</h4>
                    <p><strong>{alert['nom_artiste']}</strong></p>
                    <p>{alert['message']}</p>
                </div>
            """, unsafe_allow_html=True)

# TAB 5: À PROPOS (EN DERNIER)
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
        
        <h4 style="color: {COLORS['accent1']};">🎁 Bonus et Malus</h4>
        <div class="score-formula">
        ✅ BONUS +5 pts : Si 5 000-15 000 fans (zone pépite)<br>
        ❌ MALUS -15% : Si plus de 40 000 fans (trop connu)
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