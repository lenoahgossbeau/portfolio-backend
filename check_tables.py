import psycopg2
from database import DATABASE_URL

try:
    print("🔍 VÉRIFICATION DE VOTRE BASE DE DONNÉES")
    print("=" * 50)
    
    # Connexion à la base de données
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Exécution de la requête - méthode correcte
    cur.execute("SELECT 1")
    result = cur.fetchone()
    
    if result and result[0] == 1:
        print("✅ Connexion PostgreSQL réussie")
        
        # Vérifier les tables existantes
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        
        print(f"📊 Tables trouvées ({len(tables)}):")
        for table in tables:
            print(f"   - {table[0]}")
            
    cur.close()
    conn.close()
    
except ImportError:
    print("❌ database.py non trouvé")
except psycopg2.OperationalError as e:
    print(f"❌ Erreur de connexion PostgreSQL: {e}")
    print("\nVérifiez que:")
    print("1. PostgreSQL est démarré")
    print("2. Votre database.py a les bons identifiants:")
    print(f"   DATABASE_URL = '{DATABASE_URL}'")
except Exception as e:
    print(f"❌ Erreur: {e}")