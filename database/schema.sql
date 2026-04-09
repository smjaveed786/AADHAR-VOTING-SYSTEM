-- ============================================
-- VOTING SYSTEM DATABASE SCHEMA
-- ============================================

-- Voters table (stores registered voter data)
CREATE TABLE voters (
    id SERIAL PRIMARY KEY,
    aadhaar_number VARCHAR(12) UNIQUE NOT NULL,
    phone_number VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    voter_id VARCHAR(20) UNIQUE NOT NULL,
    constituency_no INTEGER NOT NULL,
    face_embedding BYTEA,
    has_voted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Candidates table (loaded from CSV)
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    constituency_no INTEGER NOT NULL,
    constituency_name VARCHAR(100) NOT NULL,
    party VARCHAR(100) NOT NULL,
    candidate VARCHAR(100) NOT NULL
);

-- Blockchain votes table (anonymous vote records)
CREATE TABLE blockchain (
    id SERIAL PRIMARY KEY,
    block_index INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    vote_hash VARCHAR(64) NOT NULL,
    candidate_id INTEGER REFERENCES candidates(id),
    constituency_no INTEGER NOT NULL,
    previous_hash VARCHAR(64) NOT NULL,
    nonce INTEGER DEFAULT 0
);

-- Indexes for faster queries
CREATE INDEX idx_voters_aadhaar ON voters(aadhaar_number);
CREATE INDEX idx_voters_constituency ON voters(constituency_no);
CREATE INDEX idx_candidates_constituency ON candidates(constituency_no);
CREATE INDEX idx_blockchain_constituency ON blockchain(constituency_no);
