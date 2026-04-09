"""
Blockchain Service

Wrapper around the blockchain module with vote anonymization.
Provides clean interface for:
- Adding anonymous votes
- Querying vote counts
- Verifying chain integrity
"""

import hashlib
import os
from datetime import datetime, timezone
from typing import Dict, Optional, List

from settings import get_settings


class BlockchainService:
    """
    Service for managing blockchain-based voting.
    
    Key features:
    - Anonymous vote storage
    - Chain integrity verification
    - Vote counting by candidate/constituency
    """
    
    _instance = None
    _blockchain = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize blockchain connection."""
        if self._blockchain is not None:
            return
        
        try:
            # Import the existing blockchain module
            import sys
            sys.path.insert(0, str(get_settings().base_dir.parent / "database"))
            
            from blockchain import Blockchain
            
            settings = get_settings()
            
            # Parse database URL
            # Format: postgresql://user:password@host:port/database
            db_url = settings.database_url
            
            # For now, use default connection string
            # In production, parse the URL properly
            self._blockchain = Blockchain()
            print("✅ Blockchain service initialized!")
            
        except Exception as e:
            print(f"⚠️ Failed to initialize blockchain: {e}")
            print("Blockchain voting will not be available.")
            self._blockchain = None
    
    @property
    def is_available(self) -> bool:
        """Check if blockchain is available."""
        return self._blockchain is not None
    
    def submit_vote(
        self, 
        voter_id: str, 
        candidate_id: int, 
        constituency_no: int
    ) -> Dict:
        """
        Submit an anonymous vote to the blockchain.
        
        Creates a hash of the vote that includes voter_id for uniqueness,
        but the voter_id itself is NOT stored in the blockchain.
        
        Args:
            voter_id: Voter's unique ID
            candidate_id: ID of the selected candidate
            constituency_no: Constituency number
            
        Returns:
            dict with block_index, vote_hash, and status
        """
        if not self.is_available:
            return {
                "success": False,
                "message": "Blockchain not available"
            }
        
        try:
            # The add_vote method in blockchain.py will handle
            # hash creation and block addition
            block = self._blockchain.add_vote(
                voter_id=voter_id,
                candidate_id=candidate_id,
                constituency_no=constituency_no
            )
            
            return {
                "success": True,
                "block_index": block['block_index'],
                "vote_hash": block['vote_hash'][:16] + "...",  # Partial hash
                "timestamp": block['timestamp'],
                "message": "Vote recorded successfully"
            }
            
        except Exception as e:
            print(f"Error submitting vote: {e}")
            return {
                "success": False,
                "message": f"Failed to record vote: {str(e)}"
            }
    
    def verify_chain(self) -> bool:
        """
        Verify the integrity of the blockchain.
        
        Returns True if all blocks are valid and properly linked.
        """
        if not self.is_available:
            return False
        
        try:
            return self._blockchain.verify_chain()
        except Exception as e:
            print(f"Error verifying chain: {e}")
            return False
    
    def get_vote_counts(self, constituency_no: Optional[int] = None) -> Dict:
        """
        Get vote counts from the blockchain.
        
        Args:
            constituency_no: Optional filter for specific constituency
            
        Returns:
            dict mapping candidate_id to vote count
        """
        if not self.is_available:
            return {}
        
        try:
            # Query all blocks from blockchain
            # This would need to be implemented in the blockchain module
            # For now, return placeholder
            return {}
            
        except Exception as e:
            print(f"Error getting vote counts: {e}")
            return {}
    
    def get_stats(self) -> Dict:
        """
        Get blockchain statistics.
        
        Returns:
            dict with total_blocks, chain_valid, etc.
        """
        if not self.is_available:
            return {
                "total_blocks": 0,
                "chain_valid": False,
                "message": "Blockchain not available"
            }
        
        try:
            latest = self._blockchain.get_latest_block()
            
            return {
                "total_blocks": latest['block_index'] + 1,
                "chain_valid": self._blockchain.verify_chain(),
                "latest_block_hash": self._blockchain.calculate_block_hash(latest),
                "message": "Blockchain is operational"
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                "total_blocks": 0,
                "chain_valid": False,
                "message": str(e)
            }
    
    def close(self):
        """Close blockchain connection."""
        if self._blockchain:
            try:
                self._blockchain.close()
            except:
                pass


# Note: Don't create singleton on import since it requires DB connection
# Use get_blockchain_service() instead
_blockchain_service: Optional[BlockchainService] = None


def get_blockchain_service() -> BlockchainService:
    """Get or create blockchain service instance."""
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainService()
    return _blockchain_service
