from database import engine
from models import Base
from models.user import User
from models.profile import Profile
from models.refresh_token import RefreshToken
from models.audit import Audit
from models.publication import Publication
from models.message_contact import MessageContact
from models.comment import Comment
from models.project import Project
from models.academic_career import AcademicCareer
from models.media_artefact import MediaArtefact
from models.distinction import Distinction
from models.cours import Cours
from models.subscription import Subscription

print("Création des tables...")
Base.metadata.create_all(bind=engine)
print("Tables créées avec succès !")