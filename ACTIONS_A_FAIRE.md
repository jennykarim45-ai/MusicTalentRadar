# 🎯 RÉSUMÉ : CE QU'IL FAUT FAIRE MAINTENANT

## ✅ SCRIPTS FINAUX À GARDER

### 📁 Dans `/scripts/`

**À GARDER (PROD) :**
1. **deezer_scraper.py** → REMPLACER par V6_FINAL
2. **spotify_scraper.py** → Garder tel quel
3. **database_postgres_fix.py** → Pour import Supabase
4. **streamlit_dashboard_cloud.py** → Corriger ligne 643

**À SUPPRIMER (DEBUG) :**
- debug_raplume.py
- detect_alerts.py
- raplumeinsearch.py  
- test_artist.py
- database_postgres.py (ancien)
- database_setup.py (SQLite obsolète)

---

## 📝 ACTIONS DÉTAILLÉES

### **1️⃣ Remplacer deezer_scraper.py**

```bash
# Copier la version V6_FINAL
cp deezer_scraper_V6_FINAL.py deezer_scraper.py
```

**OU depuis Git Bash :**
```bash
cp /c/path/to/outputs/scripts/deezer_scraper_V6_FINAL.py ~/OneDrive/Documents/projetdata/projetdata/DataAnalyst_Projet3/MusicTalentRadar/scripts/deezer_scraper.py
```

---

### **2️⃣ Corriger streamlit_dashboard_cloud.py**

**Ligne 643 à corriger :**

❌ **ANCIEN TEXTE (ligne 643)** :
```
Plus de 40 000 = malus (trop connu)
```

✅ **NOUVEAU TEXTE** :
```
Plus de 30 000 = décroissance (déjà établis)
```

**Remplacer tout le bloc d'explication (lignes ~620-660) par :**

```python
st.markdown("""
### 📊 **Calcul du Score de Potentiel (0-100)**

Le score est calculé de manière réaliste, **SANS bonus ni malus** :

#### **1. Fans / Followers (30 points max)**
- **1K-5K** : 0-15 pts (émergents)
- **5K-15K** : 15-25 pts (prometteurs)
- **15K-30K** : 25-30 pts (zone optimale)
- **>30K** : Décroissance (déjà connus)

#### **2. Engagement (30 points max)**
- **>90%** : 25-30 pts (excellent)
- **70-90%** : 20-25 pts (très bon)
- **50-70%** : 15-20 pts (bon)
- **<50%** : <15 pts (faible)

#### **3. Discographie (25 points max)**
- **3-8 albums** : 20-25 pts (optimal)
- **1-2 albums** : 8-15 pts (débutant)
- **9-15 albums** : 15-18 pts (actif)
- **>15 albums** : Décroissance

#### **4. Ratio Fans/Albums (15 points max)**
- **2K-8K ratio** : 15 pts (efficace)
- **<2K** : Décroissance
- **>8K** : Décroissance

**⚠️ Total max réaliste : 85-90 points**  
(100 serait un artiste parfait)
""")
```

---

### **3️⃣ Importer les données Deezer dans Supabase**

```bash
cd scripts
python database_postgres_fix.py
```

Cela va :
- ✅ Créer les tables PostgreSQL
- ✅ Importer tous les CSV (Spotify + Deezer)
- ✅ Générer des artist_id uniques

---

### **4️⃣ Tester le dashboard en local**

```bash
cd ~/OneDrive/Documents/projetdata/projetdata/DataAnalyst_Projet3/MusicTalentRadar
streamlit run streamlit_dashboard_cloud.py
```

---

### **5️⃣ Configurer GitHub Actions (optionnel)**

Créer `.github/workflows/daily_collection.yml` :

```yaml
name: Collecte Quotidienne

on:
  schedule:
    - cron: '0 2 * * *'  # Tous les jours à 2h
  workflow_dispatch:  # Manuel

jobs:
  collect:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install requests pandas spotipy psycopg2-binary python-dotenv
      
      - name: Run Spotify scraper
        env:
          SPOTIPY_CLIENT_ID: ${{ secrets.SPOTIPY_CLIENT_ID }}
          SPOTIPY_CLIENT_SECRET: ${{ secrets.SPOTIPY_CLIENT_SECRET }}
        run: python scripts/spotify_scraper.py
      
      - name: Run Deezer scraper
        run: python scripts/deezer_scraper.py
      
      - name: Import to Supabase
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: python scripts/database_postgres_fix.py
```

---

## ✅ CHECKLIST FINALE

- [ ] Remplacer deezer_scraper.py par V6_FINAL
- [ ] Corriger ligne 643 du streamlit_dashboard
- [ ] Importer données dans Supabase
- [ ] Tester le dashboard en local
- [ ] Supprimer les scripts de debug
- [ ] Configurer GitHub Actions (optionnel)
- [ ] Déployer sur Streamlit Cloud

---

## 🎯 ORDRE RECOMMANDÉ

1. ✅ Remplacer deezer_scraper.py
2. ✅ Importer dans Supabase  
3. ✅ Corriger streamlit_dashboard
4. ✅ Tester en local
5. ✅ Supprimer les fichiers debug
6. ✅ Push sur GitHub
7. ✅ Déployer Streamlit Cloud

---

Bon courage ! 💪🎤
