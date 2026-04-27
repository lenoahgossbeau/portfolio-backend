from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from database import Base

class TechnicalSkill(Base):
    __tablename__ = "technical_skills"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    skill_name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)

class SoftSkill(Base):
    __tablename__ = "soft_skills"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    skill_name = Column(String(100), nullable=False)

class Degree(Base):
    __tablename__ = "degrees"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    title = Column(String(200), nullable=False)
    institution = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    description = Column(Text)

class Experience(Base):
    __tablename__ = "experiences"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    description = Column(Text)

class Language(Base):
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    language = Column(String(50), nullable=False)
    level = Column(String(50), nullable=False)