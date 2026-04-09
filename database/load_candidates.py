import psycopg2

conn = psycopg2.connect(database="voting_system")
cursor = conn.cursor()

csv_path = '/Users/hemanthtavva/Desktop/project_final/database/candidates.csv'

inserted = 0
with open(csv_path, 'r') as f:
    next(f)  # Skip header
    for line in f:
        line = line.strip()
        if not line:
            continue
        
        # Split only first 3 commas (constituency_no, name, party, then rest is candidate)
        parts = line.split(',', 3)
        if len(parts) < 4:
            continue
        
        constituency_no = parts[0].strip()
        constituency_name = parts[1].strip()
        party = parts[2].strip()
        candidate = parts[3].strip()
        
        if not constituency_no.isdigit():
            continue
        
        cursor.execute("""
            INSERT INTO candidates (constituency_no, constituency_name, party, candidate)
            VALUES (%s, %s, %s, %s)
        """, (int(constituency_no), constituency_name, party, candidate))
        inserted += 1

conn.commit()
print(f"✅ Inserted {inserted} candidates")

cursor.execute("SELECT COUNT(*) FROM candidates")
print(f"Total in database: {cursor.fetchone()[0]}")

cursor.execute("SELECT DISTINCT constituency_no, constituency_name FROM candidates ORDER BY constituency_no LIMIT 10")
print("\nFirst 10 constituencies:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
