-- Load candidates from CSV file
-- Using QUOTE to handle commas inside candidate names
\copy candidates(constituency_no, constituency_name, party, candidate) FROM '/Users/hemanthtavva/Desktop/project_final/database/candidates.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '"');

-- Verify the data was loaded
SELECT COUNT(*) as total_candidates FROM candidates;
SELECT DISTINCT constituency_no, constituency_name FROM candidates ORDER BY constituency_no LIMIT 10;
