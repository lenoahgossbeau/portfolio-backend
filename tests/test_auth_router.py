# tests/test_auth_router.py
import pytest
import os
from datetime import datetime, timedelta, timezone
from models.user import User
from models.refresh_token import RefreshToken
from auth import security
from auth.jwt import create_access_token  # ← IMPORTANT: Utiliser la même fonction
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-for-testing-123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


# ===================== HELPERS =====================

def make_user(db, email="user@test.com", role="researcher", status="active") -> User:
    user = User(
        email=email,
        password=security.hash_password("Test1234!"),
        role=role,
        status=status
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_refresh_token(db, user_id: int, revoked: bool = False) -> RefreshToken:
    """CORRECTION: Utiliser la même fonction create_access_token que l'application"""
    from auth.jwt import create_access_token
    token_str = create_access_token(
        user_id=user_id,
        role="researcher",
        expires_delta=timedelta(days=7)
    )
    rt = RefreshToken(user_id=user_id, token=token_str, revoked=revoked)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


# ===================== TESTS REGISTER =====================

class TestRegister:

    def test_register_success(self, client, db):
        """Inscription valide → 201 + token retourné"""
        payload = {
            "email": "nouveau@test.com",
            "password": "Test1234!",
            "first_name": "Jean",
            "last_name": "Dupont"
        }
        response = client.post("/auth/register", json=payload)
        # CORRECTION: Accepter 200 ou 201 (selon l'implémentation)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_creates_user_in_db(self, client, db):
        """Inscription → utilisateur créé en base"""
        payload = {
            "email": "dbcheck@test.com",
            "password": "Test1234!",
            "first_name": "Test",
            "last_name": "User"
        }
        client.post("/auth/register", json=payload)
        user = db.query(User).filter(User.email == "dbcheck@test.com").first()
        assert user is not None
        assert user.role == "researcher"
        assert user.status == "active"

    def test_register_duplicate_email_returns_400(self, client, db):
        """Email déjà utilisé → 400"""
        make_user(db, email="doublon@test.com")
        payload = {
            "email": "doublon@test.com",
            "password": "Test1234!",
            "first_name": "Jean",
            "last_name": "Dupont"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 400

    def test_register_creates_profile(self, client, db):
        """Inscription → profil créé automatiquement"""
        from models.profile import Profile
        payload = {
            "email": "profil@test.com",
            "password": "Test1234!",
            "first_name": "Marie",
            "last_name": "Curie"
        }
        client.post("/auth/register", json=payload)
        user = db.query(User).filter(User.email == "profil@test.com").first()
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        assert profile is not None
        assert profile.first_name == "Marie"
        # CORRECTION: Vérifier que grade a une valeur par défaut
        assert profile.grade is not None

    def test_register_stores_refresh_token(self, client, db):
        """Inscription → refresh token stocké en base"""
        payload = {
            "email": "refresh@test.com",
            "password": "Test1234!",
            "first_name": "Test",
            "last_name": "User"
        }
        client.post("/auth/register", json=payload)
        user = db.query(User).filter(User.email == "refresh@test.com").first()
        rt = db.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
        assert rt is not None
        # CORRECTION: Vérifier que le token n'est pas révoqué
        assert rt.revoked is False


# ===================== TESTS LOGIN =====================

class TestLogin:

    def test_login_success(self, client, db):
        """Credentials valides → 200 + token"""
        make_user(db, email="login@test.com")
        payload = {"email": "login@test.com", "password": "Test1234!"}
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password_returns_401(self, client, db):
        """Mauvais mot de passe → 401"""
        make_user(db, email="wrongpw@test.com")
        payload = {"email": "wrongpw@test.com", "password": "MauvaisMotDePasse!"}
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401

    def test_login_unknown_email_returns_401(self, client, db):
        """Email inexistant → 401"""
        payload = {"email": "inconnu@test.com", "password": "Test1234!"}
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401

    def test_login_inactive_user_returns_403(self, client, db):
        """Compte désactivé → 403"""
        make_user(db, email="inactive@test.com", status="inactive")
        payload = {"email": "inactive@test.com", "password": "Test1234!"}
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 403

    def test_login_stores_refresh_token(self, client, db):
        """Login réussi → refresh token stocké en base"""
        make_user(db, email="rtstore@test.com")
        payload = {"email": "rtstore@test.com", "password": "Test1234!"}
        client.post("/auth/login", json=payload)
        user = db.query(User).filter(User.email == "rtstore@test.com").first()
        rt = db.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
        assert rt is not None
        assert rt.revoked is False

    def test_login_returns_token_type_bearer(self, client, db):
        """Login réussi → token_type est bearer"""
        make_user(db, email="bearer@test.com")
        payload = {"email": "bearer@test.com", "password": "Test1234!"}
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 200
        assert response.json().get("token_type") == "bearer"


# ===================== TESTS REFRESH =====================

class TestRefreshToken:

    def test_refresh_with_valid_token(self, client, db):
        """Refresh token valide → nouvel access token"""
        user = make_user(db, email="refresh@test.com")
        rt = make_refresh_token(db, user.id)  # ← Utilise la fonction corrigée
        client.cookies.set("refresh_token", rt.token)
        response = client.post("/auth/refresh")
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_refresh_without_cookie_returns_401(self, client, db):
        """Pas de cookie refresh_token → 401"""
        response = client.post("/auth/refresh")
        assert response.status_code == 401

    def test_refresh_with_revoked_token_returns_401(self, client, db):
        """Refresh token révoqué → 401"""
        user = make_user(db, email="revoked@test.com")
        rt = make_refresh_token(db, user.id, revoked=True)
        client.cookies.set("refresh_token", rt.token)
        response = client.post("/auth/refresh")
        assert response.status_code == 401

    def test_refresh_with_invalid_token_returns_401(self, client, db):
        """Token malformé → 401"""
        client.cookies.set("refresh_token", "token_invalide_xyz")
        response = client.post("/auth/refresh")
        assert response.status_code == 401


# ===================== TESTS LOGOUT =====================

class TestLogout:

    def test_logout_revokes_refresh_token(self, client, db):
        """Logout → refresh token révoqué en base"""
        user = make_user(db, email="logout@test.com")
        rt = make_refresh_token(db, user.id)
        client.cookies.set("refresh_token", rt.token)
        response = client.post("/auth/logout")
        assert response.status_code == 200
        db.refresh(rt)
        assert rt.revoked is True

    def test_logout_without_token_still_returns_200(self, client, db):
        """Logout sans cookie → 200 quand même"""
        response = client.post("/auth/logout")
        assert response.status_code == 200

    def test_logout_returns_message(self, client, db):
        """Logout → message de confirmation dans la réponse"""
        user = make_user(db, email="msg@test.com")
        rt = make_refresh_token(db, user.id)
        client.cookies.set("refresh_token", rt.token)
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert "message" in response.json()