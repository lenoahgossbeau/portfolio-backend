from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
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
    
    new_subscription = Subscription(
        profile_id=subscription.profile_id,
        start_date=subscription.start_date,
        end_date=subscription.end_date,
        type=subscription.type,
        payment_method=subscription.payment_method
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription