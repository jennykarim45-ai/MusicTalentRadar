"""
Générateur de hash de mot de passe pour l'authentification Streamlit
"""
import hashlib
import getpass

def hash_password(password):
    """Hash un mot de passe avec SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("=" * 60)
    print("🔐 GÉNÉRATEUR DE HASH POUR AUTHENTIFICATION")
    print("=" * 60)
    print()
    print("Ce script génère un hash SHA256 de votre mot de passe")
    print("À copier dans .streamlit/secrets.toml")
    print()
    
    while True:
        username = input("👤 Nom d'utilisateur : ").strip()
        
        if not username:
            print("❌ Le nom d'utilisateur ne peut pas être vide")
            continue
        
        password = getpass.getpass("🔑 Mot de passe : ")
        password_confirm = getpass.getpass("🔑 Confirmez le mot de passe : ")
        
        if password != password_confirm:
            print("❌ Les mots de passe ne correspondent pas\n")
            continue
        
        if len(password) < 6:
            print("⚠️ Mot de passe trop court (minimum 6 caractères)\n")
            continue
        
        # Générer le hash
        password_hash = hash_password(password)
        
        print("\n" + "=" * 60)
        print("✅ HASH GÉNÉRÉ")
        print("=" * 60)
        print()
        print("Ajoutez cette ligne à .streamlit/secrets.toml :")
        print()
        print(f'{username} = "{password_hash}"')
        print()
        print("Exemple complet de secrets.toml :")
        print()
        print("[users]")
        print(f'{username} = "{password_hash}"')
        print()
        
        another = input("Générer un autre utilisateur ? (o/n) : ").strip().lower()
        if another != 'o':
            break
        print()
    
    print("\n✅ Terminé !")
    print("\n💡 N'oubliez pas de redémarrer Streamlit après modification de secrets.toml")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Annulé")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
