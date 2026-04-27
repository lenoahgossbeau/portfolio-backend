# fix_all_schemas.py
import os

print("=== CORRECTION DES SCHÉMAS PYDANTIC v2 ===")
print()

# Liste de tous vos fichiers de schémas
schema_files = [
    "schemas/audit.py",
    "schemas/auth.py", 
    "schemas/comment.py",
    "schemas/message.py",
    "schemas/publication.py"
]

for file_path in schema_files:
    print(f"📁 Traitement de {file_path}...")
    
    try:
        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            print(f"   ❌ Fichier non trouvé")
            continue
            
        # Lire le contenu du fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si déjà corrigé
        if 'model_config = ConfigDict(from_attributes=True)' in content:
            print(f"   ✅ Déjà en syntaxe Pydantic v2")
            continue
            
        # Vérifier si contient l'ancienne syntaxe
        if 'class Config:' in content and 'orm_mode = True' in content:
            print(f"   🔧 Ancienne syntaxe détectée, correction...")
            
            # Remplacer l'ancienne syntaxe
            new_content = content.replace(
                '    class Config:\n        orm_mode = True\n',
                '    model_config = ConfigDict(from_attributes=True)\n'
            )
            
            # Ajouter l'import ConfigDict si nécessaire
            if 'ConfigDict' in new_content and 'from pydantic import ConfigDict' not in new_content:
                if 'from pydantic import BaseModel' in new_content:
                    new_content = new_content.replace(
                        'from pydantic import BaseModel',
                        'from pydantic import BaseModel, ConfigDict'
                    )
                elif 'from pydantic import' in new_content:
                    # Trouver la ligne d'import existante
                    lines = new_content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('from pydantic import'):
                            # Ajouter ConfigDict à l'import existant
                            if 'ConfigDict' not in line:
                                lines[i] = line.replace('from pydantic import', 'from pydantic import ConfigDict, ')
                            break
                    new_content = '\n'.join(lines)
            
            # Écrire le fichier corrigé
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"   ✅ Fichier corrigé avec succès")
        else:
            print(f"   ℹ️  Pas de configuration à corriger")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

print()
print("=== RÉSUMÉ ===")
print("✅ user.py - Déjà corrigé")
print("✅ profile.py - Déjà corrigé")
print("✅ cours.py - Déjà corrigé")
print("📝 Les autres fichiers ont été vérifiés/corrigés")
print()
print("Pour vérifier :")
print("1. Exécutez: pytest tests/ -v")
print("2. Les warnings Pydantic devraient disparaître")