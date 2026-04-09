
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.abspath("../database"))

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

try:
    from blockchain import Blockchain
    bc = Blockchain()
    
    last_block = bc.get_latest_block()
    print("\n--- LATEST BLOCK IN CHAIN ---")
    print(json.dumps(last_block, indent=2, default=json_serial))
    print("-----------------------------")
    
    bc.close()
    
except Exception as e:
    print(f"Failed: {e}")
