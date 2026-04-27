import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Détecte l'environnement et choisit la bonne URL
ENV = os.getenv("ENV", "local")

# Priorité : Render (si DATABASE_URL est définie directement)
if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
elif ENV == "docker":
    DATABASE_URL = os.getenv("DATABASE_URL_DOCKER")
else:
    DATABASE_URL = os.getenv("DATABASE_URL_LOCAL")

if not DATABASE_URL:
    raise ValueError(f"Aucune DATABASE_URL trouvée pour ENV='{ENV}'. Vérifie ton .env")

# Configuration SSL pour Render (PostgreSQL)
if "onrender.com" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"sslmode": "require"}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()