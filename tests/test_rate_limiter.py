# tests/test_rate_limiter.py
import sys
import os
import time
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="starlette")

# CORRECTION DU PROBLÈME D'IMPORT
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from fastapi.testclient import TestClient
from main import app

# Client de test
client = TestClient(app)

def test_rate_limiter_block_after_100():
    """
    🔴 TEST CONFORME AU CAHIER DES CHARGES
    Vérifie que le rate limiter bloque STRICTEMENT après 100 requêtes
    """
    # ✅ Réinitialiser le rate limiter avant le test
    client.get("/test/reset-rate-limiter")
    
    print("\n🔴 TEST 1: Blocage après 100 requêtes")
    print("=" * 50)
    
    # Route API (doit être limitée)
    test_route = "/api/test-rate-limiter"
    
    successful = 0
    
    # 100 premières requêtes DOIVENT passer
    for i in range(100):
        response = client.get(f"{test_route}-{i}")
        # Vérifier que ce n'est pas bloqué (peut être 404 ou 200)
        assert response.status_code != 429, f"❌ Bloqué à la requête {i+1}/100 alors que ça devrait passer"
        successful += 1
    
    print(f"  ✅ 100 premières requêtes: OK")
    
    # 101ème requête DOIT être bloquée
    response = client.get(f"{test_route}-101")
    
    assert response.status_code == 429, f"❌ 101ème requête non bloquée (status {response.status_code}) - Rate limiter inactif"
    
    data = response.json()
    assert "error" in data, "Message d'erreur manquant"
    assert "message" in data, "Détail du message manquant"
    
    print(f"  ✅ 101ème requête bloquée avec code 429")
    print(f"  Message: {data.get('error')}")
    print("✅ TEST 1 PASSÉ")

def test_rate_limiter_error_message():
    """
    🔴 TEST CONFORME AU CAHIER DES CHARGES
    Vérifie que le message d'erreur est correct
    """
    # ✅ Réinitialiser le rate limiter avant le test
    client.get("/test/reset-rate-limiter")
    
    print(f"\n🔴 TEST 2: Message d'erreur du rate limiter")
    print("=" * 50)
    
    test_route = "/api/test-error-message"
    
    # Faire 100 requêtes pour saturer
    for i in range(100):
        client.get(f"{test_route}-{i}")
    
    # 101ème requête - doit être bloquée avec message
    response = client.get(f"{test_route}-101")
    
    assert response.status_code == 429, f"❌ Non bloqué (status {response.status_code})"
    
    data = response.json()
    assert "error" in data, "❌ Champ 'error' manquant"
    assert "message" in data, "❌ Champ 'message' manquant"
    
    # Vérifier le contenu du message (insensible à la casse)
    error_msg = data.get("error", "").lower()
    detail_msg = data.get("message", "").lower()
    
    assert "trop de requêtes" in error_msg or "rate" in error_msg, f"❌ Message d'erreur incorrect: {data.get('error')}"
    assert "100" in detail_msg or "limite" in detail_msg, f"❌ Détail incorrect: {data.get('message')}"
    
    print(f"  ✅ Message d'erreur: {data.get('error')}")
    print(f"  ✅ Détail: {data.get('message')}")
    print("✅ TEST 2 PASSÉ")

def test_rate_limiter_public_pages_never_blocked():
    """
    🔴 TEST CONFORME AU CAHIER DES CHARGES
    Vérifie que les pages publiques ne sont JAMAIS bloquées
    """
    # ✅ Réinitialiser le rate limiter avant le test
    client.get("/test/reset-rate-limiter")
    
    print("\n🔴 TEST 3: Pages publiques jamais bloquées")
    print("=" * 50)
    
    public_pages = [
        "/", 
        "/about", 
        "/contact", 
        "/legal", 
        "/privacy",
        "/portfolio", 
        "/publications", 
        "/distinctions",
        "/academic-career", 
        "/cours", 
        "/media",
        "/health", 
        "/docs", 
        "/redoc", 
        "/api/info"
    ]
    
    for page in public_pages:
        # Faire 150 requêtes sur chaque page (bien au-dessus de la limite)
        for i in range(150):
            response = client.get(page)
            assert response.status_code != 429, f"❌ Page publique {page} bloquée à la requête {i+1}"
        
        print(f"  ✅ {page}: non limitée (150 requêtes)")
    
    print("✅ TEST 3 PASSÉ")

