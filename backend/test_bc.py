
import sys
import os
sys.path.append(os.path.abspath("../database"))

try:
    from blockchain import Blockchain
    bc = Blockchain()
    print("Successfully connected to blockchain DB")
    
    # Check if table exists
    with bc.conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM blockchain")
        count = cur.fetchone()[0]
        print(f"Current blocks: {count}")
        
    bc.close()
    
except Exception as e:
    print(f"Failed: {e}")
