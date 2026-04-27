from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from database import get_db
from models.user import User
from models.profile import Profile
from models.audit import Audit
from models.refresh_token import RefreshToken

from auth.schemas import UserCreate, UserLogin, Token
from auth.security import hash_password, verify_password
from auth.jwt import create_access_token, create_refresh_token, decode_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# ======================
# REGISTER
# ======================
@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Créer l'utilisateur
    user = User(
        email=user_data.email,
        password=hash_password(user_data.password),
        role="researcher",
        status="active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Créer le profil - ✅ CORRIGÉ: ajout de grade
    profile = Profile(
        user_id=user.id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        grade="Non spécifié"  # Valeur par défaut pour éviter NOT NULL
    )
    db.add(profile)
    db.commit()

    # Audit
    audit_log = Audit(
        user_id=user.id,
        user_role=user.role,
        action_description="Nouvel utilisateur inscrit"
    )
    db.add(audit_log)
    db.commit()

    # Créer les tokens
    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=15)
    )
    refresh_token = create_refresh_token(
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(days=7)
    )

    # Stocker refresh token
    db_refresh = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        revoked=False
    )
    db.add(db_refresh)
    db.commit()

    response = JSONResponse({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    })
    response.set_cookie("access_token", access_token, httponly=True, secure=False, samesite="lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="lax")
    return response


# ======================
# LOGIN
# ======================
@router.post("/login", response_model=Token)
def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants incorrects")

    if user.status != "active":
        raise HTTPException(status_code=403, detail="Compte désactivé")

    # Créer les tokens
    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=15)
    )
    refresh_token = create_refresh_token(
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(days=7)
    )

    # Audit
    audit_log = Audit(
        user_id=user.id,
        user_role=user.role,
        action_description="Connexion réussie"
    )
    db.add(audit_log)

    # Stocker refresh token
    db_refresh = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        revoked=False
    )
    db.add(db_refresh)
    db.commit()

    response = JSONResponse({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    })
    response.set_cookie("access_token", access_token, httponly=True, secure=False, samesite="lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="lax")
    return response


# ======================
# REFRESH
# ======================
@router.post("/refresh")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token manquant")

    payload = decode_access_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token invalide ou expiré")

    db_token = db.query(RefreshToken).filter_by(token=refresh_token, revoked=False).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Refresh token révoqué ou inexistant")

    if db_token.expires_at and db_token.expires_at < datetime.now(timezone.utc):
        db_token.revoked = True
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expiré")

    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    new_access_token = create_access_token(
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=15)
    )

    response = JSONResponse({
        "access_token": new_access_token,
        "token_type": "bearer"
    })
    response.set_cookie("access_token", new_access_token, httponly=True, secure=False, samesite="lax")
    return response


# ======================
# LOGOUT - ✅ CORRIGÉ
# ======================
@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    user_id = None
    user_role = "anonymous"
    
    if refresh_token:
        db_token = db.query(RefreshToken).filter_by(token=refresh_token).first()
        if db_token:
            user_id = db_token.user_id
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_role = user.role
            db_token.revoked = True
            db.commit()

    # ✅ NE CRÉER L'AUDIT QUE SI ON A UN USER_ID VALIDE
    if user_id is not None:
        audit_log = Audit(
            user_id=user_id,
            user_role=user_role,
            action_description="Déconnexion"
        )
        db.add(audit_log)
        db.commit()

    response = JSONResponse({"message": "Déconnecté ✅"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response