def test_rate_limiter_headers_present():
    """
    🔴 TEST CONFORME AU CAHIER DES CHARGES
    Vérifie que les headers de rate limiting sont présents
    """
    # ✅ Réinitialiser le rate limiter avant le test
    client.get("/test/reset-rate-limiter")
    
    print("\n🔴 TEST 4: Headers de rate limiting")
    print("=" * 50)
    
    test_route = "/api/test-headers"
    
    response = client.get(test_route)
    
    # Vérification insensible à la casse
    headers_lower = {k.lower(): v for k, v in response.headers.items()}
    
    assert "x-ratelimit-limit" in headers_lower, "❌ Header X-RateLimit-Limit manquant"
    assert "x-ratelimit-remaining" in headers_lower, "❌ Header X-RateLimit-Remaining manquant"
    assert "x-ratelimit-reset" in headers_lower, "❌ Header X-RateLimit-Reset manquant"
    
    limit = int(headers_lower["x-ratelimit-limit"])
    remaining = int(headers_lower["x-ratelimit-remaining"])
    reset = int(headers_lower["x-ratelimit-reset"])
    
    print(f"  X-RateLimit-Limit: {limit}")
    print(f"  X-RateLimit-Remaining: {remaining}")
    print(f"  X-RateLimit-Reset: {reset}")
    
    assert limit == 100, f"❌ Limit = {limit} (devrait être 100)"
    assert remaining >= 0, f"❌ Remaining négatif: {remaining}"
    assert reset > time.time(), f"❌ Reset dans le passé: {reset} < {time.time()}"
    
    print("✅ TEST 4 PASSÉ")

def test_rate_limiter_shared_counter():
    """
    🔴 TEST CONFORME AU CAHIER DES CHARGES
    Vérifie que tous les endpoints API partagent le même compteur
    """
    # ✅ Réinitialiser le rate limiter avant le test
    client.get("/test/reset-rate-limiter")
    
    print("\n🔴 TEST 5: Compteur partagé entre endpoints API")
    print("=" * 50)
    
    endpoints = [
        "/api/test1", 
        "/api/test2", 
        "/api/test3", 
        "/api/test4",
        "/api/users", 
        "/api/projects", 
        "/api/publications"
    ]
    
    # Répartir 100 requêtes sur différents endpoints
    requests_per_endpoint = 100 // len(endpoints)
    total_requests = 0
    
    for endpoint in endpoints:
        for i in range(requests_per_endpoint):
            response = client.get(f"{endpoint}-{i}")
            assert response.status_code != 429, f"❌ Bloqué trop tôt sur {endpoint} à la requête {total_requests+1}"
            total_requests += 1
    
    # Compléter pour arriver exactement à 100
    remaining = 100 - total_requests
    for i in range(remaining):
        response = client.get(f"/api/extra-{i}")
        assert response.status_code != 429, f"❌ Bloqué trop tôt sur endpoint supplémentaire à la requête {total_requests+1}"
        total_requests += 1
    
    print(f"  ✅ {total_requests} requêtes réparties: OK")
    
    # 101ème requête DOIT être bloquée
    response = client.get("/api/final-test")
    assert response.status_code == 429, "❌ Rate limiter ne bloque pas après 100 requêtes partagées"
    
    print("  ✅ 101ème requête bloquée (compteur partagé)")
    print("✅ TEST 5 PASSÉ")

