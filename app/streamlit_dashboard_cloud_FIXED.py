import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
from PIL import Image

# Détection de l'environnement avec affichage des erreurs
USE_POSTGRES = False
DB_URL = None

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    st.sidebar.info("✅ psycopg2 chargé")
    
    # Essayer de récupérer DATABASE_URL
    try:
        DB_URL = st.secrets["DATABASE_URL"]
        st.sidebar.success("✅ DATABASE_URL trouvée dans secrets")
    except Exception as e:
        st.sidebar.error(f"❌ Erreur secrets: {e}")
        st.error("DATABASE_URL introuvable dans .streamlit/secrets.toml")
        st.info("Vérifiez que le fichier .streamlit/secrets.toml existe et contient DATABASE_URL")
        st.stop()
    
    # Tester la connexion
    try:
        test_conn = psycopg2.connect(DB_URL)
        test_conn.close()
        USE_POSTGRES = True
        st.sidebar.success("✅ PostgreSQL connecté")
    except Exception as e:
        st.sidebar.error(f"❌ Erreur connexion: {e}")
        st.error(f"Impossible de se connecter à PostgreSQL: {e}")
        st.stop()
        
except ImportError as e:
    st.error(f"❌ psycopg2 non installé: {e}")
    st.code("pip install psycopg2-binary")
    st.stop()