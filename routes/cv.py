from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from models.profile import Profile
from sqlalchemy import text

router = APIRouter(prefix="/cv", tags=["CV"])

# ==================== SCHÉMAS PYDANTIC ====================
class TechnicalSkillCreate(BaseModel):
    name: str
    level: int

class SoftSkillCreate(BaseModel):
    name: str

class LanguageCreate(BaseModel):
    name: str
    level: str
    percent: Optional[int] = 50

class DegreeCreate(BaseModel):
    title: str
    institution: str
    year: str
    description: str

class ExperienceCreate(BaseModel):
    title: str
    company: str
    start_date: str
    end_date: Optional[str] = None
    description: str

# ==================== GET /me ====================
@router.get("/me")
def get_my_cv(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    profile_id = profile.id
    
    tech_result = db.execute(text("SELECT id, skill_name, level FROM technical_skills WHERE profile_id = :pid"), {"pid": profile_id})
    technical_skills = [{"id": row[0], "name": row[1], "level": row[2]} for row in tech_result]
    
    soft_result = db.execute(text("SELECT id, skill_name FROM soft_skills WHERE profile_id = :pid"), {"pid": profile_id})
    soft_skills = [{"id": row[0], "name": row[1], "level": 50} for row in soft_result]
    
    lang_result = db.execute(text("SELECT id, language, level FROM languages WHERE profile_id = :pid"), {"pid": profile_id})
    languages = [{"id": row[0], "name": row[1], "level": row[2], "percent": 50} for row in lang_result]
    
    degree_result = db.execute(text("SELECT id, title, institution, year, description FROM degrees WHERE profile_id = :pid"), {"pid": profile_id})
    degrees = [{"id": row[0], "title": row[1], "institution": row[2], "year": row[3], "description": row[4] or ""} for row in degree_result]
    
    exp_result = db.execute(text("SELECT id, title, company, start_date, end_date, description FROM experiences WHERE profile_id = :pid"), {"pid": profile_id})
    experiences = [{"id": row[0], "title": row[1], "company": row[2], "start_date": str(row[3]), "end_date": str(row[4]) if row[4] else None, "description": row[5] or ""} for row in exp_result]
    
    return {
        "technical_skills": technical_skills,
        "soft_skills": soft_skills,
        "languages": languages,
        "degrees": degrees,
        "experiences": experiences
    }

# ==================== TECHNICAL SKILLS CRUD ====================
@router.post("/technical-skills")
def add_technical_skill(skill: TechnicalSkillCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    db.execute(text("INSERT INTO technical_skills (profile_id, skill_name, level) VALUES (:pid, :name, :level)"), 
               {"pid": profile.id, "name": skill.name, "level": skill.level})
    db.commit()
    return {"message": "Skill ajoutée"}

@router.put("/technical-skills/{skill_id}")
def update_technical_skill(skill_id: int, skill: TechnicalSkillCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    db.execute(text("UPDATE technical_skills SET skill_name = :name, level = :level WHERE id = :sid AND profile_id = :pid"),
               {"name": skill.name, "level": skill.level, "sid": skill_id, "pid": profile.id})
    db.commit()
    return {"message": "Skill mise à jour"}

@router.delete("/technical-skills/{skill_id}")
def delete_technical_skill(skill_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    db.execute(text("DELETE FROM technical_skills WHERE id = :sid AND profile_id = :pid"), {"sid": skill_id, "pid": profile.id})
    db.commit()
    return {"message": "Skill supprimée"}

# ==================== SOFT SKILLS CRUD ====================
@router.post("/soft-skills")
def add_soft_skill(skill: SoftSkillCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    db.execute(text("INSERT INTO soft_skills (profile_id, skill_name) VALUES (:pid, :name)"), 
               {"pid": profile.id, "name": skill.name})
    db.commit()
    return {"message": "Soft skill ajoutée"}

@router.delete("/soft-skills/{skill_id}")
def delete_soft_skill(skill_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    db.execute(text("DELETE FROM soft_skills WHERE id = :sid AND profile_id = :pid"), {"sid": skill_id, "pid": profile.id})
    db.commit()
    return {"message": "Soft skill supprimée"}

# ==================== LANGUAGES CRUD ====================
@router.post("/languages")
def add_language(lang: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profil non trouvé")
        
        name = lang.get('name') or lang.get('language')
        level = lang.get('level')
        
        if not name or not level:
            raise HTTPException(status_code=400, detail="name et level sont requis")
        
        db.execute(text("INSERT INTO languages (profile_id, language, level) VALUES (:pid, :name, :level)"), 
                   {"pid": profile.id, "name": name, "level": level})
        db.commit()
        return {"message": "Langue ajoutée"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/languages/{lang_id}")
def update_language(lang_id: int, lang: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profil non trouvé")
        
        name = lang.get('name') or lang.get('language')
        level = lang.get('level')
        
        if not name or not level:
            raise HTTPException(status_code=400, detail="name et level sont requis")
        
        db.execute(text("UPDATE languages SET language = :name, level = :level WHERE id = :lid AND profile_id = :pid"),
                   {"name": name, "level": level, "lid": lang_id, "pid": profile.id})
        db.commit()
        return {"message": "Langue mise à jour"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/languages/{lang_id}")
def delete_language(lang_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    db.execute(text("DELETE FROM languages WHERE id = :lid AND profile_id = :pid"), {"lid": lang_id, "pid": profile.id})
    db.commit()
    return {"message": "Langue supprimée"}

# ==================== DEGREES CRUD (CORRIGÉ) ====================
@router.post("/degrees")
def add_degree(degree: DegreeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    # S'assurer que l'année est une chaîne
    year_str = str(degree.year) if degree.year else ""
    
    db.execute(text("INSERT INTO degrees (profile_id, title, institution, year, description) VALUES (:pid, :title, :institution, :year, :desc)"),
               {"pid": profile.id, "title": degree.title, "institution": degree.institution, "year": year_str, "desc": degree.description})
    db.commit()
    return {"message": "Diplôme ajouté"}

@router.put("/degrees/{degree_id}")
def update_degree(degree_id: int, degree: DegreeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    year_str = str(degree.year) if degree.year else ""
    
    db.execute(text("UPDATE degrees SET title = :title, institution = :institution, year = :year, description = :desc WHERE id = :did AND profile_id = :pid"),
               {"title": degree.title, "institution": degree.institution, "year": year_str, "desc": degree.description, "did": degree_id, "pid": profile.id})
    db.commit()
    return {"message": "Diplôme mis à jour"}

@router.delete("/degrees/{degree_id}")
def delete_degree(degree_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    db.execute(text("DELETE FROM degrees WHERE id = :did AND profile_id = :pid"), {"did": degree_id, "pid": profile.id})
    db.commit()
    return {"message": "Diplôme supprimé"}

# ==================== EXPERIENCES CRUD (CORRIGÉ) ====================
@router.post("/experiences")
def add_experience(exp: ExperienceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    # Gérer les dates nulles
    end_date = exp.end_date if exp.end_date else None
    
    db.execute(text("INSERT INTO experiences (profile_id, title, company, start_date, end_date, description) VALUES (:pid, :title, :company, :start, :end, :desc)"),
               {"pid": profile.id, "title": exp.title, "company": exp.company, "start": exp.start_date, "end": end_date, "desc": exp.description})
    db.commit()
    return {"message": "Expérience ajoutée"}

@router.put("/experiences/{exp_id}")
def update_experience(exp_id: int, exp: ExperienceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    end_date = exp.end_date if exp.end_date else None
    
    db.execute(text("UPDATE experiences SET title = :title, company = :company, start_date = :start, end_date = :end, description = :desc WHERE id = :eid AND profile_id = :pid"),
               {"title": exp.title, "company": exp.company, "start": exp.start_date, "end": end_date, "desc": exp.description, "eid": exp_id, "pid": profile.id})
    db.commit()
    return {"message": "Expérience mise à jour"}

@router.delete("/experiences/{exp_id}")
def delete_experience(exp_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    db.execute(text("DELETE FROM experiences WHERE id = :eid AND profile_id = :pid"), {"eid": exp_id, "pid": profile.id})
    db.commit()
    return {"message": "Expérience supprimée"}