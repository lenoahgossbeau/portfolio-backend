import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='inchtechs_db',
    user='admin',
    password='admin'
)
cur = conn.cursor()
cur.execute("DELETE FROM users WHERE email = 'admin@test.com';")
conn.commit()
print('✅ Utilisateur supprimé')
cur.close()
conn.close()
