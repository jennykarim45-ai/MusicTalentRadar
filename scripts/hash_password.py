import hashlib

password = input("Entrez votre mot de passe : ")
hash_result = hashlib.sha256(password.encode()).hexdigest()

print("\n" + "="*60)
print("Copiez cette ligne dans .streamlit/secrets.toml :")
print("="*60)
print(f'jenny = "{hash_result}"')
print("="*60)
