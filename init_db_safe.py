# init_db_safe.py - Version sécurisée
from database import engine, Base
import traceback

def init_db_safe():
    """Initialisation sécurisée de la base"""
    print("🔧 Initialisation sécurisée de la base...")
    
    try:
        # 1. Vérifier la connexion
        with engine.connect() as conn:
            print("✅ Connexion à la base OK")
        
        # 2. Importer TOUS les modèles
        print("📦 Importation des modèles...")
        
        # Liste de tous vos modèles
        models_to_import = [
            'models.user',
            'models.refresh_token', 
            'models.profile',
            'models.audit',
            'models.publication',
            'models.message_contact',
            'models.comment',
            'models.project',
            'models.academic_career',
            'models.media_artefact',
            'models.distinction',
            'models.cours',
            'models.subscription'
        ]
        
        for model in models_to_import:
            try:
                __import__(model)
                print(f"  ✅ {model}")
            except Exception as e:
                print(f"  ⚠️  {model}: {str(e)[:50]}")
        
        # 3. Créer les tables
        print("\n🏗️  Création des tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès")
    assert True
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        traceback.print_exc()
        print("\n⚠️  L'application démarre en mode dégradé")
    assert False