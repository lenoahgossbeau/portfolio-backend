from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models.user import User
from models.subscription import Subscription
from models.profile import Profile
from schemas.subscription import SubscriptionOut, SubscriptionCreate
from auth.dependencies import get_current_admin

router = APIRouter(
    prefix="/admin/subscriptions",
    tags=["Admin Subscriptions"]
)

@router.get("/", response_model=List[SubscriptionOut])
def get_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Récupère tous les abonnements (admin uniquement)"""
    subscriptions = db.query(Subscription).all()
    return subscriptions

@router.post("/", response_model=SubscriptionOut, status_code=status.HTTP_201_CREATED)
def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Crée un nouvel abonnement (admin uniquement)"""
    # Vérifier que le profil existe
    profile = db.query(Profile).filter(Profile.id == subscription.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    # Convertir les dates des strings en objets date
    start_date = datetime.strptime(subscription.start_date, '%Y-%m-%d').date() if subscription.start_date else None
    end_date = datetime.strptime(subscription.end_date, '%Y-%m-%d').date() if subscription.end_date else None
    
    new_subscription = Subscription(
        profile_id=subscription.profile_id,
        start_date=start_date,
        end_date=end_date,
        type=subscription.type,
        payment_method=subscription.payment_method
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription

@router.put("/{subscription_id}", response_model=SubscriptionOut)
def update_subscription(
    subscription_id: int,
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Modifie un abonnement existant (admin uniquement)"""
    # Vérifier que l'abonnement existe
    existing = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    # Vérifier que le profil existe
    profile = db.query(Profile).filter(Profile.id == subscription.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    # Convertir les dates des strings en objets date
    start_date = datetime.strptime(subscription.start_date, '%Y-%m-%d').date() if subscription.start_date else None
    end_date = datetime.strptime(subscription.end_date, '%Y-%m-%d').date() if subscription.end_date else None
    
    # Mettre à jour l'abonnement
    existing.profile_id = subscription.profile_id
    existing.start_date = start_date
    existing.end_date = end_date
    existing.type = subscription.type
    existing.payment_method = subscription.payment_method
    
    db.commit()
    db.refresh(existing)
    return existing

# ✅ NOUVELLE ROUTE DELETE AJOUTÉE ICI
@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Supprime un abonnement (admin uniquement)"""
    # Vérifier que l'abonnement existe
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    db.delete(subscription)
    db.commit()
    return None