# schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

# 🔹 Schéma de base (champs communs)
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None  # ✅ Rendre optionnel
    role: Optional[str] = "user"
    status: Optional[str] = "active"

# 🔹 Schéma pour la création (requête POST)
class UserCreate(UserBase):
    password: str

# 🔹 Schéma pour la sortie (réponse API)
class UserOut(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)