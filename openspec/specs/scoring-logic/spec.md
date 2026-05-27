# scoring-logic Specification

## Purpose
Define the core scoring algorithms for survey assessments, including threshold-based dynamic text selection and persistent storage of individual results for reporting.
## Requirements
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

### Requirement: Precise Testing
Tests MUST verify the actual score logic rather than relying on assumed buckets matching hardcoded values.

#### Scenario: Participant score is below the next threshold (e.g. 69)
- **Given** a participant score of 69
- **And** thresholds defined at 50, 70, and 100
- **When** the test calculates the expected `min_score`
- **Then** it should expect the text associated with `min_score=50` (the highest threshold $\le$ score)

#### Scenario: Participant score is just below 100 (e.g. 99)
- **Given** a participant with a score of exactly 99
- **And** thresholds defined at 50, 70, and 100
- **When** the test calculates the expected `min_score`
- **Then** it should expect the text associated with `min_score=70` (the highest threshold $\le$ score), and NOT blindly validate against the 100-score text.

