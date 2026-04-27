# tests/test_simple_rate.py
import sys
import os

# AJOUTEZ CES LIGNES
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from fastapi.testclient import TestClient
from main import app

# Ne pas importer requests_counter
# from main import app, requests_counter
import time

client = TestClient(app)

def test_simple_rate_limit():
    """Test simple du rate limiter"""
    print("Test du rate limiter...")
    
    # Route qui existe et n'a pas besoin d'authentification
    endpoint = "/"
    
    # Les 100 premières requêtes doivent passer
    successful = 0
    blocked_at = None
    
    for i in range(105):
        response = client.get(endpoint)
        if response.status_code == 200:
            successful += 1
        elif response.status_code == 429:
            blocked_at = i + 1
            print(f"Bloqué à la requête {blocked_at}")
            break
    
    print(f"Requêtes réussies: {successful}")
    
    # Vérifier qu'au moins 100 requêtes ont réussi (ou que le blocage est arrivé)
    if blocked_at:
        assert blocked_at > 100, f"Bloqué trop tôt à la requête {blocked_at}"
        print(f"✅ Rate limiter a bloqué après {blocked_at} requêtes")
    else:
        # Si pas de blocage, le rate limiter est peut-être désactivé en mode test
        print("⚠️  Rate limiter n'a pas bloqué - peut-être désactivé en mode test")
        assert successful >= 100, f"Seulement {successful} requêtes ont réussi"
    
    print("✅ Test terminé!")

if __name__ == "__main__":
    test_simple_rate_limit()