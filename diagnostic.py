# diagnostic.py
import traceback

print("🔍 DIAGNOSTIC COMPLET")
print("="*60)

# Test 1: Imports de base
print("\n1. Tests des imports...")
try:
    from fastapi import FastAPI
    print("✅ FastAPI OK")
except Exception as e:
    print(f"❌ FastAPI: {e}")

try:
    from sqlalchemy import create_engine
    print("✅ SQLAlchemy OK")
except Exception as e:
    print(f"❌ SQLAlchemy: {e}")

# Test 2: Modèles
print("\n2. Tests des modèles...")
try:
    from models.user import User
    print("✅ User OK")
except Exception as e:
    print(f"❌ User: {e}")
    traceback.print_exc()

try:
    from models.refresh_token import RefreshToken
    print("✅ RefreshToken OK")
except Exception as e:
    print(f"❌ RefreshToken: {e}")

# Test 3: Routes
print("\n3. Tests des routes...")
try:
    from routes.auth import router as auth_router
    print("✅ auth_router OK")
except Exception as e:
    print(f"❌ auth_router: {e}")
    traceback.print_exc()

try:
    from routes.dashboard import router as dashboard_router
    print("✅ dashboard_router OK")
except Exception as e:
    print(f"❌ dashboard_router: {e}")

try:
    from routes.pdf import router as pdf_router
    print("✅ pdf_router OK")
except Exception as e:
    print(f"❌ pdf_router: {e}")

# Test 4: Base de données
print("\n4. Test base de données...")
try:
    from database import SessionLocal, engine
    print("✅ Database OK")
    
    # Tester la connexion
    with engine.connect() as conn:
        print("✅ Connexion DB OK")
except Exception as e:
    print(f"❌ Database: {e}")

print("\n" + "="*60)
print("🎯 PROCHAINES ÉTAPES:")
print("1. Exécutez: python diagnostic.py")
print("2. Partagez les erreurs")
print("="*60)