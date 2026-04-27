# test_final_login.py
import requests

BASE_URL = "http://localhost:8000"
print("🔐 TEST FINAL DU LOGIN")
print("="*60)

# Testez les deux endpoints
for endpoint in ["/auth/login", "/login"]:
    print(f"\nTest {endpoint}:")
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json={"email": "admin@test.com", "password": "admin123"},
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"  ✅ SUCCÈS ! Token: {token[:50]}...")
            
            # Sauvegarder le token
            with open("token.txt", "w") as f:
                f.write(token)
            print(f"  💾 Token sauvegardé dans token.txt")
            
            break  # Sortir de la boucle si succès
            
        elif response.status_code == 500:
            print(f"  ❌ 500 - Erreur serveur")
            print(f"  Message: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")

print("\n" + "="*60)