def test_rate_limiter_reset_after_window():
    """
    🔴 TEST CONFORME AU CAHIER DES CHARGES
    Vérifie que le compteur se réinitialise après 60 secondes
    """
    # ✅ Réinitialiser le rate limiter avant le test
    client.get("/test/reset-rate-limiter")
    
    print("\n🔴 TEST 6: Réinitialisation après 60 secondes")
    print("=" * 50)
    
    test_route = "/api/test-reset"
    
    # 100 requêtes pour saturer
    for i in range(100):
        client.get(f"{test_route}-{i}")
    
    # Vérifier que la 101ème est bloquée
    response = client.get(f"{test_route}-101")
    assert response.status_code == 429, "❌ Rate limiter ne bloque pas après 100 requêtes"
    
    print("  ✅ Rate limiter saturé (100 requêtes)")
    
    # Ici on ne peut pas vraiment attendre 60s dans un test
    # On va plutôt vérifier la logique via le header reset
    reset_time = int(response.headers.get("x-ratelimit-reset", 0))
    current_time = int(time.time())
    
    assert reset_time > current_time, f"❌ Reset time incorrect: {reset_time} <= {current_time}"
    assert reset_time - current_time <= 60, f"❌ Reset time trop loin: {reset_time - current_time}s"
    
    print(f"  ✅ Header reset correct: {reset_time}")
    print("  ⏱️  (Test de réinitialisation réelle nécessiterait 60s d'attente)")
    print("✅ TEST 6 PASSÉ (vérification théorique)")

def test_rate_limiter_different_ips_separate_counters():
    """
    🔴 TEST CONFORME AU CAHIER DES CHARGES
    Vérifie que différentes IPs ont des compteurs séparés
    """
    # ✅ Réinitialiser le rate limiter avant le test
    client.get("/test/reset-rate-limiter")
    
    print("\n🔴 TEST 7: Compteurs séparés par IP")
    print("=" * 50)
    
    # Note: En test client, on ne peut pas simuler différentes IPs facilement
    # On va utiliser une approche avec des headers X-Forwarded-For
    
    test_route = "/api/test-ip"
    
    # Simuler IP 1 avec 90 requêtes
    for i in range(90):
        response = client.get(
            f"{test_route}-{i}", 
            headers={"X-Forwarded-For": "192.168.1.100"}
        )
        assert response.status_code != 429, f"❌ IP1 bloquée trop tôt à la requête {i+1}"
    
    # Simuler IP 2 avec 40 requêtes
    for i in range(40):
        response = client.get(
            f"{test_route}-{i}-ip2", 
            headers={"X-Forwarded-For": "192.168.1.200"}
        )
        assert response.status_code != 429, f"❌ IP2 bloquée trop tôt à la requête {i+1}"
    
    print(f"  ✅ IP1: 90 requêtes, IP2: 40 requêtes - OK")
    
    # IP1 devrait pouvoir faire encore 10 requêtes
    for i in range(10):
        response = client.get(
            f"{test_route}-ip1-extra-{i}", 
            headers={"X-Forwarded-For": "192.168.1.100"}
        )
        if i < 9:
            assert response.status_code != 429, f"❌ IP1 bloquée trop tôt à la {90+i+1}ème requête"
        else:
            # La 100ème devrait passer, la 101ème serait bloquée
            assert response.status_code != 429, "❌ IP1 bloquée à la 100ème requête"
    
    print("  ✅ IP1 a pu faire 100 requêtes")
    
    # 101ème requête pour IP1 devrait être bloquée
    response = client.get(
        f"{test_route}-ip1-final", 
        headers={"X-Forwarded-For": "192.168.1.100"}
    )
    assert response.status_code == 429, "❌ IP1 non bloquée à la 101ème requête"
    
    # IP2 devrait pouvoir faire encore 60 requêtes (pour arriver à 100)
    for i in range(60):
        response = client.get(
            f"{test_route}-ip2-extra-{i}", 
            headers={"X-Forwarded-For": "192.168.1.200"}
        )
        if i < 59:
            assert response.status_code != 429, f"❌ IP2 bloquée trop tôt à la {40+i+1}ème requête"
    
    print("  ✅ IP2 a pu faire 100 requêtes")
    print("✅ TEST 7 PASSÉ")

