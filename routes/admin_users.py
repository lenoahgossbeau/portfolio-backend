from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from sqlalchemy.orm import Session
from io import StringIO
import csv
from datetime import datetime, timezone

from database import get_db
from models.user import User
from models.audit import Audit
from models.profile import Profile
from auth.jwt import get_current_user
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

admin_users_router = APIRouter(
    prefix="/admin/users",
    tags=["Admin Users"]
)

templates = Jinja2Templates(directory="templates")

# Schéma pour le changement de rôle
class RoleChangeRequest(BaseModel):
    role: str

# ======================
# LISTE DES UTILISATEURS (JSON) avec audit
# ======================
@admin_users_router.get("/")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role: str = Query(None),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    # CORRIGÉ : Accepter admin et super_admin
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    query = db.query(User)

    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)

    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()

    audit_log = Audit(
        user_id=current_user.id,
        user_role=current_user.role,
        action_description=f"Consultation utilisateurs (role={role}, status={status}, page={page})",
        date=datetime.now(timezone.utc)
    )
    db.add(audit_log)
    db.commit()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "status": u.status,
                "profile": {
                    "first_name": u.profile.first_name if u.profile else None,
                    "last_name": u.profile.last_name if u.profile else None
                } if u.profile else None
            }
            for u in users
        ]
    }

# ======================
# EXPORT CSV avec audit
# ======================
@admin_users_router.get("/export")
def export_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role: str = Query(None),
    status: str = Query(None)
):
    # CORRIGÉ : Accepter admin et super_admin
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)

    users = query.all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Email", "Role", "Status", "Prénom", "Nom"])
    for u in users:
        writer.writerow([
            u.id, 
            u.email, 
            u.role, 
            u.status,
            u.profile.first_name if u.profile else "",
            u.profile.last_name if u.profile else ""
        ])

    output.seek(0)

    audit_log = Audit(
        user_id=current_user.id,
        user_role=current_user.role,
        action_description=f"Export CSV utilisateurs (role={role}, status={status})",
        date=datetime.now(timezone.utc)
    )
    db.add(audit_log)
    db.commit()

    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=users_export.csv"
    })

# ======================
# PAGE HTML
# ======================
@admin_users_router.get("/page", response_class=HTMLResponse)
def users_page(request: Request, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return templates.TemplateResponse(request, "users.html")

# ======================
# CHANGER LE RÔLE D'UN UTILISATEUR
# ======================
@admin_users_router.put("/{user_id}/role")
def change_user_role(
    user_id: int,
    payload: RoleChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Changer le rôle d'un utilisateur (admin uniquement)"""
    # Vérifier que l'utilisateur actuel est super_admin (seul lui peut changer les rôles)
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Seul un super_admin peut changer les rôles")
    
    # Vérifier que l'utilisateur cible existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Vérifier que le nouveau rôle est valide
    new_role = payload.role
    if new_role not in ["researcher", "admin", "super_admin"]:
        raise HTTPException(status_code=400, detail="Rôle invalide")
    
    # Enregistrer l'ancien rôle
    old_role = user.role
    
    # Changer le rôle
    user.role = new_role
    db.commit()
    
    # Audit log
    audit_log = Audit(
        user_id=current_user.id,
        user_role=current_user.role,
        action_description=f"Changement de rôle de l'utilisateur {user.email} de {old_role} vers {new_role}",
        date=datetime.now(timezone.utc)
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "message": f"Rôle de l'utilisateur {user.email} changé avec succès",
        "user_id": user.id,
        "old_role": old_role,
        "new_role": new_role
    }

# ======================
# SUPPRIMER UN UTILISATEUR
# ======================
@admin_users_router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un utilisateur (admin uniquement)"""
    # Vérifier que l'utilisateur actuel est super_admin
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    # Vérifier que l'utilisateur cible existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Empêcher la suppression de son propre compte
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")
    
    # Audit log avant suppression
    audit_log = Audit(
        user_id=current_user.id,
        user_role=current_user.role,
        action_description=f"Suppression de l'utilisateur {user.email} (ID: {user.id})",
        date=datetime.now(timezone.utc)
    )
    db.add(audit_log)
    
    # Supprimer l'utilisateur
    db.delete(user)
    db.commit()
    
    return None  # 204 No Content