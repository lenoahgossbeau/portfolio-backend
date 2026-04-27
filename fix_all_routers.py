import os
import re

routers = [
    ('auth/router.py', 'auth'),
    ('routes/user.py', 'users'),
    ('routes/profile.py', 'profiles'),
    ('routes/publication.py', 'publications'),
    ('routes/project.py', 'projects'),
    ('routes/admin.py', 'admin'),
    ('routes/admin_users.py', 'admin/users'),
    ('routes/auth.py', 'auth'),
]

print("🔧 Correction de tous les routeurs...\n")

for router_file, expected_prefix in routers:
    if os.path.exists(router_file):
        with open(router_file, 'r') as f:
            content = f.read()
        
        # Chercher APIRouter avec préfixe
        pattern = r'(router\s*=\s*APIRouter\(.*?prefix\s*=\s*["\'])([^"\']+)(["\'].*?\))'
        
        if re.search(pattern, content):
            # Remplacer par router = APIRouter() sans préfixe
            new_content = re.sub(pattern, r'router = APIRouter()', content)
            
            # Sauvegarder
            with open(router_file, 'w') as f:
                f.write(new_content)
            
            print(f"✅ {router_file}: préfixe supprimé")
        else:
            print(f"⏭️  {router_file}: déjà correct")
    else:
        print(f"⚠️  {router_file}: fichier non trouvé")

print("\n🎯 Après correction, redémarrez le serveur et testez :")
print("curl http://localhost:8000/openapi.json | python -m json.tool")