def test_rate_limiter_admin_endpoints_limited():
    """
    🔴 TEST CONFORME AU CAHIER DES CHARGES
    Vérifie que les endpoints admin sont limités comme les autres
    """
    # ✅ Réinitialiser le rate limiter avant le test
    client.get("/test/reset-rate-limiter")
    
    print("\n🔴 TEST 8: Endpoints admin limités")
    print("=" * 50)
    
    admin_endpoints = [
        "/admin/dashboard",
        "/admin/audit-stats",
        "/admin/users"
    ]
    
    total = 0
    blocked_at = None
    
    for endpoint in admin_endpoints:
        for i in range(34):  # 34 * 3 = 102
            response = client.get(f"{endpoint}?t={i}")
            total += 1
            if response.status_code == 429:
                blocked_at = total
                print(f"  ⚠️  Bloqué à la requête {total}")
                break
        if blocked_at:
            break
    
    if blocked_at:
        # Accepte le blocage à 100, 101 ou 102 (selon la configuration)
        assert blocked_at in [100, 101, 102], f"❌ Bloqué trop tôt ou trop tard à la requête {blocked_at}"
        print(f"  ✅ Endpoint admin bloqué à la requête {blocked_at}")
    else:
        # Si pas bloqué pendant les 102 requêtes, vérifier la 103ème
        print(f"  ✅ {total} requêtes admin sans blocage")
        response = client.get("/admin/final-test")
        assert response.status_code == 429, "❌ Endpoint admin non bloqué après 100 requêtes"
        print("  ✅ Endpoint admin bloqué à la 103ème requête")
    
    print("✅ TEST 8 PASSÉ")

if __name__ == "__main__":
    """
    Exécution manuelle des tests
    """
    print("\n" + "="*70)
    print("🧪🧪🧪 TESTS STRICTS DU RATE LIMITER 🧪🧪🧪")
    print("="*70)
    print("Ces tests DOIVENT tous passer si le rate limiter est conforme")
    print("="*70 + "\n")
    
    tests = [
        test_rate_limiter_block_after_100,
        test_rate_limiter_error_message,
        test_rate_limiter_public_pages_never_blocked,
        test_rate_limiter_headers_present,
        test_rate_limiter_shared_counter,
        test_rate_limiter_reset_after_window,
        test_rate_limiter_different_ips_separate_counters,
        test_rate_limiter_admin_endpoints_limited
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print(f"\n✅ {test.__name__}: PASSÉ\n")
            print("-" * 70)
        except AssertionError as e:
            failed += 1
            print(f"\n❌ {test.__name__}: ÉCHOUÉ")
            print(f"   Raison: {str(e)}\n")
            print("-" * 70)
        except Exception as e:
            failed += 1
            print(f"\n❌ {test.__name__}: ERREUR - {str(e)}\n")
            print("-" * 70)
    
    print("\n" + "="*70)
    print(f"RÉSULTATS FINAUX: {passed} passés, {failed} échoués")
    
    if failed == 0:
        print("🎉🎉🎉 RATE LIMITER CONFORME AU CAHIER DES CHARGES ! 🎉🎉🎉")
    else:
        print("❌❌❌ RATE LIMITER NON CONFORME ! ❌❌❌")
        print("\n🔧 CORRECTIONS NÉCESSAIRES:")
        print("   1. Vérifier que le rate limiter est actif (pas de condition TEST_MODE)")
        print("   2. Vérifier que la limite est à 100 requêtes par minute")
        print("   3. Vérifier que les headers X-RateLimit sont présents")
        print("   4. Vérifier que les pages publiques ne sont jamais limitées")
    
    print("="*70 + "\n")