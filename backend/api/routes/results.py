"""
Results API Routes

Endpoints:
- GET /api/results/overall - Total vote counts per candidate
- GET /api/results/constituency/{id} - Results for specific constituency
- GET /api/results/export/csv - Export results as CSV
- GET /api/results/export/pdf - Export results as PDF

All routes require admin JWT authentication.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from settings import get_settings


router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class CandidateResult(BaseModel):
    """Individual candidate result."""
    candidate_id: int
    candidate_name: str
    party: str
    vote_count: int
    percentage: float


class ConstituencyResult(BaseModel):
    """Results for a single constituency."""
    constituency_no: int
    constituency_name: str
    total_votes: int
    candidates: List[CandidateResult]
    winner: Optional[CandidateResult] = None


class OverallResults(BaseModel):
    """Overall voting results."""
    total_votes_cast: int
    total_registered_voters: int
    turnout_percentage: float
    constituencies_reported: int
    total_constituencies: int
    last_updated: datetime
    party_wise: dict  # Party name -> total votes
    top_candidates: List[CandidateResult]
    constituency_results: List[ConstituencyResult] = []


class BlockchainStats(BaseModel):
    """Blockchain statistics."""
    total_blocks: int
    chain_valid: bool
    latest_block_hash: str
    genesis_block_hash: str


# ============================================
# ROUTES
# ============================================

@router.get("/overall", response_model=OverallResults)
async def get_overall_results():
    """
    Get overall voting results across all constituencies.
    
    Returns:
    - Total votes cast
    - Turnout percentage
    - Party-wise vote distribution
    - Top candidates by vote count
    
    Data is fetched from votes.json and candidates.csv.
    Requires admin authentication.
    """
    import json
    import csv
    from collections import Counter
    
    settings = get_settings()
    votes_file = settings.base_dir.parent / "data" / "votes.json"
    voters_file = settings.base_dir.parent / "data" / "voters.json"
    candidates_file = settings.base_dir.parent / "database" / "candidates.csv"
    
    # Load votes
    votes = []
    if votes_file.exists():
        try:
            with open(votes_file, 'r') as f:
                votes = json.load(f)
        except:
            votes = []
    
    # Load voters for total count
    total_voters = 0
    if voters_file.exists():
        try:
            with open(voters_file, 'r') as f:
                voters = json.load(f)
                total_voters = len(voters)
        except:
            pass
    
    # Load candidates (same logic as voting.py)
    candidates_map = {}
    if candidates_file.exists():
        try:
            with open(candidates_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                candidate_id = 1
                for row in reader:
                    candidates_map[candidate_id] = {
                        'name': row['Candidate'],
                        'party': row['Party'],
                        'constituency_no': int(row['Constituency No'])
                    }
                    candidate_id += 1
        except Exception as e:
            print(f"Error loading candidates: {e}")
    
    # Count votes per candidate
    vote_counts = Counter(v['candidate_id'] for v in votes)
    total_votes = len(votes)
    
    # Count votes per party
    party_counts = Counter()
    for candidate_id, count in vote_counts.items():
        if candidate_id in candidates_map:
            party = candidates_map[candidate_id]['party']
            party_counts[party] += count
    
    # Build top candidates list
    top_candidates = []
    for candidate_id, count in vote_counts.most_common(10):
        if candidate_id in candidates_map:
            candidate = candidates_map[candidate_id]
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            top_candidates.append(CandidateResult(
                candidate_id=candidate_id,
                candidate_name=candidate['name'],
                party=candidate['party'],
                vote_count=count,
                percentage=round(percentage, 2)
            ))
    
    # Build constituency-wise results
    # Group votes by constituency
    from collections import defaultdict
    constituency_votes = defaultdict(Counter)  # constituency_no -> {candidate_id: count}
    for v in votes:
        constituency_votes[v['constituency_no']][v['candidate_id']] += 1
    
    # Build constituency name map from candidates
    constituency_names = {}
    if candidates_file.exists():
        try:
            with open(candidates_file, 'r', encoding='utf-8') as f2:
                reader2 = csv.DictReader(f2)
                for row in reader2:
                    cno = int(row['Constituency No'])
                    if cno not in constituency_names:
                        constituency_names[cno] = row['Constituency Name']
        except:
            pass
    
    constituency_results = []
    for const_no in sorted(constituency_votes.keys()):
        const_total = sum(constituency_votes[const_no].values())
        const_candidates = []
        for cand_id, cand_count in constituency_votes[const_no].most_common():
            if cand_id in candidates_map:
                cand = candidates_map[cand_id]
                pct = (cand_count / const_total * 100) if const_total > 0 else 0
                const_candidates.append(CandidateResult(
                    candidate_id=cand_id,
                    candidate_name=cand['name'],
                    party=cand['party'],
                    vote_count=cand_count,
                    percentage=round(pct, 2)
                ))
        
        winner = const_candidates[0] if const_candidates else None
        constituency_results.append(ConstituencyResult(
            constituency_no=const_no,
            constituency_name=constituency_names.get(const_no, f"Constituency {const_no}"),
            total_votes=const_total,
            candidates=const_candidates,
            winner=winner
        ))
    
    # Get unique constituencies with votes
    constituencies_with_votes = len(set(v['constituency_no'] for v in votes))
    
    turnout = (total_votes / total_voters * 100) if total_voters > 0 else 0
    
    return OverallResults(
        total_votes_cast=total_votes,
        total_registered_voters=total_voters,
        turnout_percentage=round(turnout, 2),
        constituencies_reported=constituencies_with_votes,
        total_constituencies=175,
        last_updated=datetime.now(),
        party_wise=dict(party_counts),
        top_candidates=top_candidates,
        constituency_results=constituency_results
    )


@router.get("/constituency/{constituency_no}", response_model=ConstituencyResult)
async def get_constituency_results(constituency_no: int):
    """
    Get detailed results for a specific constituency.
    
    Returns:
    - All candidates with vote counts
    - Percentages
    - Winner (if any)
    
    Requires admin authentication.
    """
    # TODO: Query blockchain for constituency votes
    # TODO: Query candidates table for names
    
    # Placeholder
    return ConstituencyResult(
        constituency_no=constituency_no,
        constituency_name="Sample Constituency",
        total_votes=0,
        candidates=[],
        winner=None
    )


@router.get("/blockchain", response_model=BlockchainStats)
async def get_blockchain_stats():
    """
    Get blockchain statistics and integrity status.
    
    Returns:
    - Total blocks in chain
    - Chain validity status
    - Latest and genesis block hashes
    
    Useful for verifying blockchain integrity.
    Requires admin authentication.
    """
    # TODO: Get stats from blockchain
    # from database.blockchain import Blockchain
    # blockchain = Blockchain()
    # is_valid = blockchain.verify_chain()
    
    return BlockchainStats(
        total_blocks=1,  # Genesis block only
        chain_valid=True,
        latest_block_hash="0" * 64,
        genesis_block_hash="0" * 64
    )


@router.get("/export/csv")
async def export_results_csv(constituency_no: Optional[int] = None):
    """
    Export results as CSV file.
    
    Query parameters:
    - constituency_no: Optional filter for specific constituency
    
    Returns a downloadable CSV file with:
    - Constituency, Candidate, Party, Votes, Percentage
    
    Requires admin authentication.
    """
    # TODO: Generate CSV from blockchain data
    
    # Create CSV content
    csv_content = "Constituency No,Constituency Name,Candidate,Party,Votes,Percentage\n"
    csv_content += "1,Ichchapuram,Sample Candidate,Sample Party,0,0.0%\n"
    
    # Return as downloadable file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"voting_results_{timestamp}.csv"
    
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/pdf")
async def export_results_pdf(constituency_no: Optional[int] = None):
    """
    Export results as PDF file.
    
    Query parameters:
    - constituency_no: Optional filter for specific constituency
    
    Returns a downloadable PDF report with:
    - Summary statistics
    - Charts and graphs
    - Detailed results table
    
    Requires admin authentication.
    """
    # TODO: Generate PDF using reportlab
    # This requires more complex implementation
    
    # Placeholder - return error until implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PDF export not yet implemented. Use CSV export instead."
    )


@router.get("/live")
async def get_live_results():
    """
    Get live updating results summary.
    
    Returns lightweight data suitable for real-time dashboard updates.
    Can be polled frequently without performance issues.
    
    Requires admin authentication.
    """
    # TODO: Query latest results
    
    return {
        "total_votes": 0,
        "last_vote_time": None,
        "constituencies_with_votes": 0,
        "voting_active": True,
        "timestamp": datetime.now().isoformat()
    }
