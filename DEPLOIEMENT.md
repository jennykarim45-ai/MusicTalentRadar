# 🚀 GUIDE DE DÉPLOIEMENT - JEK2 RECORDS TALENT RADAR

## ☁️ STREAMLIT CLOUD + SUPABASE (GRATUIT)

---

## 📋 PARTIE 1 : CONFIGURATION SUPABASE (10 min)

### 1. Créer un compte Supabase

1. Allez sur **https://supabase.com**
2. Cliquez **"Start your project"**
3. Connectez-vous avec GitHub

### 2. Créer un projet

1. Cliquez **"New project"**
2. Remplissez :
   - **Name** : `jek2-records`
   - **Database Password** : Créez un mot de passe fort (NOTEZ-LE !)
   - **Region** : Europe West (Frankfurt)
3. Cliquez **"Create new project"**
4. ⏳ Attendez 2-3 minutes que le projet se crée

### 3. Récupérer l'URL de connexion

1. Dans votre projet, allez dans **Settings** (⚙️) → **Database**
2. Descendez jusqu'à **Connection string**
3. Sélectionnez **URI**
4. Copiez l'URL (format : `postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres`)
5. Remplacez `[PASSWORD]` par votre vrai mot de passe

**GARDEZ CETTE URL SECRÈTE !** ⚠️

---

## 📋 PARTIE 2 : PRÉPARER GITHUB (5 min)

### 1. Sur votre PC local

Ouvrez Git Bash dans votre projet :

```bash
cd ~/OneDrive/Documents/projetdata/projetdata/DataAnalyst_Projet3/MusicTalentRadar
```

### 2. Initialiser Git

```bash
# Initialiser le repo
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - JEK2 Records Talent Radar"
```

### 3. Créer un repo GitHub

1. Allez sur **https://github.com**
2. Connectez-vous (ou créez un compte)
3. Cliquez **"New repository"** (bouton vert)
4. Remplissez :
   - **Repository name** : `MusicTalentRadar`
   - **Description** : `Application de talent scouting pour artistes rap/hip-hop émergents`
   - **Public** ou **Private** (au choix)
   - ⚠️ **NE PAS** cocher "Initialize with README"
5. Cliquez **"Create repository"**

### 4. Pousser votre code sur GitHub

```bash
# Remplacez VOTRE_USERNAME par votre nom d'utilisateur GitHub
git remote add origin https://github.com/VOTRE_USERNAME/MusicTalentRadar.git

git branch -M main

git push -u origin main
```

Si demandé, entrez vos identifiants GitHub.

---

## 📋 PARTIE 3 : INITIALISER LA BASE SUPABASE (5 min)

### 1. Sur votre PC, installez psycopg2

```bash
pip install psycopg2-binary
```

### 2. Créez un fichier `.env` (TEMPORAIRE, pour test local)

```bash
# À la racine du projet
echo 'DATABASE_URL="votre_url_supabase_ici"' > .env
```

Remplacez par votre vraie URL Supabase.

### 3. Exécutez le script d'initialisation

```bash
# Exporter la variable d'environnement
export DATABASE_URL="votre_url_supabase_ici"

# Ou sur Windows PowerShell
$env:DATABASE_URL="votre_url_supabase_ici"

# Lancer le script
python scripts/database_postgres.py
```

Cela va :
- ✅ Créer les tables PostgreSQL
- ✅ Importer vos données CSV existantes
- ✅ Configurer les index

---

## 📋 PARTIE 4 : DÉPLOYER SUR STREAMLIT CLOUD (5 min)

### 1. Aller sur Streamlit Cloud

1. Allez sur **https://share.streamlit.io**
2. Cliquez **"Sign up"**
3. Connectez-vous avec votre compte GitHub

### 2. Créer une nouvelle app

1. Cliquez **"New app"**
2. Remplissez :
   - **Repository** : Sélectionnez `VOTRE_USERNAME/MusicTalentRadar`
   - **Branch** : `main`
   - **Main file path** : `app/streamlit_dashboard_cloud.py`
3. Cliquez **"Advanced settings"**

### 3. Configurer les secrets (IMPORTANT)

Dans la section **Secrets**, collez :

```toml
DATABASE_URL = "postgresql://postgres:VOTRE_MOT_DE_PASSE@db.xxx.supabase.co:5432/postgres"
```

⚠️ **REMPLACEZ** par votre vraie URL Supabase !

### 4. Déployer

1. Cliquez **"Deploy!"**
2. ⏳ Attendez 3-5 minutes
3. 🎉 Votre app sera disponible à : `https://VOTRE_USERNAME-musictalentradar.streamlit.app`

---

## 📋 PARTIE 5 : TESTER L'APPLICATION

### 1. Vérifier que tout fonctionne

1. Ouvrez votre URL Streamlit
2. Vérifiez que les données s'affichent
3. Testez les filtres
4. Changez d'onglets

### 2. Partager l'URL

Votre dashboard est maintenant :
- ✅ **Accessible 24/7**
- ✅ **De n'importe où dans le monde**
- ✅ **Sur mobile et desktop**
- ✅ **Avec HTTPS sécurisé**

---

## 🔄 MISE À JOUR DE L'APPLICATION

### Pour mettre à jour votre app après modification :

```bash
# Faire vos modifications localement

# Ajouter les changements
git add .

# Commit
git commit -m "Description de vos modifications"

# Pousser sur GitHub
git push
```

Streamlit Cloud redéploiera automatiquement ! 🚀

---

## 📊 COLLECTE DE DONNÉES EN PRODUCTION

### Option A : Manuellement (simple)

1. Sur votre PC local, lancez les scrapers
2. Lancez le script PostgreSQL pour importer

```bash
python scripts/spotify_scraper.py
python scripts/deezer_scraper.py

export DATABASE_URL="votre_url"
python scripts/database_postgres.py
```

### Option B : GitHub Actions (automatique, avancé)

À configurer plus tard pour collecte automatique quotidienne.

---

## 🆘 DÉPANNAGE

### Erreur : "DATABASE_URL non configurée"
→ Vérifiez les secrets dans Streamlit Cloud Settings

### Erreur : "Connection refused"
→ Vérifiez votre URL Supabase et mot de passe

### App qui ne démarre pas
→ Regardez les logs dans Streamlit Cloud (bouton "Manage app" → "Logs")

### Données ne s'affichent pas
→ Vérifiez que database_postgres.py a bien tourné

---

## 📞 SUPPORT

- **Supabase Docs** : https://supabase.com/docs
- **Streamlit Docs** : https://docs.streamlit.io
- **Community Forum** : https://discuss.streamlit.io

---

## 🎉 FÉLICITATIONS !

Votre application JEK2 Records Talent Radar est maintenant en ligne ! 

URL type : `https://VOTRE_USERNAME-musictalentradar.streamlit.app`

Partagez-la avec qui vous voulez ! 🎤📡
