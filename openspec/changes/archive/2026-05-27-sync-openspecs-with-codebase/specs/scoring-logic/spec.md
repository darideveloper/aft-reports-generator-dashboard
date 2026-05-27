## MODIFIED Requirements

### Requirement: Dynamic Text Selection
The system MUST select the PDF summary text based on the highest configured `min_score` that the participant has achieved, rather than using hardcoded score buckets.

#### Scenario: Participant score falls between thresholds
- **Given** the database has `TextPDFSummary` records with `min_score` 0, 50, and 80
- **When** a participant achieves a score of 65
- **Then** the report should include the text corresponding to `min_score` 50 (highest value <= 65)

#### Scenario: Participant score equals a threshold
- **Given** the database has `TextPDFSummary` records with `min_score` 0, 50, and 80
- **When** a participant achieves a score of 80
- **Then** the report should include the text corresponding to `min_score` 80
