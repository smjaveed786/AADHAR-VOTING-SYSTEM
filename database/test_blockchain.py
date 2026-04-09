import os
from blockchain import Blockchain

def main():
    # Initialize blockchain
    blockchain = Blockchain()
    
    try:
        # Add some test votes
        test_votes = [
            ("voter1", 1, 1),  # (voter_id, candidate_id, constituency_no)
            ("voter2", 2, 1),
            ("voter3", 3, 1),
        ]
        
        for voter_id, candidate_id, constituency_no in test_votes:
            block = blockchain.add_vote(voter_id, candidate_id, constituency_no)
            print(f"Added vote for candidate {candidate_id} in block {block['block_index']}")
            print(f"Vote hash: {block['vote_hash']}")
            print(f"Previous hash: {block['previous_hash']}\n")
        
        # Verify blockchain integrity
        is_valid = blockchain.verify_chain()
        print(f"Blockchain is {'valid' if is_valid else 'invalid'}")
        
    finally:
        blockchain.close()

if __name__ == "__main__":
    main()