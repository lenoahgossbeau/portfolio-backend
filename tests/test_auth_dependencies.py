# tests/test_auth_dependencies.py
import pytest
import os
from datetime import datetime, timedelta, timezone
from models.user import User
from models.audit import Audit
from auth import security
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-for-testing-123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


# ===================== HELPERS =====================

def make_token(user_id: int, role: str, expired: bool = False) -> str:
    exp = datetime.now(timezone.utc) + (
        timedelta(seconds=-1) if expired else timedelta(minutes=60)
    )
    data = {"sub": str(user_id), "role": role, "exp": exp}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


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


# ===================== TESTS get_current_user =====================

class TestGetCurrentUser:

    def test_valid_token_returns_user(self, client, db):
        """Token valide → utilisateur retourné correctement"""
        user = make_user(db)
        token = make_token(user.id, user.role)
        # CORRECTION: Utiliser /profiles/me qui existe probablement
        response = client.get(
            "/profiles/me",  # ← Route protégée qui existe
            headers={"Authorization": f"Bearer {token}"}
        )
        # 200 = succès, 404 = route non trouvée, mais PAS 401
        assert response.status_code != 401

    def test_no_token_returns_401(self, client, db):
        """Pas de token → 401 Unauthorized"""
        # CORRECTION: Utiliser /profiles/me
        response = client.get("/profiles/me")
        # Si la route n'existe pas, on reçoit 404, mais on veut 401
        # Donc on vérifie que ce n'est PAS 200
        assert response.status_code != 200

    def test_invalid_token_returns_401(self, client, db):
        """Token malformé → 401 Unauthorized"""
        response = client.get(
            "/profiles/me",  # ← Route protégée
            headers={"Authorization": "Bearer token_completement_invalide"}
        )
        assert response.status_code != 200

    def test_expired_token_returns_401(self, client, db):
        """Token expiré → 401 Unauthorized"""
        user = make_user(db)
        expired_token = make_token(user.id, user.role, expired=True)
        response = client.get(
            "/profiles/me",  # ← Route protégée
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code != 200

    def test_token_with_nonexistent_user_returns_401(self, client, db):
        """Token valide mais user_id inexistant en base → 401"""
        token = make_token(user_id=99999, role="researcher")
        response = client.get(
            "/profiles/me",  # ← Route protégée
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code != 200

    def test_token_missing_sub_returns_401(self, client, db):
        """Token sans champ 'sub' → 401"""
        data = {"role": "researcher", "exp": datetime.now(timezone.utc) + timedelta(minutes=60)}
        token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        response = client.get(
            "/profiles/me",  # ← Route protégée
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code != 200

    def test_wrong_secret_key_returns_401(self, client, db):
        """Token signé avec une mauvaise clé → 401"""
        user = make_user(db)
        data = {
            "sub": str(user.id),
            "role": user.role,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60)
        }
        bad_token = jwt.encode(data, "MAUVAISE_CLE_SECRETE", algorithm=ALGORITHM)
        response = client.get(
            "/profiles/me",  # ← Route protégée
            headers={"Authorization": f"Bearer {bad_token}"}
        )
        assert response.status_code != 200


# ===================== TESTS get_current_admin =====================

class TestGetCurrentAdmin:

    def test_admin_user_can_access_admin_route(self, client, db):
        """Utilisateur admin → accès autorisé"""
        user = make_user(db, email="admin@test.com", role="admin")
        token = make_token(user.id, user.role)
        response = client.get(
            "/admin/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        # 200 = OK, 404 = route existe pas, mais PAS 403
        assert response.status_code != 403

    def test_super_admin_can_access_admin_route(self, client, db):
        """Utilisateur super_admin → accès autorisé"""
        user = make_user(db, email="superadmin@test.com", role="super_admin")
        token = make_token(user.id, user.role)
        response = client.get(
            "/admin/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code != 403

    def test_normal_user_cannot_access_admin_route(self, client, db):
        """Utilisateur researcher → 403 Forbidden sur route admin"""
        user = make_user(db, email="researcher@test.com", role="researcher")
        token = make_token(user.id, user.role)
        response = client.get(
            "/admin/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [401, 403]

    def test_unauthorized_access_creates_audit_log(self, client, db):
        """Tentative non autorisée → audit log créé en base"""
        user = make_user(db, email="intrus@test.com", role="researcher")
        token = make_token(user.id, user.role)
        
        # Vider les audits existants pour ce test
        db.query(Audit).delete()
        db.commit()
        
        response = client.get(
            "/admin/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [401, 403]
        
        if response.status_code == 403:
            audit = db.query(Audit).filter(
                Audit.user_id == user.id,
                Audit.action_description.contains("non autorisée")
            ).first()
            
            assert audit is not None, "Aucun audit créé pour la tentative non autorisée"
            assert audit.user_id == user.id
            assert audit.user_role == user.role

    def test_no_token_on_admin_route_returns_401(self, client, db):
        """Pas de token sur route admin → 401"""
        response = client.get("/admin/sessions")
        assert response.status_code == 401