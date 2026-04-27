# get_token.py - VERSION FONCTIONNELLE
print("="*50)
print("GÉNÉRATION DE TOKEN JWT")
print("="*50)

# 1. IMPORTATION STRATÉGIQUE (même ordre que create_admin.py)
print("📦 Importation des modèles...")

from database import Base

# Importez tous les modèles dans le même ordre
import models.user
import models.profile  
import models.audit
import models.refresh_token
import models.publication

print("✅ Modèles importés")

# 2. Importez maintenant les autres dépendances
from auth.jwt import create_access_token
import hashlib

print("🔌 Connexion à la base de données...")
from database import SessionLocal
db = SessionLocal()

print("✅ Base connectée")

# 3. Importez User MAINTENANT
from models.user import User

# 4. Chercher l'admin
print("\n🔍 Recherche de l'admin 'admin@test.com'...")
admin = db.query(User).filter(User.email == "admin@test.com").first()

if not admin:
    print("\n❌ ADMIN NON TROUVÉ!")
    print("   Exécutez d'abord: python create_admin.py")
    print("   Pour créer un compte admin")
else:
    print(f"\n✅ ADMIN TROUVÉ!")
    print(f"   📧 Email: {admin.email}")
    print(f"   👑 Rôle: {admin.role}")
    print(f"   📊 Statut: {admin.status}")
    print(f"   🆔 ID: {admin.id}")
    
    # 5. Générer le token JWT
    print("\n🔑 Génération du token JWT...")
    token = create_access_token(admin.id, admin.role)
    
    print("\n" + "="*60)
    print("VOTRE TOKEN JWT EST PRÊT !")
    print("="*60)
    print("\n📋 COPIEZ CE TOKEN :")
    print("-"*60)
    print(token)
    print("-"*60)
    
    print(f"\n📝 Informations du token:")
    print(f"   📧 Pour l'utilisateur: {admin.email}")
    print(f"   👑 Avec le rôle: {admin.role}")
    print(f"   🆔 User ID: {admin.id}")
    
    print("\n💡 COMMENT UTILISER CE TOKEN:")
    print("1. Démarrez votre serveur: uvicorn main:app --reload")
    print("2. Testez avec le script test_admin.py")
    print("3. Ou collez-le dans l'extension ModHeader de votre navigateur")

# 6. Fermer
db.close()

print("\n" + "="*50)
print("OPÉRATION TERMINÉE")
print("="*50)