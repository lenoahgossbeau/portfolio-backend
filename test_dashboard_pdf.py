# test_dashboard_pdf.py
import requests

BASE_URL = "http://localhost:8000"

print("🎯 TEST DU DASHBOARD ET PDF SEULEMENT")
print("="*50)

def try_login(endpoint):
    """Essaie de se connecter à un endpoint donné."""
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=login_data, timeout=5)
        return response
    except Exception as e:
        print(f"   Erreur de connexion: {e}")
        return None

# 1. D'abord, testez si vous voyez les routes dans la documentation
print("\n1. 📋 Vérification des routes dans Swagger...")
print(f"   Allez sur: http://localhost:8000/docs")
print(f"   Cherchez: /api/dashboard/stats et /api/pdf/test")

# 2. Test avec plusieurs endpoints possibles pour le login
print("\n2. 🔐 Test de login...")

# Liste des endpoints possibles pour le login
possible_login_endpoints = [
    "/auth/login",      # Si dans auth_router avec préfixe /auth
    "/login",           # Si dans auth_routes_router sans préfixe
    "/api/auth/login",  # Autre possibilité
    "/user/login",      # Encore une autre
]

token = None
for endpoint in possible_login_endpoints:
    print(f"   Essai de {endpoint}...")
    response = try_login(endpoint)
    if response is not None:
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"   ✅ Token obtenu via {endpoint}: {token[:30]}...")
            break
        else:
            print(f"   ❌ {endpoint} a échoué avec {response.status_code}")
    else:
        print(f"   ❌ {endpoint} n'a pas pu être atteint")

if token is None:
    print("   ❌ Aucun endpoint de login n'a fonctionné.")
    print("\n💡 Conseils:")
    print("   - Vérifiez que le serveur est lancé: uvicorn main:app --reload")
    print("   - Vérifiez les routes dans main.py et les routeurs d'authentification")
    print("   - Allez sur http://localhost:8000/docs pour voir les routes disponibles")
else:
    # 3. Test dashboard
    print("\n3. 📊 Test du dashboard...")
    headers = {"Authorization": f"Bearer {token}"}
    
    stats_response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
    print(f"   Status: {stats_response.status_code}")
    
    if stats_response.status_code == 200:
        data = stats_response.json()
        print(f"   ✅ Dashboard fonctionne !")
        print(f"   📈 Données reçues: {list(data.keys())}")
    elif stats_response.status_code == 403:
        print("   ⚠️  Accès refusé - Vérifiez que votre utilisateur est admin")
    else:
        print(f"   ❌ Erreur: {stats_response.text[:100]}")
    
    # 4. Test PDF
    print("\n4. 📄 Test du PDF...")
    pdf_response = requests.get(f"{BASE_URL}/api/pdf/test", headers=headers)
    print(f"   Status: {pdf_response.status_code}")
    
    if pdf_response.status_code == 200:
        with open("test_dashboard.pdf", "wb") as f:
            f.write(pdf_response.content)
        print(f"   ✅ PDF généré: test_dashboard.pdf")
        print(f"   📏 Taille: {len(pdf_response.content)} bytes")
    else:
        print(f"   ❌ Erreur PDF: {pdf_response.text[:100]}")

print("\n" + "="*50)
print("✅ Test terminé !")