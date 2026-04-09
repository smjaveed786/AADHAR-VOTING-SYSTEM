import hashlib
import json
import os
import psycopg2
from datetime import datetime
from typing import List, Dict, Optional

class Blockchain:
    def __init__(self, db_connection_string: str = "dbname=voting_system"):
        self.conn = psycopg2.connect(db_connection_string)
        self.create_tables()
        
    def create_tables(self):
        with self.conn.cursor() as cur:
            # Create blockchain table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blockchain (
                    id SERIAL PRIMARY KEY,
                    block_index INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    vote_hash VARCHAR(64) NOT NULL,
                    candidate_id INTEGER REFERENCES candidates(id),
                    constituency_no INTEGER NOT NULL,
                    previous_hash VARCHAR(64) NOT NULL,
                    nonce INTEGER DEFAULT 0
                )
            """)
            self.conn.commit()

    def create_genesis_block(self):
        """Create the first block in the blockchain (genesis block)"""
        genesis_block = {
            'block_index': 0,
            'timestamp': str(datetime.utcnow()),
            'vote_hash': self.calculate_hash("genesis"),
            'candidate_id': None,
            'constituency_no': 0,
            'previous_hash': "0" * 64,  # 64 zeros
            'nonce': 0
        }
        self._save_block(genesis_block)
        return genesis_block

    def create_vote_hash(self, voter_id: str, candidate_id: int, timestamp: str, salt: str) -> str:
        """Create a secure hash for a vote"""
        vote_data = f"{voter_id}-{candidate_id}-{timestamp}-{salt}"
        return hashlib.sha256(vote_data.encode()).hexdigest()

    def add_vote(self, voter_id: str, candidate_id: int, constituency_no: int) -> Dict:
        """Add a new vote to the blockchain"""
        # Get the last block
        last_block = self.get_latest_block()
        
        # Create vote data
        timestamp = str(datetime.utcnow())
        salt = hashlib.sha256(os.urandom(16)).hexdigest()
        vote_hash = self.create_vote_hash(voter_id, candidate_id, timestamp, salt)
        
        # Create new block
        new_block = {
            'block_index': last_block['block_index'] + 1,
            'timestamp': timestamp,
            'vote_hash': vote_hash,
            'candidate_id': candidate_id,
            'constituency_no': constituency_no,
            'previous_hash': self.calculate_block_hash(last_block),
            'nonce': 0  # For mining (simplified)
        }
        
        # Save to database
        self._save_block(new_block)
        return new_block

    def _save_block(self, block: Dict):
        """Save block to database"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO blockchain 
                (block_index, timestamp, vote_hash, candidate_id, constituency_no, previous_hash, nonce)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                block['block_index'],
                block['timestamp'],
                block['vote_hash'],
                block['candidate_id'],
                block['constituency_no'],
                block['previous_hash'],
                block['nonce']
            ))
            self.conn.commit()

    def get_latest_block(self) -> Dict:
        """Get the most recent block from the blockchain"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM blockchain 
                ORDER BY block_index DESC 
                LIMIT 1
            """)
            row = cur.fetchone()
            if not row:
                return self.create_genesis_block()
            return self._row_to_block(row)

    def get_block(self, block_index: int) -> Optional[Dict]:
        """Get a specific block by index"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM blockchain WHERE block_index = %s", (block_index,))
            row = cur.fetchone()
            return self._row_to_block(row) if row else None

    def _row_to_block(self, row) -> Dict:
        """Convert database row to block dictionary"""
        return {
            'id': row[0],
            'block_index': row[1],
            'timestamp': row[2],
            'vote_hash': row[3],
            'candidate_id': row[4],
            'constituency_no': row[5],
            'previous_hash': row[6],
            'nonce': row[7]
        }

    @staticmethod
    def calculate_hash(data: str) -> str:
        """Calculate SHA-256 hash of data"""
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def calculate_block_hash(block: Dict) -> str:
        """Calculate the hash of a block"""
        # Create a copy to avoid modifying the original block
        block_copy = block.copy()
        # Convert any datetime objects to ISO format strings
        for key, value in block_copy.items():
            if isinstance(value, datetime):
                block_copy[key] = value.isoformat()
            elif value is None:
                block_copy[key] = None
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def verify_chain(self) -> bool:
        """Verify the integrity of the blockchain"""
        current_index = 1  # Start from block 1 (genesis is 0)
        
        while True:
            current_block = self.get_block(current_index)
            if not current_block:
                break
                
            previous_block = self.get_block(current_index - 1)
            if current_block['previous_hash'] != self.calculate_block_hash(previous_block):
                return False
                
            current_index += 1
            
        return True

    def close(self):
        """Close the database connection"""
        self.conn.close()