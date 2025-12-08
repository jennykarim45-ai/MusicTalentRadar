"""
Module d'authentification JEK2 Records - VERSION FINALE
"""
import streamlit as st
import hashlib
import os

# Couleurs JEK2 Records
COLORS = {
    'primary': "#0E587A",
    'secondary': "#793267",
    'accent1': "#F00606",
    'accent2': "#4A0B7E",
    'accent3': "#21B178",
    'bg_dark': "#070707",
    'bg_card': "#000000",
    'text': "#D7C2A0"
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_users():
    try:
        return dict(st.secrets["users"])
    except:
        return {
            "admin": hash_password("admin123"),
            "jenny": hash_password("jenny2024")
        }

def login_form():
    """Formulaire de connexion"""
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, {COLORS['bg_dark']} 0%, #1a0a2e 100%);
        }}
        .login-container {{
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, #1a0a2e 0%, #16213e 100%);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown(f'<h1 style="text-align: center; color:{COLORS["secondary"]}, {COLORS["primary"]};"> JEK2 RECORDS</h1>', unsafe_allow_html=True)
        st.markdown("### 🔐 CONNEXION")
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "👤 Nom d'utilisateur",
                placeholder="Entrez votre nom d'utilisateur"
            )
            
            password = st.text_input(
                "🔑 Mot de passe",
                type="password",
                placeholder="Entrez votre mot de passe"
            )
            
            submit = st.form_submit_button("**SE CONNECTER**", use_container_width=True, type="primary")
            
            if submit:
                if username and password:
                    users = get_users()
                    
                    if username in users:
                        if hash_password(password) == users[username]:
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.success("✅ Connexion réussie !")
                            st.balloons()
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Mot de passe incorrect")
                    else:
                        st.error("❌ Utilisateur inconnu")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.info("**Identifiants de test :** admin / admin123")

def logout_button():
    """Bouton de déconnexion"""
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"👤 **Connecté:** {st.session_state.get('username', 'Invité')}")
        if st.button("🚪 Se déconnecter", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

def require_authentication():
    """Vérifie si l'utilisateur est authentifié"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def public_page_about():
    """Page publique À propos avec les vraies couleurs JEK2"""
    
    # Appliquer les styles JEK2
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, {COLORS['bg_dark']} 0%, #1a0a2e 100%);
        }}
        h1, h2, h3 {{
            color: {COLORS['accent3']} !important;
        }}
        p, li {{
            color: {COLORS['text']} !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Logo - essayer plusieurs chemins
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_found = False
        # Essayer différents chemins
        for logo_path in ["logo.png", "../logo.png", "../../logo.png", "./logo.png"]:
            try:
                if os.path.exists(logo_path):
                    st.image(logo_path, width=200)
                    logo_found = True
                    break
            except:
                continue
        
        # Logo CSS si aucun fichier trouvé
        if not logo_found:
            st.markdown(f"""
                <div style="text-align: center; margin: 2rem 0;">
                    <div style="width: 200px; height: 200px; margin: 0 auto;
                                background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']}, {COLORS['accent1']});
                                border-radius: 50%; display: flex; align-items: center;
                                justify-content: center; font-size: 5rem;
                                box-shadow: 0 10px 40px rgba(255, 27, 141, 0.4);
                                animation: pulse 2s infinite;">
                        🎤
                    </div>
                    <p style="color: {COLORS['primary']}; font-size: 1.5rem; 
                              font-weight: bold; margin-top: 1rem; letter-spacing: 2px;
                              text-align: center;">
                        JEK2 RECORDS
                    </p>
                </div>
                <style>
                @keyframes pulse {{
                    0%, 100% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.05); }}
                }}
                </style>
            """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <h1 style="text-align: center; 
                   background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']}, {COLORS['accent1']}); 
                   -webkit-background-clip: text; 
                   -webkit-text-fill-color: transparent;
                   font-size: 3rem;
                   margin-bottom: 2rem;">
            JEK2 RECORDS - TALENT RADAR
        </h1>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ###  **Notre Mission**
        
        Découvrir les **talents émergents** du rap français avant tout le monde.
        
        Nous utilisons la **data science** et l'**IA** pour :
        - 🔍 Identifier les artistes prometteurs
        - 📊 Analyser leur potentiel de croissance
        
        """)
    
    with col2:
        st.markdown("""
        ###  **Notre Approche**
        
        **Collecte de données** en temps réel :
        - 🎵 Spotify
        - 🎧 Deezer
        
        
        **Analyse prédictive** basée sur :
        - Nombre de fans/followers
        - Taux d'engagement
        - Vitesse de croissance
        - Activité récente
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🏆 **Le Score de Potentiel**
    
    Notre algorithme calcule un **score de 0 à 100** pour chaque artiste :
    """)
    
    # Tableau avec style personnalisé
    st.markdown(f"""
        <style>
        .score-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        .score-table th {{
            background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']});
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: bold;
        }}
        .score-table td {{
            padding: 0.8rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: {COLORS['text']};
        }}
        .score-table tr:hover {{
            background: rgba(255, 27, 141, 0.1);
        }}
        .score-table .icon {{
            font-size: 1.2rem;
            margin-right: 0.5rem;
        }}
        </style>
        
        <table class="score-table">
            <thead>
                <tr>
                    <th>Critère</th>
                    <th>Poids</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><span class="icon">👥</span> <strong>Audience</strong></td>
                    <td><strong>30%</strong></td>
                    <td>Taille de la communauté (1K-100K)</td>
                </tr>
                <tr>
                    <td><span class="icon">🔥</span> <strong>Engagement</strong></td>
                    <td><strong>30%</strong></td>
                    <td>Interaction avec les fans</td>
                </tr>
                <tr>
                    <td><span class="icon">💿</span> <strong>Discographie</strong></td>
                    <td><strong>25%</strong></td>
                    <td>Nombre et qualité des sorties</td>
                </tr>
                <tr>
                    <td><span class="icon">⚡</span> <strong>Efficacité</strong></td>
                    <td><strong>15%</strong></td>
                    <td>Ratio fans/albums</td>
                </tr>
            </tbody>
        </table>
        
        <p style="color: {COLORS['accent3']}; font-weight: bold; margin-top: 1rem;">
            ⭐ <strong>Score optimal</strong> : 75-90 points
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_a, col_b, col_c = st.columns([1, 1, 1])
    
    with col_b:
        if st.button("🔐 Se connecter", type="primary", use_container_width=True):
            st.session_state.show_login = True
            st.rerun()
    
    st.info("💡 Connectez-vous pour accéder au tableau de bord complet et découvrir les artistes !")