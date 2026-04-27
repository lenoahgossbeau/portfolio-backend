from pydantic import BaseModel
from typing import Optional

class SubscriptionBase(BaseModel):
    profile_id: int
    start_date: str
    end_date: str
    type: str
    payment_method: str

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionOut(SubscriptionBase):
    id: int
    
    class Config:
        from_attributes = True